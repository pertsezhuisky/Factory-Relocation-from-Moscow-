# scenarios.py

"""
Определения всех сценариев для моделирования.
Ключ словаря используется внутри программы, а 'name' будет отображаться в отчетах.
"""

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
        "efficiency_multiplier": 1.25              # Эффективность +25%
    },
    "4_Move_Advanced_Automation": {
        "name": "4. Move Advanced Automation",
        "staff_attrition_rate": 0.25,
        "hr_investment_rub": 0,
        "automation_investment_rub": 300_000_000, # 300 млн руб. на роботов
        "efficiency_multiplier": 2.0               # Эффективность x2
    }
}