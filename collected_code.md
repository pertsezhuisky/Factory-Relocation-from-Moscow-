## `core\data_model.py`

```py
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
```

## `core\flexsim_bridge.py`

```py
"""
Модуль для взаимодействия с FlexSim: генерация JSON и имитация API.
"""
import json
import os
from typing import Dict, Any, Optional

import config
from core.data_model import LocationSpec, ScenarioResult
from analysis import FleetOptimizer

class FlexSimAPIBridge:
    """
    Управляет созданием конфигурационных файлов для FlexSim и
    имитирует отправку команд через Socket API.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[FlexSimAPIBridge] Инициализирован. Выходная директория: '{self.output_dir}'")

    def send_config(self, json_data: dict) -> bool:
        """Имитирует отправку JSON-конфигурации через сокет."""
        print("  > [API] Отправка конфигурации в FlexSim...")
        response = self._send_command("LOAD_CONFIG", data=json_data)
        return response.get("status") == "OK"

    def start_simulation(self, scenario_id: str) -> bool:
        """Имитирует команду запуска симуляции в FlexSim."""
        print(f"  > [API] Запуск симуляции для сценария '{scenario_id}'...")
        response = self._send_command("START_SIMULATION", data={"scenario": scenario_id})
        return response.get("status") == "OK"

    def receive_kpi(self) -> Dict[str, Any]:
        """Имитирует прием ключевых метрик от FlexSim."""
        print("  > [API] Получение KPI от FlexSim...")
        response = self._send_command("GET_KPI")
        if response.get("status") == "OK":
            # Возвращаем пример словаря, как указано в задаче
            kpi_data = {
                'achieved_throughput': 10500, 
                'resource_utilization': 0.85
            }
            print(f"  > [API] Получены KPI: {kpi_data}")
            return kpi_data
        return {}

    def generate_json_config(self, location_spec: LocationSpec, scenario_result: ScenarioResult, scenario_data: dict):
        """Создает и сохраняет JSON-конфигурацию для одного сценария."""

        # Создаем экземпляр FleetOptimizer для расчетов
        fleet_optimizer = FleetOptimizer()

        # Определяем тип автоматизации на основе инвестиций
        automation_investment = scenario_data.get('automation_investment', 0)
        automation_type = "None"
        if automation_investment == 100_000_000:
            automation_type = "Conveyors+WMS"
        elif automation_investment > 100_000_000:
            automation_type = "AutoStore+AGV"
            
        config_data = {
            "FINANCIALS": {
                "Total_CAPEX": scenario_data['total_capex'],
                "Annual_OPEX": scenario_data['total_opex']
            },
            "LAYOUT": {
                "Total_Area_SQM": config.WAREHOUSE_TOTAL_AREA_SQM,
                "Ceiling_Height": 12,
                "GPP_ZONES": [
                    {"Zone": "Cool_2_8C", "Pallet_Capacity": 3000},
                    {"Zone": "Controlled_15_25C", "Pallet_Capacity": 17000}
                ]
            },
            "RESOURCES": {
                "Staff_Operators": scenario_data['staff_count'],
                "Automation_Type": automation_type,
                "Processing_Time_Coefficient": scenario_data['processing_efficiency']
            },
            "LOGISTICS": {
                "Location_Coords": [location_spec.lat, location_spec.lon],
                "Required_Own_Fleet_Count": fleet_optimizer.calculate_required_fleet(),
                "Delivery_Flows": [
                    {"Dest": "SVO_Aviation", "Volume_Pct": fleet_optimizer.AIR_DELIVERY_SHARE * 100},
                    {"Dest": "CFD_Own_Fleet", "Volume_Pct": fleet_optimizer.CFO_OWN_FLEET_SHARE * 100},
                    {"Dest": "Moscow_LPU", "Volume_Pct": fleet_optimizer.LOCAL_DELIVERY_SHARE * 100}
                ]
            }
        }
        
        # Формируем имя файла на основе имени сценария
        scenario_name = scenario_data.get('name', 'Unknown_Scenario')
        safe_scenario_name = scenario_name.replace('. ', '_').replace(' ', '_')
        filename = f"flexsim_setup_{safe_scenario_name}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        print(f"  > [OK] JSON-конфиг сохранен: {filename}")
        
        # Демонстрация для Сценария 4
        if "4_Move_Advanced_Automation" in safe_scenario_name:
            print("\n--- Демонстрация JSON для Сценария 4 ---")
            print(json.dumps(config_data, ensure_ascii=False, indent=4))
            print("-----------------------------------------\n")

    def _send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Имитирует отправку команды FlexSim (stub-версия из api_bridge.py)."""
        # print(f"[FlexSimAPIBridge STUB] Отправка команды '{command}'...")
        try:
            # Имитируем ошибку подключения, так как сервера нет
            raise ConnectionRefusedError("No FlexSim server is listening (as expected for a stub).")
        except ConnectionRefusedError as e:
            # print(f"[FlexSimAPIBridge STUB] Ошибка (это нормально для заглушки): {e}")
            if command == "LOAD_CONFIG":
                return {"status": "OK", "message": "Configuration loaded."}
            elif command == "START_SIMULATION":
                return {"status": "OK", "message": "Simulation started."}
            elif command == "GET_KPI":
                 return {"status": "OK", "kpi": {"achieved_throughput": 10500, "resource_utilization": 0.85}}
            return {"status": "ERROR", "message": "Unknown command"}
```

## `core\location.py`

```py
# core/location.py

"""
Модуль для конфигурации склада и расчета базовых финансовых показателей (CAPEX, OPEX).
"""
from typing import Dict, Tuple
from math import radians, sin, cos, sqrt, atan2

import config

class WarehouseConfigurator:
    """
    Рассчитывает базовые CAPEX и OPEX для склада, включая затраты на помещение и оборудование.
    """
    def __init__(self, ownership_type: str, rent_rate_sqm_year: float, purchase_cost: float, lat: float, lon: float):
        # Нормализуем тип владения: POKUPKA_BTS -> POKUPKA
        if ownership_type == "POKUPKA_BTS":
            ownership_type = "POKUPKA"

        if ownership_type not in {"ARENDA", "POKUPKA"}:
            raise ValueError("Неверный тип владения: должен быть 'ARENDA', 'POKUPKA' или 'POKUPKA_BTS'")

        self.ownership_type = ownership_type
        self.rent_rate_sqm_year = rent_rate_sqm_year
        self.purchase_cost = purchase_cost
        self.lat = lat
        self.lon = lon

    def calculate_fixed_capex(self) -> float:
        """Рассчитывает обязательные первоначальные инвестиции (CAPEX) для склада."""
        capex_racking = 50_000_000  # Стеллажное оборудование
        capex_climate = 250_000_000 # Климатическое оборудование (установка + настройка)
        return capex_racking + capex_climate

    def calculate_annual_opex(self) -> float:
        """Рассчитывает годовые операционные расходы (OPEX) на помещение."""
        total_area = 17000  # Общая площадь в м²
        if self.ownership_type == "ARENDA":
            return total_area * self.rent_rate_sqm_year
        else:  # POKUPKA
            # Налог/обслуживание как 15% от гипотетической стоимости аренды
            return (total_area * self.rent_rate_sqm_year) * 0.15

    def _haversine_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Расчет расстояния по прямой с коэффициентом на кривизну дорог."""
        R = 6371.0  # Радиус Земли в километрах
        lat1, lon1, lat2, lon2 = map(radians, [p1[0], p1[1], p2[0], p2[1]])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Коэффициент 1.4 для имитации реального пробега по дорогам
        return (R * c) * 1.4

    def get_transport_cost_change_rub(self) -> float:
        """Рассчитывает годовое ИЗМЕНЕНИЕ транспортных расходов при переезде."""
        total_dist_increase_km = 0
        new_hub_coords = (self.lat, self.lon)
        # Ключевые точки доставки: аэропорт и усредненные центры для ЦФО и Москвы
        key_points = [
            config.KEY_GEO_POINTS["Airport_SVO"],
            config.KEY_GEO_POINTS["CFD_HUBs_Avg"],
            config.KEY_GEO_POINTS["Moscow_Clients_Avg"]
        ]
        
        for point in key_points:
            dist_old = self._haversine_distance(config.KEY_GEO_POINTS["Current_HUB"], point)
            dist_new = self._haversine_distance(new_hub_coords, point)
            total_dist_increase_km += (dist_new - dist_old)

        avg_dist_increase_per_trip = total_dist_increase_km / len(key_points)
        
        # Допущение: каждый заказ - это условная поездка для оценки относительного изменения
        total_annual_extra_km = avg_dist_increase_per_trip * (config.TARGET_ORDERS_MONTH * 12)
        
        return total_annual_extra_km * config.TRANSPORT_TARIFF_RUB_PER_KM

    def get_base_financials(self) -> Dict[str, float]:
        """
        Рассчитывает базовые CAPEX и OPEX, зависящие ТОЛЬКО от локации и типа владения.
        OPEX здесь включает в себя аренду/обслуживание здания и изменение транспортных расходов.
        """
        base_capex = self.calculate_fixed_capex()
        base_opex_location = self.calculate_annual_opex()

        if self.ownership_type == "POKUPKA":
            base_capex += self.purchase_cost

        # Суммируем OPEX от локации (аренда/обслуживание) и OPEX от транспорта
        total_base_opex = base_opex_location + self.get_transport_cost_change_rub()

        return {
            "base_capex": base_capex,
            "base_opex": total_base_opex
        }
```

## `core\simulation_engine.py`

```py
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
```

## `core\__init__.py`

```py

```

## `analysis.py`

