## `core/__init__.py`

```py

```

## `core/location.py`

```py
# core/location.py

"""
Объединенный модуль для анализа геолокации и связанных с ней финансовых расчетов.
Он объединил в себе логику из flexible_location_model.py и geo_analyzer.py.
"""
from typing import Dict, Tuple
from math import radians, sin, cos, sqrt, atan2

from core.data_model import LocationSpec
import config

class LocationAnalyzer:
    """
    Рассчитывает все затраты и метрики, зависящие от физического расположения склада.
    """
    def __init__(self, spec: LocationSpec):
        self.spec = spec

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
        new_hub_coords = (self.spec.lat, self.spec.lon)
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
        base_capex = config.BASE_EQUIPMENT_CAPEX_RUB
        base_opex_location = 0

        if self.spec.ownership_type == "ARENDA":
            base_opex_location = config.WAREHOUSE_TOTAL_AREA_SQM * config.ANNUAL_RENT_PER_SQM_RUB
        elif self.spec.ownership_type == "POKUPKA":
            base_capex += config.PURCHASE_BUILDING_COST_RUB
            base_opex_location = config.MAINTENANCE_COST_OF_OWNED_BUILDING_RUB_YEAR
        else:
            raise ValueError("Неверный тип владения: должен быть 'ARENDA' или 'POKUPKA'")

        # Суммируем OPEX от локации (аренда/обслуживание) и OPEX от транспорта
        total_base_opex = base_opex_location + self.get_transport_cost_change_rub()

        return {
            "base_capex": base_capex,
            "base_opex": total_base_opex
        }
```

## `core/simulation_engine.py`

```py
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
```

## `core/flexsim_bridge.py`

```py
"""
Модуль для взаимодействия с FlexSim: генерация JSON и имитация API.
"""
import json
import os
from typing import Dict, Any, Optional

import config
from core.data_model import LocationSpec, ScenarioResult

class FlexsimBridge:
    """
    Управляет созданием конфигурационных файлов для FlexSim и
    имитирует отправку команд через Socket API.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[FlexsimBridge] Инициализирован. Выходная директория: '{self.output_dir}'")

    def generate_json_config(self, location_spec: LocationSpec, scenario_result: ScenarioResult, scenario_params: dict):
        """Создает и сохраняет JSON-конфигурацию для одного сценария."""
        
        # Определяем, какие системы автоматизации включены в сценарии
        automation_systems = []
        automation_investment = scenario_params.get('automation_investment_rub', 0)
        if automation_investment == 100_000_000:
            automation_systems.append("Conveyors")
        elif automation_investment > 100_000_000:
            automation_systems.extend(["Conveyors", "AGV", "RoboticArms"])
            
        config_data = {
            "Global_Settings": {
                "Scenario_Name": scenario_result.scenario_name,
                "location_name": location_spec.name,
                "coordinates": {"lat": location_spec.lat, "lon": location_spec.lon}
            },
            "Resource_Pool": {
                "Operators": scenario_result.staff_count,
                "Automated_Systems": automation_systems
            },
            "Process_Times": {
                "Base_Efficiency_Multiplier": scenario_params.get('efficiency_multiplier', 1.0)
            },
            "Throughput_Targets": {
                "Monthly_Orders_Target": config.TARGET_ORDERS_MONTH,
                "Monthly_Orders_Achieved": scenario_result.throughput_orders
            }
        }
        
        # Формируем имя файла на основе имени сценария
        safe_scenario_name = scenario_result.scenario_name.replace('. ', '_').replace(' ', '_')
        filename = f"flexsim_setup_{safe_scenario_name}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        print(f"  > ✅ JSON-конфиг сохранен: {filename}")

    def send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Имитирует отправку команды FlexSim (stub-версия из api_bridge.py)."""
        print(f"[FlexsimBridge STUB] Отправка команды '{command}'...")
        try:
            # Имитируем ошибку подключения, так как сервера нет
            raise ConnectionRefusedError("No FlexSim server is listening (as expected for a stub).")
        except ConnectionRefusedError as e:
            print(f"[FlexsimBridge STUB] Ошибка (это нормально для заглушки): {e}")
            if command == "LOAD_CONFIG":
                return {"status": "OK", "message": "Configuration loaded."}
            elif command == "START_SIMULATION":
                return {"status": "OK", "message": "Simulation started."}
            elif command == "GET_KPI":
                 return {"status": "OK", "kpi": {"throughput": 999, "utilization": 0.9}}
            return {"status": "ERROR", "message": "Unknown command"}
```

## `core/data_model.py`

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

## `scenarios.py`

