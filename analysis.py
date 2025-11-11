from config import ScenarioParams, INITIAL_STAFF, BASE_SALARY_RUB_MONTH, COST_PER_NEW_HIRE_RUB, BASE_ANNUAL_OPEX_NO_LABOR_RUB, WORKING_DAYS
from simulation_model import StaffManager

class FinancialCalculator:
    """Рассчитывает финансовые KPI на основе результатов симуляции."""
    def calculate(self, scenario: ScenarioParams, sim_stats: dict, staff_mgr: StaffManager) -> dict:
        staff_remaining = staff_mgr.get_staff_count()
        staff_to_hire = INITIAL_STAFF - staff_remaining
        
        # CAPEX
        capex = scenario.capex_mln_rub * 1_000_000
        hr_investments = scenario.hr_cost_mln_rub * 1_000_000
        
        # Annual OPEX
        labor_cost = staff_remaining * BASE_SALARY_RUB_MONTH * 12
        other_opex = BASE_ANNUAL_OPEX_NO_LABOR_RUB
        total_opex_before_savings = labor_cost + other_opex
        opex_savings = total_opex_before_savings * scenario.opex_savings_rate
        annual_opex = total_opex_before_savings - opex_savings
        
        # Year 1 Costs
        hiring_cost = staff_to_hire * COST_PER_NEW_HIRE_RUB
        total_cost_year1 = capex + hr_investments + annual_opex + hiring_cost
        
        # Throughput
        projected_monthly_throughput = (sim_stats['processed_orders'] / WORKING_DAYS) * WORKING_DAYS
        
        return {
            "Scenario Name": scenario.name,
            "Staff Remaining": staff_remaining,
            "Projected Throughput (Month)": int(projected_monthly_throughput),
            "Avg Lead Time (min)": sim_stats['avg_lead_time_min'],
            "Total Cost Year 1 (mln RUB)": round(total_cost_year1 / 1_000_000, 2),
            "CAPEX (mln RUB)": scenario.capex_mln_rub,
            "Annual Opex (mln RUB)": round(annual_opex / 1_000_000, 2),
            "HR Investment (mln RUB)": scenario.hr_cost_mln_rub,
            "Hiring Cost (mln RUB)": round(hiring_cost / 1_000_000, 2),
        }