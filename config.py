"""
Глобальные статические константы и базовые настройки проекта.
"""

# --- Финансовые и HR константы ---
INITIAL_STAFF_COUNT = 100
OPERATOR_SALARY_RUB_MONTH = 85000  # Скорректировано: средняя зарплата для региона 80-90k
STAFF_TRAINING_COST_PER_PERSON = 50000  # Единоразовые расходы на обучение нового сотрудника
STAFF_ADAPTATION_RATE = 0.20  # 20% от зарплаты в первый месяц на адаптацию
STAFF_RELOCATION_COMPENSATION = 100000  # Компенсация при переезде на человека

TRANSPORT_TARIFF_RUB_PER_KM = 13.4  # Средний тариф для 18-20т фуры
TRANSPORT_MAINTENANCE_RATE = 0.15  # 15% от транспортных расходов на ремонт
TRANSPORT_DOWNTIME_RATE = 0.05  # 5% времени в простое

# --- Параметры текущего актива (старый склад на "Сходненской") ---
CURRENT_WAREHOUSE_IS_OWNED = True  # Мы владеем текущим складом? True - да, False - нет (в аренде)
CURRENT_WAREHOUSE_SALE_VALUE_RUB = 800_000_000 # Оценочная стоимость продажи текущего склада в руб.

# --- Константы склада и локации ---
WAREHOUSE_TOTAL_AREA_SQM = 17000
MIN_AREA_SQM = 17000  # Минимально требуемая площадь
TARGET_AREA_SQM = 17500  # Целевая площадь
ANNUAL_RENT_PER_SQM_RUB = 7500.0
PURCHASE_BUILDING_COST_RUB = 1_500_000_000
BASE_EQUIPMENT_CAPEX_RUB = 350_000_000  # Стеллажи, климат, валидация
MAINTENANCE_COST_OF_OWNED_BUILDING_RUB_YEAR = 50_000_000

# --- Экономические константы ---
INFLATION_RATE = 0.08  # 8% годовая инфляция для корректировки CAPEX
EQUIPMENT_OPEX_MAINTENANCE_RATE = 0.18  # 18% от CAPEX на обслуживание оборудования в год
EMERGENCY_REPAIR_BUDGET_RATE = 0.05  # 5% бюджета на незапланированные ремонты

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

# --- Новые константы: Ограничения для грузовиков в Москве ---
MOSCOW_RESTRICTION_TONNAGE = 3.5  # Максимальная грузоподъемность в тоннах без пропуска
FREE_PASSES_PER_MONTH = 2         # Количество бесплатных рейсов в месяц для >3.5т
# Повышенный тариф для моделирования использования более мелкого и дорогого транспорта в Москве
MOSCOW_DELIVERY_TARIFF_RUB_PER_KM = 18.5 

# --- Настройки вывода ---
OUTPUT_DIR = "output"
RESULTS_CSV_FILENAME = "simulation_results_dynamic.csv"

# --- Кандидаты на релокацию (имитация данных из парсера) ---
ALL_CANDIDATE_LOCATIONS = {
    "logopark_sever_2": {
        "name": "Логопарк Север-2",
        "type": "ARENDA",
        "lat": 56.03,
        "lon": 37.59,
        "area_offered_sqm": 17000,
        "cost_metric_base": 8000.0,  # руб/м²/год
        "current_class": "A_verified"
    },
    "bely_rast": {
        "name": "Белый Раст Логистика",
        "type": "ARENDA",
        "lat": 56.09,
        "lon": 37.49,
        "area_offered_sqm": 20000,
        "cost_metric_base": 10000.0, # руб/м²/год
        "current_class": "A_verified"
    },
    "troitse_seltso": {
        "name": "Склад Троице-сельцо",
        "type": "ARENDA",
        "lat": 55.98,
        "lon": 37.60,
        "area_offered_sqm": 25000,
        "cost_metric_base": 15000.0, # руб/м²/год
        "current_class": "A_requires_mod"
    },
    "plt_severnoe_sheremetievo": {
        "name": "ПЛТ Северное Шереметьево",
        "type": "ARENDA",
        "lat": 56.00,
        "lon": 37.50,
        "area_offered_sqm": 30000,
        "cost_metric_base": 10000.0, # руб/м²/год
        "current_class": "A_verified"
    },
    "pnk_chashnikovo": {
        "name": "PNK Чашниково BTS",
        "type": "POKUPKA_BTS",
        "lat": 56.01,
        "lon": 37.10,
        "area_offered_sqm": 17500,
        "cost_metric_base": 1_500_000_000, # общая стоимость
        "current_class": "A_requires_mod"
    },
    "esipovo_bts": {
        "name": "Деревня Есипово BTS",
        "type": "POKUPKA_BTS",
        "lat": 56.02,
        "lon": 37.00,
        "area_offered_sqm": 25000,
        "cost_metric_base": 2_000_000_000, # общая стоимость
        "current_class": "A_requires_mod"
    }
}