```py
# scenarios.py

"""
Определения всех сценариев для моделирования.
Ключ словаря используется внутри программы, а 'name' будет отображаться в отчетах.
"""

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
        "efficiency_multiplier": 1.25              # Эффективность +25%
    },
    "4_Move_Advanced_Automation": {
        "name": "4. Move Advanced Automation",
        "staff_attrition_rate": 0.25,
        "hr_investment_rub": 0,
        "automation_investment_rub": 300_000_000, # 300 млн руб. на роботов
        "efficiency_multiplier": 2.0               # Эффективность x2
    }
}
```

## `analysis.py`

```py
# analysis.py

"""
Скрипт для анализа и визуализации результатов ПОСЛЕ выполнения симуляции.
Запускается отдельно командой: python analysis.py
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config

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
    plot_results()
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
```

## `collected_code.md`

```md
## `core/__init__.py`

```py

```

## `core/location.py`

```py
# core/location.py

"""
Объединенный модуль для анализа геолокации и связанных с ней финансовых расчетов.
Он объединил в себе логику из flexible_location_model.py и geo_analyzer.py.
"""
from typing import Dict, Tuple
from math import radians, sin, cos, sqrt, atan2

from core.data_model import LocationSpec
import config

class LocationAnalyzer:
    """
    Рассчитывает все затраты и метрики, зависящие от физического расположения склада.
    """
    def __init__(self, spec: LocationSpec):
        self.spec = spec

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
        new_hub_coords = (self.spec.lat, self.spec.lon)
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
        base_capex = config.BASE_EQUIPMENT_CAPEX_RUB
        base_opex_location = 0

        if self.spec.ownership_type == "ARENDA":
            base_opex_location = config.WAREHOUSE_TOTAL_AREA_SQM * config.ANNUAL_RENT_PER_SQM_RUB
        elif self.spec.ownership_type == "POKUPKA":
            base_capex += config.PURCHASE_BUILDING_COST_RUB
            base_opex_location = config.MAINTENANCE_COST_OF_OWNED_BUILDING_RUB_YEAR
        else:
            raise ValueError("Неверный тип владения: должен быть 'ARENDA' или 'POKUPKA'")

        # Суммируем OPEX от локации (аренда/обслуживание) и OPEX от транспорта
        total_base_opex = base_opex_location + self.get_transport_cost_change_rub()

        return {
            "base_capex": base_capex,
            "base_opex": total_base_opex
        }
```

## `core/simulation_engine.py`

```py
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
```

## `core/flexsim_bridge.py`

```py
"""
Модуль для взаимодействия с FlexSim: генерация JSON и имитация API.
"""
import json
import os
from typing import Dict, Any, Optional

import config
from core.data_model import LocationSpec, ScenarioResult

class FlexsimBridge:
    """
    Управляет созданием конфигурационных файлов для FlexSim и
    имитирует отправку команд через Socket API.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[FlexsimBridge] Инициализирован. Выходная директория: '{self.output_dir}'")

    def generate_json_config(self, location_spec: LocationSpec, scenario_result: ScenarioResult, scenario_params: dict):
        """Создает и сохраняет JSON-конфигурацию для одного сценария."""
        
        # Определяем, какие системы автоматизации включены в сценарии
        automation_systems = []
        automation_investment = scenario_params.get('automation_investment_rub', 0)
        if automation_investment == 100_000_000:
            automation_systems.append("Conveyors")
        elif automation_investment > 100_000_000:
            automation_systems.extend(["Conveyors", "AGV", "RoboticArms"])
            
        config_data = {
            "Global_Settings": {
                "Scenario_Name": scenario_result.scenario_name,
                "location_name": location_spec.name,
                "coordinates": {"lat": location_spec.lat, "lon": location_spec.lon}
            },
            "Resource_Pool": {
                "Operators": scenario_result.staff_count,
                "Automated_Systems": automation_systems
            },
            "Process_Times": {
                "Base_Efficiency_Multiplier": scenario_params.get('efficiency_multiplier', 1.0)
            },
            "Throughput_Targets": {
                "Monthly_Orders_Target": config.TARGET_ORDERS_MONTH,
                "Monthly_Orders_Achieved": scenario_result.throughput_orders
            }
        }
        
        # Формируем имя файла на основе имени сценария
        safe_scenario_name = scenario_result.scenario_name.replace('. ', '_').replace(' ', '_')
        filename = f"flexsim_setup_{safe_scenario_name}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        print(f"  > ✅ JSON-конфиг сохранен: {filename}")

    def send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Имитирует отправку команды FlexSim (stub-версия из api_bridge.py)."""
        print(f"[FlexsimBridge STUB] Отправка команды '{command}'...")
        try:
            # Имитируем ошибку подключения, так как сервера нет
            raise ConnectionRefusedError("No FlexSim server is listening (as expected for a stub).")
        except ConnectionRefusedError as e:
            print(f"[FlexsimBridge STUB] Ошибка (это нормально для заглушки): {e}")
            if command == "LOAD_CONFIG":
                return {"status": "OK", "message": "Configuration loaded."}
            elif command == "START_SIMULATION":
                return {"status": "OK", "message": "Simulation started."}
            elif command == "GET_KPI":
                 return {"status": "OK", "kpi": {"throughput": 999, "utilization": 0.9}}
            return {"status": "ERROR", "message": "Unknown command"}
