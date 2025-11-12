# core/simulation_engine.py

"""
Единый, гибкий движок для дискретно-событийного моделирования на SimPy.
"""
import simpy
from typing import Dict
import config

class WarehouseSimulator:
    """
    Принимает динамические операционные параметры (штат, эффективность)
    и возвращает операционные KPI по результатам симуляции.
    """
    def __init__(self, staff_count: int, efficiency_multiplier: float):
        self.env = simpy.Environment()
        
        # Динамические параметры, приходящие извне
        self.staff_count = staff_count
        self.efficiency_multiplier = efficiency_multiplier
        
        # Внутренние вычисляемые параметры
        self.order_processing_time = config.BASE_ORDER_PROCESSING_TIME_MIN / self.efficiency_multiplier
        
        # SimPy ресурсы
        self.operators = simpy.Resource(self.env, capacity=self.staff_count)
        
        # Сбор статистики
        self.processed_orders_count = 0
        self.total_cycle_time_min = 0.0

    def _process_order(self):
        """Процесс обработки одного заказа от поступления до завершения."""
        start_time = self.env.now
        
        # Запрос ресурса "оператор"
        with self.operators.request() as request:
            yield request # Ожидание, пока оператор не освободится
            # Имитация работы
            yield self.env.timeout(self.order_processing_time)
            
            # Сбор статистики после завершения обработки
            self.processed_orders_count += 1
            cycle_time = self.env.now - start_time
            self.total_cycle_time_min += cycle_time

    def _order_generator(self):
        """Генерирует поток заказов в соответствии с месячным планом."""
        # Рассчитываем, как часто должен появляться новый заказ, чтобы выполнить месячный план
        arrival_interval = (config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY) / config.TARGET_ORDERS_MONTH
        
        # Генерируем ровно целевое количество заказов
        for _ in range(config.TARGET_ORDERS_MONTH):
            self.env.process(self._process_order())
            # Ожидаем перед генерацией следующего заказа
            yield self.env.timeout(arrival_interval)

    def run(self) -> Dict[str, float]:
        """Запускает симуляцию и возвращает итоговые операционные KPI."""
        
        # Запускаем генератор заказов
        self.env.process(self._order_generator())
        
        # Задаем общую длительность симуляции с запасом по времени,
        # чтобы все сгенерированные заказы успели обработаться
        simulation_duration = config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY
        self.env.run(until=simulation_duration * 1.5)

        # Рассчитываем итоговую статистику
        avg_cycle_time = self.total_cycle_time_min / self.processed_orders_count if self.processed_orders_count > 0 else 0
        
        return {
            "achieved_throughput": self.processed_orders_count,
            "avg_cycle_time_min": round(avg_cycle_time, 2)
        }