```py
"""
Скрипт для анализа и визуализации результатов ПОСЛЕ выполнения симуляции.
Запускается отдельно командой: python analysis.py

ВАЖНО: Использует бесплатные API:
- OSRM (https://router.project-osrm.org) для маршрутизации
- Nominatim/geopy для геокодирования
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config
import math
import requests  # Для HTTP-запросов к OSRM API
import time
from typing import Optional, Dict, Tuple
from geopy.geocoders import Nominatim  # Для геокодирования адресов
# from bs4 import BeautifulSoup  # Для парсинга HTML ЦИАН/Яндекс.Недвижимость (опционально)

# Импорт детального транспортного планировщика
from transport_planner import DetailedFleetPlanner, DockSimulator

class AvitoParserStub:
    """
    Заглушка для парсера Авито/ЦИАН. Фильтрует и оценивает локации
    по требованиям фармацевтического склада.
    """
    # 1. Константы на основе требований
    REQUIRED_TOTAL_AREA = 17000
    CAPEX_FIXED_EQUIPMENT = 50_000_000       # Стеллажное оборудование
    CAPEX_GPP_GDP_CLIMATE = 250_000_000      # Установка и валидация климатики
    CAPEX_MODIFICATION_IF_NEEDED = 100_000_000 # Доведение до класса А/фармстандартов

    def filter_and_score_locations(self, candidate_locations: dict) -> list:
        """
        Фильтрует и оценивает локации из предоставленного списка.
        """
        scored_locations = []
        
        for key, loc in candidate_locations.items():
            # 2.1 Фильтрация по площади
            if loc['area_offered_sqm'] < self.REQUIRED_TOTAL_AREA:
                continue

            # 2.2 Расчет CAPEX
            total_initial_capex = self.CAPEX_FIXED_EQUIPMENT + self.CAPEX_GPP_GDP_CLIMATE

            # 2.3 Условная модификация
            if loc['current_class'] == 'A_requires_mod':
                total_initial_capex += self.CAPEX_MODIFICATION_IF_NEEDED

            # 2.4 Расчет OPEX (помещение) и добавление стоимости покупки в CAPEX
            annual_building_opex = 0
            if loc['type'] == 'ARENDA':
                annual_building_opex = loc['cost_metric_base'] * loc['area_offered_sqm']
            elif loc['type'] == 'POKUPKA_BTS':
                # Добавляем стоимость самого здания в CAPEX
                total_initial_capex += loc['cost_metric_base']
                # Расчет условных расходов на обслуживание
                notional_rent_rate = 7000  # руб/м²/год
                annual_building_opex = (notional_rent_rate * loc['area_offered_sqm']) * 0.05

            scored_locations.append({
                "location_name": loc['name'],
                "lat": loc['lat'],
                "lon": loc['lon'],
                "type": loc['type'],
                "area_offered_sqm": loc['area_offered_sqm'],
                "annual_building_opex": annual_building_opex,
                "total_initial_capex": total_initial_capex,
                "current_class": loc['current_class']
            })

        return scored_locations


# ============================================================================
# ПРОМПТ 1: Полный Парсер Авито/ЦИАН (Класс AvitoCIANScraper)
# ============================================================================

class AvitoCIANScraper:
    """
    Полный парсер Авито/ЦИАН с имитацией реальных HTTP-запросов и обработки HTML/JSON.
    Этот класс демонстрирует, как бы выглядел настоящий парсер с использованием
    requests и BeautifulSoup для получения и обработки данных о складах класса А/GPP.
    """

    # Константы требований к складу (основаны на фармацевтических стандартах)
    REQUIRED_TOTAL_AREA = 17000  # м² - минимальная требуемая площадь
    CAPEX_FIXED_EQUIPMENT = 50_000_000  # руб. - новое стеллажное оборудование
    CAPEX_GPP_GDP_CLIMATE = 250_000_000  # руб. - установка и валидация климатических систем (2-8°C и 15-25°C)
    CAPEX_MODIFICATION_IF_NEEDED = 50_000_000  # руб. - дополнительные затраты на доведение до стандарта

    def __init__(self):
        """Инициализация парсера с базовыми настройками."""
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

    def fetch_raw_offers_data(self, search_url: Optional[str] = None) -> dict:
        """
        Имитирует реальный HTTP-запрос к API Авито/ЦИАН для получения списка объектов.

        В реальной реализации здесь был бы код:
        -----------------------------------------------
        response = requests.get(search_url, headers=self.session_headers, timeout=30)
        if response.status_code == 200:
            raw_json = response.json()
            return raw_json['offers']
        -----------------------------------------------

        Args:
            search_url: URL для поиска складов (в stub-режиме игнорируется)

        Returns:
            Словарь с "сырыми" данными объектов (имитация JSON-ответа API)
        """
        print("  > [HTTP] Имитация запроса к API Авито/ЦИАН...")
        print(f"  > [HTTP] URL: {search_url or 'https://api.avito.ru/search?category=warehouse&city=moscow'}")
        print("  > [HTTP] Статус: 200 OK")
        print("  > [HTTP] Content-Type: application/json")

        # В stub-режиме возвращаем данные из config.py
        # В реальном режиме здесь был бы парсинг JSON-ответа от API
        raw_data = config.ALL_CANDIDATE_LOCATIONS
        print(f"  > [HTTP] Получено объектов: {len(raw_data)}")

        return raw_data

    def parse_and_filter_offers(self, raw_data: dict) -> list:
        """
        Имитирует парсинг HTML/JSON с использованием BeautifulSoup и фильтрацию по требованиям.

        В реальной реализации здесь был бы код:
        -----------------------------------------------
        soup = BeautifulSoup(html_content, 'html.parser')
        for offer_block in soup.find_all('div', class_='offer-card'):
            title = offer_block.find('h3', class_='title').text
            area = float(offer_block.find('span', class_='area').text.replace(' м²', ''))
            ...
        -----------------------------------------------

        Args:
            raw_data: Сырые данные от API

        Returns:
            Список финансово оцененных и отфильтрованных локаций
        """
        print("\n  > [PARSER] Запуск парсинга и фильтрации объектов...")
        scored_locations = []

        for key, loc in raw_data.items():
            # Имитация извлечения данных из HTML (в реальности через BeautifulSoup)
            print(f"    - Обработка: '{loc['name']}'")

            # ====== ФИЛЬТРАЦИЯ ПО ПЛОЩАДИ ======
            if loc['area_offered_sqm'] < self.REQUIRED_TOTAL_AREA:
                print(f"      [SKIP] Площадь {loc['area_offered_sqm']} кв.м < требуемых {self.REQUIRED_TOTAL_AREA} кв.м")
                continue

            # ====== РАСЧЕТ CAPEX GPP/GDP ======
            # Базовый CAPEX всегда включает:
            # 1. Стеллажное оборудование (50 млн)
            # 2. Климатические системы GPP/GDP (250 млн)
            total_initial_capex = self.CAPEX_FIXED_EQUIPMENT + self.CAPEX_GPP_GDP_CLIMATE

            # Если помещение требует модификации до класса А
            if loc['current_class'] == 'A_requires_mod':
                total_initial_capex += self.CAPEX_MODIFICATION_IF_NEEDED
                print(f"      [CAPEX] +{self.CAPEX_MODIFICATION_IF_NEEDED:,} руб. на модификацию до класса А")

            # ====== РАСЧЕТ OPEX (ПОМЕЩЕНИЕ) ======
            annual_building_opex = 0

            if loc['type'] == 'ARENDA':
                # Для аренды: стоимость = тариф * площадь
                annual_building_opex = loc['cost_metric_base'] * loc['area_offered_sqm']
                print(f"      [OPEX] Аренда: {loc['cost_metric_base']:,.0f} руб/кв.м * {loc['area_offered_sqm']} кв.м = {annual_building_opex:,.0f} руб/год")

            elif loc['type'] == 'POKUPKA_BTS':
                # Для покупки/BTS:
                # 1. Добавляем стоимость здания в CAPEX
                total_initial_capex += loc['cost_metric_base']
                print(f"      [CAPEX] Стоимость здания: +{loc['cost_metric_base']:,} руб.")

                # 2. OPEX = условные расходы на обслуживание (5% от гипотетической аренды)
                notional_rent_rate = 7000  # руб/м²/год
                annual_building_opex = (notional_rent_rate * loc['area_offered_sqm']) * 0.05
                print(f"      [OPEX] Обслуживание (5%): {annual_building_opex:,.0f} руб/год")

            # ====== ФОРМИРОВАНИЕ РЕЗУЛЬТАТА ======
            scored_locations.append({
                "location_name": loc['name'],
                "lat": loc['lat'],
                "lon": loc['lon'],
                "type": loc['type'],
                "area_offered_sqm": loc['area_offered_sqm'],
                "annual_building_opex": annual_building_opex,
                "total_initial_capex": total_initial_capex,
                "current_class": loc['current_class']
            })

            print(f"      [OK] Итоговый CAPEX: {total_initial_capex:,} руб, Годовой OPEX: {annual_building_opex:,.0f} руб/год")

        print(f"\n  > [PARSER] Фильтрация завершена. Подходящих локаций: {len(scored_locations)}")
        return scored_locations


# ============================================================================
# ПРОМПТ 2: Бесплатный роутер на OSRM (Класс OSRMGeoRouter)
# ============================================================================

class OSRMGeoRouter:
    """
    Бесплатный геороутер на базе OSRM API и Nominatim для геокодирования.

    OSRM (Open Source Routing Machine) - бесплатный API для маршрутизации:
    - Публичный сервер: https://router.project-osrm.org
    - Не требует API ключей или регистрации
    - Формат координат: lon,lat (долгота, широта)

    Nominatim - бесплатный геокодер OpenStreetMap через geopy:
    - Преобразование адресов в координаты
    - Требует User-Agent и соблюдения rate limits (1 запрос/сек)
    """

    # Константы координат ключевых точек (формат: lat, lon)
    CURRENT_HUB_COORDS = (55.857, 37.436)  # Сходненская (текущий склад)
    SVO_COORDS = (55.97, 37.41)  # Аэропорт Шереметьево
    AVG_LPU_COORDS = (55.75, 37.62)  # Усредненный клиент ЛПУ (Москва)
    AVG_CFD_COORDS = (54.51, 36.26)  # Усредненный хаб ЦФО (Калуга/Тула)

    # OSRM API endpoints
    OSRM_BASE_URL = "https://router.project-osrm.org"

    def __init__(self, use_geocoding: bool = False):
        """
        Инициализация роутера.

        Args:
            use_geocoding: Использовать ли Nominatim для геокодирования адресов
        """
        self.use_geocoding = use_geocoding

        if use_geocoding:
            # Инициализируем геокодер Nominatim
            # ВАЖНО: Необходимо указать User-Agent для соблюдения правил использования
            self.geolocator = Nominatim(user_agent="warehouse_relocation_analyzer/1.0")

        # Кэш для геокодирования (чтобы не делать повторные запросы)
        self.geocode_cache = {}

        # Счетчик запросов для rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Минимум 1 секунда между запросами к Nominatim

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Преобразует адрес в координаты используя Nominatim (geopy).

        Args:
            address: Адрес для геокодирования

        Returns:
            Кортеж (lat, lon) или None если адрес не найден
        """
        if not self.use_geocoding:
            print(f"  > [Geocoding] Отключено. Используйте координаты напрямую.")
            return None

        # Проверяем кэш
        if address in self.geocode_cache:
            print(f"  > [Geocoding Cache] '{address}' -> {self.geocode_cache[address]}")
            return self.geocode_cache[address]

        try:
            # Соблюдаем rate limit (1 запрос/сек для Nominatim)
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)

            print(f"  > [Nominatim] Геокодирование адреса: '{address}'")
            location = self.geolocator.geocode(address, timeout=10)
            self.last_request_time = time.time()

            if location:
                coords = (location.latitude, location.longitude)
                self.geocode_cache[address] = coords
                print(f"  > [Nominatim] Найдено: {coords}")
                return coords
            else:
                print(f"  > [Nominatim] Адрес не найден: '{address}'")
                return None

        except Exception as e:
            print(f"  > [Nominatim Error] {e}")
            return None

    def get_route_details(self, start_coords: tuple, end_coords: tuple, mode: str = 'driving') -> dict:
        """
        Получает детали маршрута через OSRM API (бесплатно, без ключей).

        OSRM API формат:
        GET https://router.project-osrm.org/route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}

        Args:
            start_coords: Координаты начальной точки (lat, lon)
            end_coords: Координаты конечной точки (lat, lon)
            mode: Режим передвижения ('driving', 'car' - только driving поддерживается OSRM)

        Returns:
            Словарь с данными маршрута:
            - route_distance_km: Расстояние в километрах
            - travel_time_h: Время в пути в часах
            - status: Статус запроса
        """
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords

        # ВАЖНО: OSRM использует формат lon,lat (не lat,lon!)
        osrm_coords = f"{lon1},{lat1};{lon2},{lat2}"

        # Формируем URL для OSRM API
        # overview=false - не возвращать геометрию маршрута (экономим трафик)
        # steps=false - не возвращать пошаговые инструкции
        url = f"{self.OSRM_BASE_URL}/route/v1/driving/{osrm_coords}?overview=false&steps=false"

        try:
            # print(f"  > [OSRM API] Запрос маршрута: {start_coords} -> {end_coords}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data['code'] == 'Ok' and len(data['routes']) > 0:
                route = data['routes'][0]

                # distance в метрах, duration в секундах
                distance_m = route['distance']
                duration_s = route['duration']

                # Конвертируем в км и часы
                distance_km = distance_m / 1000
                time_h = duration_s / 3600

                return {
                    'route_distance_km': round(distance_km, 2),
                    'travel_time_h': round(time_h, 2),
                    'mode': mode,
                    'status': 'success',
                    'source': 'OSRM'
                }
            else:
                print(f"  > [OSRM API Error] {data.get('message', 'Unknown error')}")
                return {
                    'route_distance_km': 0,
                    'travel_time_h': 0,
                    'mode': mode,
                    'status': 'error',
                    'source': 'OSRM'
                }

        except requests.exceptions.RequestException as e:
            print(f"  > [OSRM API Error] Ошибка запроса: {e}")
            # Fallback на упрощенный расчет
            return self._fallback_distance_calculation(start_coords, end_coords, mode)

    def _fallback_distance_calculation(self, start_coords: tuple, end_coords: tuple, mode: str) -> dict:
        """
        Упрощенный расчет расстояния (fallback на случай недоступности OSRM).
        Использует формулу гаверсинуса с коэффициентом для дорог.
        """
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords

        # Формула Хаверсина для расчета расстояния по прямой
        from math import radians, sin, cos, sqrt, atan2

        R = 6371.0  # Радиус Земли в км
        lat1_rad, lon1_rad = radians(lat1), radians(lon1)
        lat2_rad, lon2_rad = radians(lat2), radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Расстояние по прямой с коэффициентом 1.3 для учета кривизны дорог
        distance_km = R * c * 1.3

        # Время при средней скорости 50 км/ч
        time_h = distance_km / 50

        print(f"  > [Fallback] Используется упрощенный расчет: {distance_km:.1f} км")

        return {
            'route_distance_km': round(distance_km, 2),
            'travel_time_h': round(time_h, 2),
            'mode': mode,
            'status': 'fallback',
            'source': 'haversine'
        }

    def calculate_weighted_annual_distance(self, new_location_coords: tuple) -> dict:
        """
        Рассчитывает взвешенное годовое расстояние S для всех транспортных потоков.

        Args:
            new_location_coords: Координаты новой локации (lat, lon)

        Returns:
            Словарь с расстояниями и временем для каждого потока
        """
        print(f"\n  > [OSRMGeoRouter] Расчет взвешенного годового расстояния для локации {new_location_coords}")

        # Потоки и их доли (из документации)
        flows = {
            'CFO': {'coords': self.AVG_CFD_COORDS, 'share': 0.46, 'name': 'ЦФО (собственный флот)'},
            'SVO': {'coords': self.SVO_COORDS, 'share': 0.25, 'name': 'Авиа (Шереметьево)'},
            'LPU': {'coords': self.AVG_LPU_COORDS, 'share': 0.29, 'name': 'Местные ЛПУ (Москва)'}
        }

        results = {}
        total_weighted_distance = 0

        for flow_id, flow_data in flows.items():
            route = self.get_route_details(new_location_coords, flow_data['coords'])

            # Взвешенное расстояние для этого потока
            weighted_distance = route['route_distance_km'] * flow_data['share']
            total_weighted_distance += weighted_distance

            results[flow_id] = {
                'distance_km': route['route_distance_km'],
                'time_h': route['travel_time_h'],
                'share': flow_data['share'],
                'weighted_distance_km': weighted_distance,
                'name': flow_data['name'],
                'source': route.get('source', 'unknown')
            }

            print(f"    - {flow_data['name']}: {route['route_distance_km']:.1f} км, {route['travel_time_h']:.2f} ч (доля {flow_data['share']*100:.0f}%) [{route.get('source', 'unknown')}]")

        results['total_weighted_distance_km'] = total_weighted_distance
        print(f"  > Итоговое взвешенное расстояние: {total_weighted_distance:.1f} км")

        return results


# ============================================================================
# СТАРЫЙ КЛАСС (для обратной совместимости, удалить после миграции)
# ============================================================================

class YandexGeoRouter:
    """
    Имитация API Яндекс.Карт для получения точных дорожных расстояний и времени в пути.
    Использует API Геокодера и Матрицы расстояний для расчета S (дорожное плечо) и T (время).
    """

    # Константы координат ключевых точек (имитация Геокодера)
    CURRENT_HUB_COORDS = (55.857, 37.436)  # Сходненская (текущий склад)
    SVO_COORDS = (55.97, 37.41)  # Аэропорт Шереметьево
    AVG_LPU_COORDS = (55.75, 37.62)  # Усредненный клиент ЛПУ (Москва)
    AVG_CFD_COORDS = (54.51, 36.26)  # Усредненный хаб ЦФО (Калуга/Тула)

    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация роутера.

        Args:
            api_key: API ключ Яндекс.Карт (в stub-режиме не используется)
        """
        self.api_key = api_key or "YOUR_YANDEX_MAPS_API_KEY"

    def get_route_details(self, start_coords: tuple, end_coords: tuple, mode: str = 'driving') -> dict:
        """
        Имитирует HTTP-запрос к API Матрицы расстояний Яндекс.Карт.

        В реальной реализации здесь был бы код:
        -----------------------------------------------
        url = f"https://api.routing.yandex.net/v2/route"
        params = {
            'apikey': self.api_key,
            'waypoints': f'{start_coords[1]},{start_coords[0]}|{end_coords[1]},{end_coords[0]}',
            'mode': mode
        }
        response = requests.get(url, params=params)
        route_data = response.json()
        return {
            'route_distance_km': route_data['route']['distance'] / 1000,
            'travel_time_h': route_data['route']['duration'] / 3600
        }
        -----------------------------------------------

        Args:
            start_coords: Координаты начальной точки (lat, lon)
            end_coords: Координаты конечной точки (lat, lon)
            mode: Режим передвижения ('driving', 'walking', etc.)

        Returns:
            Словарь с данными маршрута (имитация JSON-ответа API)
        """
        # print(f"  > [API Яндекс.Карт] Запрос маршрута: {start_coords} -> {end_coords}")

        # ====== РАСЧЕТ S (ДОРОЖНОЕ ПЛЕЧО) ======
        # Формула Евклидова расстояния с поправкой на реальность дорог
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords

        # Простое евклидово расстояние (в градусах)
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        euclidean_dist_deg = math.sqrt(delta_lat**2 + delta_lon**2)

        # Перевод в километры (1 градус ≈ 111 км)
        # Коэффициент 1.3 - поправка на кривизну дорог
        route_distance_km = euclidean_dist_deg * 111 * 1.3

        # ====== РАСЧЕТ T (ВРЕМЯ В ПУТИ) ======
        # Средняя скорость для грузового транспорта: 50 км/ч
        avg_speed_kmh = 50
        travel_time_h = route_distance_km / avg_speed_kmh

        # Имитация JSON-ответа от API
        return {
            'route_distance_km': round(route_distance_km, 2),
            'travel_time_h': round(travel_time_h, 2),
            'mode': mode,
            'status': 'success'
        }

    def calculate_weighted_annual_distance(self, new_location_coords: tuple) -> dict:
        """
        Рассчитывает взвешенное годовое расстояние S для всех транспортных потоков.

        Args:
            new_location_coords: Координаты новой локации (lat, lon)

        Returns:
            Словарь с расстояниями и временем для каждого потока
        """
        print(f"\n  > [YandexGeoRouter] Расчет взвешенного годового расстояния для локации {new_location_coords}")

        # Потоки и их доли (из документации)
        flows = {
            'CFO': {'coords': self.AVG_CFD_COORDS, 'share': 0.46, 'name': 'ЦФО (собственный флот)'},
            'SVO': {'coords': self.SVO_COORDS, 'share': 0.25, 'name': 'Авиа (Шереметьево)'},
            'LPU': {'coords': self.AVG_LPU_COORDS, 'share': 0.29, 'name': 'Местные ЛПУ (Москва)'}
        }

        results = {}
        total_weighted_distance = 0

        for flow_id, flow_data in flows.items():
            route = self.get_route_details(new_location_coords, flow_data['coords'])

            # Взвешенное расстояние для этого потока
            weighted_distance = route['route_distance_km'] * flow_data['share']
            total_weighted_distance += weighted_distance

            results[flow_id] = {
                'distance_km': route['route_distance_km'],
                'time_h': route['travel_time_h'],
                'share': flow_data['share'],
                'weighted_distance_km': weighted_distance,
                'name': flow_data['name']
            }

            print(f"    - {flow_data['name']}: {route['route_distance_km']:.1f} км, {route['travel_time_h']:.2f} ч (доля {flow_data['share']*100:.0f}%)")

        results['total_weighted_distance_km'] = total_weighted_distance
        print(f"  > Итоговое взвешенное расстояние: {total_weighted_distance:.1f} км")

        return results


class FleetOptimizer:
    """
    Анализирует транспортные потоки для расчета необходимого флота и годовых затрат.
    """
    # 1. Константы транспортных потоков
    CFO_OWN_FLEET_SHARE = 0.46
    AIR_DELIVERY_SHARE = 0.25
    LOCAL_DELIVERY_SHARE = 0.29

    # 2. Константы логистики
    MONTHLY_ORDERS = config.TARGET_ORDERS_MONTH  # 10 000
    CFO_TRIPS_PER_WEEK_PER_TRUCK = 2

    # Тарифы
    OWN_FLEET_TARIFF_RUB_KM = config.TRANSPORT_TARIFF_RUB_PER_KM # 13.4 руб/км
    LOCAL_FLEET_TARIFF_RUB_KM = 11.2 # Усредненный тариф для местных перевозок

    def calculate_required_fleet(self) -> int:
        """
        Рассчитывает минимальное количество собственных 18-20 тонных грузовиков для ЦФО.
        """
        # Рассчитываем количество заказов, которые нужно доставить в ЦФО за неделю
        cfo_orders_per_month = self.MONTHLY_ORDERS * self.CFO_OWN_FLEET_SHARE
        weeks_in_month = 4.33 # Среднее количество недель в месяце
        cfo_orders_per_week = cfo_orders_per_month / weeks_in_month

        # Допущение: 1 рейс = 1 заказ (консолидированный до точки в ЦФО)
        # Это упрощение, так как один рейс может содержать несколько заказов.
        # Здесь "рейс" означает поездку до одного из хабов ЦФО.
        total_cfo_trips_per_week = cfo_orders_per_week

        # Расчет необходимого количества грузовиков
        required_trucks = total_cfo_trips_per_week / self.CFO_TRIPS_PER_WEEK_PER_TRUCK
        
        return math.ceil(required_trucks)

    def calculate_annual_transport_cost(self, avg_dist_cfo: float, avg_dist_svo: float, avg_dist_local: float) -> float:
        """
        Рассчитывает годовые транспортные расходы для всех трех потоков.
        """
        annual_orders = self.MONTHLY_ORDERS * 12

        # Затраты на ЦФО (собственный флот)
        cost_cfo = (annual_orders * self.CFO_OWN_FLEET_SHARE) * avg_dist_cfo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на Авиа (доставка в SVO)
        cost_svo = (annual_orders * self.AIR_DELIVERY_SHARE) * avg_dist_svo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на местные перевозки (наемный транспорт)
        cost_local = (annual_orders * self.LOCAL_DELIVERY_SHARE) * avg_dist_local * self.LOCAL_FLEET_TARIFF_RUB_KM

        return cost_cfo + cost_svo + cost_local

    # ============================================================================
    # ПРОМПТ 3: Интеграция и оптимизация - новые методы FleetOptimizer
    # ============================================================================

    def calculate_optimal_fleet_and_cost(self, location_data: dict, geo_router: OSRMGeoRouter) -> dict:
        """
        Рассчитывает T_год (годовые транспортные расходы) и оптимальный флот для локации.

        Args:
            location_data: Данные о локации (координаты и другие параметры)
            geo_router: Экземпляр OSRMGeoRouter для расчета маршрутов

        Returns:
            Словарь с данными о флоте и транспортных расходах
        """
        print(f"\n  > [FleetOptimizer] Расчет флота и T_год для '{location_data['location_name']}'")

        # Получаем точные дорожные расстояния через OSRMGeoRouter
        location_coords = (location_data['lat'], location_data['lon'])
        route_data = geo_router.calculate_weighted_annual_distance(location_coords)

        # Извлекаем расстояния для каждого потока
        dist_cfo = route_data['CFO']['distance_km']
        dist_svo = route_data['SVO']['distance_km']
        dist_lpu = route_data['LPU']['distance_km']

        # Рассчитываем годовые транспортные расходы (T_год) используя тарифы
        annual_orders = self.MONTHLY_ORDERS * 12

        # Затраты на ЦФО (собственный флот, тариф 13.4 руб/км)
        cost_cfo = (annual_orders * self.CFO_OWN_FLEET_SHARE) * dist_cfo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на Авиа (доставка в SVO, тариф 13.4 руб/км)
        cost_svo = (annual_orders * self.AIR_DELIVERY_SHARE) * dist_svo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на местные перевозки (наемный транспорт, тариф 11.2 руб/км)
        cost_local = (annual_orders * self.LOCAL_DELIVERY_SHARE) * dist_lpu * self.LOCAL_FLEET_TARIFF_RUB_KM

        total_annual_transport_cost = cost_cfo + cost_svo + cost_local

        # Рассчитываем необходимый флот
        # 1. Грузовики 18-20 тонн для ЦФО (2 рейса/нед)
        cfo_orders_per_month = self.MONTHLY_ORDERS * self.CFO_OWN_FLEET_SHARE
        weeks_in_month = 4.33
        cfo_orders_per_week = cfo_orders_per_month / weeks_in_month
        required_heavy_trucks = math.ceil(cfo_orders_per_week / self.CFO_TRIPS_PER_WEEK_PER_TRUCK)

        # 2. Грузовики 5 тонн для Москвы (ежедневно, 6-8 точек)
        local_orders_per_day = (self.MONTHLY_ORDERS * self.LOCAL_DELIVERY_SHARE) / 22  # 22 рабочих дня
        points_per_truck = 7  # Среднее между 6 и 8
        required_light_trucks = math.ceil(local_orders_per_day / points_per_truck)

        print(f"    - T_год (общие транспортные расходы): {total_annual_transport_cost:,.0f} руб/год")
        print(f"    - Требуется 18-20т грузовиков (ЦФО): {required_heavy_trucks} шт")
        print(f"    - Требуется 5т грузовиков (Москва): {required_light_trucks} шт")

        return {
            'total_annual_transport_cost': total_annual_transport_cost,
            'cost_breakdown': {
                'cfo': cost_cfo,
                'svo': cost_svo,
                'local': cost_local
            },
            'fleet_required': {
                'heavy_trucks_18_20t': required_heavy_trucks,
                'light_trucks_5t': required_light_trucks
            },
            'distances': {
                'cfo_km': dist_cfo,
                'svo_km': dist_svo,
                'local_km': dist_lpu
            }
        }

    def calculate_relocation_capex(self, new_location_coords: tuple, geo_router: OSRMGeoRouter) -> dict:
        """
        Рассчитывает стоимость единовременного физического переезда товара.
        Использует тариф наемного транспорта 2,500 руб/час.

        Args:
            new_location_coords: Координаты новой локации (lat, lon)
            geo_router: Экземпляр OSRMGeoRouter для расчета времени в пути

        Returns:
            Словарь с данными о CAPEX переезда
        """
        print(f"\n  > [FleetOptimizer] Расчет CAPEX переезда в локацию {new_location_coords}")

        # Тариф наемного транспорта для переезда
        HIRED_TRANSPORT_TARIFF_RUB_H = 2500  # руб/час

        # Время на погрузку/разгрузку (фиксированное)
        LOADING_UNLOADING_TIME_H = 4  # часа (по 2 часа на каждую операцию)

        # Получаем маршрут от текущего склада (Сходненская) до новой локации
        current_hub = geo_router.CURRENT_HUB_COORDS
        route = geo_router.get_route_details(current_hub, new_location_coords)

        # Время в пути (туда-обратно, так как транспорт возвращается)
        travel_time_one_way_h = route['travel_time_h']
        travel_time_round_trip_h = travel_time_one_way_h * 2

        # Общее время одного рейса
        total_trip_time_h = travel_time_round_trip_h + LOADING_UNLOADING_TIME_H

        # Оценка количества рейсов (на основе объема товара)
        # Допущение: 17,000 м² склада, средняя загрузка 40% = 6,800 м² товара
        # Один грузовик 20т ≈ 80 м³ ≈ примерно покрывает 100 м² площади при высоте 0.8м
        warehouse_area_sqm = config.WAREHOUSE_TOTAL_AREA_SQM
        avg_load_ratio = 0.4  # 40% загрузка склада
        area_per_truck_sqm = 100  # м² товара на один рейс грузовика

        estimated_trips = math.ceil((warehouse_area_sqm * avg_load_ratio) / area_per_truck_sqm)

        # Общее время всех рейсов
        total_time_all_trips_h = estimated_trips * total_trip_time_h

        # Стоимость транспортировки
        transport_cost_rub = total_time_all_trips_h * HIRED_TRANSPORT_TARIFF_RUB_H

        print(f"    - Расстояние: {route['route_distance_km']:.1f} км (в одну сторону)")
        print(f"    - Время в пути (туда-обратно): {travel_time_round_trip_h:.2f} ч")
        print(f"    - Общее время одного рейса: {total_trip_time_h:.2f} ч")
        print(f"    - Необходимо рейсов: {estimated_trips}")
        print(f"    - Общее время всех рейсов: {total_time_all_trips_h:.1f} ч")
        print(f"    - CAPEX транспортировки товара: {transport_cost_rub:,.0f} руб")

        return {
            'transport_capex_rub': transport_cost_rub,
            'distance_km': route['route_distance_km'],
            'estimated_trips': estimated_trips,
            'total_time_hours': total_time_all_trips_h,
            'tariff_rub_per_hour': HIRED_TRANSPORT_TARIFF_RUB_H
        }


def plot_results():
    """
    Читает итоговый CSV, выводит данные в консоль и строит
    сравнительный график KPI для всех сценариев.
    """
    csv_path = os.path.join(config.OUTPUT_DIR, config.RESULTS_CSV_FILENAME)
    
    # Проверка, что файл с результатами существует
    if not os.path.exists(csv_path):
        print(f"Ошибка: Файл с результатами не найден по пути '{csv_path}'")
        print("Пожалуйста, сначала запустите симуляцию командой: python main.py")
        return

    # Загружаем данные. Указываем правильные разделители.
    df = pd.read_csv(csv_path, sep=';', decimal='.')
    
    print("\n" + "="*80)
    print("Загружены данные для анализа:")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80 + "\n")

    # --- Настройка визуализации ---
    sns.set_theme(style="whitegrid")
    # Создаем фигуру с двумя осями Y для отображения данных разного масштаба
    fig, ax1 = plt.subplots(figsize=(13, 8))

    # Ось Y 1 (левая): Пропускная способность (столбчатая диаграмма)
    color1 = 'tab:blue'
    ax1.set_xlabel('Сценарии', fontsize=12)
    ax1.set_ylabel('Пропускная способность (обработано заказов)', color=color1, fontsize=12)
    # Используем Seaborn для красивых столбцов
    plot1 = sns.barplot(
        x='Scenario_Name', 
        y='Achieved_Throughput_Monthly', 
        data=df, 
        ax=ax1, 
        palette='Blues_d',
        label='Пропускная способность'
    )
    ax1.tick_params(axis='y', labelcolor=color1)
    # Поворачиваем подписи по оси X для лучшей читаемости
    plt.xticks(rotation=15, ha="right")

    # Ось Y 2 (правая): Годовой OPEX (линейный график)
    ax2 = ax1.twinx()  # Создаем вторую ось, которая делит ось X с первой
    color2 = 'tab:red'
    ax2.set_ylabel('Годовой OPEX (млн руб.)', color=color2, fontsize=12)
    # Рисуем линию поверх столбцов
    plot2 = sns.lineplot(
        x='Scenario_Name', 
        y=df['Total_Annual_OPEX_RUB'] / 1_000_000, 
        data=df, 
        ax=ax2, 
        color=color2, 
        marker='o', 
        linewidth=2,
        label='Годовой OPEX'
    )
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Общий заголовок и компоновка
    plt.title(f"Сравнение сценариев для локации '{df['Location_Name'][0]}'", fontsize=16, pad=20)
    fig.tight_layout()  # Автоматически подбирает отступы, чтобы ничего не обрезалось

    # Сохранение итогового изображения
    output_image_path = os.path.join(config.OUTPUT_DIR, "simulation_comparison.png")
    plt.savefig(output_image_path)
    
    print(f"[Analysis] Сравнительный график успешно сохранен: '{output_image_path}'")
    plt.show()

if __name__ == "__main__":
    # Демонстрация работы AvitoParserStub
    print("\n" + "="*80)
    print("ЗАПУСК ПАРСЕРА-ЗАГЛУШКИ (AvitoParserStub)")
    print("="*80)

    parser = AvitoParserStub()

    # Используем данные из config.py
    candidate_locations = config.ALL_CANDIDATE_LOCATIONS
    print(f"Найдено {len(candidate_locations)} потенциальных локаций для анализа.")

    scored_results = parser.filter_and_score_locations(candidate_locations)

    print(f"\nПосле фильтрации и оценки осталось {len(scored_results)} подходящих локаций:")
    print("-" * 80)

    # Демонстрация для конкретных локаций
    for loc in scored_results:
        if loc['location_name'] in ['Белый Раст Логистика', 'PNK Чашниково BTS']:
            print(f"Локация: '{loc['location_name']}' ({loc['type']})")
            print(f"  > Площадь: {loc['area_offered_sqm']} кв.м")
            print(f"  > OPEX (помещение): {loc['annual_building_opex']:,.0f} руб./год")
            print(f"  > CAPEX (начальный):  {loc['total_initial_capex']:,.0f} руб.")
            print("-" * 80)

    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ НОВЫХ КЛАССОВ (AvitoCIANScraper, OSRMGeoRouter, FleetOptimizer)")
    print("="*80)

    # ============================================================================
    # ПРОМПТ 1: Демонстрация AvitoCIANScraper
    # ============================================================================
    print("\n[1] Демонстрация AvitoCIANScraper (полный парсер с HTTP-запросами)")
    print("="*80)

    scraper = AvitoCIANScraper()

    # Имитация HTTP-запроса к API
    raw_offers = scraper.fetch_raw_offers_data("https://api.avito.ru/search?category=warehouse&area_min=17000")

    # Парсинг и фильтрация
    filtered_offers = scraper.parse_and_filter_offers(raw_offers)

    print(f"\n[AvitoCIANScraper] Итого найдено подходящих локаций: {len(filtered_offers)}")

    # ============================================================================
    # ПРОМПТ 2: Демонстрация OSRMGeoRouter (бесплатный API)
    # ============================================================================
    print("\n" + "="*80)
    print("[2] Демонстрация OSRMGeoRouter (бесплатный OSRM API)")
    print("="*80)

    geo_router = OSRMGeoRouter(use_geocoding=False)  # Geocoding отключен для быстроты

    # Пример: маршрут Сходненская -> Логопарк Север-2
    test_location_coords = (56.03, 37.59)  # Логопарк Север-2

    print(f"\nТестовый маршрут: Сходненская {geo_router.CURRENT_HUB_COORDS} -> Логопарк Север-2 {test_location_coords}")
    route_demo = geo_router.get_route_details(geo_router.CURRENT_HUB_COORDS, test_location_coords)

    print("\n  > [JSON-ответ от OSRM API]")
    print(f"    {{")
    print(f"      'status': '{route_demo['status']}',")
    print(f"      'mode': '{route_demo['mode']}',")
    print(f"      'route_distance_km': {route_demo['route_distance_km']},")
    print(f"      'travel_time_h': {route_demo['travel_time_h']},")
    print(f"      'source': '{route_demo.get('source', 'unknown')}'")
    print(f"    }}")

    # Расчет взвешенного годового расстояния
    weighted_distance_demo = geo_router.calculate_weighted_annual_distance(test_location_coords)

    # ============================================================================
    # ПРОМПТ 3: Демонстрация новых методов FleetOptimizer
    # ============================================================================
    print("\n" + "="*80)
    print("[3] Демонстрация FleetOptimizer (расчет флота и CAPEX переезда)")
    print("="*80)

    fleet_opt = FleetOptimizer()

    # Выбираем тестовую локацию
    test_location = filtered_offers[0]

    # Расчет оптимального флота и годовых расходов
    fleet_cost_result = fleet_opt.calculate_optimal_fleet_and_cost(test_location, geo_router)

    # Расчет CAPEX переезда
    relocation_capex = fleet_opt.calculate_relocation_capex(test_location_coords, geo_router)

    print("\n[ИТОГОВАЯ СВОДКА]")
    print(f"  Локация: {test_location['location_name']}")
    print(f"  T_год (годовые транспортные расходы): {fleet_cost_result['total_annual_transport_cost']:,.0f} руб")
    print(f"  CAPEX переезда (транспортировка товара): {relocation_capex['transport_capex_rub']:,.0f} руб")
    print(f"  Флот 18-20т: {fleet_cost_result['fleet_required']['heavy_trucks_18_20t']} шт")
    print(f"  Флот 5т: {fleet_cost_result['fleet_required']['light_trucks_5t']} шт")

    # ============================================================================
    # ДЕМОНСТРАЦИЯ ДЕТАЛЬНОГО ТРАНСПОРТНОГО ПЛАНИРОВЩИКА
    # ============================================================================
    print("\n" + "="*80)
    print("[4] Демонстрация DetailedFleetPlanner (детальный расчет транспорта)")
    print("="*80)

    detailed_planner = DetailedFleetPlanner()

    # Используем расстояния из предыдущего расчета
    distances = {
        'cfo_km': fleet_cost_result['distances']['cfo_km'],
        'svo_km': fleet_cost_result['distances']['svo_km'],
        'local_km': fleet_cost_result['distances']['local_km']
    }

    # Детальный расчет флота
    fleet_summary = detailed_planner.calculate_fleet_requirements(distances)

    # Расчет доков
    dock_requirements = detailed_planner.calculate_dock_requirements(fleet_summary)

    # График работы
    transport_schedule = detailed_planner.generate_transport_schedule(fleet_summary)

    # Симуляция доков
    print("\n  > [DockSimulator] Проверка пропускной способности доков")
    dock_sim = DockSimulator(
        inbound_docks=dock_requirements['inbound_docks'],
        outbound_docks=dock_requirements['outbound_docks']
    )
    dock_simulation = dock_sim.simulate_dock_operations(dock_requirements['peak_trips_per_day'])

    print(f"    - Утилизация inbound: {dock_simulation['inbound_utilization_percent']:.1f}%")
    print(f"    - Утилизация outbound: {dock_simulation['outbound_utilization_percent']:.1f}%")
    print(f"    - Достаточность: {'ДА' if dock_simulation['is_sufficient'] else 'НЕТ, требуется больше доков'}")

    print("\n[ДЕТАЛЬНАЯ ТРАНСПОРТНАЯ СВОДКА]")
    print(f"  Всего единиц техники: {fleet_summary['total_vehicles']}")
    print(f"  Рекомендация: {'Аренда флота' if fleet_summary['recommendation'] == 'lease' else 'Покупка флота'}")
    print(f"  Годовой OPEX (собственный): {fleet_summary['total_opex_own_fleet']:,.0f} руб")
    print(f"  Годовой OPEX (аренда): {fleet_summary['total_opex_lease']:,.0f} руб")
    print(f"  CAPEX (покупка): {fleet_summary['total_capex_purchase']:,.0f} руб")
    print(f"  Доков (приемка/отгрузка): {dock_requirements['inbound_docks']}/{dock_requirements['outbound_docks']}")

    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*80)
```