```

## `core/data_model.py`

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

## `scenarios.py`

```py
# scenarios.py

"""
Определения всех сценариев для моделирования.
Ключ словаря используется внутри программы, а 'name' будет отображаться в отчетах.
"""

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
        "efficiency_multiplier": 1.25              # Эффективность +25%
    },
    "4_Move_Advanced_Automation": {
        "name": "4. Move Advanced Automation",
        "staff_attrition_rate": 0.25,
        "hr_investment_rub": 0,
        "automation_investment_rub": 300_000_000, # 300 млн руб. на роботов
        "efficiency_multiplier": 2.0               # Эффективность x2
    }
}
```

## `analysis.py`

```py

```

## `simulation_runner.py`

```py
import pandas as pd
import math
from typing import List
import os

# Импорт модулей ядра и настроек
from core.data_model import LocationSpec, ScenarioResult
from core.location import LocationAnalyzer
from core.simulation_engine import WarehouseSimulator
from core.flexsim_bridge import FlexsimBridge
import config
from scenarios import SCENARIOS_CONFIG

class SimulationRunner:
    """
    Главный класс-оркестратор. Управляет полным циклом анализа
    и генерации результатов для заданной локации.
    """
    
    def __init__(self, location_spec: LocationSpec):
        self.location_spec = location_spec
        # Инициализируем все необходимые нам "инструменты"
        self.location_analyzer = LocationAnalyzer(location_spec)
        self.flexsim_bridge = FlexsimBridge(config.OUTPUT_DIR)
        # Готовим пустой список для сбора итоговых результатов
        self.results: List[ScenarioResult] = []

    def run_all_scenarios(self):
        """Запускает полный цикл анализа для всех сценариев из scenarios.py."""
        print(f"\n{'='*80}\nЗАПУСК АНАЛИЗА ДЛЯ ЛОКАЦИИ: '{self.location_spec.name}'\n{'='*80}")
        
        # 1. Сначала рассчитываем базовые финансовые показатели, зависящие только от локации
        base_finance = self.location_analyzer.get_base_financials()
        baseline_annual_opex = 0  # OPEX базового сценария для расчета экономии

        # 2. Проходим в цикле по каждому сценарию
        for key, params in SCENARIOS_CONFIG.items():
            print(f"\n--- Обработка сценария: {params['name']} ---")

            # 3. Расчет персонала
            staff_count = math.floor(config.INITIAL_STAFF_COUNT * (1 - params['staff_attrition_rate']))
            
            # 4. Запуск SimPy симуляции для получения операционных KPI
            print(f"  > Запуск SimPy с {staff_count} чел. и эффективностью x{params['efficiency_multiplier']}...")
            sim = WarehouseSimulator(staff_count, params['efficiency_multiplier'])
            sim_kpi = sim.run()
            print(f"  > SimPy завершен. Обработано заказов: {sim_kpi['achieved_throughput']}")

            # 5. Расчет итоговых финансовых KPI для этого сценария
            total_capex = base_finance['base_capex'] + params['hr_investment_rub'] + params['automation_investment_rub']
            opex_labor = staff_count * config.OPERATOR_SALARY_RUB_MONTH * 12
            total_opex = base_finance['base_opex'] + opex_labor

            # Запоминаем OPEX первого ("базового") сценария
            if 'No_Mitigation' in key:
                baseline_annual_opex = total_opex
            
            # 6. Расчет срока окупаемости для сценариев с автоматизацией
            payback = float('nan') # По умолчанию "не число", т.е. неприменимо
            if params['automation_investment_rub'] > 0 and baseline_annual_opex > 0:
                annual_savings = baseline_annual_opex - total_opex
                if annual_savings > 0:
                    payback = round(params['automation_investment_rub'] / annual_savings, 2)
            
            # 7. Сборка всех KPI в единую структуру данных
            result = ScenarioResult(
                location_name=self.location_spec.name,
                scenario_name=params['name'],
                staff_count=staff_count,
                throughput_orders=int(sim_kpi['achieved_throughput']),
                avg_cycle_time_min=int(sim_kpi['avg_cycle_time_min']),
                total_annual_opex_rub=int(total_opex),
                total_capex_rub=int(total_capex),
                payback_period_years=payback
            )
            # Добавляем результат в общий список
            self.results.append(result)
            
            # 8. Генерация JSON-файла для FlexSim
            self.flexsim_bridge.generate_json_config(self.location_spec, result, params)

        # 9. После завершения цикла сохраняем сводный CSV-файл
        self._save_summary_csv()
        print(f"\n--- Анализ для локации '{self.location_spec.name}' завершен. ---")

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

