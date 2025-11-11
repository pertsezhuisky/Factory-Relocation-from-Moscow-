import pandas as pd
import math
from typing import List
import os

# Импорт модулей ядра и настроек
from core.data_model import LocationSpec, ScenarioResult
from core.location import LocationAnalyzer
from core.simulation_engine import WarehouseSimulator
from core.flexsim_bridge import FlexsimBridge
import config
from scenarios import SCENARIOS_CONFIG

class SimulationRunner:
    """
    Главный класс-оркестратор. Управляет полным циклом анализа
    и генерации результатов для заданной локации.
    """
    
    def __init__(self, location_spec: LocationSpec):
        self.location_spec = location_spec
        # Инициализируем все необходимые нам "инструменты"
        self.location_analyzer = LocationAnalyzer(location_spec)
        self.flexsim_bridge = FlexsimBridge(config.OUTPUT_DIR)
        # Готовим пустой список для сбора итоговых результатов
        self.results: List[ScenarioResult] = []

    def run_all_scenarios(self):
        """Запускает полный цикл анализа для всех сценариев из scenarios.py."""
        print(f"\n{'='*80}\nЗАПУСК АНАЛИЗА ДЛЯ ЛОКАЦИИ: '{self.location_spec.name}'\n{'='*80}")
        
        # 1. Сначала рассчитываем базовые финансовые показатели, зависящие только от локации
        base_finance = self.location_analyzer.get_base_financials()
        baseline_annual_opex = 0  # OPEX базового сценария для расчета экономии

        # 2. Проходим в цикле по каждому сценарию
        for key, params in SCENARIOS_CONFIG.items():
            print(f"\n--- Обработка сценария: {params['name']} ---")

            # 3. Расчет персонала
            staff_count = math.floor(config.INITIAL_STAFF_COUNT * (1 - params['staff_attrition_rate']))
            
            # 4. Запуск SimPy симуляции для получения операционных KPI
            print(f"  > Запуск SimPy с {staff_count} чел. и эффективностью x{params['efficiency_multiplier']}...")
            sim = WarehouseSimulator(staff_count, params['efficiency_multiplier'])
            sim_kpi = sim.run()
            print(f"  > SimPy завершен. Обработано заказов: {sim_kpi['achieved_throughput']}")

            # 5. Расчет итоговых финансовых KPI для этого сценария
            total_capex = base_finance['base_capex'] + params['hr_investment_rub'] + params['automation_investment_rub']
            opex_labor = staff_count * config.OPERATOR_SALARY_RUB_MONTH * 12
            total_opex = base_finance['base_opex'] + opex_labor

            # Запоминаем OPEX первого ("базового") сценария
            if 'No_Mitigation' in key:
                baseline_annual_opex = total_opex
            
            # 6. Расчет срока окупаемости для сценариев с автоматизацией
            payback = float('nan') # По умолчанию "не число", т.е. неприменимо
            if params['automation_investment_rub'] > 0 and baseline_annual_opex > 0:
                annual_savings = baseline_annual_opex - total_opex
                if annual_savings > 0:
                    payback = round(params['automation_investment_rub'] / annual_savings, 2)
            
            # 7. Сборка всех KPI в единую структуру данных
            result = ScenarioResult(
                location_name=self.location_spec.name,
                scenario_name=params['name'],
                staff_count=staff_count,
                throughput_orders=int(sim_kpi['achieved_throughput']),
                avg_cycle_time_min=int(sim_kpi['avg_cycle_time_min']),
                total_annual_opex_rub=int(total_opex),
                total_capex_rub=int(total_capex),
                payback_period_years=payback
            )
            # Добавляем результат в общий список
            self.results.append(result)
            
            # 8. Генерация JSON-файла для FlexSim
            self.flexsim_bridge.generate_json_config(self.location_spec, result, params)

        # 9. После завершения цикла сохраняем сводный CSV-файл
        self._save_summary_csv()
        print(f"\n--- Анализ для локации '{self.location_spec.name}' завершен. ---")

    def _save_summary_csv(self):
        """Сохраняет сводный CSV-файл со всеми результатами."""
        if not self.results: return
        
        # Преобразуем список объектов ScenarioResult в DataFrame
        df = pd.DataFrame([res.__dict__ for res in self.results])
        
        # Переименовываем колонки для совместимости с требованиями FlexSim
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