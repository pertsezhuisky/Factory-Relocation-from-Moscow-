# scenarios.py

"""
Определения и генерация данных для всех сценариев моделирования.
Ключ словаря используется внутри программы, а 'name' будет отображаться в отчетах.
"""
from typing import Dict, Any
import math
import config

SCENARIOS_CONFIG = {
    "1_Move_No_Mitigation": {
        "name": "1. Move No Mitigation",
        "staff_attrition_rate": 0.25,      # 25% уволилось
        "hr_investment_rub": 0,            # 0 руб. на удержание
        "automation_investment_rub": 0,    # 0 руб. на автоматизацию
        "efficiency_multiplier": 1.0       # Базовая эффективность
    },
    "2_Move_With_Compensation": {
        "name": "2. Move With Compensation",
        "staff_attrition_rate": 0.15,      # 15% уволилось
        "hr_investment_rub": 50_000_000,   # 50 млн руб. на удержание
        "automation_investment_rub": 0,
        "efficiency_multiplier": 1.0
    },
    "3_Move_Basic_Automation": {
        "name": "3. Move Basic Automation",
        "staff_attrition_rate": 0.25,
        "hr_investment_rub": 0,
        "automation_investment_rub": 100_000_000, # 100 млн руб. на конвейеры
        "efficiency_multiplier": 1.2               # Эффективность +20%
    },
    "4_Move_Advanced_Automation": {
        "name": "4. Move Advanced Automation",
        "staff_attrition_rate": 0.25,
        "hr_investment_rub": 0,
        "automation_investment_rub": 300_000_000, # 300 млн руб. на роботов
        "efficiency_multiplier": 1.5               # Эффективность +50%
    }
}

def generate_scenario_data(base_finance: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    """
    Генерирует полный набор данных для каждого сценария на основе базовых финансовых показателей.

    Args:
        base_finance: Словарь с 'base_capex' и 'base_opex' от LocationAnalyzer.

    Returns:
        Словарь, где ключ - ID сценария, а значение - словарь с его полными параметрами.
    """
    all_scenarios_data = {}

    for key, params in SCENARIOS_CONFIG.items():
        # Расчет персонала
        staff_count = math.floor(config.INITIAL_STAFF_COUNT * (1 - params['staff_attrition_rate']))
        
        # Расчет итоговых CAPEX и OPEX
        total_capex = base_finance['base_capex'] + params['hr_investment_rub'] + params['automation_investment_rub']
        opex_labor = staff_count * config.OPERATOR_SALARY_RUB_MONTH * 12
        total_opex = base_finance['base_opex'] + opex_labor

        all_scenarios_data[key] = {
            "name": params['name'],
            "staff_count": staff_count,
            "processing_efficiency": params['efficiency_multiplier'],
            "total_capex": total_capex,
            "total_opex": total_opex,
            "automation_investment": params['automation_investment_rub'] # Для расчета окупаемости
        }
        
    return all_scenarios_data