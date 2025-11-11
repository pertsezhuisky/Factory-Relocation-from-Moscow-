# main_simulation_runner.py

import math
import pandas as pd

# Импортируем наши собственные модули
from flexible_location_model import LocationParameters, YandexGeoAnalyzer
from dynamic_simpy_model import DynamicWarehouseSim

# --- Базовые HR и операционные константы ---
INITIAL_STAFF_COUNT = 100
OPERATOR_SALARY_RUB_YEAR = 105000 * 12

def run_all_scenarios_for_location(location: LocationParameters):
    """
    Запускает симуляцию для 4-х سناريوهات, рассчитывает финансовые KPI
    и возвращает DataFrame с результатами.
    """
    
    # 1. Сначала рассчитываем базовые финансовые параметры самой локации
    location_base_finance = location.calculate_full_finance_profile()
    base_capex = location_base_finance["Initial CAPEX (RUB)"]
    base_opex_location_transport = (
        location_base_finance["Annual Location Cost (RUB)"] + 
        location_base_finance["Annual Transport Cost Change (RUB)"]
    )
    
    # 2. Определяем 4 обязательных сценария
    scenarios_config = [
        {'name': '1. Move No Mitigation', 'attrition': 0.25, 'invest_hr_rub': 0, 'invest_auto_rub': 0, 'efficiency': 1.0},
        {'name': '2. Move With Compensation', 'attrition': 0.15, 'invest_hr_rub': 50_000_000, 'invest_auto_rub': 0, 'efficiency': 1.0},
        {'name': '3. Move Basic Automation', 'attrition': 0.25, 'invest_hr_rub': 0, 'invest_auto_rub': 100_000_000, 'efficiency': 1.2},
        {'name': '4. Move Advanced Automation', 'attrition': 0.25, 'invest_hr_rub': 0, 'invest_auto_rub': 300_000_000, 'efficiency': 1.5},
    ]

    all_results = []
    baseline_annual_cost = 0 # Запомним стоимость первого сценария для расчета ROI

    # 3. Цикл по каждому сценарию
    for i, scenario in enumerate(scenarios_config):
        print(f"\n--- Анализ сценария: {scenario['name']} ---")

        # a. Готовим параметры для SimPy
        staff_count = math.floor(INITIAL_STAFF_COUNT * (1 - scenario['attrition']))
        
        # b. Запускаем симуляцию
        sim = DynamicWarehouseSim(staff_count, scenario['efficiency'])
        sim_results = sim.run()
        
        # c. Рассчитываем итоговые финансовые показатели
        total_capex = base_capex + scenario['invest_hr_rub'] + scenario['invest_auto_rub']
        
        opex_labor = staff_count * OPERATOR_SALARY_RUB_YEAR
        total_annual_cost = base_opex_location_transport + opex_labor
        
        # d. Рассчитываем ROI/Payback Period для сценариев автоматизации
        payback_years = float('nan') # По умолчанию NaN
        if i == 0:
            baseline_annual_cost = total_annual_cost
        
        if scenario['invest_auto_rub'] > 0:
            annual_savings = baseline_annual_cost - total_annual_cost
            investment_delta = scenario['invest_auto_rub']
            if annual_savings > 0:
                payback_years = investment_delta / annual_savings
            else:
                payback_years = float('inf') # Если экономии нет, окупаемость бесконечна

        # e. Собираем все KPI
        all_results.append({
            "Scenario": scenario['name'],
            "Staff Count": staff_count,
            "Throughput (Orders)": sim_results['achieved_throughput'],
            "Total Annual Cost (RUB)": int(total_annual_cost),
            "Total CAPEX (RUB)": int(total_capex),
            "Payback Period (Years)": payback_years,
        })
        
    return pd.DataFrame(all_results)

# --- ИСПОЛНЯЕМЫЙ БЛОК ---
if __name__ == "__main__":
    
    # 1. Выбираем локацию для анализа (например, Логопарк Север-2)
    # Сначала инициализируем "API" Яндекса
    geo_api = YandexGeoAnalyzer()
    # Создаем объект локации
    target_location = LocationParameters("Логопарк Север-2", 56.095, 37.388, "ARENDA", geo_api)
    
    print("="*80)
    print(f"ЗАПУСК КОМПЛЕКСНОГО АНАЛИЗА ДЛЯ ЛОКАЦИИ: '{target_location.location_name}'")
    print("="*80)

    # 2. Запускаем анализ всех 4-х سناريوهات для этой локации
    results_df = run_all_scenarios_for_location(target_location)
    
    # 3. Выводим красивую итоговую таблицу
    print("\n" + "="*80)
    print("ИТОГОВАЯ СРАВНИТЕЛЬНАЯ ТАБЛИЦА СЦЕНАРИЕВ")
    print("="*80)
    
    # Форматирование для лучшей читаемости
    results_df["Total Annual Cost (RUB)"] = results_df["Total Annual Cost (RUB)"].apply(lambda x: f"{x:,.0f}")
    results_df["Total CAPEX (RUB)"] = results_df["Total CAPEX (RUB)"].apply(lambda x: f"{x:,.0f}")
    results_df["Payback Period (Years)"] = results_df["Payback Period (Years)"].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "N/A")
    
    print(results_df.to_string(index=False))