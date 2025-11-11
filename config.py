# config.py

"""
Глобальные статические константы и базовые настройки проекта.
"""

# --- Финансовые и HR константы ---
INITIAL_STAFF_COUNT = 100
OPERATOR_SALARY_RUB_MONTH = 105000
TRANSPORT_TARIFF_RUB_PER_KM = 13.4  # Средний тариф для 18-20т фуры

# --- Константы склада и локации ---
WAREHOUSE_TOTAL_AREA_SQM = 17000
ANNUAL_RENT_PER_SQM_RUB = 7500.0
PURCHASE_BUILDING_COST_RUB = 1_500_000_000
BASE_EQUIPMENT_CAPEX_RUB = 350_000_000  # Стеллажи, климат, валидация
MAINTENANCE_COST_OF_OWNED_BUILDING_RUB_YEAR = 50_000_000

# --- Симуляционные константы ---
BASE_ORDER_PROCESSING_TIME_MIN = 15.0
TARGET_ORDERS_MONTH = 10000
SIMULATION_WORKING_DAYS = 20
MINUTES_PER_WORKING_DAY = 8 * 60

# --- Гео-константы для анализа ---
KEY_GEO_POINTS = {
    "Current_HUB": (55.858, 37.433),
    "Airport_SVO": (55.97, 37.41),
    "CFD_HUBs_Avg": (54.51, 36.26),
    "Moscow_Clients_Avg": (55.75, 37.62),
}

# --- Настройки вывода ---
OUTPUT_DIR = "output"
RESULTS_CSV_FILENAME = "simulation_results_dynamic.csv"