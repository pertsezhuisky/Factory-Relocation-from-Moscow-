# flexible_location_model.py

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from math import radians, sin, cos, sqrt, atan2 # Для формулы гаверсинуса

# =============================================================================
# ШАГ 1: Конфигурация локаций и финансов (без изменений)
# =============================================================================

CONSTRUCTION_CONSTANTS = {
    "total_area_sqm": 17000,
    "rent_rate_rub_sqm_year": 7500,
    "pokupka_building_cost_rub": 1_500_000_000,
    "capex_base_shelving_validation_rub": 350_000_000,
    "opex_maintenance_base_rub_year": 50_000_000,
}

# =============================================================================
# ШАГ 2: Имитация интеграции с Яндекс.Картами
# =============================================================================

# --- Константы для транспортного анализа ---
TRANSPORT_CONSTANTS = {
    "current_hub_coords": (55.858, 37.433),  # Сходненская
    "sheremetyevo_coords": (55.97, 37.41),    # Шереметьево
    # Имитация 8 ключевых ЛПУ (Лечебно-профилактические учреждения) в Москве
    "moscow_lpu_points": [
        (55.75, 37.61), (55.79, 37.53), (55.67, 37.48), (55.65, 37.76),
        (55.87, 37.66), (55.83, 37.44), (55.73, 37.79), (55.60, 37.57)
    ],
    # Финансовые тарифы (из источников)
    "annual_orders_count": 10000 * 12, # 10 000 заказов/мес
    "transport_tariff_rub_per_km": 13.4, # Средний тариф для 18-20т фуры
}