## `collected_code.md`

```md
## `core\data_model.py`

```py
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
```

## `core\flexsim_bridge.py`

```py
"""
Модуль для взаимодействия с FlexSim: генерация JSON и имитация API.
"""
import json
import os
from typing import Dict, Any, Optional

import config
from core.data_model import LocationSpec, ScenarioResult
from analysis import FleetOptimizer

class FlexSimAPIBridge:
    """
    Управляет созданием конфигурационных файлов для FlexSim и
    имитирует отправку команд через Socket API.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[FlexSimAPIBridge] Инициализирован. Выходная директория: '{self.output_dir}'")

    def send_config(self, json_data: dict) -> bool:
        """Имитирует отправку JSON-конфигурации через сокет."""
        print("  > [API] Отправка конфигурации в FlexSim...")
        response = self._send_command("LOAD_CONFIG", data=json_data)
        return response.get("status") == "OK"

    def start_simulation(self, scenario_id: str) -> bool:
        """Имитирует команду запуска симуляции в FlexSim."""
        print(f"  > [API] Запуск симуляции для сценария '{scenario_id}'...")
        response = self._send_command("START_SIMULATION", data={"scenario": scenario_id})
        return response.get("status") == "OK"

    def receive_kpi(self) -> Dict[str, Any]:
        """Имитирует прием ключевых метрик от FlexSim."""
        print("  > [API] Получение KPI от FlexSim...")
        response = self._send_command("GET_KPI")
        if response.get("status") == "OK":
            # Возвращаем пример словаря, как указано в задаче
            kpi_data = {
                'achieved_throughput': 10500, 
                'resource_utilization': 0.85
            }
            print(f"  > [API] Получены KPI: {kpi_data}")
            return kpi_data
        return {}

    def generate_json_config(self, location_spec: LocationSpec, scenario_result: ScenarioResult, scenario_data: dict):
        """Создает и сохраняет JSON-конфигурацию для одного сценария."""

        # Создаем экземпляр FleetOptimizer для расчетов
        fleet_optimizer = FleetOptimizer()

        # Определяем тип автоматизации на основе инвестиций
        automation_investment = scenario_data.get('automation_investment', 0)
        automation_type = "None"
        if automation_investment == 100_000_000:
            automation_type = "Conveyors+WMS"
        elif automation_investment > 100_000_000:
            automation_type = "AutoStore+AGV"
            
        config_data = {
            "FINANCIALS": {
                "Total_CAPEX": scenario_data['total_capex'],
                "Annual_OPEX": scenario_data['total_opex']
            },
            "LAYOUT": {
                "Total_Area_SQM": config.WAREHOUSE_TOTAL_AREA_SQM,
                "Ceiling_Height": 12,
                "GPP_ZONES": [
                    {"Zone": "Cool_2_8C", "Pallet_Capacity": 3000},
                    {"Zone": "Controlled_15_25C", "Pallet_Capacity": 17000}
                ]
            },
            "RESOURCES": {
                "Staff_Operators": scenario_data['staff_count'],
                "Automation_Type": automation_type,
                "Processing_Time_Coefficient": scenario_data['processing_efficiency']
            },
            "LOGISTICS": {
                "Location_Coords": [location_spec.lat, location_spec.lon],
                "Required_Own_Fleet_Count": fleet_optimizer.calculate_required_fleet(),
                "Delivery_Flows": [
                    {"Dest": "SVO_Aviation", "Volume_Pct": fleet_optimizer.AIR_DELIVERY_SHARE * 100},
                    {"Dest": "CFD_Own_Fleet", "Volume_Pct": fleet_optimizer.CFO_OWN_FLEET_SHARE * 100},
                    {"Dest": "Moscow_LPU", "Volume_Pct": fleet_optimizer.LOCAL_DELIVERY_SHARE * 100}
                ]
            }
        }
        
        # Формируем имя файла на основе имени сценария
        scenario_name = scenario_data.get('name', 'Unknown_Scenario')
        safe_scenario_name = scenario_name.replace('. ', '_').replace(' ', '_')
        filename = f"flexsim_setup_{safe_scenario_name}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        print(f"  > [OK] JSON-конфиг сохранен: {filename}")
        
        # Демонстрация для Сценария 4
        if "4_Move_Advanced_Automation" in safe_scenario_name:
            print("\n--- Демонстрация JSON для Сценария 4 ---")
            print(json.dumps(config_data, ensure_ascii=False, indent=4))
            print("-----------------------------------------\n")

    def _send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Имитирует отправку команды FlexSim (stub-версия из api_bridge.py)."""
        # print(f"[FlexSimAPIBridge STUB] Отправка команды '{command}'...")
        try:
            # Имитируем ошибку подключения, так как сервера нет
            raise ConnectionRefusedError("No FlexSim server is listening (as expected for a stub).")
        except ConnectionRefusedError as e:
            # print(f"[FlexSimAPIBridge STUB] Ошибка (это нормально для заглушки): {e}")
            if command == "LOAD_CONFIG":
                return {"status": "OK", "message": "Configuration loaded."}
            elif command == "START_SIMULATION":
                return {"status": "OK", "message": "Simulation started."}
            elif command == "GET_KPI":
                 return {"status": "OK", "kpi": {"achieved_throughput": 10500, "resource_utilization": 0.85}}
            return {"status": "ERROR", "message": "Unknown command"}
```

## `core\location.py`

```py
# core/location.py

"""
Модуль для конфигурации склада и расчета базовых финансовых показателей (CAPEX, OPEX).
"""
from typing import Dict, Tuple
from math import radians, sin, cos, sqrt, atan2

import config

class WarehouseConfigurator:
    """
    Рассчитывает базовые CAPEX и OPEX для склада, включая затраты на помещение и оборудование.
    """
    def __init__(self, ownership_type: str, rent_rate_sqm_year: float, purchase_cost: float, lat: float, lon: float):
        # Нормализуем тип владения: POKUPKA_BTS -> POKUPKA
        if ownership_type == "POKUPKA_BTS":
            ownership_type = "POKUPKA"

        if ownership_type not in {"ARENDA", "POKUPKA"}:
            raise ValueError("Неверный тип владения: должен быть 'ARENDA', 'POKUPKA' или 'POKUPKA_BTS'")

        self.ownership_type = ownership_type
        self.rent_rate_sqm_year = rent_rate_sqm_year
        self.purchase_cost = purchase_cost
        self.lat = lat
        self.lon = lon

    def calculate_fixed_capex(self) -> float:
        """Рассчитывает обязательные первоначальные инвестиции (CAPEX) для склада."""
        capex_racking = 50_000_000  # Стеллажное оборудование
        capex_climate = 250_000_000 # Климатическое оборудование (установка + настройка)
        return capex_racking + capex_climate

    def calculate_annual_opex(self) -> float:
        """Рассчитывает годовые операционные расходы (OPEX) на помещение."""
        total_area = 17000  # Общая площадь в м²
        if self.ownership_type == "ARENDA":
            return total_area * self.rent_rate_sqm_year
        else:  # POKUPKA
            # Налог/обслуживание как 15% от гипотетической стоимости аренды
            return (total_area * self.rent_rate_sqm_year) * 0.15

    def _haversine_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Расчет расстояния по прямой с коэффициентом на кривизну дорог."""
        R = 6371.0  # Радиус Земли в километрах
        lat1, lon1, lat2, lon2 = map(radians, [p1[0], p1[1], p2[0], p2[1]])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Коэффициент 1.4 для имитации реального пробега по дорогам
        return (R * c) * 1.4

    def get_transport_cost_change_rub(self) -> float:
        """Рассчитывает годовое ИЗМЕНЕНИЕ транспортных расходов при переезде."""
        total_dist_increase_km = 0
        new_hub_coords = (self.lat, self.lon)
        # Ключевые точки доставки: аэропорт и усредненные центры для ЦФО и Москвы
        key_points = [
            config.KEY_GEO_POINTS["Airport_SVO"],
            config.KEY_GEO_POINTS["CFD_HUBs_Avg"],
            config.KEY_GEO_POINTS["Moscow_Clients_Avg"]
        ]
        
        for point in key_points:
            dist_old = self._haversine_distance(config.KEY_GEO_POINTS["Current_HUB"], point)
            dist_new = self._haversine_distance(new_hub_coords, point)
            total_dist_increase_km += (dist_new - dist_old)

        avg_dist_increase_per_trip = total_dist_increase_km / len(key_points)
        
        # Допущение: каждый заказ - это условная поездка для оценки относительного изменения
        total_annual_extra_km = avg_dist_increase_per_trip * (config.TARGET_ORDERS_MONTH * 12)
        
        return total_annual_extra_km * config.TRANSPORT_TARIFF_RUB_PER_KM

    def get_base_financials(self) -> Dict[str, float]:
        """
        Рассчитывает базовые CAPEX и OPEX, зависящие ТОЛЬКО от локации и типа владения.
        OPEX здесь включает в себя аренду/обслуживание здания и изменение транспортных расходов.
        """
        base_capex = self.calculate_fixed_capex()
        base_opex_location = self.calculate_annual_opex()

        if self.ownership_type == "POKUPKA":
            base_capex += self.purchase_cost

        # Суммируем OPEX от локации (аренда/обслуживание) и OPEX от транспорта
        total_base_opex = base_opex_location + self.get_transport_cost_change_rub()

        return {
            "base_capex": base_capex,
            "base_opex": total_base_opex
        }
```

## `core\simulation_engine.py`

```py
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
```

## `core\__init__.py`

```py

```

## `analysis.py`

```py
"""
Скрипт для анализа и визуализации результатов ПОСЛЕ выполнения симуляции.
Запускается отдельно командой: python analysis.py