## `main.py`

```py
# main.py

"""
Единственная точка входа в приложение.
Парсит аргументы командной строки и запускает оркестратор симуляций.
"""
import argparse
from core.data_model import LocationSpec
from simulation_runner import SimulationRunner

def main():
    """Главная исполняемая функция."""
    
    parser = argparse.ArgumentParser(
        description="Запуск комплексного анализа релокации склада для FlexSim.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Для красивого вывода помощи
    )
    
    parser.add_argument("--name", type=str, default="Логопарк Север-2", help="Название анализируемой локации.")
    parser.add_argument("--lat", type=float, default=56.095, help="Широта локации.")
    parser.add_argument("--lon", type=float, default=37.388, help="Долгота локации.")
    parser.add_argument("--type", type=str, default="ARENDA", choices=["ARENDA", "POKUPKA"], help="Тип владения: аренда или покупка.")
    
    args = parser.parse_args()

    # 1. Создание объекта (структуры данных) с параметрами локации из аргументов CLI.
    location = LocationSpec(
        name=args.name, 
        lat=args.lat, 
        lon=args.lon, 
        ownership_type=args.type.upper()
    )
    
    # 2. Инициализация и запуск главного исполнителя.
    runner = SimulationRunner(location_spec=location)
    runner.run_all_scenarios()

if __name__ == "__main__":
    main()
```

## `output/flexsim_setup_1_Move_No_Mitigation.json`

```json
{
    "Global_Settings": {
        "Scenario_Name": "1. Move No Mitigation",
        "location_name": "Логопарк Север-2",
        "coordinates": {
            "lat": 56.095,
            "lon": 37.388
        }
    },
    "Resource_Pool": {
        "Operators": 75,
        "Automated_Systems": []
    },
    "Process_Times": {
        "Base_Efficiency_Multiplier": 1.0
    },
    "Throughput_Targets": {
        "Monthly_Orders_Target": 10000,
        "Monthly_Orders_Achieved": 10000
    }
}
```

## `output/flexsim_setup_4_Move_Advanced_Automation.json`

```json
{
    "Global_Settings": {
        "Scenario_Name": "4. Move Advanced Automation",
        "location_name": "Логопарк Север-2",
        "coordinates": {
            "lat": 56.095,
            "lon": 37.388
        }
    },
    "Resource_Pool": {
        "Operators": 75,
        "Automated_Systems": [
            "Conveyors",
            "AGV",
            "RoboticArms"
        ]
    },
    "Process_Times": {
        "Base_Efficiency_Multiplier": 2.0
    },
    "Throughput_Targets": {
        "Monthly_Orders_Target": 10000,
        "Monthly_Orders_Achieved": 10000
    }
}
```

## `output/flexsim_setup_3_Move_Basic_Automation.json`

```json
{
    "Global_Settings": {
        "Scenario_Name": "3. Move Basic Automation",
        "location_name": "Логопарк Север-2",
        "coordinates": {
            "lat": 56.095,
            "lon": 37.388
        }
    },
    "Resource_Pool": {
        "Operators": 75,
        "Automated_Systems": [
            "Conveyors"
        ]
    },
    "Process_Times": {
        "Base_Efficiency_Multiplier": 1.25
    },
    "Throughput_Targets": {
        "Monthly_Orders_Target": 10000,
        "Monthly_Orders_Achieved": 10000
    }
}
```

## `output/flexsim_setup_2_Move_With_Compensation.json`

```json
{
    "Global_Settings": {
        "Scenario_Name": "2. Move With Compensation",
        "location_name": "Логопарк Север-2",
        "coordinates": {
            "lat": 56.095,
            "lon": 37.388
        }
    },
    "Resource_Pool": {
        "Operators": 85,
        "Automated_Systems": []
    },
    "Process_Times": {
        "Base_Efficiency_Multiplier": 1.0
    },
    "Throughput_Targets": {
        "Monthly_Orders_Target": 10000,
        "Monthly_Orders_Achieved": 10000
    }
}
```

