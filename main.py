# main.py

"""
1Главный исполняемый файл.
Оркестрирует полный цикл анализа релокации склада: от ввода данных до расчета ROI.
"""
import pandas as pd
from typing import Dict, Any

# Импорт всех необходимых компонентов
from core.location import WarehouseConfigurator
from core.simulation_engine import WarehouseSimulator
from core.flexsim_bridge import FlexSimAPIBridge
from analysis import FleetOptimizer
from scenarios import generate_scenario_data
import config

def get_user_input() -> Dict[str, Any]:
    """
    Имитирует получение пользовательского ввода для выбора локации.
    Предлагает предустановленные варианты или ручной ввод.
    """
    print("\n--- Выбор локации для анализа ---")
    print("1. Логопарк Север-2 (Аренда, 35 км от МКАД, 8000 руб/м²/год)")
    print("2. Индустриальный парк 'Коледино' (Покупка, 1.5 млрд руб)")
    
    choice = input("Выберите вариант (1 или 2, Enter для варианта 1): ").strip() or "1"

    if choice == "1":
        print("Выбран: Логопарк Север-2.")
        return {
            "name": "Логопарк Север-2",
            "lat": 56.095,
            "lon": 37.388,
            "ownership_type": "ARENDA",
            "rent_rate_sqm_year": 8000.0,
            "purchase_cost": 0
        }
    elif choice == "2":
        print("Выбран: Индустриальный парк 'Коледино'.")
        return {
            "name": "Индустриальный парк 'Коледино'",
            "lat": 55.40,
            "lon": 37.58,
            "ownership_type": "POKUPKA",
            "rent_rate_sqm_year": 8000.0, # Гипотетическая ставка для расчета налога
            "purchase_cost": 1_500_000_000
        }
    else:
        print("Некорректный выбор. Используется вариант 1 по умолчанию.")
        return get_user_input()

def run_full_analysis(location_params: Dict[str, Any]):
    """
    Выполняет полный 5-шаговый анализ для выбранной локации.
    """
    print(f"\n{'='*80}\nЗАПУСК АНАЛИЗА ДЛЯ ЛОКАЦИИ: '{location_params['name']}'\n{'='*80}")

    # --- Шаг 1: Финансовая конфигурация помещения ---
    configurator = WarehouseConfigurator(
        ownership_type=location_params['ownership_type'],
        rent_rate_sqm_year=location_params['rent_rate_sqm_year'],
        purchase_cost=location_params['purchase_cost'],
        lat=location_params['lat'],
        lon=location_params['lon']
    )
    base_finance = configurator.get_base_financials()
    print(f"[Шаг 1] Базовый CAPEX (оборудование): {base_finance['base_capex']:,.0f} руб.")
    print(f"[Шаг 1] Базовый OPEX (помещение и транспорт): {base_finance['base_opex']:,.0f} руб./год")

    # --- Шаг 2: Логистический анализ ---
    fleet_optimizer = FleetOptimizer()
    required_fleet = fleet_optimizer.calculate_required_fleet()
    # Используем заглушки для расстояний, как было определено ранее
    annual_transport_cost = fleet_optimizer.calculate_annual_transport_cost(400, 30, 60)
    print(f"[Шаг 2] Требуемый собственный флот: {required_fleet} грузовиков")
    print(f"[Шаг 2] Общие транспортные расходы: {annual_transport_cost:,.0f} руб./год")

    # --- Шаг 3: Генерация 4 сценариев ---
    # Заменяем изменение транспортных расходов на полный расчет из FleetOptimizer
    base_finance['base_opex'] = configurator.calculate_annual_opex() + annual_transport_cost
    all_scenarios = generate_scenario_data(base_finance)
    print("[Шаг 3] Сгенерированы данные для 4-х сценариев (S1-S4).")

    # --- Шаг 4 и 5: Симуляция, экспорт и расчет ROI ---
    results = []
    flexsim_api = FlexSimAPIBridge(config.OUTPUT_DIR)

    # Расчет OPEX текущего склада для ROI
    current_rent_opex = 12000 * config.WAREHOUSE_TOTAL_AREA_SQM # 1000 руб/м2/мес * 12
    current_labor_opex = config.INITIAL_STAFF_COUNT * config.OPERATOR_SALARY_RUB_MONTH * 12
    total_baseline_opex = current_rent_opex + current_labor_opex

    for key, scenario_data in all_scenarios.items():
        print(f"\n--- Обработка сценария: {scenario_data['name']} ---")
        
        # Шаг 4.1: SimPy симуляция
        sim = WarehouseSimulator(scenario_data['staff_count'], scenario_data['processing_efficiency'])
        sim_kpi = sim.run()
        print(f"  > SimPy: обработано {sim_kpi['achieved_throughput']} заказов/мес.")

        # Шаг 4.2: Экспорт в JSON и имитация вызова FlexSim
        flexsim_api.generate_json_config(location_spec=type('obj', (object,), location_params)(), scenario_data=scenario_data, fleet_optimizer=fleet_optimizer)
        flexsim_api.start_simulation(key)

        # Шаг 5: Расчет ROI (Payback Period)
        annual_savings = total_baseline_opex - scenario_data['total_opex']
        payback_period = None
        if annual_savings > 0:
            payback_period = scenario_data['total_capex'] / annual_savings

        results.append({
            "Сценарий": scenario_data['name'],
            "Общий CAPEX, млн руб.": scenario_data['total_capex'] / 1_000_000,
            "Годовой OPEX, млн руб.": scenario_data['total_opex'] / 1_000_000,
            "Срок окупаемости, лет": payback_period
        })

    # --- Финальный вывод результатов ---
    print(f"\n{'='*80}\nИТОГОВЫЕ РЕЗУЛЬТАТЫ АНАЛИЗА для '{location_params['name']}'\n{'='*80}")
    
    df_results = pd.DataFrame(results)
    
    # Форматирование для красивого вывода
    df_results['Общий CAPEX, млн руб.'] = df_results['Общий CAPEX, млн руб.'].map('{:,.1f}'.format)
    df_results['Годовой OPEX, млн руб.'] = df_results['Годовой OPEX, млн руб.'].map('{:,.1f}'.format)
    df_results['Срок окупаемости, лет'] = df_results['Срок окупаемости, лет'].map(
        lambda x: f'{x:.2f}' if pd.notna(x) else 'не окупается'
    )

    print(df_results.to_string(index=False))
    print(f"\n{'='*80}")


if __name__ == "__main__":
    try:
        location_data = get_user_input()
        run_full_analysis(location_data)
    except Exception as e:
        print(f"\n[ОШИБКА] Произошла непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()