from dataclasses import dataclass

# --- Базовые неизменяемые параметры ---
INITIAL_STAFF = 100
BASE_SALARY_RUB_MONTH = 105000
BASE_PROCESSING_TIME_MIN = 15
TOTAL_WAREHOUSE_AREA_SQM = 15500 + 1500
ANNUAL_RENT_PER_SQM_RUB = 8000 # Стоимость аренды, руб/м²/год

TARGET_ORDERS_MONTH = 10000
WORKING_DAYS = 20
DAY_LENGTH_MIN = 8 * 60

# --- Сценарии ---
@dataclass
class ScenarioParams:
    """Хранит уникальные параметры для одного сценария."""
    id: int
    name: str
    attrition_rate: float
    capital_investment_mln_rub: float
    automation_efficiency: float = 1.0 # Коэффициент производительности

SCENARIOS = {
    1: ScenarioParams(1, "Move No Mitigation", 0.25, 0, 1.0),
    2: ScenarioParams(2, "Move With Compensation", 0.15, 50, 1.0),
    3: ScenarioParams(3, "Move Basic Automation", 0.25, 100, 1.25), # 1 / 0.8 = 1.25
    4: ScenarioParams(4, "Move Advanced Automation", 0.25, 300, 2.00),  # 1 / 0.5 = 2.0
}

@dataclass
class SimulationConfig:
    """Полная конфигурация для одного запуска симуляции."""
    scenario: ScenarioParams
    simulation_duration_days: int = 20

    @property
    def duration_minutes(self): return self.simulation_duration_days * DAY_LENGTH_MIN
    @property
    def arrival_interval(self):
        daily_target = TARGET_ORDERS_MONTH / WORKING_DAYS
        return DAY_LENGTH_MIN / daily_target