ВАЖНО: Использует бесплатные API:
- OSRM (https://router.project-osrm.org) для маршрутизации
- Nominatim/geopy для геокодирования
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config
import math
import requests  # Для HTTP-запросов к OSRM API
import time
from typing import Optional, Dict, Tuple
from geopy.geocoders import Nominatim  # Для геокодирования адресов
# from bs4 import BeautifulSoup  # Для парсинга HTML ЦИАН/Яндекс.Недвижимость (опционально)

# Импорт детального транспортного планировщика
from transport_planner import DetailedFleetPlanner, DockSimulator

class AvitoParserStub:
    """
    Заглушка для парсера Авито/ЦИАН. Фильтрует и оценивает локации
    по требованиям фармацевтического склада.
    """
    # 1. Константы на основе требований
    REQUIRED_TOTAL_AREA = 17000
    CAPEX_FIXED_EQUIPMENT = 50_000_000       # Стеллажное оборудование
    CAPEX_GPP_GDP_CLIMATE = 250_000_000      # Установка и валидация климатики
    CAPEX_MODIFICATION_IF_NEEDED = 100_000_000 # Доведение до класса А/фармстандартов

    def filter_and_score_locations(self, candidate_locations: dict) -> list:
        """
        Фильтрует и оценивает локации из предоставленного списка.
        """
        scored_locations = []
        
        for key, loc in candidate_locations.items():
            # 2.1 Фильтрация по площади
            if loc['area_offered_sqm'] < self.REQUIRED_TOTAL_AREA:
                continue

            # 2.2 Расчет CAPEX
            total_initial_capex = self.CAPEX_FIXED_EQUIPMENT + self.CAPEX_GPP_GDP_CLIMATE

            # 2.3 Условная модификация
            if loc['current_class'] == 'A_requires_mod':
                total_initial_capex += self.CAPEX_MODIFICATION_IF_NEEDED

            # 2.4 Расчет OPEX (помещение) и добавление стоимости покупки в CAPEX
            annual_building_opex = 0
            if loc['type'] == 'ARENDA':
                annual_building_opex = loc['cost_metric_base'] * loc['area_offered_sqm']
            elif loc['type'] == 'POKUPKA_BTS':
                # Добавляем стоимость самого здания в CAPEX
                total_initial_capex += loc['cost_metric_base']
                # Расчет условных расходов на обслуживание
                notional_rent_rate = 7000  # руб/м²/год
                annual_building_opex = (notional_rent_rate * loc['area_offered_sqm']) * 0.05

            scored_locations.append({
                "location_name": loc['name'],
                "lat": loc['lat'],
                "lon": loc['lon'],
                "type": loc['type'],
                "area_offered_sqm": loc['area_offered_sqm'],
                "annual_building_opex": annual_building_opex,
                "total_initial_capex": total_initial_capex,
                "current_class": loc['current_class']
            })

        return scored_locations


# ============================================================================
# ПРОМПТ 1: Полный Парсер Авито/ЦИАН (Класс AvitoCIANScraper)
# ============================================================================

class AvitoCIANScraper:
    """
    Полный парсер Авито/ЦИАН с имитацией реальных HTTP-запросов и обработки HTML/JSON.
    Этот класс демонстрирует, как бы выглядел настоящий парсер с использованием
    requests и BeautifulSoup для получения и обработки данных о складах класса А/GPP.
    """

    # Константы требований к складу (основаны на фармацевтических стандартах)
    REQUIRED_TOTAL_AREA = 17000  # м² - минимальная требуемая площадь
    CAPEX_FIXED_EQUIPMENT = 50_000_000  # руб. - новое стеллажное оборудование
    CAPEX_GPP_GDP_CLIMATE = 250_000_000  # руб. - установка и валидация климатических систем (2-8°C и 15-25°C)
    CAPEX_MODIFICATION_IF_NEEDED = 50_000_000  # руб. - дополнительные затраты на доведение до стандарта

    def __init__(self):
        """Инициализация парсера с базовыми настройками."""
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

    def fetch_raw_offers_data(self, search_url: Optional[str] = None) -> dict:
        """
        Имитирует реальный HTTP-запрос к API Авито/ЦИАН для получения списка объектов.

        В реальной реализации здесь был бы код:
        -----------------------------------------------
        response = requests.get(search_url, headers=self.session_headers, timeout=30)
        if response.status_code == 200:
            raw_json = response.json()
            return raw_json['offers']
        -----------------------------------------------

        Args:
            search_url: URL для поиска складов (в stub-режиме игнорируется)

        Returns:
            Словарь с "сырыми" данными объектов (имитация JSON-ответа API)
        """
        print("  > [HTTP] Имитация запроса к API Авито/ЦИАН...")
        print(f"  > [HTTP] URL: {search_url or 'https://api.avito.ru/search?category=warehouse&city=moscow'}")
        print("  > [HTTP] Статус: 200 OK")
        print("  > [HTTP] Content-Type: application/json")

        # В stub-режиме возвращаем данные из config.py
        # В реальном режиме здесь был бы парсинг JSON-ответа от API
        raw_data = config.ALL_CANDIDATE_LOCATIONS
        print(f"  > [HTTP] Получено объектов: {len(raw_data)}")

        return raw_data

    def parse_and_filter_offers(self, raw_data: dict) -> list:
        """
        Имитирует парсинг HTML/JSON с использованием BeautifulSoup и фильтрацию по требованиям.

        В реальной реализации здесь был бы код:
        -----------------------------------------------
        soup = BeautifulSoup(html_content, 'html.parser')
        for offer_block in soup.find_all('div', class_='offer-card'):
            title = offer_block.find('h3', class_='title').text
            area = float(offer_block.find('span', class_='area').text.replace(' м²', ''))
            ...
        -----------------------------------------------

        Args:
            raw_data: Сырые данные от API

        Returns:
            Список финансово оцененных и отфильтрованных локаций
        """
        print("\n  > [PARSER] Запуск парсинга и фильтрации объектов...")
        scored_locations = []

        for key, loc in raw_data.items():
            # Имитация извлечения данных из HTML (в реальности через BeautifulSoup)
            print(f"    - Обработка: '{loc['name']}'")

            # ====== ФИЛЬТРАЦИЯ ПО ПЛОЩАДИ ======
            if loc['area_offered_sqm'] < self.REQUIRED_TOTAL_AREA:
                print(f"      [SKIP] Площадь {loc['area_offered_sqm']} кв.м < требуемых {self.REQUIRED_TOTAL_AREA} кв.м")
                continue

            # ====== РАСЧЕТ CAPEX GPP/GDP ======
            # Базовый CAPEX всегда включает:
            # 1. Стеллажное оборудование (50 млн)
            # 2. Климатические системы GPP/GDP (250 млн)
            total_initial_capex = self.CAPEX_FIXED_EQUIPMENT + self.CAPEX_GPP_GDP_CLIMATE

            # Если помещение требует модификации до класса А
            if loc['current_class'] == 'A_requires_mod':
                total_initial_capex += self.CAPEX_MODIFICATION_IF_NEEDED
                print(f"      [CAPEX] +{self.CAPEX_MODIFICATION_IF_NEEDED:,} руб. на модификацию до класса А")

            # ====== РАСЧЕТ OPEX (ПОМЕЩЕНИЕ) ======
            annual_building_opex = 0

            if loc['type'] == 'ARENDA':
                # Для аренды: стоимость = тариф * площадь
                annual_building_opex = loc['cost_metric_base'] * loc['area_offered_sqm']
                print(f"      [OPEX] Аренда: {loc['cost_metric_base']:,.0f} руб/кв.м * {loc['area_offered_sqm']} кв.м = {annual_building_opex:,.0f} руб/год")

            elif loc['type'] == 'POKUPKA_BTS':
                # Для покупки/BTS:
                # 1. Добавляем стоимость здания в CAPEX
                total_initial_capex += loc['cost_metric_base']
                print(f"      [CAPEX] Стоимость здания: +{loc['cost_metric_base']:,} руб.")

                # 2. OPEX = условные расходы на обслуживание (5% от гипотетической аренды)
                notional_rent_rate = 7000  # руб/м²/год
                annual_building_opex = (notional_rent_rate * loc['area_offered_sqm']) * 0.05
                print(f"      [OPEX] Обслуживание (5%): {annual_building_opex:,.0f} руб/год")

            # ====== ФОРМИРОВАНИЕ РЕЗУЛЬТАТА ======
            scored_locations.append({
                "location_name": loc['name'],
                "lat": loc['lat'],
                "lon": loc['lon'],
                "type": loc['type'],
                "area_offered_sqm": loc['area_offered_sqm'],
                "annual_building_opex": annual_building_opex,
                "total_initial_capex": total_initial_capex,
                "current_class": loc['current_class']
            })

            print(f"      [OK] Итоговый CAPEX: {total_initial_capex:,} руб, Годовой OPEX: {annual_building_opex:,.0f} руб/год")

        print(f"\n  > [PARSER] Фильтрация завершена. Подходящих локаций: {len(scored_locations)}")
        return scored_locations


# ============================================================================
# ПРОМПТ 2: Бесплатный роутер на OSRM (Класс OSRMGeoRouter)
# ============================================================================

class OSRMGeoRouter:
    """
    Бесплатный геороутер на базе OSRM API и Nominatim для геокодирования.

    OSRM (Open Source Routing Machine) - бесплатный API для маршрутизации:
    - Публичный сервер: https://router.project-osrm.org
    - Не требует API ключей или регистрации
    - Формат координат: lon,lat (долгота, широта)

    Nominatim - бесплатный геокодер OpenStreetMap через geopy:
    - Преобразование адресов в координаты
    - Требует User-Agent и соблюдения rate limits (1 запрос/сек)
    """

    # Константы координат ключевых точек (формат: lat, lon)
    CURRENT_HUB_COORDS = (55.857, 37.436)  # Сходненская (текущий склад)
    SVO_COORDS = (55.97, 37.41)  # Аэропорт Шереметьево
    AVG_LPU_COORDS = (55.75, 37.62)  # Усредненный клиент ЛПУ (Москва)
    AVG_CFD_COORDS = (54.51, 36.26)  # Усредненный хаб ЦФО (Калуга/Тула)

    # OSRM API endpoints
    OSRM_BASE_URL = "https://router.project-osrm.org"

    def __init__(self, use_geocoding: bool = False):
        """
        Инициализация роутера.

        Args:
            use_geocoding: Использовать ли Nominatim для геокодирования адресов
        """
        self.use_geocoding = use_geocoding

        if use_geocoding:
            # Инициализируем геокодер Nominatim
            # ВАЖНО: Необходимо указать User-Agent для соблюдения правил использования
            self.geolocator = Nominatim(user_agent="warehouse_relocation_analyzer/1.0")

        # Кэш для геокодирования (чтобы не делать повторные запросы)
        self.geocode_cache = {}

        # Счетчик запросов для rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Минимум 1 секунда между запросами к Nominatim

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Преобразует адрес в координаты используя Nominatim (geopy).

        Args:
            address: Адрес для геокодирования

        Returns:
            Кортеж (lat, lon) или None если адрес не найден
        """
        if not self.use_geocoding:
            print(f"  > [Geocoding] Отключено. Используйте координаты напрямую.")
            return None

        # Проверяем кэш
        if address in self.geocode_cache:
            print(f"  > [Geocoding Cache] '{address}' -> {self.geocode_cache[address]}")
            return self.geocode_cache[address]

        try:
            # Соблюдаем rate limit (1 запрос/сек для Nominatim)
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)

            print(f"  > [Nominatim] Геокодирование адреса: '{address}'")
            location = self.geolocator.geocode(address, timeout=10)
            self.last_request_time = time.time()

            if location:
                coords = (location.latitude, location.longitude)
                self.geocode_cache[address] = coords
                print(f"  > [Nominatim] Найдено: {coords}")
                return coords
            else:
                print(f"  > [Nominatim] Адрес не найден: '{address}'")
                return None

        except Exception as e:
            print(f"  > [Nominatim Error] {e}")
            return None

    def get_route_details(self, start_coords: tuple, end_coords: tuple, mode: str = 'driving') -> dict:
        """
        Получает детали маршрута через OSRM API (бесплатно, без ключей).

        OSRM API формат:
        GET https://router.project-osrm.org/route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}

        Args:
            start_coords: Координаты начальной точки (lat, lon)
            end_coords: Координаты конечной точки (lat, lon)
            mode: Режим передвижения ('driving', 'car' - только driving поддерживается OSRM)

        Returns:
            Словарь с данными маршрута:
            - route_distance_km: Расстояние в километрах
            - travel_time_h: Время в пути в часах
            - status: Статус запроса
        """
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords

        # ВАЖНО: OSRM использует формат lon,lat (не lat,lon!)
        osrm_coords = f"{lon1},{lat1};{lon2},{lat2}"

        # Формируем URL для OSRM API
        # overview=false - не возвращать геометрию маршрута (экономим трафик)
        # steps=false - не возвращать пошаговые инструкции
        url = f"{self.OSRM_BASE_URL}/route/v1/driving/{osrm_coords}?overview=false&steps=false"

        try:
            # print(f"  > [OSRM API] Запрос маршрута: {start_coords} -> {end_coords}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data['code'] == 'Ok' and len(data['routes']) > 0:
                route = data['routes'][0]

                # distance в метрах, duration в секундах
                distance_m = route['distance']
                duration_s = route['duration']

                # Конвертируем в км и часы
                distance_km = distance_m / 1000
                time_h = duration_s / 3600

                return {
                    'route_distance_km': round(distance_km, 2),
                    'travel_time_h': round(time_h, 2),
                    'mode': mode,
                    'status': 'success',
                    'source': 'OSRM'
                }
            else:
                print(f"  > [OSRM API Error] {data.get('message', 'Unknown error')}")
                return {
                    'route_distance_km': 0,
                    'travel_time_h': 0,
                    'mode': mode,
                    'status': 'error',
                    'source': 'OSRM'
                }

        except requests.exceptions.RequestException as e:
            print(f"  > [OSRM API Error] Ошибка запроса: {e}")
            # Fallback на упрощенный расчет
            return self._fallback_distance_calculation(start_coords, end_coords, mode)

    def _fallback_distance_calculation(self, start_coords: tuple, end_coords: tuple, mode: str) -> dict:
        """
        Упрощенный расчет расстояния (fallback на случай недоступности OSRM).
        Использует формулу гаверсинуса с коэффициентом для дорог.
        """
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords

        # Формула Хаверсина для расчета расстояния по прямой
        from math import radians, sin, cos, sqrt, atan2

        R = 6371.0  # Радиус Земли в км
        lat1_rad, lon1_rad = radians(lat1), radians(lon1)
        lat2_rad, lon2_rad = radians(lat2), radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Расстояние по прямой с коэффициентом 1.3 для учета кривизны дорог
        distance_km = R * c * 1.3

        # Время при средней скорости 50 км/ч
        time_h = distance_km / 50

        print(f"  > [Fallback] Используется упрощенный расчет: {distance_km:.1f} км")

        return {
            'route_distance_km': round(distance_km, 2),
            'travel_time_h': round(time_h, 2),
            'mode': mode,
            'status': 'fallback',
            'source': 'haversine'
        }

    def calculate_weighted_annual_distance(self, new_location_coords: tuple) -> dict:
        """
        Рассчитывает взвешенное годовое расстояние S для всех транспортных потоков.

        Args:
            new_location_coords: Координаты новой локации (lat, lon)

        Returns:
            Словарь с расстояниями и временем для каждого потока
        """
        print(f"\n  > [OSRMGeoRouter] Расчет взвешенного годового расстояния для локации {new_location_coords}")

        # Потоки и их доли (из документации)
        flows = {
            'CFO': {'coords': self.AVG_CFD_COORDS, 'share': 0.46, 'name': 'ЦФО (собственный флот)'},
            'SVO': {'coords': self.SVO_COORDS, 'share': 0.25, 'name': 'Авиа (Шереметьево)'},
            'LPU': {'coords': self.AVG_LPU_COORDS, 'share': 0.29, 'name': 'Местные ЛПУ (Москва)'}
        }

        results = {}
        total_weighted_distance = 0

        for flow_id, flow_data in flows.items():
            route = self.get_route_details(new_location_coords, flow_data['coords'])

            # Взвешенное расстояние для этого потока
            weighted_distance = route['route_distance_km'] * flow_data['share']
            total_weighted_distance += weighted_distance

            results[flow_id] = {
                'distance_km': route['route_distance_km'],
                'time_h': route['travel_time_h'],
                'share': flow_data['share'],
                'weighted_distance_km': weighted_distance,
                'name': flow_data['name'],
                'source': route.get('source', 'unknown')
            }

            print(f"    - {flow_data['name']}: {route['route_distance_km']:.1f} км, {route['travel_time_h']:.2f} ч (доля {flow_data['share']*100:.0f}%) [{route.get('source', 'unknown')}]")

        results['total_weighted_distance_km'] = total_weighted_distance
        print(f"  > Итоговое взвешенное расстояние: {total_weighted_distance:.1f} км")

        return results


# ============================================================================
# СТАРЫЙ КЛАСС (для обратной совместимости, удалить после миграции)
# ============================================================================

class YandexGeoRouter:
    """
    Имитация API Яндекс.Карт для получения точных дорожных расстояний и времени в пути.
    Использует API Геокодера и Матрицы расстояний для расчета S (дорожное плечо) и T (время).
    """

    # Константы координат ключевых точек (имитация Геокодера)
    CURRENT_HUB_COORDS = (55.857, 37.436)  # Сходненская (текущий склад)
    SVO_COORDS = (55.97, 37.41)  # Аэропорт Шереметьево
    AVG_LPU_COORDS = (55.75, 37.62)  # Усредненный клиент ЛПУ (Москва)
    AVG_CFD_COORDS = (54.51, 36.26)  # Усредненный хаб ЦФО (Калуга/Тула)

    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация роутера.

        Args:
            api_key: API ключ Яндекс.Карт (в stub-режиме не используется)
        """
        self.api_key = api_key or "YOUR_YANDEX_MAPS_API_KEY"

    def get_route_details(self, start_coords: tuple, end_coords: tuple, mode: str = 'driving') -> dict:
        """
        Имитирует HTTP-запрос к API Матрицы расстояний Яндекс.Карт.

        В реальной реализации здесь был бы код:
        -----------------------------------------------
        url = f"https://api.routing.yandex.net/v2/route"
        params = {
            'apikey': self.api_key,
            'waypoints': f'{start_coords[1]},{start_coords[0]}|{end_coords[1]},{end_coords[0]}',
            'mode': mode
        }
        response = requests.get(url, params=params)
        route_data = response.json()
        return {
            'route_distance_km': route_data['route']['distance'] / 1000,
            'travel_time_h': route_data['route']['duration'] / 3600
        }
        -----------------------------------------------

        Args:
            start_coords: Координаты начальной точки (lat, lon)
            end_coords: Координаты конечной точки (lat, lon)
            mode: Режим передвижения ('driving', 'walking', etc.)

        Returns:
            Словарь с данными маршрута (имитация JSON-ответа API)
        """
        # print(f"  > [API Яндекс.Карт] Запрос маршрута: {start_coords} -> {end_coords}")

        # ====== РАСЧЕТ S (ДОРОЖНОЕ ПЛЕЧО) ======
        # Формула Евклидова расстояния с поправкой на реальность дорог
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords

        # Простое евклидово расстояние (в градусах)
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        euclidean_dist_deg = math.sqrt(delta_lat**2 + delta_lon**2)

        # Перевод в километры (1 градус ≈ 111 км)
        # Коэффициент 1.3 - поправка на кривизну дорог
        route_distance_km = euclidean_dist_deg * 111 * 1.3

        # ====== РАСЧЕТ T (ВРЕМЯ В ПУТИ) ======
        # Средняя скорость для грузового транспорта: 50 км/ч
        avg_speed_kmh = 50
        travel_time_h = route_distance_km / avg_speed_kmh

        # Имитация JSON-ответа от API
        return {
            'route_distance_km': round(route_distance_km, 2),
            'travel_time_h': round(travel_time_h, 2),
            'mode': mode,
            'status': 'success'
        }

    def calculate_weighted_annual_distance(self, new_location_coords: tuple) -> dict:
        """
        Рассчитывает взвешенное годовое расстояние S для всех транспортных потоков.

        Args:
            new_location_coords: Координаты новой локации (lat, lon)

        Returns:
            Словарь с расстояниями и временем для каждого потока
        """
        print(f"\n  > [YandexGeoRouter] Расчет взвешенного годового расстояния для локации {new_location_coords}")

        # Потоки и их доли (из документации)
        flows = {
            'CFO': {'coords': self.AVG_CFD_COORDS, 'share': 0.46, 'name': 'ЦФО (собственный флот)'},
            'SVO': {'coords': self.SVO_COORDS, 'share': 0.25, 'name': 'Авиа (Шереметьево)'},
            'LPU': {'coords': self.AVG_LPU_COORDS, 'share': 0.29, 'name': 'Местные ЛПУ (Москва)'}
        }

        results = {}
        total_weighted_distance = 0

        for flow_id, flow_data in flows.items():
            route = self.get_route_details(new_location_coords, flow_data['coords'])

            # Взвешенное расстояние для этого потока
            weighted_distance = route['route_distance_km'] * flow_data['share']
            total_weighted_distance += weighted_distance

            results[flow_id] = {
                'distance_km': route['route_distance_km'],
                'time_h': route['travel_time_h'],
                'share': flow_data['share'],
                'weighted_distance_km': weighted_distance,
                'name': flow_data['name']
            }

            print(f"    - {flow_data['name']}: {route['route_distance_km']:.1f} км, {route['travel_time_h']:.2f} ч (доля {flow_data['share']*100:.0f}%)")

        results['total_weighted_distance_km'] = total_weighted_distance
        print(f"  > Итоговое взвешенное расстояние: {total_weighted_distance:.1f} км")

        return results


class FleetOptimizer:
    """
    Анализирует транспортные потоки для расчета необходимого флота и годовых затрат.
    """
    # 1. Константы транспортных потоков
    CFO_OWN_FLEET_SHARE = 0.46
    AIR_DELIVERY_SHARE = 0.25
    LOCAL_DELIVERY_SHARE = 0.29

    # 2. Константы логистики
    MONTHLY_ORDERS = config.TARGET_ORDERS_MONTH  # 10 000
    CFO_TRIPS_PER_WEEK_PER_TRUCK = 2

    # Тарифы
    OWN_FLEET_TARIFF_RUB_KM = config.TRANSPORT_TARIFF_RUB_PER_KM # 13.4 руб/км
    LOCAL_FLEET_TARIFF_RUB_KM = 11.2 # Усредненный тариф для местных перевозок

    def calculate_required_fleet(self) -> int:
        """
        Рассчитывает минимальное количество собственных 18-20 тонных грузовиков для ЦФО.
        """
        # Рассчитываем количество заказов, которые нужно доставить в ЦФО за неделю
        cfo_orders_per_month = self.MONTHLY_ORDERS * self.CFO_OWN_FLEET_SHARE
        weeks_in_month = 4.33 # Среднее количество недель в месяце
        cfo_orders_per_week = cfo_orders_per_month / weeks_in_month

        # Допущение: 1 рейс = 1 заказ (консолидированный до точки в ЦФО)
        # Это упрощение, так как один рейс может содержать несколько заказов.
        # Здесь "рейс" означает поездку до одного из хабов ЦФО.
        total_cfo_trips_per_week = cfo_orders_per_week

        # Расчет необходимого количества грузовиков
        required_trucks = total_cfo_trips_per_week / self.CFO_TRIPS_PER_WEEK_PER_TRUCK
        
        return math.ceil(required_trucks)

    def calculate_annual_transport_cost(self, avg_dist_cfo: float, avg_dist_svo: float, avg_dist_local: float) -> float:
        """
        Рассчитывает годовые транспортные расходы для всех трех потоков.
        """
        annual_orders = self.MONTHLY_ORDERS * 12

        # Затраты на ЦФО (собственный флот)
        cost_cfo = (annual_orders * self.CFO_OWN_FLEET_SHARE) * avg_dist_cfo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на Авиа (доставка в SVO)
        cost_svo = (annual_orders * self.AIR_DELIVERY_SHARE) * avg_dist_svo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на местные перевозки (наемный транспорт)
        cost_local = (annual_orders * self.LOCAL_DELIVERY_SHARE) * avg_dist_local * self.LOCAL_FLEET_TARIFF_RUB_KM

        return cost_cfo + cost_svo + cost_local

    # ============================================================================
    # ПРОМПТ 3: Интеграция и оптимизация - новые методы FleetOptimizer
    # ============================================================================

    def calculate_optimal_fleet_and_cost(self, location_data: dict, geo_router: OSRMGeoRouter) -> dict:
        """
        Рассчитывает T_год (годовые транспортные расходы) и оптимальный флот для локации.

        Args:
            location_data: Данные о локации (координаты и другие параметры)
            geo_router: Экземпляр OSRMGeoRouter для расчета маршрутов

        Returns:
            Словарь с данными о флоте и транспортных расходах
        """
        print(f"\n  > [FleetOptimizer] Расчет флота и T_год для '{location_data['location_name']}'")

        # Получаем точные дорожные расстояния через OSRMGeoRouter
        location_coords = (location_data['lat'], location_data['lon'])
        route_data = geo_router.calculate_weighted_annual_distance(location_coords)

        # Извлекаем расстояния для каждого потока
        dist_cfo = route_data['CFO']['distance_km']
        dist_svo = route_data['SVO']['distance_km']
        dist_lpu = route_data['LPU']['distance_km']

        # Рассчитываем годовые транспортные расходы (T_год) используя тарифы
        annual_orders = self.MONTHLY_ORDERS * 12

        # Затраты на ЦФО (собственный флот, тариф 13.4 руб/км)
        cost_cfo = (annual_orders * self.CFO_OWN_FLEET_SHARE) * dist_cfo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на Авиа (доставка в SVO, тариф 13.4 руб/км)
        cost_svo = (annual_orders * self.AIR_DELIVERY_SHARE) * dist_svo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на местные перевозки (наемный транспорт, тариф 11.2 руб/км)
        cost_local = (annual_orders * self.LOCAL_DELIVERY_SHARE) * dist_lpu * self.LOCAL_FLEET_TARIFF_RUB_KM

        total_annual_transport_cost = cost_cfo + cost_svo + cost_local

        # Рассчитываем необходимый флот
        # 1. Грузовики 18-20 тонн для ЦФО (2 рейса/нед)
        cfo_orders_per_month = self.MONTHLY_ORDERS * self.CFO_OWN_FLEET_SHARE
        weeks_in_month = 4.33
        cfo_orders_per_week = cfo_orders_per_month / weeks_in_month
        required_heavy_trucks = math.ceil(cfo_orders_per_week / self.CFO_TRIPS_PER_WEEK_PER_TRUCK)

        # 2. Грузовики 5 тонн для Москвы (ежедневно, 6-8 точек)
        local_orders_per_day = (self.MONTHLY_ORDERS * self.LOCAL_DELIVERY_SHARE) / 22  # 22 рабочих дня
        points_per_truck = 7  # Среднее между 6 и 8
        required_light_trucks = math.ceil(local_orders_per_day / points_per_truck)

        print(f"    - T_год (общие транспортные расходы): {total_annual_transport_cost:,.0f} руб/год")
        print(f"    - Требуется 18-20т грузовиков (ЦФО): {required_heavy_trucks} шт")
        print(f"    - Требуется 5т грузовиков (Москва): {required_light_trucks} шт")

        return {
            'total_annual_transport_cost': total_annual_transport_cost,
            'cost_breakdown': {
                'cfo': cost_cfo,
                'svo': cost_svo,
                'local': cost_local
            },
            'fleet_required': {
                'heavy_trucks_18_20t': required_heavy_trucks,
                'light_trucks_5t': required_light_trucks
            },
            'distances': {
                'cfo_km': dist_cfo,
                'svo_km': dist_svo,
                'local_km': dist_lpu
            }
        }

    def calculate_relocation_capex(self, new_location_coords: tuple, geo_router: OSRMGeoRouter) -> dict:
        """
        Рассчитывает стоимость единовременного физического переезда товара.
        Использует тариф наемного транспорта 2,500 руб/час.

        Args:
            new_location_coords: Координаты новой локации (lat, lon)
            geo_router: Экземпляр OSRMGeoRouter для расчета времени в пути

        Returns:
            Словарь с данными о CAPEX переезда
        """
        print(f"\n  > [FleetOptimizer] Расчет CAPEX переезда в локацию {new_location_coords}")

        # Тариф наемного транспорта для переезда
        HIRED_TRANSPORT_TARIFF_RUB_H = 2500  # руб/час

        # Время на погрузку/разгрузку (фиксированное)
        LOADING_UNLOADING_TIME_H = 4  # часа (по 2 часа на каждую операцию)

        # Получаем маршрут от текущего склада (Сходненская) до новой локации
        current_hub = geo_router.CURRENT_HUB_COORDS
        route = geo_router.get_route_details(current_hub, new_location_coords)

        # Время в пути (туда-обратно, так как транспорт возвращается)
        travel_time_one_way_h = route['travel_time_h']
        travel_time_round_trip_h = travel_time_one_way_h * 2

        # Общее время одного рейса
        total_trip_time_h = travel_time_round_trip_h + LOADING_UNLOADING_TIME_H

        # Оценка количества рейсов (на основе объема товара)
        # Допущение: 17,000 м² склада, средняя загрузка 40% = 6,800 м² товара
        # Один грузовик 20т ≈ 80 м³ ≈ примерно покрывает 100 м² площади при высоте 0.8м
        warehouse_area_sqm = config.WAREHOUSE_TOTAL_AREA_SQM
        avg_load_ratio = 0.4  # 40% загрузка склада
        area_per_truck_sqm = 100  # м² товара на один рейс грузовика

        estimated_trips = math.ceil((warehouse_area_sqm * avg_load_ratio) / area_per_truck_sqm)

        # Общее время всех рейсов
        total_time_all_trips_h = estimated_trips * total_trip_time_h

        # Стоимость транспортировки
        transport_cost_rub = total_time_all_trips_h * HIRED_TRANSPORT_TARIFF_RUB_H

        print(f"    - Расстояние: {route['route_distance_km']:.1f} км (в одну сторону)")
        print(f"    - Время в пути (туда-обратно): {travel_time_round_trip_h:.2f} ч")
        print(f"    - Общее время одного рейса: {total_trip_time_h:.2f} ч")
        print(f"    - Необходимо рейсов: {estimated_trips}")
        print(f"    - Общее время всех рейсов: {total_time_all_trips_h:.1f} ч")
        print(f"    - CAPEX транспортировки товара: {transport_cost_rub:,.0f} руб")

        return {
            'transport_capex_rub': transport_cost_rub,
            'distance_km': route['route_distance_km'],
            'estimated_trips': estimated_trips,
            'total_time_hours': total_time_all_trips_h,
            'tariff_rub_per_hour': HIRED_TRANSPORT_TARIFF_RUB_H
        }


def plot_results():
    """
    Читает итоговый CSV, выводит данные в консоль и строит
    сравнительный график KPI для всех сценариев.
    """
    csv_path = os.path.join(config.OUTPUT_DIR, config.RESULTS_CSV_FILENAME)
    
    # Проверка, что файл с результатами существует
    if not os.path.exists(csv_path):
        print(f"Ошибка: Файл с результатами не найден по пути '{csv_path}'")
        print("Пожалуйста, сначала запустите симуляцию командой: python main.py")
        return

    # Загружаем данные. Указываем правильные разделители.
    df = pd.read_csv(csv_path, sep=';', decimal='.')
    
    print("\n" + "="*80)
    print("Загружены данные для анализа:")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80 + "\n")

    # --- Настройка визуализации ---
    sns.set_theme(style="whitegrid")
    # Создаем фигуру с двумя осями Y для отображения данных разного масштаба
    fig, ax1 = plt.subplots(figsize=(13, 8))

    # Ось Y 1 (левая): Пропускная способность (столбчатая диаграмма)
    color1 = 'tab:blue'
    ax1.set_xlabel('Сценарии', fontsize=12)
    ax1.set_ylabel('Пропускная способность (обработано заказов)', color=color1, fontsize=12)
    # Используем Seaborn для красивых столбцов
    plot1 = sns.barplot(
        x='Scenario_Name', 
        y='Achieved_Throughput_Monthly', 
        data=df, 
        ax=ax1, 
        palette='Blues_d',
        label='Пропускная способность'
    )
    ax1.tick_params(axis='y', labelcolor=color1)
    # Поворачиваем подписи по оси X для лучшей читаемости
    plt.xticks(rotation=15, ha="right")

    # Ось Y 2 (правая): Годовой OPEX (линейный график)
    ax2 = ax1.twinx()  # Создаем вторую ось, которая делит ось X с первой
    color2 = 'tab:red'
    ax2.set_ylabel('Годовой OPEX (млн руб.)', color=color2, fontsize=12)
    # Рисуем линию поверх столбцов
    plot2 = sns.lineplot(
        x='Scenario_Name', 
        y=df['Total_Annual_OPEX_RUB'] / 1_000_000, 
        data=df, 
        ax=ax2, 
        color=color2, 
        marker='o', 
        linewidth=2,
        label='Годовой OPEX'
    )
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Общий заголовок и компоновка
    plt.title(f"Сравнение сценариев для локации '{df['Location_Name'][0]}'", fontsize=16, pad=20)
    fig.tight_layout()  # Автоматически подбирает отступы, чтобы ничего не обрезалось

    # Сохранение итогового изображения
    output_image_path = os.path.join(config.OUTPUT_DIR, "simulation_comparison.png")
    plt.savefig(output_image_path)
    
    print(f"[Analysis] Сравнительный график успешно сохранен: '{output_image_path}'")
    plt.show()

