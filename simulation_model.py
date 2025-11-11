import simpy
import math
from typing import List

from config import SimulationConfig, INITIAL_STAFF, BASE_PROCESSING_TIME_MIN, TARGET_ORDERS_MONTH

class StatsCollector:
    """Собирает operational-метрики в ходе симуляции."""
    def __init__(self):
        self.completed_orders = 0
        self.cycle_times: List[float] = []

    def log_order_completion(self, start_time, end_time):
        self.completed_orders += 1
        self.cycle_times.append(end_time - start_time)

    def get_summary(self):
        avg_cycle_time = sum(self.cycle_times) / len(self.cycle_times) if self.cycle_times else 0
        return {
            "achieved_throughput": self.completed_orders,
            "average_cycle_time_min": round(avg_cycle_time, 2),
        }

class StaffManager:
    """Управляет ресурсом 'персонал'."""
    def __init__(self, env: simpy.Environment, scenario_params):
        attrition_rate = scenario_params.attrition_rate
        raw_staff = INITIAL_STAFF * (1 - attrition_rate)
        self.staff_count = math.floor(raw_staff)
        self.resource = simpy.Resource(env, capacity=self.staff_count)
        # Время обработки вычисляется с учетом эффективности автоматизации
        self.process_time = BASE_PROCESSING_TIME_MIN / scenario_params.automation_efficiency

    def get_staff_count(self) -> int: return self.staff_count
    def get_process_time(self) -> float: return self.process_time

class WarehouseModel:
    """Главный класс-оркестратор симуляции."""
    def __init__(self, config: SimulationConfig):
        self.env = simpy.Environment()
        self.cfg = config
        self.stats = StatsCollector()
        self.staff_mgr = StaffManager(self.env, self.cfg.scenario)

    def _process_order(self, order_id):
        start_time = self.env.now
        with self.staff_mgr.resource.request() as request:
            yield request
            yield self.env.timeout(self.staff_mgr.get_process_time())
            end_time = self.env.now
            self.stats.log_order_completion(start_time, end_time)

    def _order_generator(self):
        order_id = 0
        # Теперь переменная TARGET_ORDERS_MONTH здесь корректно определена
        num_orders_to_generate = int(TARGET_ORDERS_MONTH)
        for _ in range(num_orders_to_generate):
            # Задержка перед созданием нового заказа
            yield self.env.timeout(self.cfg.arrival_interval)
            order_id += 1
            # Запуск процесса обработки
            self.env.process(self._process_order(order_id))

    def run(self):
        print(f"\n>>> Запуск симуляции: '{self.cfg.scenario.name}'...")
        print(f"    Персонал: {self.staff_mgr.get_staff_count()}, Время обработки: {self.staff_mgr.get_process_time():.2f} мин.")
        
        self.env.process(self._order_generator())
        # Запускаемся немного дольше, чтобы все сгенерированные заказы успели обработаться
        self.env.run(until=self.cfg.duration_minutes * 1.1) 
        
        sim_summary = self.stats.get_summary()
        print(f"    ...Симуляция завершена. Обработано: {sim_summary['achieved_throughput']} заказов.")
        return sim_summary, self.staff_mgr