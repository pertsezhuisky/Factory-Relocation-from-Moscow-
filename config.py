# config.py

"""
Глобальные статические константы и базовые настройки проекта.
"""

# --- Финансовые и HR константы ---
INITIAL_STAFF_COUNT = 100
OPERATOR_SALARY_RUB_MONTH = 105000
TRANSPORT_TARIFF_RUB_PER_KM = 13.4  # Средний тариф для 18-20т фуры
TRANSPORT_MAINTENANCE_RATE = 0.15  # 15% на техническое обслуживание транспорта
TRANSPORT_DOWNTIME_RATE = 0.05  # 5% на простои транспорта

# --- Дополнительные расходы на персонал ---
STAFF_TRAINING_COST_PER_PERSON = 50000  # Обучение нового сотрудника
STAFF_ADAPTATION_RATE = 0.20  # 20% от зарплаты на адаптацию
STAFF_RELOCATION_COMPENSATION = 100000  # Компенсация переезда

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

# --- Симуляционные константы ---
BASE_ORDER_PROCESSING_TIME_MIN = 15.0
BASE_ORDER_CYCLE_TIME_MIN = 15.0  # Алиас для simulation_engine
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

# --- Параметры GPP/GDP и валидации ---
GPP_GDP_VALIDATION_COST_RUB = 25_000_000  # Стоимость валидации GPP/GDP
GPP_GDP_CLIMATE_SYSTEM_COST_RUB = 150_000_000  # Климатические системы
GPP_GDP_MONITORING_COST_RUB = 20_000_000  # Системы мониторинга (температура, влажность)
GPP_GDP_ANNUAL_MAINTENANCE_RATE = 0.05  # 5% от CAPEX на годовое обслуживание

# --- Параметры автоматизации (по уровням 0-3) ---
AUTOMATION_LEVELS = {
    0: {  # Без автоматизации
        'name': 'Без автоматизации',
        'capex': 0,
        'annual_opex_rate': 0,
        'labor_reduction': 0,
        'efficiency_multiplier': 1.0
    },
    1: {  # Базовая автоматизация (WMS + сканеры)
        'name': 'Базовая автоматизация',
        'capex': 50_000_000,
        'annual_opex_rate': 0.10,  # 10% от CAPEX
        'labor_reduction': 0.20,  # 20% сокращение персонала
        'efficiency_multiplier': 1.3  # +30% производительность
    },
    2: {  # Продвинутая (WMS + конвейеры + сортировка)
        'name': 'Продвинутая автоматизация',
        'capex': 200_000_000,
        'annual_opex_rate': 0.15,
        'labor_reduction': 0.50,  # 50% сокращение
        'efficiency_multiplier': 2.0  # 2x производительность
    },
    3: {  # Полная автоматизация (AS/RS + AGV + роботы)
        'name': 'Полная автоматизация',
        'capex': 600_000_000,
        'annual_opex_rate': 0.18,
        'labor_reduction': 0.80,  # 80% сокращение
        'efficiency_multiplier': 3.5  # 3.5x производительность
    }
}

# --- Параметры HR и компенсаций (по сценариям) ---
HR_COMPENSATION_PLANS = {
    'no_mitigation': {
        'name': 'Без компенсаций',
        'cost': 0,
        'attrition_rate': 0.25  # 25% уйдут
    },
    'with_compensation': {
        'name': 'С компенсациями',
        'cost': 50_000_000,  # 50 млн на удержание
        'attrition_rate': 0.15  # 15% уйдут (снижено!)
    }
}

# --- Параметры складских операций ---
RACK_SYSTEM_COST_PER_POSITION_RUB = 15000  # Стоимость одного паллето-места
DOCK_DOOR_COST_RUB = 2_500_000  # Стоимость одной докдвери
FORKLIFT_COST_RUB = 3_000_000  # Стоимость погрузчика
FORKLIFT_ANNUAL_MAINTENANCE_RUB = 500_000  # Годовое обслуживание погрузчика

# --- Параметры климатических зон ---
CLIMATE_ZONES = {
    'normal': {  # Обычное хранение (+15...+25°C)
        'temp_range': (15, 25),
        'humidity_range': (40, 60),
        'cost_per_sqm_capex': 8000,  # руб/м² CAPEX
        'cost_per_sqm_opex_year': 1200  # руб/м²/год OPEX
    },
    'cold_chain': {  # Холодовая цепь (+2...+8°C)
        'temp_range': (2, 8),
        'humidity_range': (40, 60),
        'cost_per_sqm_capex': 25000,  # руб/м² CAPEX (дороже!)
        'cost_per_sqm_opex_year': 4500  # руб/м²/год OPEX
    },
    'frozen': {  # Заморозка (-18...-25°C)
        'temp_range': (-25, -18),
        'humidity_range': (30, 50),
        'cost_per_sqm_capex': 40000,
        'cost_per_sqm_opex_year': 8000
    }
}

# --- Параметры транспорта (детальные) ---
TRANSPORT_TYPES = {
    'truck_18t': {  # Фура 18-20т
        'capacity_pallets': 33,
        'cost_per_km_rub': 13.4,
        'purchase_cost_rub': 8_000_000,
        'lease_cost_month_rub': 250_000,
        'fuel_consumption_per_100km': 30,  # литров
        'fuel_cost_per_liter_rub': 55
    },
    'van_3_5t': {  # Газель 3.5т
        'capacity_pallets': 8,
        'cost_per_km_rub': 18.5,
        'purchase_cost_rub': 2_500_000,
        'lease_cost_month_rub': 80_000,
        'fuel_consumption_per_100km': 15,
        'fuel_cost_per_liter_rub': 55
    }
}

# --- Параметры качества и KPI ---
TARGET_ORDER_ACCURACY_PERCENT = 99.5  # Целевая точность комплектации
TARGET_ORDER_CYCLE_TIME_HOURS = 4  # Целевое время цикла заказа
MAX_ACCEPTABLE_CYCLE_TIME_HOURS = 8  # Максимально допустимое время
MIN_DOCK_UTILIZATION_PERCENT = 60  # Минимальная утилизация доков
MAX_DOCK_UTILIZATION_PERCENT = 85  # Максимальная утилизация доков

# --- Бюджетные ограничения ---
MAX_TOTAL_CAPEX_RUB = 2_500_000_000  # Максимальный бюджет CAPEX (2.5 млрд)
MAX_ANNUAL_OPEX_RUB = 500_000_000  # Максимальный годовой OPEX (500 млн)
TARGET_PAYBACK_YEARS = 5  # Целевой срок окупаемости
MAX_ACCEPTABLE_PAYBACK_YEARS = 7  # Максимально допустимый срок

# --- Требования по SKU ---
TOTAL_SKU_COUNT = 15_000  # Общее количество SKU
SKU_DISTRIBUTION = {
    'normal_storage': 0.60,  # 60% - обычное хранение
    'cold_chain': 0.30,      # 30% - холодовая цепь
    'special_handling': 0.10  # 10% - особое обращение
}

# --- Настройки вывода ---
OUTPUT_DIR = "output"
RESULTS_CSV_FILENAME = "simulation_results_dynamic.csv"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

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
        "area_offered_sqm": 20000,
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