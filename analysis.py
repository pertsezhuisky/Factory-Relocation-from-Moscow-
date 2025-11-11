from config import ScenarioParams, BASE_SALARY_RUB_MONTH, TOTAL_WAREHOUSE_AREA_SQM, ANNUAL_RENT_PER_SQM_RUB
from simulation_model import StaffManager

class KpiAnalyzer:
    """
    Отвечает за расчет и сборку всех KPI на основе
    параметров сценария и результатов симуляции.
    """

    def _calculate_annual_costs(self, staff_count: int) -> float:
        """Рассчитывает годовые операционные расходы (аренда + ФОТ)."""
        # Годовые затраты на персонал (ФОТ)
        annual_salary_cost = staff_count * BASE_SALARY_RUB_MONTH * 12
        # Годовые затраты на аренду
        annual_rent_cost = TOTAL_WAREHOUSE_AREA_SQM * ANNUAL_RENT_PER_SQM_RUB
        
        total_opex = annual_salary_cost + annual_rent_cost
        return total_opex

    def generate_kpis(self, scenario: ScenarioParams, sim_stats: dict, staff_mgr: StaffManager) -> dict:
        """
        Собирает все требуемые KPI для одного сценария в словарь.
        """
        staff_count = staff_mgr.get_staff_count()
        
        # 1. Staff Count
        kpi_staff_count = staff_count
        
        # 2. Total Operational Cost
        kpi_op_cost = self._calculate_annual_costs(staff_count)
        
        # 3. Investment
        # Включаем и CAPEX, и затраты на удержание, если они есть
        kpi_investment = scenario.capital_investment_mln_rub
        
        # 4. Achieved Throughput
        kpi_throughput = sim_stats['achieved_throughput']

        # 5. Average Cycle Time
        kpi_avg_cycle_time = sim_stats['average_cycle_time_min']
        
        return {
            "Scenario Name": scenario.name,
            "Staff Count": kpi_staff_count,
            "Total Operational Cost (RUB)": int(kpi_op_cost),
            "Investment (mln RUB)": kpi_investment,
            "Achieved Throughput": kpi_throughput,
            "Average Cycle Time (min)": kpi_avg_cycle_time
        }