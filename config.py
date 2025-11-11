from dataclasses import dataclass

# --- Базовые неизменяемые параметры ---
INITIAL_STAFF = 100
BASE_SALARY_RUB_MONTH = 105000
BASE_PROCESSING_TIME_MIN = 15
TARGET_ORDERS_MONTH = 10000
WORKING_DAYS = 20
DAY_LENGTH_MIN = 8 * 60

# --- Финансовые допущения ---
COST_PER_NEW_HIRE_RUB = 200000  # Стоимость найма и обучения одного нового сотрудника
BASE_ANNUAL_OPEX_NO_LABOR_RUB = 150_000_000  # Базовые годовые OPEX (аренда, транспорт и т.д.) без ФОТ

# --- Структуры данных для сценариев ---
@dataclass
class ScenarioParams:
    """Хранит уникальные параметры для одного сценария."""
    id: int
    name: str
    attrition_rate: float
    capex_mln_rub: float
    automation_efficiency: float = 1.0
    opex_savings_rate: float = 0.0
    hr_cost_mln_rub: float = 0

# --- Определение 4-х сценариев ---
SCENARIOS = {
    1: ScenarioParams(1, "Move No Mitigation", 0.25, 0, 1.0, 0.0, 0),
    2: ScenarioParams(2, "Move With Compensation", 0.15, 0, 1.0, 0.0, 50),
    3: ScenarioParams(3, "Move Basic Automation", 0.25, 100, 1.20, 0.15),
    4: ScenarioParams(4, "Move Advanced Automation", 0.25, 300, 1.50, 0.35),
}

@dataclass
class SimulationConfig:
    """Полная конфигурация для одного запуска симуляции."""
    scenario: ScenarioParams
    simulation_duration_days: int = 20

    @property
    def duration_minutes(self):
        return self.simulation_duration_days * DAY_LENGTH_MIN

    @property
    def orders_per_month_target(self):
        return TARGET_ORDERS_MONTH

    @property
    def arrival_interval(self):
        daily_target = self.orders_per_month_target / WORKING_DAYS
        return DAY_LENGTH_MIN / daily_target