## `core/__init__.py`

```py

```

## `core/location.py`

```py
# core/location.py

"""
Объединенный модуль для анализа геолокации и связанных с ней финансовых расчетов.
Он объединил в себе логику из flexible_location_model.py и geo_analyzer.py.
"""
from typing import Dict, Tuple
from math import radians, sin, cos, sqrt, atan2

from core.data_model import LocationSpec
import config

class LocationAnalyzer:
    """
    Рассчитывает все затраты и метрики, зависящие от физического расположения склада.
    """
    def __init__(self, spec: LocationSpec):
        self.spec = spec

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
        new_hub_coords = (self.spec.lat, self.spec.lon)
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
        base_capex = config.BASE_EQUIPMENT_CAPEX_RUB
        base_opex_location = 0

        if self.spec.ownership_type == "ARENDA":
            base_opex_location = config.WAREHOUSE_TOTAL_AREA_SQM * config.ANNUAL_RENT_PER_SQM_RUB
        elif self.spec.ownership_type == "POKUPKA":
            base_capex += config.PURCHASE_BUILDING_COST_RUB
            base_opex_location = config.MAINTENANCE_COST_OF_OWNED_BUILDING_RUB_YEAR
        else:
            raise ValueError("Неверный тип владения: должен быть 'ARENDA' или 'POKUPKA'")

        # Суммируем OPEX от локации (аренда/обслуживание) и OPEX от транспорта
        total_base_opex = base_opex_location + self.get_transport_cost_change_rub()

        return {
            "base_capex": base_capex,
            "base_opex": total_base_opex
        }
```

## `core/simulation_engine.py`

```py
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
```

## `core/flexsim_bridge.py`

```py
"""
Модуль для взаимодействия с FlexSim: генерация JSON и имитация API.
"""
import json
import os
from typing import Dict, Any, Optional

import config
from core.data_model import LocationSpec, ScenarioResult

class FlexsimBridge:
    """
    Управляет созданием конфигурационных файлов для FlexSim и
    имитирует отправку команд через Socket API.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[FlexsimBridge] Инициализирован. Выходная директория: '{self.output_dir}'")

    def generate_json_config(self, location_spec: LocationSpec, scenario_result: ScenarioResult, scenario_params: dict):
        """Создает и сохраняет JSON-конфигурацию для одного сценария."""
        
        # Определяем, какие системы автоматизации включены в сценарии
        automation_systems = []
        automation_investment = scenario_params.get('automation_investment_rub', 0)
        if automation_investment == 100_000_000:
            automation_systems.append("Conveyors")
        elif automation_investment > 100_000_000:
            automation_systems.extend(["Conveyors", "AGV", "RoboticArms"])
            
        config_data = {
            "Global_Settings": {
                "Scenario_Name": scenario_result.scenario_name,
                "location_name": location_spec.name,
                "coordinates": {"lat": location_spec.lat, "lon": location_spec.lon}
            },
            "Resource_Pool": {
                "Operators": scenario_result.staff_count,
                "Automated_Systems": automation_systems
            },
            "Process_Times": {
                "Base_Efficiency_Multiplier": scenario_params.get('efficiency_multiplier', 1.0)
            },
            "Throughput_Targets": {
                "Monthly_Orders_Target": config.TARGET_ORDERS_MONTH,
                "Monthly_Orders_Achieved": scenario_result.throughput_orders
            }
        }
        
        # Формируем имя файла на основе имени сценария
        safe_scenario_name = scenario_result.scenario_name.replace('. ', '_').replace(' ', '_')
        filename = f"flexsim_setup_{safe_scenario_name}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        print(f"  > ✅ JSON-конфиг сохранен: {filename}")

    def send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Имитирует отправку команды FlexSim (stub-версия из api_bridge.py)."""
        print(f"[FlexsimBridge STUB] Отправка команды '{command}'...")
        try:
            # Имитируем ошибку подключения, так как сервера нет
            raise ConnectionRefusedError("No FlexSim server is listening (as expected for a stub).")
        except ConnectionRefusedError as e:
            print(f"[FlexsimBridge STUB] Ошибка (это нормально для заглушки): {e}")
            if command == "LOAD_CONFIG":
                return {"status": "OK", "message": "Configuration loaded."}
            elif command == "START_SIMULATION":
                return {"status": "OK", "message": "Simulation started."}
            elif command == "GET_KPI":
                 return {"status": "OK", "kpi": {"throughput": 999, "utilization": 0.9}}
            return {"status": "ERROR", "message": "Unknown command"}
```

## `core/data_model.py`

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

