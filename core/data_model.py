# core/data_models.py

"""
Структуры данных (dataclasses) для типизации и чистоты кода.
"""
from dataclasses import dataclass

@dataclass
class LocationSpec:
    """Полное описание анализируемой локации."""
    name: str
    lat: float
    lon: float
    ownership_type: str  # "ARENDA" или "POKUPKA"

@dataclass
class ScenarioResult:
    """Хранит все итоговые KPI, рассчитанные для одного сценария."""
    location_name: str
    scenario_name: str
    staff_count: int
    throughput_orders: int
    avg_cycle_time_min: float
    total_annual_opex_rub: int
    total_capex_rub: int
    payback_period_years: float