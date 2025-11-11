import os
import pandas as pd

# Импортируем наши собственные модули
from config import SCENARIOS, SimulationConfig
from simulation_model import WarehouseModel
from analysis import FinancialCalculator

def run_full_analysis():
    """Главная функция, запускающая весь процесс."""
    
    final_results = []
    calculator = FinancialCalculator()
    
    for scenario_id in SCENARIOS.keys():
        params = SCENARIOS[scenario_id]
        config = SimulationConfig(scenario=params)
        
        # Запускаем симуляцию
        model = WarehouseModel(config)
        simulation_stats, staff_manager = model.run()
        
        # Выполняем финансовый анализ
        financial_kpi = calculator.calculate(params, simulation_stats, staff_manager)
        final_results.append(financial_kpi)
    
    return pd.DataFrame(final_results)

def display_and_save_results(results_df):
    """Форматирует, выводит в консоль и сохраняет результаты."""
    
    # Задаем желаемый порядок колонок
    column_order = [
        "Scenario Name", "Staff Remaining", "Projected Throughput (Month)",
        "Avg Lead Time (min)", "Total Cost Year 1 (mln RUB)", "CAPEX (mln RUB)",
        "Annual Opex (mln RUB)", "HR Investment (mln RUB)", "Hiring Cost (mln RUB)"
    ]
    results_df = results_df[column_order]

    print("\n" + "="*120)
    print("ИТОГОВАЯ СРАВНИТЕЛЬНАЯ ТАБЛИЦА KPI")
    print("="*120)
    print(results_df.to_string(index=False))
    print("="*120)

    # Создаем папку 'output', если она не существует
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем результаты в CSV-файл для FlexSim
    file_path = os.path.join(output_dir, 'final_kpi_for_flexsim.csv')
    results_df.to_csv(file_path, index=False, decimal='.', sep=';')
    print(f"\n✅ Итоговые KPI сохранены в файл: {file_path}")

if __name__ == "__main__":
    results_dataframe = run_full_analysis()
    display_and_save_results(results_dataframe)