if __name__ == "__main__":
    # Демонстрация работы AvitoParserStub
    print("\n" + "="*80)
    print("ЗАПУСК ПАРСЕРА-ЗАГЛУШКИ (AvitoParserStub)")
    print("="*80)

    parser = AvitoParserStub()

    # Используем данные из config.py
    candidate_locations = config.ALL_CANDIDATE_LOCATIONS
    print(f"Найдено {len(candidate_locations)} потенциальных локаций для анализа.")

    scored_results = parser.filter_and_score_locations(candidate_locations)

    print(f"\nПосле фильтрации и оценки осталось {len(scored_results)} подходящих локаций:")
    print("-" * 80)

    # Демонстрация для конкретных локаций
    for loc in scored_results:
        if loc['location_name'] in ['Белый Раст Логистика', 'PNK Чашниково BTS']:
            print(f"Локация: '{loc['location_name']}' ({loc['type']})")
            print(f"  > Площадь: {loc['area_offered_sqm']} кв.м")
            print(f"  > OPEX (помещение): {loc['annual_building_opex']:,.0f} руб./год")
            print(f"  > CAPEX (начальный):  {loc['total_initial_capex']:,.0f} руб.")
            print("-" * 80)

    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ НОВЫХ КЛАССОВ (AvitoCIANScraper, OSRMGeoRouter, FleetOptimizer)")
    print("="*80)

    # ============================================================================
    # ПРОМПТ 1: Демонстрация AvitoCIANScraper
    # ============================================================================
    print("\n[1] Демонстрация AvitoCIANScraper (полный парсер с HTTP-запросами)")
    print("="*80)

    scraper = AvitoCIANScraper()

    # Имитация HTTP-запроса к API
    raw_offers = scraper.fetch_raw_offers_data("https://api.avito.ru/search?category=warehouse&area_min=17000")

    # Парсинг и фильтрация
    filtered_offers = scraper.parse_and_filter_offers(raw_offers)

    print(f"\n[AvitoCIANScraper] Итого найдено подходящих локаций: {len(filtered_offers)}")

    # ============================================================================
    # ПРОМПТ 2: Демонстрация OSRMGeoRouter (бесплатный API)
    # ============================================================================
    print("\n" + "="*80)
    print("[2] Демонстрация OSRMGeoRouter (бесплатный OSRM API)")
    print("="*80)

    geo_router = OSRMGeoRouter(use_geocoding=False)  # Geocoding отключен для быстроты

    # Пример: маршрут Сходненская -> Логопарк Север-2
    test_location_coords = (56.03, 37.59)  # Логопарк Север-2

    print(f"\nТестовый маршрут: Сходненская {geo_router.CURRENT_HUB_COORDS} -> Логопарк Север-2 {test_location_coords}")
    route_demo = geo_router.get_route_details(geo_router.CURRENT_HUB_COORDS, test_location_coords)

    print("\n  > [JSON-ответ от OSRM API]")
    print(f"    {{")
    print(f"      'status': '{route_demo['status']}',")
    print(f"      'mode': '{route_demo['mode']}',")
    print(f"      'route_distance_km': {route_demo['route_distance_km']},")
    print(f"      'travel_time_h': {route_demo['travel_time_h']},")
    print(f"      'source': '{route_demo.get('source', 'unknown')}'")
    print(f"    }}")

    # Расчет взвешенного годового расстояния
    weighted_distance_demo = geo_router.calculate_weighted_annual_distance(test_location_coords)

    # ============================================================================
    # ПРОМПТ 3: Демонстрация новых методов FleetOptimizer
    # ============================================================================
    print("\n" + "="*80)
    print("[3] Демонстрация FleetOptimizer (расчет флота и CAPEX переезда)")
    print("="*80)

    fleet_opt = FleetOptimizer()

    # Выбираем тестовую локацию
    test_location = filtered_offers[0]

    # Расчет оптимального флота и годовых расходов
    fleet_cost_result = fleet_opt.calculate_optimal_fleet_and_cost(test_location, geo_router)

    # Расчет CAPEX переезда
    relocation_capex = fleet_opt.calculate_relocation_capex(test_location_coords, geo_router)

    print("\n[ИТОГОВАЯ СВОДКА]")
    print(f"  Локация: {test_location['location_name']}")
    print(f"  T_год (годовые транспортные расходы): {fleet_cost_result['total_annual_transport_cost']:,.0f} руб")
    print(f"  CAPEX переезда (транспортировка товара): {relocation_capex['transport_capex_rub']:,.0f} руб")
    print(f"  Флот 18-20т: {fleet_cost_result['fleet_required']['heavy_trucks_18_20t']} шт")
    print(f"  Флот 5т: {fleet_cost_result['fleet_required']['light_trucks_5t']} шт")

    # ============================================================================
    # ДЕМОНСТРАЦИЯ ДЕТАЛЬНОГО ТРАНСПОРТНОГО ПЛАНИРОВЩИКА
    # ============================================================================
    print("\n" + "="*80)
    print("[4] Демонстрация DetailedFleetPlanner (детальный расчет транспорта)")
    print("="*80)

    detailed_planner = DetailedFleetPlanner()

    # Используем расстояния из предыдущего расчета
    distances = {
        'cfo_km': fleet_cost_result['distances']['cfo_km'],
        'svo_km': fleet_cost_result['distances']['svo_km'],
        'local_km': fleet_cost_result['distances']['local_km']
    }

    # Детальный расчет флота
    fleet_summary = detailed_planner.calculate_fleet_requirements(distances)

    # Расчет доков
    dock_requirements = detailed_planner.calculate_dock_requirements(fleet_summary)

    # График работы
    transport_schedule = detailed_planner.generate_transport_schedule(fleet_summary)

    # Симуляция доков
    print("\n  > [DockSimulator] Проверка пропускной способности доков")
    dock_sim = DockSimulator(
        inbound_docks=dock_requirements['inbound_docks'],
        outbound_docks=dock_requirements['outbound_docks']
    )
    dock_simulation = dock_sim.simulate_dock_operations(dock_requirements['peak_trips_per_day'])

    print(f"    - Утилизация inbound: {dock_simulation['inbound_utilization_percent']:.1f}%")
    print(f"    - Утилизация outbound: {dock_simulation['outbound_utilization_percent']:.1f}%")
    print(f"    - Достаточность: {'ДА' if dock_simulation['is_sufficient'] else 'НЕТ, требуется больше доков'}")

    print("\n[ДЕТАЛЬНАЯ ТРАНСПОРТНАЯ СВОДКА]")
    print(f"  Всего единиц техники: {fleet_summary['total_vehicles']}")
    print(f"  Рекомендация: {'Аренда флота' if fleet_summary['recommendation'] == 'lease' else 'Покупка флота'}")
    print(f"  Годовой OPEX (собственный): {fleet_summary['total_opex_own_fleet']:,.0f} руб")
    print(f"  Годовой OPEX (аренда): {fleet_summary['total_opex_lease']:,.0f} руб")
    print(f"  CAPEX (покупка): {fleet_summary['total_capex_purchase']:,.0f} руб")
    print(f"  Доков (приемка/отгрузка): {dock_requirements['inbound_docks']}/{dock_requirements['outbound_docks']}")

    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*80)
```

## `config.py`

```py
# config.py

"""
Глобальные статические константы и базовые настройки проекта.
"""

# --- Финансовые и HR константы ---
INITIAL_STAFF_COUNT = 100
OPERATOR_SALARY_RUB_MONTH = 105000
TRANSPORT_TARIFF_RUB_PER_KM = 13.4  # Средний тариф для 18-20т фуры

# --- Константы склада и локации ---
WAREHOUSE_TOTAL_AREA_SQM = 17000
ANNUAL_RENT_PER_SQM_RUB = 7500.0
PURCHASE_BUILDING_COST_RUB = 1_500_000_000
BASE_EQUIPMENT_CAPEX_RUB = 350_000_000  # Стеллажи, климат, валидация
MAINTENANCE_COST_OF_OWNED_BUILDING_RUB_YEAR = 50_000_000

# --- Симуляционные константы ---
BASE_ORDER_PROCESSING_TIME_MIN = 15.0
TARGET_ORDERS_MONTH = 10000
SIMULATION_WORKING_DAYS = 20
MINUTES_PER_WORKING_DAY = 8 * 60

# --- Гео-константы для анализа ---
KEY_GEO_POINTS = {
    "Current_HUB": (55.858, 37.433),
    "Airport_SVO": (55.97, 37.41),
    "CFD_HUBs_Avg": (54.51, 36.26),
    "Moscow_Clients_Avg": (55.75, 37.62),
}

# --- Настройки вывода ---
OUTPUT_DIR = "output"
RESULTS_CSV_FILENAME = "simulation_results_dynamic.csv"

# --- Кандидаты на релокацию (имитация данных из парсера) ---
ALL_CANDIDATE_LOCATIONS = {
    "logopark_sever_2": {
        "name": "Логопарк Север-2",
        "type": "ARENDA",
        "lat": 56.03,
        "lon": 37.59,
        "area_offered_sqm": 17000,
        "cost_metric_base": 8000.0,  # руб/м²/год
        "current_class": "A_verified"
    },
    "bely_rast": {
        "name": "Белый Раст Логистика",
        "type": "ARENDA",
        "lat": 56.09,
        "lon": 37.49,
        "area_offered_sqm": 20000,
        "cost_metric_base": 10000.0, # руб/м²/год
        "current_class": "A_verified"
    },
    "troitse_seltso": {
        "name": "Склад Троице-сельцо",
        "type": "ARENDA",
        "lat": 55.98,
        "lon": 37.60,
        "area_offered_sqm": 25000,
        "cost_metric_base": 15000.0, # руб/м²/год
        "current_class": "A_requires_mod"
    },
    "plt_severnoe_sheremetievo": {
        "name": "ПЛТ Северное Шереметьево",
        "type": "ARENDA",
        "lat": 56.00,
        "lon": 37.50,
        "area_offered_sqm": 30000,
        "cost_metric_base": 10000.0, # руб/м²/год
        "current_class": "A_verified"
    },
    "pnk_chashnikovo": {
        "name": "PNK Чашниково BTS",
        "type": "POKUPKA_BTS",
        "lat": 56.01,
        "lon": 37.10,
        "area_offered_sqm": 20000,
        "cost_metric_base": 1_500_000_000, # общая стоимость
        "current_class": "A_requires_mod"
    },
    "esipovo_bts": {
        "name": "Деревня Есипово BTS",
        "type": "POKUPKA_BTS",
        "lat": 56.02,
        "lon": 37.00,
        "area_offered_sqm": 25000,
        "cost_metric_base": 2_000_000_000, # общая стоимость
        "current_class": "A_requires_mod"
    }
}
```

## `HACKATHON_PLAN_14H.md`

```md
# 🏁 ХАКАТОН: Перенос HUB-склада за МКАД (14 часов)

## 🎯 Условия

- **Время:** 14 часов (может меньше)
- **Команда:** 4 человека
- **Задача:** Железобетонно переезжаем за МКАД, выбрать оптимальную стратегию
- **Стек:** FlexSim + SimPy
- **Инструменты:** Яндекс.Карты (не Google Maps)

---

## 📊 4 Сценария для анализа

❌ ~~Stay_Moscow~~ - НЕ рассматриваем

✅ **Сценарий 1: Move_No_Mitigation**
- Переезд без компенсаций
- Атрицион: 25% персонала
- Автоматизация: 0
- Инвестиции: Минимальные

✅ **Сценарий 2: Move_With_Compensation**
- Переезд + HR компенсации
- Атрицион: 15% (снижен!)
- Автоматизация: 0
- Инвестиции: 50М руб на удержание

✅ **Сценарий 3: Move_Basic_Automation**
- Переезд + базовая автоматизация
- Атрицион: 25%
- Автоматизация: WMS + конвейеры
- Инвестиции: 100М руб

✅ **Сценарий 4: Move_Advanced_Automation**
- Переезд + высокая автоматизация
- Атрицион: 25%
- Автоматизация: AutoStore + AGV + роботизация
- Инвестиции: 300М руб

---

## 👥 4 Параллельных блока (по человеку)

### 🟦 БЛОК 1: Logistics & Location (Аналитика)
**Ответственный:** Logistics Analyst  
**Время:** 14 часов  
**Инструменты:** Python + Яндекс.Карты API + Excel

**Задачи:**

#### 1.1 Выбор локации за МКАД (4 часа)
```python
# Анализ 3 локаций:
locations = [
    {
        'name': 'Химки',
        'coords': (55.8970, 37.4460),
        'distance_sheremetyevo': 20,  # км
        'rental_cost': 7000,  # руб/м²/год
        'pros': 'Близко к аэропорту',
        'cons': 'Дорого'
    },
    {
        'name': 'Красногорск',
        'coords': (55.8206, 37.3297),
        'distance_sheremetyevo': 30,
        'rental_cost': 5200,
        'pros': 'Оптимальный баланс',
        'cons': 'Средние показатели'
    },
    {
        'name': 'Солнечногорск',
        'coords': (56.1838, 36.9778),
        'distance_sheremetyevo': 35,
        'rental_cost': 3800,
        'pros': 'Дёшево, место для расширения',
        'cons': 'Далеко от Москвы'
    }
]

# Scoring matrix с весами
weights = {
    'distance_sheremetyevo': 0.30,
    'rental_cost': 0.25,
    'transport_access': 0.20,
    'staff_accessibility': 0.15,
    'expansion_potential': 0.10
}

# Выбрать топ-1 локацию
```

#### 1.2 Карты маршрутов с Яндекс.Картами (3 часа)
```python
import requests
import folium

# Яндекс.Карты API
YANDEX_API_KEY = "your_key"

# Маршрут: Шереметьево → Новый склад
route_sheremetyevo = get_route_yandex(
    start=(55.9726, 37.4145),  # Шереметьево
    end=selected_location['coords']
)

# Маршруты доставки по ЦФО
cfo_routes = [
    ('Москва', (55.7558, 37.6173)),
    ('Владимир', (56.1366, 40.3966)),
    ('Тверь', (56.8587, 35.9176)),
    # ... еще 5-7 городов
]

# Визуализация на карте
map = folium.Map(location=[55.75, 37.62], zoom_start=7)
# Добавить маршруты
```

#### 1.3 Расчёт транспортных затрат (3 часа)
```python
# Текущие vs Новые затраты
transport_analysis = {
    'current_moscow': {
        'sheremetyevo_distance': 35,  # км
        'avg_cfo_distance': 120,
        'annual_cost': calculate_cost(35, 120)
    },
    'new_location': {
        'sheremetyevo_distance': location['distance_sheremetyevo'],
        'avg_cfo_distance': 145,  # +25 км
        'annual_cost': calculate_cost(location['distance'], 145)
    },
    'delta': new_cost - current_cost,
    'delta_percent': (new_cost / current_cost - 1) * 100
}
```

#### 1.4 Excel-отчёт (4 часа)
- Сравнение 3 локаций
- Транспортные затраты
- Карты маршрутов (screenshots)
- Рекомендация

**Deliverables:**
- ✅ `output/location_comparison.xlsx`
- ✅ `output/maps/yandex_routes_*.png`
- ✅ Python скрипт: `analysis/logistics_yandex.py`

---

### 🟩 БЛОК 2: HR & Attrition (Аналитика + ML)
**Ответственный:** HR Analyst / Data Scientist  
**Время:** 14 часов  
**Инструменты:** Python + scikit-learn + Excel

**Задачи:**

#### 2.1 ML-модель прогноза атрицион (6 часов)
```python
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

# Dataset: 100 сотрудников
employees = pd.DataFrame({
    'id': range(1, 101),
    'position': ['комплектовщик']*60 + ['оператор']*25 + ['менеджер']*15,
    'age': np.random.randint(25, 55, 100),
    'years_in_company': np.random.randint(1, 15, 100),
    'salary': [...],
    'commute_time_current': np.random.randint(30, 90, 100),
    'commute_time_new': np.random.randint(60, 150, 100),  # +30-60 мин
    'has_children': np.random.choice([0, 1], 100),
    'home_location': [...]
})

# Features engineering
employees['commute_increase'] = employees['commute_time_new'] - employees['commute_time_current']
employees['young_with_kids'] = (employees['age'] < 35) & (employees['has_children'] == 1)

# Обучить модель
X = employees[['age', 'commute_increase', 'position_encoded', ...]]
y = employees['will_leave']  # Target: 0 или 1

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# Предсказать кто уйдёт
predictions = model.predict_proba(employees)
employees['leave_probability'] = predictions[:, 1]

# Результат: 25 человек с highest probability уйдут
top_25_leaving = employees.nlargest(25, 'leave_probability')
```

#### 2.2 Компенсационные стратегии (4 часа)
```python
compensation_plans = {
    'plan_1_no_mitigation': {
        'cost': 0,
        'attrition': 0.25,
        'workers_remaining': 75,
        'hiring_cost': 25 * 150_000  # 3.75М
    },
    'plan_2_basic': {
        'cost': 6_000_000,  # Транспорт + проезд
        'attrition': 0.15,  # Снижено!
        'workers_remaining': 85,
        'hiring_cost': 15 * 150_000  # 2.25М
    },
    'plan_3_extended': {
        'cost': 50_000_000,  # Зарплаты + жильё + бонусы
        'attrition': 0.05,  # Минимум!
        'workers_remaining': 95,
        'hiring_cost': 5 * 150_000  # 0.75М
    }
}

# ROI analysis
for plan in compensation_plans:
    plan['total_cost_year1'] = plan['cost'] + plan['hiring_cost']
    plan['roi'] = calculate_roi(plan)
```

#### 2.3 Интеграция в сценарии (2 часа)
```python
# Применить к 4 сценариям
scenarios = {
    'Move_No_Mitigation': {'attrition': 0.25, 'compensation': plan_1},
    'Move_With_Compensation': {'attrition': 0.15, 'compensation': plan_2},
    'Move_Basic_Automation': {'attrition': 0.25, 'compensation': plan_1},
    'Move_Advanced_Automation': {'attrition': 0.25, 'compensation': plan_1}
}
```

#### 2.4 Отчёт (2 часа)
- ML модель и feature importance
- Список 25 человек с риском увольнения
- 3 компенсационных плана
- Рекомендации

**Deliverables:**
- ✅ `models/attrition_model.pkl`
- ✅ `output/hr_attrition_report.xlsx`
- ✅ Python скрипт: `analysis/hr_ml.py`

---

### 🟨 БЛОК 3: SimPy Simulation (Программирование)
**Ответственный:** Python Developer  
**Время:** 14 часов  
**Инструменты:** Python + SimPy

**Задачи:**

#### 3.1 Базовая SimPy модель (6 часов)
```python
import simpy
import pandas as pd

class WarehouseSimulation:
    def __init__(self, env, config, workers_count, attrition_rate=0.25):
        self.env = env
        self.config = config
        self.workers = simpy.Resource(env, capacity=int(workers_count * (1 - attrition_rate)))
        
        self.orders_processed = 0
        self.total_cycle_time = 0
        
    def receiving_process(self):
        """Приёмка товара от поставщиков"""
        while True:
            yield self.env.timeout(2)  # Каждые 2 часа поставка
            
            with self.workers.request() as req:
                yield req
                yield self.env.timeout(1)  # 1 час на приёмку
                
    def picking_process(self):
        """Комплектация заказов"""
        while True:
            yield self.env.timeout(0.5)  # Новый заказ каждые 30 мин
            
            with self.workers.request() as req:
                yield req
                # Время зависит от количества работников
                picking_time = 2.5 if self.workers.capacity == 100 else 3.0
                yield self.env.timeout(picking_time)
                
                self.orders_processed += 1
                self.total_cycle_time += picking_time

# Запуск
env = simpy.Environment()
sim = WarehouseSimulation(env, config, workers_count=100, attrition_rate=0.25)
env.run(until=720)  # 30 дней

print(f"Orders processed: {sim.orders_processed}")
print(f"Avg cycle time: {sim.total_cycle_time / sim.orders_processed:.2f} hours")
```

#### 3.2 Модель для 4 сценариев (4 часа)
```python
scenarios = [
    {
        'name': 'Move_No_Mitigation',
        'workers': 75,  # -25%
        'automation_level': 0,
        'throughput_boost': 1.0
    },
    {
        'name': 'Move_With_Compensation',
        'workers': 85,  # -15%
        'automation_level': 0,
        'throughput_boost': 1.0
    },
    {
        'name': 'Move_Basic_Automation',
        'workers': 75,  # -25%
        'automation_level': 1,
        'throughput_boost': 1.2  # +20% за счёт конвейеров
    },
    {
        'name': 'Move_Advanced_Automation',
        'workers': 50,  # Роботы заменяют 25 человек
        'automation_level': 2,
        'throughput_boost': 1.5  # +50% за счёт AutoStore
    }
]

results = []
for scenario in scenarios:
    env = simpy.Environment()
    sim = WarehouseSimulation(env, config, scenario['workers'])
    sim.throughput_boost = scenario['throughput_boost']
    env.run(until=720)
    
    results.append({
        'scenario': scenario['name'],
        'orders_processed': sim.orders_processed * sim.throughput_boost,
        'throughput': sim.orders_processed / 720 * sim.throughput_boost,
        'workers': scenario['workers']
    })

# Экспорт
pd.DataFrame(results).to_csv('output/simulation_results.csv')
```

#### 3.3 Socket API для FlexSim (опционально, 2 часа)
```python
# Только если успеем
import socket
import json

class FlexSimBridge:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 5005))
        
    def send_state(self, state):
        message = json.dumps(state).encode() + b'!'
        self.socket.sendall(message)

# В симуляции
bridge = FlexSimBridge()
bridge.send_state({
    'time': env.now,
    'orders': sim.orders_processed,
    'workers': sim.workers.capacity
})
```

#### 3.4 Финальный скрипт (2 часа)
- Красивый вывод результатов
- Графики (matplotlib)
- Экспорт в JSON/CSV

**Deliverables:**
- ✅ `simpy_models/warehouse.py`
- ✅ `simpy_models/main_simulation.py`
- ✅ `output/simulation_results.csv`
- ✅ `output/simulation_comparison.png`

---

### 🟥 БЛОК 4: FlexSim Visualization (Программирование)
**Ответственный:** FlexSim Specialist  
**Время:** 14 часов  
**Инструменты:** FlexSim

**Задачи:**

#### 4.1 Базовая 3D модель (6 часов)
```
Упрощённая модель склада:
- Зона приёмки (2 дока)
- Складская зона (упрощённые стеллажи)
- Зона комплектации (5 станций)
- Зона отгрузки (2 дока)
- Операторы: показать визуально 100 → 75 человек
```

**Приоритет:**
1. Работоспособность модели
2. Визуализация разницы в персонале
3. Dashboard с метриками

#### 4.2 Визуализация 4 сценариев (4 часа)
```
Для каждого сценария:
- Отдельный слой или состояние модели
- Показать количество работников
- Показать throughput (orders/hour)
- Показать автоматизацию (для сценариев 3-4)
```

**Сценарий 3:** Добавить конвейеры (визуально)  
**Сценарий 4:** Добавить AutoStore (можно схематично)

#### 4.3 Dashboard (2 часа)
```flexscript
// Real-time метрики
- Throughput (orders/hour)
- Workers available
- Utilization (%)
- Avg cycle time

// Comparison bars для 4 сценариев
```

#### 4.4 Экспорт видео (2 часа)
```
Короткое видео (2-3 минуты):
1. Текущая ситуация (0:30)
2. Проблема: -25% персонала (0:15)
3. Сценарий 1 (0:30)
4. Сценарий 2 (0:30)
5. Сценарий 3 (0:30)
6. Сценарий 4 (0:30)
7. Сравнение + рекомендация (0:15)
```

**Deliverables:**
- ✅ `flexsim_models/warehouse_hub.fsm`
- ✅ `output/videos/scenarios_demo.mp4`
- ✅ Screenshots dashboard

---

## ⏱️ Timeline (14 часов)

### Час 0-4: Setup & Parallel Start
```
00:00-01:00  Kickoff, распределение задач
01:00-04:00  Параллельная работа (все 4 блока)

Блок 1: Анализ локаций + API Яндекс.Карт
Блок 2: ML модель атрицион
Блок 3: Базовая SimPy модель
Блок 4: FlexSim базовая модель
```

### Час 4-10: Deep Work
```
04:00-10:00  Основная разработка (6 часов)

Блок 1: Карты маршрутов + транспортные затраты
Блок 2: Компенсационные планы + интеграция
Блок 3: 4 сценария в SimPy
Блок 4: Визуализация сценариев
```

### Час 10-12: Integration & Testing
```
10:00-11:00  Интеграция результатов
11:00-12:00  Тестирование, bug fixes
```

### Час 12-14: Finalization
```
12:00-13:00  Финальные доработки
13:00-13:30  Создание презентации
13:30-14:00  Репетиция презентации
```

---

## 📦 Минимальные Deliverables (MVP)

### Must Have:
1. ✅ **Excel-отчёт** с выбором локации (Блок 1)
2. ✅ **Excel-отчёт** по HR и атрицион (Блок 2)
3. ✅ **CSV/JSON** результаты SimPy для 4 сценариев (Блок 3)
4. ✅ **FlexSim модель** с визуализацией (Блок 4)
5. ✅ **Презентация** (5-7 слайдов) с рекомендацией