class YandexGeoAnalyzer:
    """
    Класс-заглушка для имитации расчетов гео-данных, таких как расстояния.
    Использует формулу Гаверсинуса для расчета расстояния по прямой,
    что является хорошим приближением для стратегического анализа.
    """
    def _haversine_distance(self, coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
        """Расчет расстояния между двумя точками в км."""
        R = 6371.0  # Радиус Земли в км
        
        lat1, lon1 = radians(coords1[0]), radians(coords1[1])
        lat2, lon2 = radians(coords2[0]), radians(coords2[1])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance * 1.4 # Добавляем коэффициент 1.4 для учета кривизны дорог

    def calculate_distances(self, new_hub_coords: Tuple[float, float]) -> Dict[str, float]:
        """
        Рассчитывает среднее изменение расстояния доставки при переезде
        со старого HUB на новый.
        """
        total_distance_increase_km = 0
        
        # Ключевые точки доставки: 8 ЛПУ и Шереметьево
        key_points = TRANSPORT_CONSTANTS["moscow_lpu_points"] + [TRANSPORT_CONSTANTS["sheremetyevo_coords"]]
        
        for point in key_points:
            # Расстояние от старого HUB до точки
            dist_old = self._haversine_distance(TRANSPORT_CONSTANTS["current_hub_coords"], point)
            # Расстояние от нового HUB до точки
            dist_new = self._haversine_distance(new_hub_coords, point)
            
            # Находим разницу (дополнительное "плечо") и суммируем
            total_distance_increase_km += (dist_new - dist_old)

        avg_distance_increase_per_trip = total_distance_increase_km / len(key_points)
        
        # Допущение: каждый заказ - это отдельная поездка (упрощение для модели)
        # В реальности заказы группируются, но это позволяет оценить относительное изменение
        total_annual_extra_km = avg_distance_increase_per_trip * TRANSPORT_CONSTANTS["annual_orders_count"]

        return {
            "avg_extra_distance_per_trip_km": avg_distance_increase_per_trip,
            "total_annual_extra_km": total_annual_extra_km
        }


# =============================================================================
# ШАГ 1 и 2 ИНТЕГРАЦИЯ: Обновленный класс LocationParameters
# =============================================================================

@dataclass
class LocationParameters:
    """
    Инкапсулирует все параметры локации, включая расчет транспортных расходов.
    """
    location_name: str
    lat: float
    lon: float
    ownership_type: str
    geo_analyzer: YandexGeoAnalyzer # <<-- Интеграция анализатора
    
    area_sqm: int = CONSTRUCTION_CONSTANTS["total_area_sqm"]

    def calculate_full_finance_profile(self) -> Dict[str, Any]:
        """
        Рассчитывает ПОЛНЫЙ финансовый профиль локации, включая OPEX, CAPEX
        и транспортные расходы.
        """
        # --- Блок 1: Расчет стоимости владения и базового CAPEX (как и раньше) ---
        annual_location_cost = 0
        base_capex = CONSTRUCTION_CONSTANTS["capex_base_shelving_validation_rub"]

        if self.ownership_type == "ARENDA":
            annual_location_cost = self.area_sqm * CONSTRUCTION_CONSTANTS["rent_rate_rub_sqm_year"]
        elif self.ownership_type == "POKUPKA":
            base_capex += CONSTRUCTION_CONSTANTS["pokupka_building_cost_rub"]
            # При покупке есть только расходы на обслуживание здания
            annual_location_cost = CONSTRUCTION_CONSTANTS["opex_maintenance_base_rub_year"]
        else:
            raise ValueError("Неверный тип владения.")

        # --- Блок 2: Расчет транспортных расходов на основе геолокации ---
        distance_metrics = self.geo_analyzer.calculate_distances(new_hub_coords=(self.lat, self.lon))
        total_annual_extra_km = distance_metrics["total_annual_extra_km"]
        
        # Формула Т_год = V * S * Т_тариф
        # В нашем случае (V*S) уже рассчитано как total_annual_extra_km
        # Это ИЗМЕНЕНИЕ транспортных расходов, а не их полная сумма
        annual_transport_cost_increase = total_annual_extra_km * TRANSPORT_CONSTANTS["transport_tariff_rub_per_km"]

        # --- Сведение всех KPI в итоговый словарь ---
        return {
            "Location Name": self.location_name,
            "Ownership Type": self.ownership_type,
            "Coordinates": (self.lat, self.lon),
            "Initial CAPEX (RUB)": base_capex,
            "Annual Location Cost (RUB)": annual_location_cost,
            "Annual Transport Cost Change (RUB)": round(annual_transport_cost_increase),
            "Avg Extra Distance per Trip (km)": round(distance_metrics["avg_extra_distance_per_trip_km"], 2),
        }

# --- Тестовая функция ---
if __name__ == "__main__":
    
    print("-" * 80)
    print("ТЕСТ: Расчет транспортных расходов в зависимости от локации")
    print("-" * 80)
    
    # 1. Инициализируем наш "API" один раз
    geo_api = YandexGeoAnalyzer()

    # 2. Определяем локации для анализа, передавая в них наш API
    locations_to_analyze = [
        # Локация близко к текущему HUB, ожидаем небольшие изменения
        LocationParameters("Химки", 55.89, 37.44, "ARENDA", geo_api),
        # Локация "Логопарк Север-2" (реальные координаты)
        LocationParameters("Логопарк Север-2", 56.095, 37.388, "ARENDA", geo_api),
        # Удаленная локация в качестве примера
        LocationParameters("Ногинск", 55.88, 38.44, "POKUPKA", geo_api),
    ]

    # 3. Рассчитываем и выводим результаты для каждой
    for loc in locations_to_analyze:
        profile = loc.calculate_full_finance_profile()
        print(f"\nАнализ для: '{profile['Location Name']}' (Тип: {profile['Ownership Type']})")
        print(f"  > Среднее доп. плечо на 1 поездку: {profile['Avg Extra Distance per Trip (km)']} км")
        print(f"  > Изменение годовых транспортных расходов: {profile['Annual Transport Cost Change (RUB)']:,.0f} руб.")
        print(f"  - - - - - - -")
        print(f"  > Годовые расходы на владение: {profile['Annual Location Cost (RUB)']:,.0f} руб.")
        print(f"  > Первоначальные инвестиции (CAPEX): {profile['Initial CAPEX (RUB)']:,.0f} руб.")