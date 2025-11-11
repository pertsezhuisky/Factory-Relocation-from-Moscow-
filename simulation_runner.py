import pandas as pd
import math
from typing import List, Optional, Dict, Any
import os

# Импорт модулей ядра и настроек
from core.data_model import LocationSpec, ScenarioResult
from core.location import WarehouseConfigurator
from core.simulation_engine import WarehouseSimulator
from core.flexsim_bridge import FlexSimAPIBridge
import config
from analysis import FleetOptimizer
from scenarios import generate_scenario_data

class SimulationRunner:
    """
    Главный класс-оркестратор. Управляет полным циклом анализа
    и генерации результатов для заданной локации.
    """
    
    def __init__(self, location_spec: LocationSpec):
        self.location_spec = location_spec
        # Инициализируем все необходимые нам "инструменты"
        self.location_analyzer = WarehouseConfigurator(location_spec.ownership_type, config.ANNUAL_RENT_PER_SQM_RUB, config.PURCHASE_BUILDING_COST_RUB, location_spec.lat, location_spec.lon)
        self.fleet_optimizer = FleetOptimizer()
        self.flexsim_bridge = FlexSimAPIBridge(config.OUTPUT_DIR)
        # Готовим пустой список для сбора итоговых результатов
        self.results: List[ScenarioResult] = []

    def run_all_scenarios(self, initial_base_finance: Optional[Dict[str, float]] = None):
        """Запускает полный цикл анализа для всех сценариев из scenarios.py."""
        print(f"\n{'='*80}\nЗАПУСК АНАЛИЗА ДЛЯ ЛОКАЦИИ: '{self.location_spec.name}'\n{'='*80}")

        # 1. Используем переданные базовые финансы или рассчитываем их
        if initial_base_finance is not None:
            base_finance = initial_base_finance
        else:
            base_finance = self.location_analyzer.get_base_financials()
        
        # 2. Генерируем полные данные для всех сценариев
        all_scenarios = generate_scenario_data(base_finance)

        print("\n--- Финансовая модель проекта ---")
        if config.CURRENT_WAREHOUSE_IS_OWNED:
            print(f"  [+] Учитывается продажа текущего актива.")
            print(f"  > Выручка от продажи: {config.CURRENT_WAREHOUSE_SALE_VALUE_RUB:,.0f} руб. (снижает CAPEX)")
        else:
            print("  [-] Продажа текущего актива не учитывается (он в аренде).")
        print("-------------------------------------------\n")

        # --- Демонстрация для Сценария 2 и 4 ---
        print("\n--- Демонстрация сгенерированных данных ---")
        s2_data = all_scenarios.get("2_Move_With_Compensation")
        s4_data = all_scenarios.get("4_Move_Advanced_Automation")

        # ИСПРАВЛЕННЫЙ БЛОК: Добавлена проверка на None
        if s2_data:
            print(f"Сценарий 2 ('{s2_data['name']}'):")
            print(f"  - Персонал: {s2_data['staff_count']} чел.")
            print(f"  - Эффективность: x{s2_data['processing_efficiency']}")
            print(f"  - Итоговый CAPEX: {s2_data['total_capex']:,.0f} руб.")
            print(f"  - Итоговый OPEX: {s2_data['total_opex']:,.0f} руб.")
        else:
            print("[ПРЕДУПРЕЖДЕНИЕ] Данные для Сценария 2 не найдены в конфигурации.")

        if s4_data:
            print(f"Сценарий 4 ('{s4_data['name']}'):")
            print(f"  - Персонал: {s4_data['staff_count']} чел.")
            print(f"  - Эффективность: x{s4_data['processing_efficiency']}")
            print(f"  - Итоговый CAPEX: {s4_data['total_capex']:,.0f} руб.")
            print(f"  - Итоговый OPEX: {s4_data['total_opex']:,.0f} руб.")
        else:
            print("[ПРЕДУПРЕЖДЕНИЕ] Данные для Сценария 4 не найдены в конфигурации.")
        
        print("-------------------------------------------\n")

        baseline_annual_opex = 0  # OPEX базового сценария для расчета экономии

        # 3. Проходим в цикле по каждому сценарию
        for key, scenario_data in all_scenarios.items():
            print(f"\n--- Обработка сценария: {scenario_data['name']} ---")

            # 4. Запуск SimPy симуляции
            print(f"  > Запуск SimPy с {scenario_data['staff_count']} чел. и эффективностью x{scenario_data['processing_efficiency']}...")
            sim = WarehouseSimulator(scenario_data['staff_count'], scenario_data['processing_efficiency'])
            sim_kpi = sim.run()
            print(f"  > SimPy завершен. Обработано заказов: {sim_kpi['achieved_throughput']}")

            # Запоминаем OPEX первого ("базового") сценария
            if 'No_Mitigation' in key:
                baseline_annual_opex = scenario_data['total_opex']
            
            # 5. Имитация получения KPI от FlexSim
            flexsim_kpi = self.flexsim_bridge.receive_kpi()
            
            # 6. Финальный расчет окупаемости (ROI / Payback Period)
            payback = self.calculate_roi(scenario_data)
            if payback is not None:
                print(f"  > Расчетный срок окупаемости: {payback:.2f} лет")

            # 7. Сборка всех KPI в единую структуру данных
            result = ScenarioResult(
                location_name=self.location_spec.name,
                scenario_name=scenario_data['name'],
                staff_count=scenario_data['staff_count'],
                throughput_orders=int(sim_kpi['achieved_throughput']),
                avg_cycle_time_min=int(sim_kpi['avg_cycle_time_min']),
                total_annual_opex_rub=int(scenario_data['total_opex']),
                total_capex_rub=int(scenario_data['total_capex']),
                payback_period_years=payback if payback is not None else float('nan')
            )
            self.results.append(result)
            
            # 8. Генерация JSON-файла для FlexSim
            self.flexsim_bridge.generate_json_config(self.location_spec, result, scenario_data)

        # 9. После завершения цикла сохраняем сводный CSV-файл
        self._save_summary_csv()
        print(f"\n--- Анализ для локации '{self.location_spec.name}' завершен. ---")

    def calculate_roi(self, scenario_data: Dict[str, Any]) -> Optional[float]:
        """
        Рассчитывает срок окупаемости (Payback Period) для сценария.
        Сравнивает OPEX нового склада с OPEX текущего склада в Москве.
        """
        # 1. Расчет OPEX текущего склада (Baseline)
        current_rent_opex = 12000 * config.WAREHOUSE_TOTAL_AREA_SQM
        current_labor_opex = config.INITIAL_STAFF_COUNT * config.OPERATOR_SALARY_RUB_MONTH * 12
        total_baseline_opex = current_rent_opex + current_labor_opex

        # 2. OPEX нового сценария (уже рассчитан)
        new_scenario_opex = scenario_data['total_opex']

        # 3. Расчет годовой экономии
        annual_savings = total_baseline_opex - new_scenario_opex

        if annual_savings > 0:
            # CAPEX для окупаемости должен быть "грязным" - без учета продажи старого актива,
            # так как это инвестиции, которые нужно понести.
            capex_for_roi = scenario_data['total_capex']
            if config.CURRENT_WAREHOUSE_IS_OWNED:
                # Возвращаем стоимость продажи, чтобы получить полную сумму инвестиций
                capex_for_roi += config.CURRENT_WAREHOUSE_SALE_VALUE_RUB
                
            payback_period_years = capex_for_roi / annual_savings
            return payback_period_years
        return None

    def _save_summary_csv(self):
        """Сохраняет сводный CSV-файл со всеми результатами."""
        if not self.results: return
        
        df = pd.DataFrame([res.__dict__ for res in self.results])
        
        column_map = {
            "location_name": "Location_Name", "scenario_name": "Scenario_Name",
            "total_annual_opex_rub": "Total_Annual_OPEX_RUB", "total_capex_rub": "Total_CAPEX_RUB",
            "throughput_orders": "Achieved_Throughput_Monthly", "staff_count": "Staff_Required",
            "payback_period_years": "Payback_Period_Years", "avg_cycle_time_min": "Avg_Cycle_Time_Min"
        }
        df = df.rename(columns=column_map)
        
        filepath = os.path.join(config.OUTPUT_DIR, config.RESULTS_CSV_FILENAME)
        df.to_csv(filepath, index=False, sep=';', decimal='.')
        print(f"\n[Runner] Сводные результаты сохранены: {filepath}")