### Nice to Have:
- 🔶 Яндекс.Карты с реальными маршрутами
- 🔶 FlexSim видео (2-3 мин)
- 🔶 ML модель (.pkl файл)
- 🔶 Socket интеграция FlexSim ↔ Python

---

## 🎯 Критерии успеха

### Обязательные:
- [ ] Выбрана оптимальная локация за МКАД (с обоснованием)
- [ ] Рассчитана стоимость переезда для каждого сценария
- [ ] Проанализирован атрицион персонала (25% → кто уйдёт)
- [ ] Симуляция 4 сценариев в SimPy работает
- [ ] FlexSim модель демонстрирует разницу
- [ ] Презентация с чёткой рекомендацией

### Желательные:
- [ ] Яндекс.Карты интеграция
- [ ] ML модель с feature importance
- [ ] FlexSim видео
- [ ] ROI analysis на 3-5 лет

---

## 📊 Финальная презентация (5-7 слайдов)

### Слайд 1: Проблема
- Необходимость переезда за МКАД
- Потеря 25% персонала
- Нужно выбрать оптимальную стратегию

### Слайд 2: Анализ локаций
- 3 кандидата (Химки / Красногорск / Солнечногорск)
- Scoring matrix
- **Рекомендация:** [Локация X]
- Карта Яндекс с маршрутами

### Слайд 3: HR и атрицион
- ML-прогноз: кто уйдёт (25 человек)
- 3 компенсационных плана
- Cost-benefit анализ

### Слайд 4: 4 Сценария - Результаты
```
Таблица:
| Сценарий | Throughput | Workers | Year 1 Cost | ROI |
|----------|------------|---------|-------------|-----|
| 1. No Mitigation | 1,200/day | 75 | 150М | 3 года |
| 2. With Compensation | 1,400/day | 85 | 200М | 2.5 года |
| 3. Basic Automation | 1,440/day | 75 | 250М | 3 года |
| 4. Advanced Automation | 1,800/day | 50 | 450М | 4 года |
```

### Слайд 5: FlexSim Визуализация
- Screenshot или GIF 3D модели
- Dashboard с метриками
- Сравнение сценариев

### Слайд 6: Рекомендация
**РЕКОМЕНДУЕМ: Сценарий [X]**

Обоснование:
- Оптимальный баланс cost/benefit
- Быстрый ROI
- Минимальные риски
- Соответствует бюджету

### Слайд 7: Next Steps
- План внедрения (timeline)
- Ключевые риски и митигация
- Бюджет детально

---

## 💾 Структура для быстрого старта

```
hackathon-warehouse/
├── data/
│   ├── employees.csv              # 100 человек (генерируем)
│   ├── locations.json             # 3 локации
│   └── transport_config.json      # Параметры транспорта
│
├── block1_logistics/              # Блок 1
│   ├── yandex_maps.py             # API Яндекс.Карт
│   ├── location_selection.py      # Выбор локации
│   └── transport_costs.py         # Расчёты
│
├── block2_hr/                     # Блок 2
│   ├── ml_attrition.py            # ML модель
│   └── compensation_plans.py      # HR планы
│
├── block3_simpy/                  # Блок 3
│   ├── warehouse_model.py         # SimPy модель
│   └── run_scenarios.py           # 4 сценария
│
├── block4_flexsim/                # Блок 4
│   └── warehouse.fsm              # FlexSim модель
│
└── output/
    ├── location_comparison.xlsx
    ├── hr_report.xlsx
    ├── simulation_results.csv
    ├── maps/                      # Яндекс.Карты
    ├── videos/                    # FlexSim видео
    └── presentation.pptx          # Финальная презентация
```

---

## ⚡ Quick Commands

### Setup (5 минут)
```bash
pip install simpy pandas numpy scikit-learn matplotlib openpyxl requests folium
```

### Генерация данных
```bash
python generate_synthetic_data.py
```

### Запуск блоков
```bash
# Блок 1
python block1_logistics/location_selection.py

# Блок 2
python block2_hr/ml_attrition.py

# Блок 3
python block3_simpy/run_scenarios.py

# Блок 4
# Открыть FlexSim вручную
```

---

## 🎯 Ключевые цифры для запоминания

- **100 операторов** → **75 после переезда** (-25%)
- **Шереметьево:** 35 км (сейчас) → 20-35 км (новая локация)
- **Стоимость аренды:** 3,800 - 7,000 руб/м²/год
- **Площадь склада:** ~12,000 - 15,000 м²
- **Throughput:** 1,500 заказов/день (сейчас)
- **4 сценария переезда** (без варианта остаться)

---

**ГЛАВНОЕ:** За 14 часов сделать работающий MVP с чёткой рекомендацией!

**Удачи! 🚀**

```

## `main.py`

```py
# main.py

"""
Главный исполняемый файл.
Оркестрирует полный цикл анализа релокации склада: от сбора данных до расчета ROI.
"""
from typing import Dict, Any, List, Optional
import math

# Импорт всех необходимых компонентов
from core.data_model import LocationSpec
from core.location import WarehouseConfigurator # Используется для расчета расстояний
from analysis import AvitoParserStub, FleetOptimizer, OSRMGeoRouter
from scenarios import SCENARIOS_CONFIG # Для расчета Z_перс
import config
from simulation_runner import SimulationRunner
from transport_planner import DetailedFleetPlanner, DockSimulator

def generate_detailed_relocation_plan(location_data: Dict[str, Any], z_pers_s1: float,
                                     fleet_summary: Optional[Dict[str, Any]] = None,
                                     dock_requirements: Optional[Dict[str, Any]] = None):
    """
    Генерирует текстовое описание детального плана переезда для оптимальной локации.
    """
    print(f"\n{'='*80}\n[Шаг 7] ДЕТАЛЬНЫЙ ПЛАН ПЕРЕЕЗДА ДЛЯ ОПТИМАЛЬНОЙ ЛОКАЦИИ: '{location_data['location_name']}'\n{'='*80}")
    print(f"Выбранная локация: {location_data['location_name']}")
    print(f"Тип владения: {'Аренда' if location_data['type'] == 'ARENDA' else 'Покупка/BTS'}")
    print(f"Предложенная площадь: {location_data['area_offered_sqm']} кв.м")
    print(f"Координаты: {location_data['lat']}, {location_data['lon']}")
    print(f"\nФинансовые показатели (Сценарий 1 - без смягчения):")
    print(f"  - Начальный CAPEX (здание, оборудование, GPP/GDP, модификации): {location_data['total_initial_capex']:,.0f} руб.")
    print(f"  - Годовой OPEX (помещение): {location_data['annual_building_opex']:,.0f} руб.")
    print(f"  - Годовой OPEX (персонал, мин.): {z_pers_s1:,.0f} руб.")
    print(f"  - Годовой OPEX (транспорт): {location_data['total_annual_transport_cost']:,.0f} руб.")
    print(f"  - Общий годовой OPEX (Сценарий 1): {location_data['total_annual_opex_s1']:,.0f} руб.")

    print(f"\nДетальные логистические параметры:")
    if fleet_summary:
        print(f"  - Всего единиц транспорта: {fleet_summary['total_vehicles']}")
        print(f"  - Рекомендация по флоту: {'Аренда' if fleet_summary['recommendation'] == 'lease' else 'Покупка'}")
        print(f"  - OPEX транспорта (при аренде): {fleet_summary['total_opex_lease']:,.0f} руб/год")
        print(f"  - CAPEX транспорта (при покупке): {fleet_summary['total_capex_purchase']:,.0f} руб")

        # Детализация по типам транспорта
        for fleet in fleet_summary['fleet_breakdown']:
            print(f"    * {fleet['vehicle_name']}: {fleet['required_count']} шт, {fleet['annual_trips']} рейсов/год")
    else:
        print(f"  - Требуемый собственный флот (ЦФО, упрощенный расчет): {location_data['required_fleet_count']} грузовиков")

    if dock_requirements:
        print(f"\nТребования к инфраструктуре доков:")
        print(f"  - Inbound доков (приемка): {dock_requirements['inbound_docks']}")
        print(f"  - Outbound доков (отгрузка): {dock_requirements['outbound_docks']}")
        print(f"  - Пиковая нагрузка: {dock_requirements['peak_trips_per_day']:.1f} рейсов/день")
        print(f"  - Утилизация доков: {dock_requirements['dock_utilization_percent']:.1f}%")
    print("\nРекомендации для диаграммы Ганта:")
    print("1. Фаза планирования (1-2 месяца):")
    print("   - Детальный анализ выбранной локации, юридическая проверка.")
    print("   - Разработка проектной документации для GPP/GDP и модификаций.")
    print("   - Тендеры на поставщиков оборудования и строительные работы.")
    print("2. Фаза подготовки (3-6 месяцев):")
    print("   - Строительно-монтажные работы (модификации, установка климатики).")
    print("   - Закупка и монтаж стеллажного оборудования.")
    print("   - Валидация GPP/GDP систем.")
    print("   - Набор и обучение нового персонала.")
    print("3. Фаза переезда и запуска (1-2 месяца):")
    print("   - Поэтапный перенос запасов и оборудования.")
    print("   - Тестовый запуск операций.")
    print("   - Оптимизация процессов.")
    print("\nДополнительные соображения:")
    if location_data['current_class'] == 'A_requires_mod':
        print("  - Требуются значительные инвестиции в доведение помещения до фармацевтических стандартов.")
    print("  - Необходимо разработать детальный план минимизации рисков при переезде.")
    print(f"{'='*80}\n")

def main_multi_location_runner():
    """
    Оркестрирует полный процесс анализа множества локаций,
    выбирает оптимальную и запускает для нее детальный анализ.
    """
    print("\n" + "="*80)
    print("ЗАПУСК КОМПЛЕКСНОГО АНАЛИЗА МНОЖЕСТВА ЛОКАЦИЙ")
    print("="*80)

    # 1. Сбор и фильтрация данных (Avito Stub)
    parser = AvitoParserStub()
    candidate_locations_raw = config.ALL_CANDIDATE_LOCATIONS
    filtered_locations: List[Dict[str, Any]] = parser.filter_and_score_locations(candidate_locations_raw)
    print(f"\n[Шаг 1] Отфильтровано {len(filtered_locations)} подходящих локаций из {len(candidate_locations_raw)}.")

    if not filtered_locations:
        print("Нет локаций, удовлетворяющих минимальным требованиям. Анализ прекращен.")
        return

    enriched_locations: List[Dict[str, Any]] = []

    # Расчет Z_перс (минимальные расходы на персонал для Сценария 1)
    s1_staff_attrition_rate = SCENARIOS_CONFIG["1_Move_No_Mitigation"]["staff_attrition_rate"]
    s1_staff_count = math.floor(config.INITIAL_STAFF_COUNT * (1 - s1_staff_attrition_rate))
    z_pers_s1 = s1_staff_count * config.OPERATOR_SALARY_RUB_MONTH * 12
    print(f"[Шаг 3] Расчет минимальных расходов на персонал (Сценарий 1): {z_pers_s1:,.0f} руб./год")

    for loc_data in filtered_locations:
        print(f"\n[Шаг 2] Анализ логистики для '{loc_data['location_name']}'...")
        
        # Используем WarehouseConfigurator для расчета расстояний
        # Передаем фиктивные значения rent_rate_sqm_year и purchase_cost,
        # так как для расчета расстояний они не используются.
        geo_calculator = WarehouseConfigurator(
            ownership_type=loc_data['type'],
            rent_rate_sqm_year=config.ANNUAL_RENT_PER_SQM_RUB,
            purchase_cost=config.PURCHASE_BUILDING_COST_RUB,
            lat=loc_data['lat'],
            lon=loc_data['lon']
        )
        
        # Расчет расстояний до ключевых гео-точек
        avg_dist_cfo = geo_calculator._haversine_distance((loc_data['lat'], loc_data['lon']), config.KEY_GEO_POINTS["CFD_HUBs_Avg"])
        avg_dist_svo = geo_calculator._haversine_distance((loc_data['lat'], loc_data['lon']), config.KEY_GEO_POINTS["Airport_SVO"])
        avg_dist_local = geo_calculator._haversine_distance((loc_data['lat'], loc_data['lon']), config.KEY_GEO_POINTS["Moscow_Clients_Avg"])

        fleet_optimizer = FleetOptimizer()
        total_annual_transport_cost = fleet_optimizer.calculate_annual_transport_cost(avg_dist_cfo, avg_dist_svo, avg_dist_local)
        required_fleet_count = fleet_optimizer.calculate_required_fleet()

        print(f"  > Расчетные расстояния: ЦФО={avg_dist_cfo:.0f}км, SVO={avg_dist_svo:.0f}км, Local={avg_dist_local:.0f}км")
        print(f"  > Годовые транспортные расходы: {total_annual_transport_cost:,.0f} руб.")
        print(f"  > Требуемый флот (ЦФО): {required_fleet_count} грузовиков")

        # 3. Расчет Total_Annual_OPEX (Z_общ) для Сценария 1
        total_annual_opex_s1 = loc_data['annual_building_opex'] + z_pers_s1 + total_annual_transport_cost
        print(f"  > Total_Annual_OPEX (Сценарий 1): {total_annual_opex_s1:,.0f} руб./год")

        loc_data['total_annual_transport_cost'] = total_annual_transport_cost
        loc_data['required_fleet_count'] = required_fleet_count
        loc_data['total_annual_opex_s1'] = total_annual_opex_s1
        enriched_locations.append(loc_data)

    # 4. Поиск Оптимума
    optimal_location = min(enriched_locations, key=lambda x: x['total_annual_opex_s1'])
    print(f"\n{'='*80}\n[Шаг 4] ОПТИМАЛЬНАЯ ЛОКАЦИЯ НАЙДЕНА: '{optimal_location['location_name']}'")
    print(f"Минимальный Total_Annual_OPEX (Сценарий 1): {optimal_location['total_annual_opex_s1']:,.0f} руб./год")
    print(f"{'='*80}\n")

    # 5. НОВОЕ: Детальный транспортный анализ для оптимальной локации
    print(f"\n{'='*80}\n[Шаг 5] ДЕТАЛЬНЫЙ ТРАНСПОРТНЫЙ АНАЛИЗ ОПТИМАЛЬНОЙ ЛОКАЦИИ\n{'='*80}")

    # Используем OSRM для точных расстояний
    geo_router = OSRMGeoRouter(use_geocoding=False)
    optimal_coords = (optimal_location['lat'], optimal_location['lon'])

    # Получаем точные расстояния через OSRM
    route_data = geo_router.calculate_weighted_annual_distance(optimal_coords)

    distances = {
        'cfo_km': route_data['CFO']['distance_km'],
        'svo_km': route_data['SVO']['distance_km'],
        'local_km': route_data['LPU']['distance_km']
    }

    # Детальный расчет флота
    detailed_planner = DetailedFleetPlanner()
    fleet_summary = detailed_planner.calculate_fleet_requirements(distances)

    # Расчет доков
    dock_requirements = detailed_planner.calculate_dock_requirements(fleet_summary)

    # Генерация графика работы (сохраняем для будущего использования)
    _ = detailed_planner.generate_transport_schedule(fleet_summary)

    # Проверка достаточности доков
    dock_sim = DockSimulator(
        inbound_docks=dock_requirements['inbound_docks'],
        outbound_docks=dock_requirements['outbound_docks']
    )
    dock_simulation = dock_sim.simulate_dock_operations(dock_requirements['peak_trips_per_day'])

    print(f"\n[Проверка достаточности доков]")
    print(f"  - Утилизация inbound: {dock_simulation['inbound_utilization_percent']:.1f}%")
    print(f"  - Утилизация outbound: {dock_simulation['outbound_utilization_percent']:.1f}%")
    if not dock_simulation['is_sufficient']:
        print(f"  - [!] ПРЕДУПРЕЖДЕНИЕ: Доков недостаточно! Требуется увеличение.")
    else:
        print(f"  - [OK] Доков достаточно для текущей нагрузки")

    print(f"\n[Рекомендация по транспорту]")
    if fleet_summary['recommendation'] == 'lease':
        print(f"  - РЕКОМЕНДУЕТСЯ: Аренда транспорта")
        print(f"  - Экономия: {fleet_summary['total_opex_own_fleet'] - fleet_summary['total_opex_lease']:,.0f} руб/год vs покупки")
    else:
        print(f"  - РЕКОМЕНДУЕТСЯ: Покупка транспорта")
        print(f"  - ROI достигается через ~5 лет")

    # 6. Детализация Сценариев и SimPy для Оптимальной Локации
    print(f"\n{'='*80}\n[Шаг 6] ЗАПУСК SIMPY СИМУЛЯЦИИ ДЛЯ ВСЕХ СЦЕНАРИЕВ\n{'='*80}")

    # Создаем LocationSpec для SimulationRunner
    optimal_location_spec = LocationSpec(
        name=optimal_location['location_name'],
        lat=optimal_location['lat'],
        lon=optimal_location['lon'],
        ownership_type=optimal_location['type']
    )

    # Формируем initial_base_finance для SimulationRunner
    # base_capex берется из AvitoParserStub (total_initial_capex)
    # base_opex = annual_building_opex (из AvitoParserStub) + total_annual_transport_cost (рассчитано здесь)
    initial_base_finance_for_runner = {
        "base_capex": optimal_location['total_initial_capex'],
        "base_opex": optimal_location['annual_building_opex'] + optimal_location['total_annual_transport_cost']
    }

    runner = SimulationRunner(location_spec=optimal_location_spec)
    runner.run_all_scenarios(initial_base_finance=initial_base_finance_for_runner)

    # 7. Вывод Плана Переезда
    generate_detailed_relocation_plan(optimal_location, z_pers_s1, fleet_summary, dock_requirements)

