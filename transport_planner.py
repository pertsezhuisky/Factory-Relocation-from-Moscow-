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
