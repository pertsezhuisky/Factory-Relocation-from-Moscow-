import simpy
import math
from typing import List
from config import SimulationConfig, INITIAL_STAFF, BASE_PROCESSING_TIME_MIN

class StatsCollector:
    """Собирает operational-метрики в ходе симуляции."""
    def __init__(self):
        self.completed_orders = 0
        self.lead_times: List[float] = []
        self.wait_times: List[float] = []

    def log_order_completion(self, arrival_time, start_process_time, end_time):
        self.completed_orders += 1
        self.wait_times.append(start_process_time - arrival_time)
        self.lead_times.append(end_time - arrival_time)

    def get_summary(self):
        avg_lead = sum(self.lead_times) / len(self.lead_times) if self.lead_times else 0
        avg_wait = sum(self.wait_times) / len(self.wait_times) if self.wait_times else 0
        return {
            "processed_orders": self.completed_orders,
            "avg_lead_time_min": round(avg_lead, 2),
            "avg_wait_time_min": round(avg_wait, 2),
        }

class StaffManager:
    """Управляет ресурсом 'персонал'."""
    def __init__(self, env: simpy.Environment, scenario_params):
        attrition_rate = scenario_params.attrition_rate
        raw_staff = INITIAL_STAFF * (1 - attrition_rate)
        self.staff_count = math.floor(raw_staff)
        self.resource = simpy.Resource(env, capacity=self.staff_count)
        self.process_time = BASE_PROCESSING_TIME_MIN / scenario_params.automation_efficiency

    def get_staff_count(self) -> int:
        return self.staff_count

    def get_process_time(self) -> float:
        return self.process_time

class WarehouseModel:
    """Главный класс-оркестратор симуляции."""
    def __init__(self, config: SimulationConfig):
        self.env = simpy.Environment()
        self.cfg = config
        self.stats = StatsCollector()
        self.staff_mgr = StaffManager(self.env, self.cfg.scenario)

    def _process_order(self, order_id):
        arrival_time = self.env.now
        with self.staff_mgr.resource.request() as request:
            yield request
            start_processing = self.env.now
            yield self.env.timeout(self.staff_mgr.get_process_time())
            end_processing = self.env.now
            self.stats.log_order_completion(arrival_time, start_processing, end_processing)

    def _order_generator(self):
        order_id = 0
        while True:
            yield self.env.timeout(self.cfg.arrival_interval)
            order_id += 1
            self.env.process(self._process_order(order_id))

    def run(self):
        print(f"\n>>> Запуск симуляции: '{self.cfg.scenario.name}'...")
        print(f"    Персонал: {self.staff_mgr.get_staff_count()} чел., Время обработки: {self.staff_mgr.get_process_time():.2f} мин.")
        
        self.env.process(self._order_generator())
        self.env.run(until=self.cfg.duration_minutes)
        
        sim_summary = self.stats.get_summary()
        print(f"    ...Симуляция завершена. Обработано заказов: {sim_summary['processed_orders']}")
        return sim_summary, self.staff_mgr