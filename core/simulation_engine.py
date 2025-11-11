# core/simulation_engine.py

"""
Единый, гибкий движок для дискретно-событийного моделирования на SimPy.
Расширенная версия с симуляцией доков, очередей грузовиков и логистики.
"""
import simpy
from typing import Dict, List
import config
import random

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


class EnhancedWarehouseSimulator(WarehouseSimulator):
    """
    Расширенная симуляция склада с моделированием:
    - Доков (inbound/outbound) как ресурсов
    - Очередей грузовиков на погрузку/разгрузку
    - Времени ожидания и утилизации доков
    """

    def __init__(self, staff_count: int, efficiency_multiplier: float,
                 inbound_docks: int = 4, outbound_docks: int = 4,
                 enable_dock_simulation: bool = True):
        """
        Args:
            staff_count: Количество операторов склада
            efficiency_multiplier: Коэффициент эффективности обработки
            inbound_docks: Количество доков для приёмки
            outbound_docks: Количество доков для отгрузки
            enable_dock_simulation: Включить симуляцию доков (False = базовая симуляция)
        """
        super().__init__(staff_count, efficiency_multiplier)

        self.enable_dock_simulation = enable_dock_simulation

        if enable_dock_simulation:
            # Доки как ресурсы SimPy
            self.inbound_docks = simpy.Resource(self.env, capacity=inbound_docks)
            self.outbound_docks = simpy.Resource(self.env, capacity=outbound_docks)

            # Статистика доков
            self.inbound_trucks_served = 0
            self.outbound_trucks_served = 0
            self.total_inbound_wait_time_min = 0.0
            self.total_outbound_wait_time_min = 0.0
            self.inbound_wait_times: List[float] = []
            self.outbound_wait_times: List[float] = []

            # Запускаем генераторы грузовиков
            self.env.process(self._inbound_truck_generator())
            self.env.process(self._outbound_truck_generator())

    def _inbound_truck_generator(self):
        """Генерирует прибытие грузовиков на приёмку (inbound)."""
        # Предполагаем, что 40% от общего числа заказов приходит через inbound
        # Среднее время между прибытиями грузовиков
        total_inbound_trucks = int(config.TARGET_ORDERS_MONTH * 0.4 / 10)  # Консолидация по 10 заказов на грузовик
        arrival_interval = (config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY) / total_inbound_trucks

        for truck_id in range(total_inbound_trucks):
            # Добавляем случайность ±20%
            actual_interval = arrival_interval * random.uniform(0.8, 1.2)
            yield self.env.timeout(actual_interval)
            self.env.process(self._process_inbound_truck(truck_id))

    def _outbound_truck_generator(self):
        """Генерирует грузовики на отгрузку (outbound)."""
        # 60% заказов идёт на outbound
        total_outbound_trucks = int(config.TARGET_ORDERS_MONTH * 0.6 / 10)
        arrival_interval = (config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY) / total_outbound_trucks

        for truck_id in range(total_outbound_trucks):
            actual_interval = arrival_interval * random.uniform(0.8, 1.2)
            yield self.env.timeout(actual_interval)
            self.env.process(self._process_outbound_truck(truck_id))

    def _process_inbound_truck(self, truck_id: int):
        """Процесс разгрузки одного грузовика на inbound доке."""
        arrival_time = self.env.now

        # Ожидание в очереди на док
        with self.inbound_docks.request() as dock_request:
            yield dock_request

            wait_time = self.env.now - arrival_time
            self.total_inbound_wait_time_min += wait_time
            self.inbound_wait_times.append(wait_time)

            # Разгрузка (120 минут в среднем)
            unloading_time = random.uniform(90, 150)
            yield self.env.timeout(unloading_time)

            self.inbound_trucks_served += 1

    def _process_outbound_truck(self, truck_id: int):
        """Процесс погрузки одного грузовика на outbound доке."""
        arrival_time = self.env.now

        # Ожидание в очереди на док
        with self.outbound_docks.request() as dock_request:
            yield dock_request

            wait_time = self.env.now - arrival_time
            self.total_outbound_wait_time_min += wait_time
            self.outbound_wait_times.append(wait_time)

            # Погрузка (90 минут в среднем)
            loading_time = random.uniform(60, 120)
            yield self.env.timeout(loading_time)

            self.outbound_trucks_served += 1

    def run(self) -> Dict[str, float]:
        """Запускает расширенную симуляцию и возвращает KPI + метрики доков."""

        # Запускаем генератор заказов
        self.env.process(self._order_generator())

        # Задаем общую длительность симуляции
        simulation_duration = config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY
        self.env.run(until=simulation_duration * 1.5)

        # Базовые KPI
        avg_cycle_time = self.total_cycle_time_min / self.processed_orders_count if self.processed_orders_count > 0 else 0

        result = {
            "achieved_throughput": self.processed_orders_count,
            "avg_cycle_time_min": round(avg_cycle_time, 2)
        }

        # Добавляем метрики доков (если включена расширенная симуляция)
        if self.enable_dock_simulation:
            avg_inbound_wait = self.total_inbound_wait_time_min / self.inbound_trucks_served if self.inbound_trucks_served > 0 else 0
            avg_outbound_wait = self.total_outbound_wait_time_min / self.outbound_trucks_served if self.outbound_trucks_served > 0 else 0

            result.update({
                "inbound_trucks_served": self.inbound_trucks_served,
                "outbound_trucks_served": self.outbound_trucks_served,
                "avg_inbound_wait_min": round(avg_inbound_wait, 2),
                "avg_outbound_wait_min": round(avg_outbound_wait, 2),
                "max_inbound_wait_min": round(max(self.inbound_wait_times) if self.inbound_wait_times else 0, 2),
                "max_outbound_wait_min": round(max(self.outbound_wait_times) if self.outbound_wait_times else 0, 2)
            })

        return result