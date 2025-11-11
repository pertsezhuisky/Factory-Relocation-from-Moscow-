# dynamic_simpy_model.py

import simpy
import math
from typing import Dict

# --- Базовые операционные константы ---
BASE_PROCESSING_TIME_MIN = 15.0 # Время обработки 1 заказа без автоматизации
TARGET_ORDERS_MONTH = 10000
WORKING_DAYS = 20
DAY_LENGTH_MIN = 8 * 60

class DynamicWarehouseSim:
    """
    Гибкая SimPy модель, принимающая динамические параметры
    для одного симуляционного прогона.
    """
    def __init__(self, staff_count: int, efficiency_multiplier: float):
        self.env = simpy.Environment()
        
        # Динамические параметры
        self.staff_count = staff_count
        self.order_processing_time = BASE_PROCESSING_TIME_MIN / efficiency_multiplier
        
        # Ресурсы
        self.operators = simpy.Resource(self.env, capacity=self.staff_count)
        
        # Сбор статистики
        self.processed_orders = 0
        self.total_cycle_time = 0.0

    def _process_order(self):
        start_time = self.env.now
        with self.operators.request() as request:
            yield request
            yield self.env.timeout(self.order_processing_time)
            
            # Логируем результат после завершения обработки
            self.processed_orders += 1
            self.total_cycle_time += (self.env.now - start_time)

    def _order_generator(self):
        # Рассчитываем интервал поступления заказов для достижения цели
        arrival_interval = (WORKING_DAYS * DAY_LENGTH_MIN) / TARGET_ORDERS_MONTH
        
        for _ in range(TARGET_ORDERS_MONTH):
            self.env.process(self._process_order())
            yield self.env.timeout(arrival_interval)

    def run(self) -> Dict[str, float]:
        """Запускает симуляцию и возвращает операционные KPI."""
        
        print(f"    ▶️ Запуск SimPy: {self.staff_count} чел., скорость x{self.order_processing_time/BASE_PROCESSING_TIME_MIN:.2f}...")
        
        # Запускаем генератор заказов
        self.env.process(self._order_generator())
        
        # Запускаем симуляцию (с небольшим запасом времени, чтобы все заказы успели обработаться)
        self.env.run(until=(WORKING_DAYS * DAY_LENGTH_MIN) * 1.5)

        avg_cycle_time = self.total_cycle_time / self.processed_orders if self.processed_orders > 0 else 0
        
        print(f"    ⏹️ SimPy завершен. Обработано заказов: {self.processed_orders}")

        return {
            "achieved_throughput": self.processed_orders,
            "avg_cycle_time_min": avg_cycle_time
        }