if __name__ == "__main__":
    try:
        main_multi_location_runner()
    except Exception as e:
        print(f"\n[ОШИБКА] Произошла непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()
```

## `scenarios.py`

```py
# scenarios.py

"""
Определения и генерация данных для всех сценариев моделирования.
Ключ словаря используется внутри программы, а 'name' будет отображаться в отчетах.
"""
from typing import Dict, Any
import math
import config

SCENARIOS_CONFIG = {
    "1_Move_No_Mitigation": {
        "name": "1. Move No Mitigation",
        "staff_attrition_rate": 0.25,      # 25% уволилось
        "hr_investment_rub": 0,            # 0 руб. на удержание
        "automation_investment_rub": 0,    # 0 руб. на автоматизацию
        "efficiency_multiplier": 1.0       # Базовая эффективность
    },
    "2_Move_With_Compensation": {
        "name": "2. Move With Compensation",
        "staff_attrition_rate": 0.15,      # 15% уволилось
        "hr_investment_rub": 50_000_000,   # 50 млн руб. на удержание
        "automation_investment_rub": 0,
        "efficiency_multiplier": 1.0
    },
    "3_Move_Basic_Automation": {
        "name": "3. Move Basic Automation",
        "staff_attrition_rate": 0.25,
        "hr_investment_rub": 0,
        "automation_investment_rub": 100_000_000, # 100 млн руб. на конвейеры
        "efficiency_multiplier": 1.2               # Эффективность +20%
    },
    "4_Move_Advanced_Automation": {
        "name": "4. Move Advanced Automation",
        "staff_attrition_rate": 0.25,
        "hr_investment_rub": 0,
        "automation_investment_rub": 300_000_000, # 300 млн руб. на роботов
        "efficiency_multiplier": 1.5               # Эффективность +50%
    }
}

def generate_scenario_data(base_finance: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    """
    Генерирует полный набор данных для каждого сценария на основе базовых финансовых показателей.

    Args:
        base_finance: Словарь с 'base_capex' и 'base_opex' от LocationAnalyzer.

    Returns:
        Словарь, где ключ - ID сценария, а значение - словарь с его полными параметрами.
    """
    all_scenarios_data = {}

    for key, params in SCENARIOS_CONFIG.items():
        # Расчет персонала
        staff_count = math.floor(config.INITIAL_STAFF_COUNT * (1 - params['staff_attrition_rate']))
        
        # Расчет итоговых CAPEX и OPEX
        total_capex = base_finance['base_capex'] + params['hr_investment_rub'] + params['automation_investment_rub']
        opex_labor = staff_count * config.OPERATOR_SALARY_RUB_MONTH * 12
        total_opex = base_finance['base_opex'] + opex_labor

        all_scenarios_data[key] = {
            "name": params['name'],
            "staff_count": staff_count,
            "processing_efficiency": params['efficiency_multiplier'],
            "total_capex": total_capex,
            "total_opex": total_opex,
            "automation_investment": params['automation_investment_rub'] # Для расчета окупаемости
        }
        
    return all_scenarios_data
```

## `simulation_runner.py`

```py
import pandas as pd
import math
from typing import List, Optional, Dict, Any
import os

# Импорт модулей ядра и настроек
from core.data_model import LocationSpec, ScenarioResult
from core.location import WarehouseConfigurator
from core.simulation_engine import WarehouseSimulator
from core.flexsim_bridge import FlexSimAPIBridge
import config
from analysis import FleetOptimizer
from scenarios import generate_scenario_data

class SimulationRunner:
    """
    Главный класс-оркестратор. Управляет полным циклом анализа
    и генерации результатов для заданной локации.
    """
    
    def __init__(self, location_spec: LocationSpec):
        self.location_spec = location_spec
        # Инициализируем все необходимые нам "инструменты"
        self.location_analyzer = WarehouseConfigurator(location_spec.ownership_type, config.ANNUAL_RENT_PER_SQM_RUB, config.PURCHASE_BUILDING_COST_RUB, location_spec.lat, location_spec.lon)
        self.fleet_optimizer = FleetOptimizer()
        self.flexsim_bridge = FlexSimAPIBridge(config.OUTPUT_DIR)
        # Готовим пустой список для сбора итоговых результатов
        self.results: List[ScenarioResult] = []

    def run_all_scenarios(self, initial_base_finance: Optional[Dict[str, float]] = None):
        """Запускает полный цикл анализа для всех сценариев из scenarios.py."""
        print(f"\n{'='*80}\nЗАПУСК АНАЛИЗА ДЛЯ ЛОКАЦИИ: '{self.location_spec.name}'\n{'='*80}")

        # 1. Используем переданные базовые финансы или рассчитываем их
        if initial_base_finance is not None:
            base_finance = initial_base_finance
        else:
            base_finance = self.location_analyzer.get_base_financials()
        
        # 2. Генерируем полные данные для всех сценариев
        all_scenarios = generate_scenario_data(base_finance)

        # --- Демонстрация для Сценария 2 и 4 ---
        print("\n--- Демонстрация сгенерированных данных ---")
        s2_data = all_scenarios.get("2_Move_With_Compensation")
        s4_data = all_scenarios.get("4_Move_Advanced_Automation")
        print(f"Сценарий 2 ('{s2_data['name']}'):")
        print(f"  - Персонал: {s2_data['staff_count']} чел.")
        print(f"  - Эффективность: x{s2_data['processing_efficiency']}")
        print(f"  - Итоговый CAPEX: {s2_data['total_capex']:,.0f} руб.")
        print(f"  - Итоговый OPEX: {s2_data['total_opex']:,.0f} руб.")
        print(f"Сценарий 4 ('{s4_data['name']}'):")
        print(f"  - Персонал: {s4_data['staff_count']} чел.")
        print(f"  - Эффективность: x{s4_data['processing_efficiency']}")
        print(f"  - Итоговый CAPEX: {s4_data['total_capex']:,.0f} руб.")
        print(f"  - Итоговый OPEX: {s4_data['total_opex']:,.0f} руб.")
        print("-------------------------------------------\n")

        baseline_annual_opex = 0  # OPEX базового сценария для расчета экономии

        # 3. Проходим в цикле по каждому сценарию
        for key, scenario_data in all_scenarios.items():
            print(f"\n--- Обработка сценария: {scenario_data['name']} ---")

            # 4. Запуск SimPy симуляции
            print(f"  > Запуск SimPy с {scenario_data['staff_count']} чел. и эффективностью x{scenario_data['processing_efficiency']}...")
            sim = WarehouseSimulator(scenario_data['staff_count'], scenario_data['processing_efficiency'])
            sim_kpi = sim.run()
            print(f"  > SimPy завершен. Обработано заказов: {sim_kpi['achieved_throughput']}")

            # Запоминаем OPEX первого ("базового") сценария
            if 'No_Mitigation' in key:
                baseline_annual_opex = scenario_data['total_opex']
            
            # 5. Имитация получения KPI от FlexSim
            flexsim_kpi = self.flexsim_bridge.receive_kpi()
            # Здесь можно было бы использовать flexsim_kpi['achieved_throughput'],
            # но для консистентности продолжим использовать KPI из нашей SimPy модели.
            
            # 6. Финальный расчет окупаемости (ROI / Payback Period)
            payback = self.calculate_roi(scenario_data)
            if payback is not None:
                print(f"  > Расчетный срок окупаемости: {payback:.2f} лет")

            # 6. Сборка всех KPI в единую структуру данных
            result = ScenarioResult(
                location_name=self.location_spec.name,
                scenario_name=scenario_data['name'],
                staff_count=scenario_data['staff_count'],
                throughput_orders=int(sim_kpi['achieved_throughput']),
                avg_cycle_time_min=int(sim_kpi['avg_cycle_time_min']),
                total_annual_opex_rub=int(scenario_data['total_opex']),
                total_capex_rub=int(scenario_data['total_capex']),
                payback_period_years=payback if payback is not None else float('nan')
            )
            # Добавляем результат в общий список
            self.results.append(result)
            
            # 7. Генерация JSON-файла для FlexSim (используем 'result' и 'scenario_data' для параметров)
            self.flexsim_bridge.generate_json_config(self.location_spec, result, scenario_data)

        # 9. После завершения цикла сохраняем сводный CSV-файл
        self._save_summary_csv()
        print(f"\n--- Анализ для локации '{self.location_spec.name}' завершен. ---")

    def calculate_roi(self, scenario_data: dict) -> Optional[float]:
        """
        Рассчитывает срок окупаемости (Payback Period) для сценария.
        Сравнивает OPEX нового склада с OPEX текущего склада в Москве.
        """
        # 1. Расчет OPEX текущего склада (Baseline)
        # Аренда в Москве: 12000 руб/м2/год (1000 руб/м2/мес * 12)
        current_rent_opex = 12000 * config.WAREHOUSE_TOTAL_AREA_SQM
        # Зарплаты в Москве (без сокращений)
        current_labor_opex = config.INITIAL_STAFF_COUNT * config.OPERATOR_SALARY_RUB_MONTH * 12
        # Транспортные расходы считаем нулевыми (это наша база для сравнения)
        total_baseline_opex = current_rent_opex + current_labor_opex

        # 2. OPEX нового сценария (уже рассчитан)
        new_scenario_opex = scenario_data['total_opex']

        # 3. Расчет годовой экономии
        annual_savings = total_baseline_opex - new_scenario_opex

        if annual_savings > 0:
            payback_period_years = scenario_data['total_capex'] / annual_savings
            return payback_period_years
        return None # Окупаемости нет, если экономия не положительная

    def _save_summary_csv(self):
        """Сохраняет сводный CSV-файл со всеми результатами."""
        if not self.results: return
        
        # Преобразуем список объектов ScenarioResult в DataFrame
        df = pd.DataFrame([res.__dict__ for res in self.results])
        
        # Переименовываем колонки для совместимости с требованиями FlexSim
        column_map = {
            "location_name": "Location_Name", "scenario_name": "Scenario_Name",
            "total_annual_opex_rub": "Total_Annual_OPEX_RUB", "total_capex_rub": "Total_CAPEX_RUB",
            "throughput_orders": "Achieved_Throughput_Monthly", "staff_count": "Staff_Required",
            "payback_period_years": "Payback_Period_Years", "avg_cycle_time_min": "Avg_Cycle_Time_Min"
        }
        df = df.rename(columns=column_map)
        
        filepath = os.path.join(config.OUTPUT_DIR, config.RESULTS_CSV_FILENAME)
        df.to_csv(filepath, index=False, sep=';', decimal='.')
        print(f"\n[Runner] Сводные результаты сохранены: {filepath}")
```

## `test_enhanced_simulation.py`

```py
"""
Тестовый скрипт для проверки расширенной SimPy симуляции с доками.
"""
from core.simulation_engine import WarehouseSimulator, EnhancedWarehouseSimulator

print("="*80)
print("ТЕСТИРОВАНИЕ РАСШИРЕННОЙ SIMPY СИМУЛЯЦИИ")
print("="*80)

# Тест 1: Базовая симуляция (без доков)
print("\n[Тест 1] Базовая симуляция (только обработка заказов)")
print("-"*80)
basic_sim = WarehouseSimulator(staff_count=75, efficiency_multiplier=1.0)
basic_results = basic_sim.run()

print(f"Обработано заказов: {basic_results['achieved_throughput']}")
print(f"Среднее время цикла: {basic_results['avg_cycle_time_min']} мин")

# Тест 2: Расширенная симуляция С доками
print("\n[Тест 2] Расширенная симуляция (с моделированием доков)")
print("-"*80)
enhanced_sim = EnhancedWarehouseSimulator(
    staff_count=75,
    efficiency_multiplier=1.0,
    inbound_docks=4,
    outbound_docks=4,
    enable_dock_simulation=True
)
enhanced_results = enhanced_sim.run()

print(f"Обработано заказов: {enhanced_results['achieved_throughput']}")
print(f"Среднее время цикла: {enhanced_results['avg_cycle_time_min']} мин")
print(f"\nМетрики доков:")
print(f"  - Inbound грузовиков обслужено: {enhanced_results['inbound_trucks_served']}")
print(f"  - Outbound грузовиков обслужено: {enhanced_results['outbound_trucks_served']}")
print(f"  - Среднее время ожидания inbound: {enhanced_results['avg_inbound_wait_min']:.2f} мин")
print(f"  - Среднее время ожидания outbound: {enhanced_results['avg_outbound_wait_min']:.2f} мин")
print(f"  - Макс. ожидание inbound: {enhanced_results['max_inbound_wait_min']:.2f} мин")
print(f"  - Макс. ожидание outbound: {enhanced_results['max_outbound_wait_min']:.2f} мин")

# Тест 3: Симуляция с недостаточным количеством доков (узкое место)
print("\n[Тест 3] Симуляция с УЗКИМ МЕСТОМ (2 дока inbound)")
print("-"*80)
bottleneck_sim = EnhancedWarehouseSimulator(
    staff_count=75,
    efficiency_multiplier=1.0,
    inbound_docks=2,  # Мало!
    outbound_docks=4,
    enable_dock_simulation=True
)
bottleneck_results = bottleneck_sim.run()

print(f"Обработано заказов: {bottleneck_results['achieved_throughput']}")
print(f"\nМетрики доков (с узким местом):")
print(f"  - Среднее время ожидания inbound: {bottleneck_results['avg_inbound_wait_min']:.2f} мин [!]")
print(f"  - Макс. ожидание inbound: {bottleneck_results['max_inbound_wait_min']:.2f} мин [!]")

if bottleneck_results['avg_inbound_wait_min'] > 60:
    print(f"\n[!] ПРЕДУПРЕЖДЕНИЕ: Среднее ожидание > 60 мин! Необходимо больше inbound доков!")

# Тест 4: Сценарий с автоматизацией (efficiency_multiplier = 1.2)
print("\n[Тест 4] Сценарий с базовой автоматизацией (эффективность +20%)")
print("-"*80)
automated_sim = EnhancedWarehouseSimulator(
    staff_count=75,
    efficiency_multiplier=1.2,  # +20% скорость обработки
    inbound_docks=4,
    outbound_docks=4,
    enable_dock_simulation=True
)
automated_results = automated_sim.run()

print(f"Обработано заказов: {automated_results['achieved_throughput']}")
print(f"Среднее время цикла: {automated_results['avg_cycle_time_min']} мин (улучшено благодаря автоматизации)")
print(f"Среднее время ожидания inbound: {automated_results['avg_inbound_wait_min']:.2f} мин")

print("\n" + "="*80)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("="*80)

```

## `to md.py`

```py
import os

def get_user_choice_directories():
    print("Поиск папок в текущей директории...")
    all_dirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and item not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.obsidian'}:
            all_dirs.append(item)

    if not all_dirs:
        print("Дополнительных папок не найдено.")
        return []

    print("\nНайденные папки:")
    for i, d in enumerate(all_dirs):
        print(f"{i+1}. {d}")

    print("\nВведите номера папок, которые нужно также включить (через запятую, Enter для пропуска):")
    try:
        choice_input = input().strip()
        if not choice_input:
            return []
        selected_indices = [int(x.strip()) - 1 for x in choice_input.split(',')]
        selected_dirs = [all_dirs[i] for i in selected_indices if 0 <= i < len(all_dirs)]
        print(f"Выбраны папки: {selected_dirs}")
        return selected_dirs
    except ValueError:
        print("Некорректный ввод. Папки не выбраны.")
        return []

def collect_code_files_to_markdown(output_file, extensions, extra_dirs=None):
    all_dirs_to_scan = {'.', *(extra_dirs or [])}
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for dir_path in all_dirs_to_scan:
            for root, dirs, files in os.walk(dir_path):
                # Исключаем системные папки
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.obsidian'}]
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        filepath = os.path.join(root, file)
                        # Относительный путь для заголовка
                        rel_path = os.path.relpath(filepath, '.')
                        out_file.write(f"## `{rel_path}`\n\n")
                        out_file.write(f"```{file.split('.')[-1]}\n")
                        try:
                            with open(filepath, 'r', encoding='utf-8') as code_file:
                                out_file.write(code_file.read())
                        except Exception as e:
                            out_file.write(f"<!-- Error reading file: {e} -->\n")
                        out_file.write("\n```\n\n")

# --- Основной код ---
output_markdown = 'collected_code.md'
file_extensions = ['.py', '.js', '.html', '.css', '.ts', '.jsx', '.json', '.md']

extra_dirs = get_user_choice_directories()

collect_code_files_to_markdown(output_markdown, file_extensions, extra_dirs)
print(f"\nКод из файлов успешно собран в {output_markdown}")
```

## `transport_planner.py`

```py
"""
Модуль детального планирования транспортной логистики.
Включает расчет флота, доков, графиков работы и детальный CAPEX/OPEX.
"""
import math
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import config


@dataclass
class VehicleType:
    """Характеристики типа транспортного средства."""
    name: str
    capacity_pallets: int
    capacity_kg: int
    fuel_consumption_l_per_100km: float
    maintenance_cost_rub_per_km: float
    driver_cost_rub_per_trip: float  # Для дальних рейсов
    driver_cost_rub_per_day: float   # Для местных рейсов
    purchase_cost_rub: int           # Стоимость покупки
    lease_cost_rub_per_month: int    # Стоимость аренды
    insurance_rub_per_year: int      # Страховка
    is_refrigerated: bool = False
    temperature_control_cost_rub_per_hour: float = 0.0


# Определяем типы транспорта для фармацевтической логистики
VEHICLE_TYPES = {
    'heavy_truck_20t': VehicleType(
        name='Грузовик 18-20т (тентованный)',
        capacity_pallets=33,  # Стандартные европаллеты
        capacity_kg=20000,
        fuel_consumption_l_per_100km=28.0,
        maintenance_cost_rub_per_km=8.5,
        driver_cost_rub_per_trip=15000,  # Межрегиональный рейс
        driver_cost_rub_per_day=0,
        purchase_cost_rub=4_500_000,
        lease_cost_rub_per_month=180_000,
        insurance_rub_per_year=120_000,
        is_refrigerated=False
    ),

    'medium_truck_5t': VehicleType(
        name='Грузовик 5т (городской)',
        capacity_pallets=8,
        capacity_kg=5000,
        fuel_consumption_l_per_100km=18.0,
        maintenance_cost_rub_per_km=5.2,
        driver_cost_rub_per_trip=0,
        driver_cost_rub_per_day=4500,  # Ежедневная работа
        purchase_cost_rub=2_800_000,
        lease_cost_rub_per_month=95_000,
        insurance_rub_per_year=65_000,
        is_refrigerated=False
    ),

    'refrigerated_truck_15t': VehicleType(
        name='Рефрижератор 15т (2-8°C)',
        capacity_pallets=24,
        capacity_kg=15000,
        fuel_consumption_l_per_100km=32.0,  # Выше из-за холодильника
        maintenance_cost_rub_per_km=12.0,
        driver_cost_rub_per_trip=18000,
        driver_cost_rub_per_day=5500,
        purchase_cost_rub=6_500_000,
        lease_cost_rub_per_month=260_000,
        insurance_rub_per_year=180_000,
        is_refrigerated=True,
        temperature_control_cost_rub_per_hour=450.0
    )
}


class DetailedFleetPlanner:
    """
    Детальный планировщик транспортного флота с расчетом:
    - Типизации флота (20т, 5т, рефрижераторы)
    - Графиков работы и расписания
    - Пропускной способности доков
    - Детального CAPEX/OPEX транспорта
    """

    # Константы потоков (из analysis.py)
    CFO_OWN_FLEET_SHARE = 0.46      # ЦФО собственный флот
    AIR_DELIVERY_SHARE = 0.25       # Авиа через SVO
    LOCAL_DELIVERY_SHARE = 0.29     # Местные ЛПУ Москвы

    # Холодная цепь (средний процент от общего объема)
    COLD_CHAIN_SHARE = 0.17  # 17% требуют 2-8°C

    # Константы работы склада
    WAREHOUSE_OPERATES_24_7 = True
    WORKING_DAYS_PER_WEEK = 7
    WORKING_HOURS_PER_DAY = 24

    # Средний вес заказа (из документации: одна паллета ≈ 250кг)
    AVG_ORDER_WEIGHT_KG = 250
    AVG_ORDER_PALLETS = 1.0

    # Константы доков
    LOADING_TIME_PER_TRUCK_HOURS = 1.5  # Время погрузки одного грузовика
    UNLOADING_TIME_PER_TRUCK_HOURS = 2.0  # Время разгрузки (дольше из-за проверок GPP/GDP)
    BUFFER_COEFFICIENT = 1.3  # Буфер на пиковые нагрузки

    # Цены на топливо
    DIESEL_PRICE_RUB_PER_LITER = 56.0

    def __init__(self):
        """Инициализация планировщика."""
        self.monthly_orders = config.TARGET_ORDERS_MONTH
        self.annual_orders = self.monthly_orders * 12

    def calculate_fleet_requirements(self, distances: Dict[str, float]) -> Dict[str, Any]:
        """
        Рассчитывает детальные требования к флоту для всех потоков.

        Args:
            distances: Словарь с расстояниями {'cfo_km': float, 'svo_km': float, 'local_km': float}

        Returns:
            Детальная информация о требуемом флоте и затратах
        """
        print(f"\n  > [DetailedFleetPlanner] Расчет детальных требований к транспортному флоту")

        # 1. ЦФО: тяжелые грузовики 18-20т
        cfo_fleet = self._calculate_cfo_fleet(distances['cfo_km'])

        # 2. Местные ЛПУ: средние грузовики 5т
        local_fleet = self._calculate_local_fleet(distances['local_km'])

        # 3. SVO авиа: средние грузовики + рефрижераторы
        svo_fleet = self._calculate_svo_fleet(distances['svo_km'])

        # 4. Холодная цепь: дополнительные рефрижераторы
        cold_chain_fleet = self._calculate_cold_chain_fleet(distances)

        # 5. Общие затраты
        total_fleet = self._aggregate_fleet_costs(cfo_fleet, local_fleet, svo_fleet, cold_chain_fleet)

        return total_fleet

    def _calculate_cfo_fleet(self, avg_distance_km: float) -> Dict[str, Any]:
        """
        Расчет флота для ЦФО (46% потока, собственный флот 18-20т).

        Логика:
        - 2 рейса в неделю на один грузовик
        - Консолидация грузов до полной загрузки
        """
        vehicle = VEHICLE_TYPES['heavy_truck_20t']

        # Заказы в ЦФО за месяц
        cfo_orders_per_month = self.monthly_orders * self.CFO_OWN_FLEET_SHARE
        cfo_orders_per_week = cfo_orders_per_month / 4.33  # Средних недель в месяце

        # Сколько паллет нужно перевезти
        total_pallets_per_week = cfo_orders_per_week * self.AVG_ORDER_PALLETS

        # Рейсов в неделю (с учетом вместимости)
        trips_per_week = math.ceil(total_pallets_per_week / vehicle.capacity_pallets)

        # Необходимое количество грузовиков (2 рейса/неделю на грузовик)
        trips_per_truck_per_week = 2
        required_trucks = math.ceil(trips_per_week / trips_per_truck_per_week)

        # Годовые расстояния
        annual_trips = trips_per_week * 52
        annual_distance_km = annual_trips * avg_distance_km * 2  # Туда-обратно

        # Затраты
        fuel_cost = (annual_distance_km / 100) * vehicle.fuel_consumption_l_per_100km * self.DIESEL_PRICE_RUB_PER_LITER
        maintenance_cost = annual_distance_km * vehicle.maintenance_cost_rub_per_km
        driver_cost = annual_trips * vehicle.driver_cost_rub_per_trip
        insurance_cost = required_trucks * vehicle.insurance_rub_per_year

        # CAPEX/OPEX: покупка vs аренда
        purchase_capex = required_trucks * vehicle.purchase_cost_rub
        lease_opex_annual = required_trucks * vehicle.lease_cost_rub_per_month * 12

        print(f"    - ЦФО (18-20т): {required_trucks} грузовиков, {annual_trips} рейсов/год")

        return {
            'fleet_type': 'heavy_truck_20t',
            'vehicle_name': vehicle.name,
            'required_count': required_trucks,
            'annual_trips': annual_trips,
            'annual_distance_km': annual_distance_km,
            'avg_distance_per_trip_km': avg_distance_km,
            'costs': {
                'fuel_rub': fuel_cost,
                'maintenance_rub': maintenance_cost,
                'driver_salaries_rub': driver_cost,
                'insurance_rub': insurance_cost,
                'total_opex_rub': fuel_cost + maintenance_cost + driver_cost + insurance_cost
            },
            'capex_purchase_rub': purchase_capex,
            'opex_lease_rub': lease_opex_annual
        }

    def _calculate_local_fleet(self, avg_distance_km: float) -> Dict[str, Any]:
        """
        Расчет флота для местных ЛПУ Москвы (29% потока, 5т грузовики).

        Логика:
        - Ежедневные развозки
        - 6-8 точек за день (в среднем 7)
        """
        vehicle = VEHICLE_TYPES['medium_truck_5t']

        # Заказы в день
        local_orders_per_day = (self.monthly_orders * self.LOCAL_DELIVERY_SHARE) / 22  # 22 рабочих дня

        # Точек доставки за день на один грузовик
        points_per_truck_per_day = 7

        # Необходимое количество грузовиков
        required_trucks = math.ceil(local_orders_per_day / points_per_truck_per_day)

        # Годовые расстояния
        working_days_per_year = 22 * 12  # 264 дня
        annual_distance_km = required_trucks * working_days_per_year * avg_distance_km

        # Затраты
        fuel_cost = (annual_distance_km / 100) * vehicle.fuel_consumption_l_per_100km * self.DIESEL_PRICE_RUB_PER_LITER
        maintenance_cost = annual_distance_km * vehicle.maintenance_cost_rub_per_km
        driver_cost = required_trucks * vehicle.driver_cost_rub_per_day * working_days_per_year
        insurance_cost = required_trucks * vehicle.insurance_rub_per_year

        purchase_capex = required_trucks * vehicle.purchase_cost_rub
        lease_opex_annual = required_trucks * vehicle.lease_cost_rub_per_month * 12

        print(f"    - Местные ЛПУ (5т): {required_trucks} грузовиков, ежедневные развозки")

        return {
            'fleet_type': 'medium_truck_5t',
            'vehicle_name': vehicle.name,
            'required_count': required_trucks,
            'annual_trips': working_days_per_year * required_trucks,
            'annual_distance_km': annual_distance_km,
            'avg_distance_per_trip_km': avg_distance_km,
            'costs': {
                'fuel_rub': fuel_cost,
                'maintenance_rub': maintenance_cost,
                'driver_salaries_rub': driver_cost,
                'insurance_rub': insurance_cost,
                'total_opex_rub': fuel_cost + maintenance_cost + driver_cost + insurance_cost
            },
            'capex_purchase_rub': purchase_capex,
            'opex_lease_rub': lease_opex_annual
        }

    def _calculate_svo_fleet(self, avg_distance_km: float) -> Dict[str, Any]:
        """
        Расчет флота для авиадоставки в SVO (25% потока).

        Логика:
        - Ежедневные поставки в карго-терминал
        - Используем 5т грузовики
        """
        vehicle = VEHICLE_TYPES['medium_truck_5t']

        # Заказы в день для авиа
        svo_orders_per_day = (self.monthly_orders * self.AIR_DELIVERY_SHARE) / 22

        # Паллет в день
        pallets_per_day = svo_orders_per_day * self.AVG_ORDER_PALLETS

        # Рейсов в день (вместимость 8 паллет)
        trips_per_day = math.ceil(pallets_per_day / vehicle.capacity_pallets)

        # Необходимое количество грузовиков (с запасом на 2 рейса в день)
        required_trucks = math.ceil(trips_per_day / 2)

        # Годовые расстояния
        working_days_per_year = 264
        annual_trips = trips_per_day * working_days_per_year
        annual_distance_km = annual_trips * avg_distance_km * 2  # Туда-обратно

        # Затраты
        fuel_cost = (annual_distance_km / 100) * vehicle.fuel_consumption_l_per_100km * self.DIESEL_PRICE_RUB_PER_LITER
        maintenance_cost = annual_distance_km * vehicle.maintenance_cost_rub_per_km
        driver_cost = required_trucks * vehicle.driver_cost_rub_per_day * working_days_per_year
        insurance_cost = required_trucks * vehicle.insurance_rub_per_year

        purchase_capex = required_trucks * vehicle.purchase_cost_rub
        lease_opex_annual = required_trucks * vehicle.lease_cost_rub_per_month * 12

        print(f"    - SVO авиа (5т): {required_trucks} грузовиков, {trips_per_day} рейсов/день")

        return {
            'fleet_type': 'medium_truck_5t_svo',
            'vehicle_name': vehicle.name + ' (SVO)',
            'required_count': required_trucks,
            'annual_trips': annual_trips,
            'annual_distance_km': annual_distance_km,
            'avg_distance_per_trip_km': avg_distance_km,
            'costs': {
                'fuel_rub': fuel_cost,
                'maintenance_rub': maintenance_cost,
                'driver_salaries_rub': driver_cost,
                'insurance_rub': insurance_cost,
                'total_opex_rub': fuel_cost + maintenance_cost + driver_cost + insurance_cost
            },
            'capex_purchase_rub': purchase_capex,
            'opex_lease_rub': lease_opex_annual
        }

    def _calculate_cold_chain_fleet(self, distances: Dict[str, float]) -> Dict[str, Any]:
        """
        Расчет рефрижераторов для холодной цепи (17% от общего объема).

        Распределяется по всем потокам пропорционально.
        """
        vehicle = VEHICLE_TYPES['refrigerated_truck_15t']

        # Холодные заказы в месяц
        cold_orders_per_month = self.monthly_orders * self.COLD_CHAIN_SHARE

        # Распределяем по потокам
        cold_cfo = cold_orders_per_month * self.CFO_OWN_FLEET_SHARE
        cold_local = cold_orders_per_month * self.LOCAL_DELIVERY_SHARE
        cold_svo = cold_orders_per_month * self.AIR_DELIVERY_SHARE

        # Рейсы в месяц (15т = 24 паллеты)
        trips_per_month = math.ceil((cold_cfo + cold_local + cold_svo) / vehicle.capacity_pallets)
        trips_per_week = trips_per_month / 4.33

        # Необходимое количество рефрижераторов (2 рейса в неделю)
        required_trucks = math.ceil(trips_per_week / 2)

        # Средняя дистанция (взвешенная)
        avg_weighted_distance = (
            distances['cfo_km'] * self.CFO_OWN_FLEET_SHARE +
            distances['local_km'] * self.LOCAL_DELIVERY_SHARE +
            distances['svo_km'] * self.AIR_DELIVERY_SHARE
        )

        # Годовые расстояния
        annual_trips = trips_per_month * 12
        annual_distance_km = annual_trips * avg_weighted_distance * 2

        # Часы работы холодильника
        avg_trip_hours = (avg_weighted_distance * 2) / 50  # Средняя скорость 50 км/ч
        annual_refrigeration_hours = annual_trips * avg_trip_hours

        # Затраты
        fuel_cost = (annual_distance_km / 100) * vehicle.fuel_consumption_l_per_100km * self.DIESEL_PRICE_RUB_PER_LITER
        maintenance_cost = annual_distance_km * vehicle.maintenance_cost_rub_per_km
        driver_cost = annual_trips * vehicle.driver_cost_rub_per_trip
        insurance_cost = required_trucks * vehicle.insurance_rub_per_year
        refrigeration_cost = annual_refrigeration_hours * vehicle.temperature_control_cost_rub_per_hour

        purchase_capex = required_trucks * vehicle.purchase_cost_rub
        lease_opex_annual = required_trucks * vehicle.lease_cost_rub_per_month * 12

        print(f"    - Холодная цепь (15т рефр.): {required_trucks} грузовиков, {annual_trips} рейсов/год")

        return {
            'fleet_type': 'refrigerated_truck_15t',
            'vehicle_name': vehicle.name,
            'required_count': required_trucks,
            'annual_trips': annual_trips,
            'annual_distance_km': annual_distance_km,
            'avg_distance_per_trip_km': avg_weighted_distance,
            'costs': {
                'fuel_rub': fuel_cost,
                'maintenance_rub': maintenance_cost,
                'driver_salaries_rub': driver_cost,
                'insurance_rub': insurance_cost,
                'refrigeration_rub': refrigeration_cost,
                'total_opex_rub': fuel_cost + maintenance_cost + driver_cost + insurance_cost + refrigeration_cost
            },
            'capex_purchase_rub': purchase_capex,
            'opex_lease_rub': lease_opex_annual
        }

    def _aggregate_fleet_costs(self, *fleet_data) -> Dict[str, Any]:
        """Агрегирует данные по всему флоту."""
        total_vehicles = sum(f['required_count'] for f in fleet_data)
        total_opex = sum(f['costs']['total_opex_rub'] for f in fleet_data)
        total_capex_purchase = sum(f['capex_purchase_rub'] for f in fleet_data)
        total_opex_lease = sum(f['opex_lease_rub'] for f in fleet_data)

        print(f"\n  > Итого транспорт: {total_vehicles} единиц техники")
        print(f"    - OPEX (собственный флот): {total_opex:,.0f} руб/год")
        print(f"    - CAPEX (покупка флота): {total_capex_purchase:,.0f} руб")
        print(f"    - OPEX (аренда флота): {total_opex_lease:,.0f} руб/год")

        return {
            'total_vehicles': total_vehicles,
            'fleet_breakdown': list(fleet_data),
            'total_opex_own_fleet': total_opex,
            'total_capex_purchase': total_capex_purchase,
            'total_opex_lease': total_opex_lease,
            'recommendation': 'lease' if total_opex_lease < (total_opex + total_capex_purchase / 5) else 'purchase'
        }

    def calculate_dock_requirements(self, fleet_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Рассчитывает требования к количеству доков (inbound и outbound).

        Args:
            fleet_summary: Сводная информация о флоте

        Returns:
            Количество доков и пропускная способность
        """
        print(f"\n  > [DetailedFleetPlanner] Расчет требований к докам")

        # Считаем пиковую нагрузку по рейсам в день
        total_trips_per_year = sum(f['annual_trips'] for f in fleet_summary['fleet_breakdown'])
        avg_trips_per_day = total_trips_per_year / 264  # 264 рабочих дня

        # Пиковая нагрузка (с буфером)
        peak_trips_per_day = avg_trips_per_day * self.BUFFER_COEFFICIENT

        # Inbound: приемка товара (разгрузка)
        # Предполагаем, что 40% рейсов - это inbound (приемка с заводов/поставщиков)
        inbound_trips_per_day = peak_trips_per_day * 0.4

        # Время работы доков (24 часа)
        dock_working_hours = 24

        # Необходимое количество inbound доков
        inbound_docks_required = math.ceil(
            (inbound_trips_per_day * self.UNLOADING_TIME_PER_TRUCK_HOURS) / dock_working_hours
        )

        # Outbound: отгрузка (погрузка)
        # 60% рейсов - это outbound (отгрузка клиентам)
        outbound_trips_per_day = peak_trips_per_day * 0.6

        # Необходимое количество outbound доков
        outbound_docks_required = math.ceil(
            (outbound_trips_per_day * self.LOADING_TIME_PER_TRUCK_HOURS) / dock_working_hours
        )

        # Минимальное количество доков по стандарту для фармсклада 17,000 м²
        min_inbound_docks = 4
        min_outbound_docks = 4

        inbound_docks = max(inbound_docks_required, min_inbound_docks)
        outbound_docks = max(outbound_docks_required, min_outbound_docks)

        print(f"    - Inbound доки (приемка): {inbound_docks} шт")
        print(f"    - Outbound доки (отгрузка): {outbound_docks} шт")
        print(f"    - Средняя нагрузка: {avg_trips_per_day:.1f} рейсов/день")
        print(f"    - Пиковая нагрузка: {peak_trips_per_day:.1f} рейсов/день")

        return {
            'inbound_docks': inbound_docks,
            'outbound_docks': outbound_docks,
            'total_docks': inbound_docks + outbound_docks,
            'avg_trips_per_day': avg_trips_per_day,
            'peak_trips_per_day': peak_trips_per_day,
            'dock_utilization_percent': (peak_trips_per_day * self.LOADING_TIME_PER_TRUCK_HOURS) / (dock_working_hours * (inbound_docks + outbound_docks)) * 100
        }

    def generate_transport_schedule(self, fleet_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерирует примерный график работы транспорта.

        Returns:
            График работы по часам/дням
        """
        print(f"\n  > [DetailedFleetPlanner] Генерация графика работы транспорта")

        schedule = {
            'cfo_heavy_trucks': {
                'schedule_type': 'Межрегиональные рейсы',
                'departure_times': ['06:00', '14:00'],  # 2 рейса в день
                'avg_trip_duration_hours': 8,
                'working_days': '7 дней в неделю'
            },
            'local_medium_trucks': {
                'schedule_type': 'Городские развозки',
                'departure_times': ['08:00', '13:00', '18:00'],  # 3 волны развозок
                'avg_trip_duration_hours': 4,
                'working_days': '6 дней в неделю (Пн-Сб)'
            },
            'svo_trucks': {
                'schedule_type': 'Авиакарго',
                'departure_times': ['04:00', '12:00', '20:00'],  # Под авиарейсы
                'avg_trip_duration_hours': 2,
                'working_days': '7 дней в неделю'
            },
            'cold_chain_trucks': {
                'schedule_type': 'Холодная цепь (приоритет)',
                'departure_times': ['Гибкий график по заявкам'],
                'avg_trip_duration_hours': 6,
                'working_days': '7 дней в неделю'
            }
        }

        print("    - График сформирован для всех типов транспорта")

        return schedule


class DockSimulator:
    """
    Упрощенный симулятор работы доков для проверки пропускной способности.
    Будет интегрирован в основную SimPy симуляцию позже.
    """

    def __init__(self, inbound_docks: int, outbound_docks: int):
        self.inbound_docks = inbound_docks
        self.outbound_docks = outbound_docks

    def simulate_dock_operations(self, trips_per_day: float) -> Dict[str, Any]:
        """
        Проверяет, справляются ли доки с заданной нагрузкой.

        Args:
            trips_per_day: Количество рейсов в день

        Returns:
            Метрики работы доков
        """
        # Упрощенная логика: проверка утилизации
        inbound_trips = trips_per_day * 0.4
        outbound_trips = trips_per_day * 0.6

        # Максимальная пропускная способность (24 часа работы)
        max_inbound_capacity = self.inbound_docks * (24 / 2.0)  # 2 часа на разгрузку
        max_outbound_capacity = self.outbound_docks * (24 / 1.5)  # 1.5 часа на погрузку

        inbound_utilization = (inbound_trips / max_inbound_capacity) * 100
        outbound_utilization = (outbound_trips / max_outbound_capacity) * 100

        return {
            'inbound_utilization_percent': inbound_utilization,
            'outbound_utilization_percent': outbound_utilization,
            'bottleneck': 'inbound' if inbound_utilization > outbound_utilization else 'outbound',
            'is_sufficient': inbound_utilization < 85 and outbound_utilization < 85
        }

```

## `.claude\settings.local.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(if not exist output mkdir output)",
      "Bash(python -c \"import simpy, pandas, matplotlib, seaborn\")",
      "Bash(pip install:*)",
      "Bash(python main.py:*)",
      "Bash(python analysis.py:*)",
      "Bash(python test_enhanced_simulation.py:*)"
    ],
    "deny": [],
    "ask": []
  }
}

