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