```

## `core\data_model.py`

```py
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
```

## `core\flexsim_bridge.py`

```py
"""
Модуль для взаимодействия с FlexSim: генерация JSON и имитация API.
"""
import json
import os
from typing import Dict, Any, Optional

import config
from core.data_model import LocationSpec, ScenarioResult
from analysis import FleetOptimizer

class FlexSimAPIBridge:
    """
    Управляет созданием конфигурационных файлов для FlexSim и
    имитирует отправку команд через Socket API.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[FlexSimAPIBridge] Инициализирован. Выходная директория: '{self.output_dir}'")

    def send_config(self, json_data: dict) -> bool:
        """Имитирует отправку JSON-конфигурации через сокет."""
        print("  > [API] Отправка конфигурации в FlexSim...")
        response = self._send_command("LOAD_CONFIG", data=json_data)
        return response.get("status") == "OK"

    def start_simulation(self, scenario_id: str) -> bool:
        """Имитирует команду запуска симуляции в FlexSim."""
        print(f"  > [API] Запуск симуляции для сценария '{scenario_id}'...")
        response = self._send_command("START_SIMULATION", data={"scenario": scenario_id})
        return response.get("status") == "OK"

    def receive_kpi(self) -> Dict[str, Any]:
        """Имитирует прием ключевых метрик от FlexSim."""
        print("  > [API] Получение KPI от FlexSim...")
        response = self._send_command("GET_KPI")
        if response.get("status") == "OK":
            # Возвращаем пример словаря, как указано в задаче
            kpi_data = {
                'achieved_throughput': 10500, 
                'resource_utilization': 0.85
            }
            print(f"  > [API] Получены KPI: {kpi_data}")
            return kpi_data
        return {}

    def generate_json_config(self, location_spec: LocationSpec, scenario_result: ScenarioResult, scenario_data: dict):
        """Создает и сохраняет JSON-конфигурацию для одного сценария."""

        # Создаем экземпляр FleetOptimizer для расчетов
        fleet_optimizer = FleetOptimizer()

        # Определяем тип автоматизации на основе инвестиций
        automation_investment = scenario_data.get('automation_investment', 0)
        automation_type = "None"
        if automation_investment == 100_000_000:
            automation_type = "Conveyors+WMS"
        elif automation_investment > 100_000_000:
            automation_type = "AutoStore+AGV"
            
        config_data = {
            "FINANCIALS": {
                "Total_CAPEX": scenario_data['total_capex'],
                "Annual_OPEX": scenario_data['total_opex']
            },
            "LAYOUT": {
                "Total_Area_SQM": config.WAREHOUSE_TOTAL_AREA_SQM,
                "Ceiling_Height": 12,
                "GPP_ZONES": [
                    {"Zone": "Cool_2_8C", "Pallet_Capacity": 3000},
                    {"Zone": "Controlled_15_25C", "Pallet_Capacity": 17000}
                ]
            },
            "RESOURCES": {
                "Staff_Operators": scenario_data['staff_count'],
                "Automation_Type": automation_type,
                "Processing_Time_Coefficient": scenario_data['processing_efficiency']
            },
            "LOGISTICS": {
                "Location_Coords": [location_spec.lat, location_spec.lon],
                "Required_Own_Fleet_Count": fleet_optimizer.calculate_required_fleet(),
                "Delivery_Flows": [
                    {"Dest": "SVO_Aviation", "Volume_Pct": fleet_optimizer.AIR_DELIVERY_SHARE * 100},
                    {"Dest": "CFD_Own_Fleet", "Volume_Pct": fleet_optimizer.CFO_OWN_FLEET_SHARE * 100},
                    {"Dest": "Moscow_LPU", "Volume_Pct": fleet_optimizer.LOCAL_DELIVERY_SHARE * 100}
                ]
            }
        }
        
        # Формируем имя файла на основе имени сценария
        scenario_name = scenario_data.get('name', 'Unknown_Scenario')
        safe_scenario_name = scenario_name.replace('. ', '_').replace(' ', '_')
        filename = f"flexsim_setup_{safe_scenario_name}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        print(f"  > [OK] JSON-конфиг сохранен: {filename}")
        
        # Демонстрация для Сценария 4
        if "4_Move_Advanced_Automation" in safe_scenario_name:
            print("\n--- Демонстрация JSON для Сценария 4 ---")
            print(json.dumps(config_data, ensure_ascii=False, indent=4))
            print("-----------------------------------------\n")

    def _send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Имитирует отправку команды FlexSim (stub-версия из api_bridge.py)."""
        # print(f"[FlexSimAPIBridge STUB] Отправка команды '{command}'...")
        try:
            # Имитируем ошибку подключения, так как сервера нет
            raise ConnectionRefusedError("No FlexSim server is listening (as expected for a stub).")
        except ConnectionRefusedError as e:
            # print(f"[FlexSimAPIBridge STUB] Ошибка (это нормально для заглушки): {e}")
            if command == "LOAD_CONFIG":
                return {"status": "OK", "message": "Configuration loaded."}
            elif command == "START_SIMULATION":
                return {"status": "OK", "message": "Simulation started."}
            elif command == "GET_KPI":
                 return {"status": "OK", "kpi": {"achieved_throughput": 10500, "resource_utilization": 0.85}}
            return {"status": "ERROR", "message": "Unknown command"}
```

## `core\location.py`

```py
# core/location.py

"""
Модуль для конфигурации склада и расчета базовых финансовых показателей (CAPEX, OPEX).
"""
from typing import Dict, Tuple
from math import radians, sin, cos, sqrt, atan2

import config

class WarehouseConfigurator:
    """
    Рассчитывает базовые CAPEX и OPEX для склада, включая затраты на помещение и оборудование.
    """
    def __init__(self, ownership_type: str, rent_rate_sqm_year: float, purchase_cost: float, lat: float, lon: float):
        # Нормализуем тип владения: POKUPKA_BTS -> POKUPKA
        if ownership_type == "POKUPKA_BTS":
            ownership_type = "POKUPKA"

        if ownership_type not in {"ARENDA", "POKUPKA"}:
            raise ValueError("Неверный тип владения: должен быть 'ARENDA', 'POKUPKA' или 'POKUPKA_BTS'")

        self.ownership_type = ownership_type
        self.rent_rate_sqm_year = rent_rate_sqm_year
        self.purchase_cost = purchase_cost
        self.lat = lat
        self.lon = lon

    def calculate_fixed_capex(self) -> float:
        """Рассчитывает обязательные первоначальные инвестиции (CAPEX) для склада."""
        capex_racking = 50_000_000  # Стеллажное оборудование
        capex_climate = 250_000_000 # Климатическое оборудование (установка + настройка)
        return capex_racking + capex_climate

    def calculate_annual_opex(self) -> float:
        """Рассчитывает годовые операционные расходы (OPEX) на помещение."""
        total_area = 17000  # Общая площадь в м²
        if self.ownership_type == "ARENDA":
            return total_area * self.rent_rate_sqm_year
        else:  # POKUPKA
            # Налог/обслуживание как 15% от гипотетической стоимости аренды
            return (total_area * self.rent_rate_sqm_year) * 0.15

    def _haversine_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Расчет расстояния по прямой с коэффициентом на кривизну дорог."""
        R = 6371.0  # Радиус Земли в километрах
        lat1, lon1, lat2, lon2 = map(radians, [p1[0], p1[1], p2[0], p2[1]])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Коэффициент 1.4 для имитации реального пробега по дорогам
        return (R * c) * 1.4

    def get_transport_cost_change_rub(self) -> float:
        """Рассчитывает годовое ИЗМЕНЕНИЕ транспортных расходов при переезде."""
        total_dist_increase_km = 0
        new_hub_coords = (self.lat, self.lon)
        # Ключевые точки доставки: аэропорт и усредненные центры для ЦФО и Москвы
        key_points = [
            config.KEY_GEO_POINTS["Airport_SVO"],
            config.KEY_GEO_POINTS["CFD_HUBs_Avg"],
            config.KEY_GEO_POINTS["Moscow_Clients_Avg"]
        ]
        
        for point in key_points:
            dist_old = self._haversine_distance(config.KEY_GEO_POINTS["Current_HUB"], point)
            dist_new = self._haversine_distance(new_hub_coords, point)
            total_dist_increase_km += (dist_new - dist_old)

        avg_dist_increase_per_trip = total_dist_increase_km / len(key_points)
        
        # Допущение: каждый заказ - это условная поездка для оценки относительного изменения
        total_annual_extra_km = avg_dist_increase_per_trip * (config.TARGET_ORDERS_MONTH * 12)
        
        return total_annual_extra_km * config.TRANSPORT_TARIFF_RUB_PER_KM

    def get_base_financials(self) -> Dict[str, float]:
        """
        Рассчитывает базовые CAPEX и OPEX, зависящие ТОЛЬКО от локации и типа владения.
        OPEX здесь включает в себя аренду/обслуживание здания и изменение транспортных расходов.
        """
        base_capex = self.calculate_fixed_capex()
        base_opex_location = self.calculate_annual_opex()

        if self.ownership_type == "POKUPKA":
            base_capex += self.purchase_cost

        # Суммируем OPEX от локации (аренда/обслуживание) и OPEX от транспорта
        total_base_opex = base_opex_location + self.get_transport_cost_change_rub()

        return {
            "base_capex": base_capex,
            "base_opex": total_base_opex
        }
```

## `core\simulation_engine.py`

```py
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
```

## `core\__init__.py`

```py

```

## `output\flexsim_setup_1_Move_No_Mitigation.json`

```json
{
    "FINANCIALS": {
        "Total_CAPEX": 1900000000,
        "Annual_OPEX": 317644372.01408386
    },
    "LAYOUT": {
        "Total_Area_SQM": 17000,
        "Ceiling_Height": 12,
        "GPP_ZONES": [
            {
                "Zone": "Cool_2_8C",
                "Pallet_Capacity": 3000
            },
            {
                "Zone": "Controlled_15_25C",
                "Pallet_Capacity": 17000
            }
        ]
    },
    "RESOURCES": {
        "Staff_Operators": 75,
        "Automation_Type": "None",
        "Processing_Time_Coefficient": 1.0
    },
    "LOGISTICS": {
        "Location_Coords": [
            56.01,
            37.1
        ],
        "Required_Own_Fleet_Count": 532,
        "Delivery_Flows": [
            {
                "Dest": "SVO_Aviation",
                "Volume_Pct": 25.0
            },
            {
                "Dest": "CFD_Own_Fleet",
                "Volume_Pct": 46.0
            },
            {
                "Dest": "Moscow_LPU",
                "Volume_Pct": 28.999999999999996
            }
        ]
    }
}
```

## `output\flexsim_setup_2_Move_With_Compensation.json`

```json
{
    "FINANCIALS": {
        "Total_CAPEX": 1950000000,
        "Annual_OPEX": 330244372.01408386
    },
    "LAYOUT": {
        "Total_Area_SQM": 17000,
        "Ceiling_Height": 12,
        "GPP_ZONES": [
            {
                "Zone": "Cool_2_8C",
                "Pallet_Capacity": 3000
            },
            {
                "Zone": "Controlled_15_25C",
                "Pallet_Capacity": 17000
            }
        ]
    },
    "RESOURCES": {
        "Staff_Operators": 85,
        "Automation_Type": "None",
        "Processing_Time_Coefficient": 1.0
    },
    "LOGISTICS": {
        "Location_Coords": [
            56.01,
            37.1
        ],
        "Required_Own_Fleet_Count": 532,
        "Delivery_Flows": [
            {
                "Dest": "SVO_Aviation",
                "Volume_Pct": 25.0
            },
            {
                "Dest": "CFD_Own_Fleet",
                "Volume_Pct": 46.0
            },
            {
                "Dest": "Moscow_LPU",
                "Volume_Pct": 28.999999999999996
            }
        ]
    }
}
```

## `output\flexsim_setup_3_Move_Basic_Automation.json`

```json
{
    "FINANCIALS": {
        "Total_CAPEX": 2000000000,
        "Annual_OPEX": 317644372.01408386
    },
    "LAYOUT": {
        "Total_Area_SQM": 17000,
        "Ceiling_Height": 12,
        "GPP_ZONES": [
            {
                "Zone": "Cool_2_8C",
                "Pallet_Capacity": 3000
            },
            {
                "Zone": "Controlled_15_25C",
                "Pallet_Capacity": 17000
            }
        ]
    },
    "RESOURCES": {
        "Staff_Operators": 75,
        "Automation_Type": "Conveyors+WMS",
        "Processing_Time_Coefficient": 1.2
    },
    "LOGISTICS": {
        "Location_Coords": [
            56.01,
            37.1
        ],
        "Required_Own_Fleet_Count": 532,
        "Delivery_Flows": [
            {
                "Dest": "SVO_Aviation",
                "Volume_Pct": 25.0
            },
            {
                "Dest": "CFD_Own_Fleet",
                "Volume_Pct": 46.0
            },
            {
                "Dest": "Moscow_LPU",
                "Volume_Pct": 28.999999999999996
            }
        ]
    }
}
```

## `output\flexsim_setup_4_Move_Advanced_Automation.json`

```json
{
    "FINANCIALS": {
        "Total_CAPEX": 2200000000,
        "Annual_OPEX": 317644372.01408386
    },
    "LAYOUT": {
        "Total_Area_SQM": 17000,
        "Ceiling_Height": 12,
        "GPP_ZONES": [
            {
                "Zone": "Cool_2_8C",
                "Pallet_Capacity": 3000
            },
            {
                "Zone": "Controlled_15_25C",
                "Pallet_Capacity": 17000
            }
        ]
    },
    "RESOURCES": {
        "Staff_Operators": 75,
        "Automation_Type": "AutoStore+AGV",
        "Processing_Time_Coefficient": 1.5
    },
    "LOGISTICS": {
        "Location_Coords": [
            56.01,
            37.1
        ],
        "Required_Own_Fleet_Count": 532,
        "Delivery_Flows": [
            {
                "Dest": "SVO_Aviation",
                "Volume_Pct": 25.0
            },
            {
                "Dest": "CFD_Own_Fleet",
                "Volume_Pct": 46.0
            },
            {
                "Dest": "Moscow_LPU",
                "Volume_Pct": 28.999999999999996
            }
        ]
    }
}
```

