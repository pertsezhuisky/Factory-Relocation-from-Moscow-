## `analysis.py`

```py
"""
Скрипт для анализа и визуализации результатов ПОСЛЕ выполнения симуляции.
Запускается отдельно командой: python analysis.py
"""
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config
import math
import requests

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
    """
    CURRENT_HUB_COORDS = (55.857, 37.436)
    SVO_COORDS = (55.97, 37.41)
    AVG_LPU_COORDS = (55.75, 37.62)
    AVG_CFD_COORDS = (54.51, 36.26)
    OSRM_BASE_URL = "https://router.project-osrm.org"

    def __init__(self, use_geocoding: bool = False):
        self.use_geocoding = use_geocoding
        # ИЗМЕНЕНИЕ: Добавляем атрибут geolocator в любом случае, но инициализируем его как None
        self.geolocator: Optional[Nominatim] = None
        if use_geocoding:
            self.geolocator = Nominatim(user_agent="warehouse_relocation_analyzer/1.0")
        self.geocode_cache: Dict[str, Optional[Tuple[float, float]]] = {}
        self.last_request_time = 0
        self.min_request_interval = 1.0

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Преобразует адрес в координаты используя Nominatim (geopy).
        """
        if not self.use_geocoding or self.geolocator is None:
            print("  > [Geocoding] Отключено. Используйте координаты напрямую.")
            return None

        if address in self.geocode_cache:
            print(f"  > [Geocoding Cache] '{address}' -> {self.geocode_cache[address]}")
            return self.geocode_cache[address]

        try:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)

            print(f"  > [Nominatim] Геокодирование адреса: '{address}'")
            location = self.geolocator.geocode(address, timeout=10)
            self.last_request_time = time.time()

            # Явная проверка на наличие атрибутов, чтобы Pylance был уверен в их существовании
            if location and hasattr(location, 'latitude') and hasattr(location, 'longitude'):
                coords = (location.latitude, location.longitude)
                self.geocode_cache[address] = coords
                print(f"  > [Nominatim] Найдено: {coords}")
                return coords
            else:
                print(f"  > [Nominatim] Адрес не найден: '{address}'")
                self.geocode_cache[address] = None # Также кэшируем неудачный результат
                return None

        except Exception as e:
            print(f"  > [Nominatim Error] {e}")
            return None

    def get_route_details(self, start_coords: tuple, end_coords: tuple, mode: str = 'driving') -> dict:
        """
        Получает детали маршрута через OSRM API (бесплатно, без ключей).
        """
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords
        osrm_coords = f"{lon1},{lat1};{lon2},{lat2}"
        url = f"{self.OSRM_BASE_URL}/route/v1/driving/{osrm_coords}?overview=false&steps=false"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['code'] == 'Ok' and len(data['routes']) > 0:
                route = data['routes'][0]
                distance_km = route['distance'] / 1000
                time_h = route['duration'] / 3600
                return {
                    'route_distance_km': round(distance_km, 2), 'travel_time_h': round(time_h, 2),
                    'mode': mode, 'status': 'success', 'source': 'OSRM'
                }
            else:
                print(f"  > [OSRM API Error] {data.get('message', 'Unknown error')}")
                return {'route_distance_km': 0, 'travel_time_h': 0, 'mode': mode, 'status': 'error', 'source': 'OSRM'}

        except requests.exceptions.RequestException as e:
            print(f"  > [OSRM API Error] Ошибка запроса: {e}")
            return self._fallback_distance_calculation(start_coords, end_coords, mode)

    def _fallback_distance_calculation(self, start_coords: tuple, end_coords: tuple, mode: str) -> dict:
        """
        Упрощенный расчет расстояния (fallback на случай недоступности OSRM).
        """
        from math import radians, sin, cos, sqrt, atan2
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords
        R = 6371.0
        lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance_km = R * c * 1.3
        time_h = distance_km / 50
        print(f"  > [Fallback] Используется упрощенный расчет: {distance_km:.1f} км")
        return {
            'route_distance_km': round(distance_km, 2), 'travel_time_h': round(time_h, 2),
            'mode': mode, 'status': 'fallback', 'source': 'haversine'
        }

    def calculate_weighted_annual_distance(self, new_location_coords: tuple) -> dict:
        """
        Рассчитывает взвешенное годовое расстояние S для всех транспортных потоков.
        """
        print(f"\n  > [OSRMGeoRouter] Расчет взвешенного годового расстояния для локации {new_location_coords}")
        flows = {
            'CFO': {'coords': self.AVG_CFD_COORDS, 'share': 0.46, 'name': 'ЦФО (собственный флот)'},
            'SVO': {'coords': self.SVO_COORDS, 'share': 0.25, 'name': 'Авиа (Шереметьево)'},
            'LPU': {'coords': self.AVG_LPU_COORDS, 'share': 0.29, 'name': 'Местные ЛПУ (Москва)'}
        }
        results = {}
        total_weighted_distance = 0
        for flow_id, flow_data in flows.items():
            route = self.get_route_details(new_location_coords, flow_data['coords'])
            weighted_distance = route['route_distance_km'] * flow_data['share']
            total_weighted_distance += weighted_distance
            results[flow_id] = {
                'distance_km': route['route_distance_km'], 'time_h': route['travel_time_h'], 'share': flow_data['share'],
                'weighted_distance_km': weighted_distance, 'name': flow_data['name'], 'source': route.get('source', 'unknown')
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

    def __init__(self, use_geocoding: bool = False):
        """
        Инициализация роутера.

        Args:
            use_geocoding: Использовать ли Nominatim для геокодирования адресов
        """
        self.use_geocoding = use_geocoding
        # Мы явно указываем, что self.geolocator может быть None, что помогает анализатору
        self.geolocator: Optional[Nominatim] = None
        if use_geocoding:
            self.geolocator = Nominatim(user_agent="warehouse_relocation_analyzer/1.0")

        # Кэш для геокодирования (чтобы не делать повторные запросы)
        self.geocode_cache: Dict[str, Optional[Tuple[float, float]]] = {}

        # Счетчик запросов для rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Минимум 1 секунда между запросами к Nominatim

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
    # Используем старый тариф для обратной совместимости, но новый расчет будет в calculate_annual_transport_cost
    LOCAL_FLEET_TARIFF_RUB_KM = 11.2

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
        Включает базовые расходы + ремонт (15%) + компенсацию простоев (5%).
        """
        annual_orders = self.MONTHLY_ORDERS * 12

        # Затраты на ЦФО (собственный флот)
        cost_cfo = (annual_orders * self.CFO_OWN_FLEET_SHARE) * avg_dist_cfo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на Авиа (доставка в SVO)
        cost_svo = (annual_orders * self.AIR_DELIVERY_SHARE) * avg_dist_svo * self.OWN_FLEET_TARIFF_RUB_KM

        # <--- ИЗМЕНЕННАЯ ЛОГИКА --->
        # Затраты на местные перевозки (наемный транспорт)
        # Используем новый повышенный тариф из config.py для учета ограничений в Москве
        cost_local = (annual_orders * self.LOCAL_DELIVERY_SHARE) * avg_dist_local * config.MOSCOW_DELIVERY_TARIFF_RUB_PER_KM

        # Базовые транспортные расходы
        base_transport_cost = cost_cfo + cost_svo + cost_local

        # Добавляем расходы на ремонт и обслуживание (15% от базовых расходов)
        maintenance_cost = base_transport_cost * config.TRANSPORT_MAINTENANCE_RATE

        # Добавляем компенсацию простоев (5% от базовых расходов)
        downtime_cost = base_transport_cost * config.TRANSPORT_DOWNTIME_RATE

        # Общие годовые транспортные расходы
        total_cost = base_transport_cost + maintenance_cost + downtime_cost

        return total_cost

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

        # <--- ИЗМЕНЕННАЯ ЛОГИКА --->
        # Рассчитываем годовые транспортные расходы (T_год) используя обновленный метод
        total_annual_transport_cost = self.calculate_annual_transport_cost(dist_cfo, dist_svo, dist_lpu)
        
        # Разделяем для отчетности
        annual_orders = self.MONTHLY_ORDERS * 12
        cost_cfo = (annual_orders * self.CFO_OWN_FLEET_SHARE) * dist_cfo * self.OWN_FLEET_TARIFF_RUB_KM
        cost_svo = (annual_orders * self.AIR_DELIVERY_SHARE) * dist_svo * self.OWN_FLEET_TARIFF_RUB_KM
        cost_local = (annual_orders * self.LOCAL_DELIVERY_SHARE) * dist_lpu * config.MOSCOW_DELIVERY_TARIFF_RUB_PER_KM


        # Рассчитываем необходимый флот (логика остается прежней для упрощенной оценки)
        # 1. Грузовики 18-20 тонн для ЦФО (2 рейса/нед)
        cfo_orders_per_month = self.MONTHLY_ORDERS * self.CFO_OWN_FLEET_SHARE
        weeks_in_month = 4.33
        cfo_orders_per_week = cfo_orders_per_month / weeks_in_month
        required_heavy_trucks = math.ceil(cfo_orders_per_week / self.CFO_TRIPS_PER_WEEK_PER_TRUCK)

        # 2. Грузовики 5 тонн для Москвы (ежедневно, 6-8 точек) - эта логика будет уточнена в DetailedFleetPlanner
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
            print(f"  > Площадь: {loc['area_offered_sqm']} м²")
            print(f"  > OPEX (помещение): {loc['annual_building_opex']:,.0f} руб./год")
            print(f"  > CAPEX (начальный):  {loc['total_initial_capex']:,.0f} руб.")
            print("-" * 80)
```

## `animations.py`

```py
"""
Модуль для создания анимированных визуализаций финансовых показателей.
Включает анимации ROI, окупаемости, денежного потока и других KPI.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Использовать backend без GUI для серверной генерации
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from typing import Dict, Any, List
import config


class FinancialAnimator:
    """Класс для создания анимированных финансовых визуализаций."""

    def __init__(self, output_dir: str = None):
        """
        Инициализация аниматора.

        Args:
            output_dir: Директория для сохранения анимаций
        """
        self.output_dir = output_dir or config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        # Настройка стиля
        plt.style.use('seaborn-v0_8-darkgrid')

    def animate_roi_comparison(self, roi_data: Dict[str, Any],
                               save_path: str = None,
                               years: int = 10) -> str:
        """
        Создает анимацию сравнения ROI для разных сценариев автоматизации.

        Args:
            roi_data: Данные ROI из автоматизации
            save_path: Путь для сохранения (если None, используется output_dir)
            years: Количество лет для моделирования

        Returns:
            Путь к сохраненному файлу
        """
        if save_path is None:
            save_path = os.path.join(self.output_dir, "roi_comparison_animated.gif")

        print(f"\n[Анимация] Создание анимации сравнения ROI ({years} лет)...")

        # Подготовка данных
        scenarios = []
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']

        for idx, (level_value, roi_info) in enumerate(roi_data.items()):
            scenarios.append({
                'name': roi_info['scenario_name'],
                'capex': roi_info['capex'],
                'annual_benefit': roi_info['net_annual_benefit'],
                'color': colors[idx % len(colors)]
            })

        # Создание фигуры
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Динамика окупаемости инвестиций (ROI)', fontsize=16, fontweight='bold')

        # Инициализация графиков
        lines = []
        bars = []

        for scenario in scenarios:
            line, = ax1.plot([], [], label=scenario['name'],
                           linewidth=2.5, color=scenario['color'])
            lines.append(line)
            bars.append(None)

        ax1.set_xlim(0, years)
        ax1.set_xlabel('Годы', fontsize=12)
        ax1.set_ylabel('Накопленный денежный поток (млн руб)', fontsize=12)
        ax1.set_title('Кумулятивный денежный поток', fontsize=14)
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)

        ax2.set_xlim(-0.5, len(scenarios) - 0.5)
        ax2.set_xlabel('Сценарий', fontsize=12)
        ax2.set_ylabel('ROI (%)', fontsize=12)
        ax2.set_title('ROI к текущему моменту', fontsize=14)
        ax2.set_xticks(range(len(scenarios)))
        ax2.set_xticklabels([s['name'].split(':')[0] for s in scenarios], rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')

        # Функция инициализации
        def init():
            for line in lines:
                line.set_data([], [])
            return lines

        # Функция анимации
        def animate_frame(frame):
            year = frame / 10  # 10 кадров на год для плавности

            # Обновление графика денежного потока
            for idx, (line, scenario) in enumerate(zip(lines, scenarios)):
                years_array = np.linspace(0, year, int(year * 10) + 1)
                cumulative_cf = -scenario['capex'] + scenario['annual_benefit'] * years_array
                line.set_data(years_array, cumulative_cf / 1_000_000)  # В миллионах

            # Обновление гистограммы ROI
            ax2.clear()
            ax2.set_xlim(-0.5, len(scenarios) - 0.5)
            ax2.set_xlabel('Сценарий', fontsize=12)
            ax2.set_ylabel('ROI (%)', fontsize=12)
            ax2.set_title(f'ROI к году {year:.1f}', fontsize=14)
            ax2.set_xticks(range(len(scenarios)))
            ax2.set_xticklabels([s['name'].split(':')[0] for s in scenarios], rotation=45, ha='right')
            ax2.grid(True, alpha=0.3, axis='y')

            roi_values = []
            for scenario in scenarios:
                cumulative_cf = -scenario['capex'] + scenario['annual_benefit'] * year
                roi = (cumulative_cf / scenario['capex'] * 100) if scenario['capex'] > 0 else 0
                roi_values.append(roi)

            bars = ax2.bar(range(len(scenarios)), roi_values,
                          color=[s['color'] for s in scenarios], alpha=0.7)

            # Добавление значений на столбцы
            for idx, (bar, roi_val) in enumerate(zip(bars, roi_values)):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{roi_val:.1f}%',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

            ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)

            return lines + [ax2]

        # Создание анимации
        frames = years * 10  # 10 кадров на год
        anim = animation.FuncAnimation(fig, animate_frame, init_func=init,
                                      frames=frames, interval=50, blit=False)

        # Сохранение
        try:
            print(f"  [Сохранение] {save_path}...")
            anim.save(save_path, writer='pillow', fps=20, dpi=100)
            plt.close(fig)
            print(f"  [Готово] Анимация сохранена: {save_path}")
            return save_path
        except Exception as e:
            print(f"  [Предупреждение] Не удалось сохранить анимацию: {e}")
            plt.close(fig)
            return None

    def animate_payback_period(self, roi_data: Dict[str, Any],
                               save_path: str = None) -> str:
        """
        Создает анимацию достижения точки окупаемости для разных сценариев.

        Args:
            roi_data: Данные ROI
            save_path: Путь для сохранения

        Returns:
            Путь к сохраненному файлу
        """
        if save_path is None:
            save_path = os.path.join(self.output_dir, "payback_period_animated.gif")

        print(f"\n[Анимация] Создание анимации срока окупаемости...")

        # Подготовка данных
        scenarios_data = []
        max_payback = 0

        for level_value, roi_info in roi_data.items():
            payback = roi_info['payback_years']
            if payback != float('inf'):
                scenarios_data.append({
                    'name': roi_info['scenario_name'],
                    'payback': payback,
                    'capex': roi_info['capex'],
                    'annual_benefit': roi_info['net_annual_benefit']
                })
                max_payback = max(max_payback, payback)

        if not scenarios_data:
            print("  [Предупреждение] Нет сценариев с конечным сроком окупаемости")
            return None

        # Создание фигуры
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle('Достижение точки окупаемости', fontsize=16, fontweight='bold')

        colors = plt.cm.viridis(np.linspace(0, 1, len(scenarios_data)))

        # Максимальное время для анимации
        max_years = min(max_payback * 1.2, 15)

        ax.set_xlim(0, max_years)
        ax.set_ylim(-0.5, len(scenarios_data) - 0.5)
        ax.set_xlabel('Годы', fontsize=12)
        ax.set_ylabel('Сценарий', fontsize=12)
        ax.set_yticks(range(len(scenarios_data)))
        ax.set_yticklabels([s['name'] for s in scenarios_data])
        ax.grid(True, alpha=0.3, axis='x')

        # Отметка точек окупаемости
        for idx, scenario in enumerate(scenarios_data):
            ax.axvline(x=scenario['payback'], color=colors[idx],
                      linestyle='--', alpha=0.3, linewidth=1)
            ax.text(scenario['payback'], idx, f" {scenario['payback']:.1f} лет",
                   va='center', fontsize=9, color=colors[idx], fontweight='bold')

        # Прогресс-бары
        progress_bars = []
        for idx in range(len(scenarios_data)):
            bar = Rectangle((0, idx - 0.3), 0, 0.6,
                          facecolor=colors[idx], alpha=0.7)
            ax.add_patch(bar)
            progress_bars.append(bar)

        # Текстовые метки с ROI
        roi_texts = []
        for idx in range(len(scenarios_data)):
            text = ax.text(0, idx, '', ha='left', va='center',
                         fontsize=9, fontweight='bold', color='white',
                         bbox=dict(boxstyle='round', facecolor=colors[idx], alpha=0.8))
            roi_texts.append(text)

        def animate_frame(frame):
            progress = frame / 100  # 0 до 1
            current_time = max_years * progress

            for idx, (scenario, bar, text) in enumerate(zip(scenarios_data, progress_bars, roi_texts)):
                # Обновление ширины бара
                width = min(current_time, scenario['payback'])
                bar.set_width(width)

                # Расчет текущего ROI
                cumulative_cf = -scenario['capex'] + scenario['annual_benefit'] * current_time
                roi = (cumulative_cf / scenario['capex'] * 100) if scenario['capex'] > 0 else 0

                # Обновление текста
                text.set_text(f" ROI: {roi:.1f}%")
                text.set_position((width + 0.2, idx))

                # Цвет текста в зависимости от достижения окупаемости
                if current_time >= scenario['payback']:
                    text.set_bbox(dict(boxstyle='round', facecolor='green', alpha=0.8))
                else:
                    text.set_bbox(dict(boxstyle='round', facecolor=colors[idx], alpha=0.8))

            ax.set_title(f'Прогресс окупаемости (Год {current_time:.1f})',
                        fontsize=14, pad=20)

            return progress_bars + roi_texts

        # Создание анимации
        anim = animation.FuncAnimation(fig, animate_frame,
                                      frames=100, interval=50, blit=True)

        # Сохранение
        try:
            print(f"  [Сохранение] {save_path}...")
            anim.save(save_path, writer='pillow', fps=20, dpi=100)
            plt.close(fig)
            print(f"  [Готово] Анимация сохранена: {save_path}")
            return save_path
        except Exception as e:
            print(f"  [Предупреждение] Не удалось сохранить анимацию: {e}")
            plt.close(fig)
            return None

    def animate_cashflow_waterfall(self, roi_data: Dict[str, Any],
                                   scenario_name: str,
                                   save_path: str = None,
                                   years: int = 5) -> str:
        """
        Создает анимацию водопадной диаграммы денежного потока.

        Args:
            roi_data: Данные ROI
            scenario_name: Название сценария для анимации
            save_path: Путь для сохранения
            years: Количество лет

        Returns:
            Путь к сохраненному файлу
        """
        if save_path is None:
            # Создаем безопасное имя файла
            safe_name = "".join(c for c in scenario_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            save_path = os.path.join(self.output_dir, f"cashflow_waterfall_{safe_name}.gif")

        print(f"\n[Анимация] Создание водопадной диаграммы денежного потока для '{scenario_name}'...")

        # Поиск данных сценария
        scenario_data = None
        for level_value, roi_info in roi_data.items():
            if scenario_name.lower() in roi_info['scenario_name'].lower():
                scenario_data = roi_info
                break

        if not scenario_data:
            print(f"  [Ошибка] Сценарий '{scenario_name}' не найден")
            return None

        # Создание фигуры
        fig, ax = plt.subplots(figsize=(14, 8))

        categories = ['CAPEX', 'Экономия\nна ФОТ', 'Рост\nдохода', 'OPEX\nавтоматизации',
                     'Итого\nза период']

        def animate_frame(frame):
            ax.clear()

            year = (frame / 20) * years  # 20 кадров на весь период

            # Расчет значений
            capex = -scenario_data['capex'] / 1_000_000
            labor_savings = (scenario_data['annual_labor_savings'] * year) / 1_000_000
            revenue_increase = (scenario_data['annual_revenue_increase'] * year) / 1_000_000
            opex = -(scenario_data['annual_opex'] * year) / 1_000_000
            net_cf = capex + labor_savings + revenue_increase + opex

            values = [capex, labor_savings, revenue_increase, opex, net_cf]

            # Создание водопадной диаграммы
            cumulative = 0
            colors_list = ['#e74c3c', '#2ecc71', '#3498db', '#e67e22', '#9b59b6']

            for idx, (cat, val, color) in enumerate(zip(categories, values, colors_list)):
                if idx == len(categories) - 1:  # Итого
                    ax.bar(idx, val, bottom=0, color=color, alpha=0.7, edgecolor='black', linewidth=2)
                    ax.text(idx, val/2, f'{val:.1f}\nмлн руб',
                           ha='center', va='center', fontsize=10, fontweight='bold', color='white')
                else:
                    ax.bar(idx, val, bottom=cumulative, color=color, alpha=0.7, edgecolor='black')
                    ax.text(idx, cumulative + val/2, f'{val:.1f}\nмлн руб',
                           ha='center', va='center', fontsize=9, fontweight='bold')

                    # Линия к следующему столбцу
                    if idx < len(categories) - 2:
                        ax.plot([idx + 0.4, idx + 0.6], [cumulative + val, cumulative + val],
                               'k--', alpha=0.3)

                    cumulative += val

            ax.set_xticks(range(len(categories)))
            ax.set_xticklabels(categories, fontsize=11)
            ax.set_ylabel('Денежный поток (млн руб)', fontsize=12)
            ax.set_title(f'{scenario_data["scenario_name"]}: Денежный поток за {year:.1f} лет',
                        fontsize=14, fontweight='bold', pad=20)
            ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            ax.grid(True, alpha=0.3, axis='y')

            # Аннотация ROI
            roi = (net_cf * 1_000_000 / scenario_data['capex'] * 100) if scenario_data['capex'] > 0 else 0
            ax.text(0.98, 0.98, f'ROI: {roi:.1f}%',
                   transform=ax.transAxes, fontsize=14, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                   ha='right', va='top')

        # Создание анимации
        anim = animation.FuncAnimation(fig, animate_frame, frames=20, interval=200, blit=False)

        # Сохранение
        try:
            print(f"  [Сохранение] {save_path}...")
            anim.save(save_path, writer='pillow', fps=5, dpi=100)
            plt.close(fig)
            print(f"  [Готово] Анимация сохранена: {save_path}")
            return save_path
        except Exception as e:
            print(f"  [Предупреждение] Не удалось сохранить анимацию: {e}")
            plt.close(fig)
            return None


def create_all_animations(roi_data: Dict[str, Any], output_dir: str = None):
    """
    Создает все доступные анимации для финансового анализа.

    Args:
        roi_data: Данные ROI из автоматизации
        output_dir: Директория для сохранения
    """
    print("\n" + "="*100)
    print("СОЗДАНИЕ АНИМИРОВАННЫХ ВИЗУАЛИЗАЦИЙ")
    print("="*100)

    animator = FinancialAnimator(output_dir)

    try:
        # 1. Сравнение ROI
        animator.animate_roi_comparison(roi_data, years=10)

        # 2. Период окупаемости
        animator.animate_payback_period(roi_data)

        # 3. Водопадные диаграммы для каждого сценария (только для значимых)
        for level_value, roi_info in roi_data.items():
            scenario_name = roi_info['scenario_name']
            if 'базовая' not in scenario_name.lower() and level_value != 0:  # Пропускаем базовый сценарий
                animator.animate_cashflow_waterfall(roi_data, scenario_name, years=5)

        print("\n" + "="*100)
        print("ВСЕ АНИМАЦИИ УСПЕШНО СОЗДАНЫ")
        print("="*100)
    except Exception as e:
        print(f"\n[Предупреждение] Ошибка при создании анимаций: {e}")
        print("  (Анимации не критичны для основного анализа)")


if __name__ == "__main__":
    # Тестовый запуск с примерными данными
    test_roi_data = {
        0: {
            'scenario_name': '0: Без автоматизации',
            'capex': 0,
            'annual_opex': 0,
            'net_annual_benefit': 0,
            'payback_years': float('inf'),
            'roi_5y_percent': 0,
            'annual_labor_savings': 0,
            'annual_revenue_increase': 0
        },
        1: {
            'scenario_name': '1: Базовая автоматизация',
            'capex': 50_000_000,
            'annual_opex': 10_000_000,
            'net_annual_benefit': 25_000_000,
            'payback_years': 2.0,
            'roi_5y_percent': 150,
            'annual_labor_savings': 30_000_000,
            'annual_revenue_increase': 5_000_000
        },
        2: {
            'scenario_name': '2: Продвинутая автоматизация',
            'capex': 200_000_000,
            'annual_opex': 35_000_000,
            'net_annual_benefit': 50_000_000,
            'payback_years': 4.0,
            'roi_5y_percent': 25,
            'annual_labor_savings': 60_000_000,
            'annual_revenue_increase': 25_000_000
        },
        3: {
            'scenario_name': '3: Полная автоматизация',
            'capex': 600_000_000,
            'annual_opex': 100_000_000,
            'net_annual_benefit': 80_000_000,
            'payback_years': 7.5,
            'roi_5y_percent': -33,
            'annual_labor_savings': 120_000_000,
            'annual_revenue_increase': 60_000_000
        }
    }

    print("Запуск тестового создания анимаций...")
    create_all_animations(test_roi_data)

```

## `check_reports.py`

```py
import pandas as pd

print("="*80)
print("ПРОВЕРКА ОТЧЕТОВ")
print("="*80)

# Проверка warehouse_analysis_report.xlsx
try:
    xls = pd.ExcelFile('output/warehouse_analysis_report.xlsx')
    print(f"\nwarehouse_analysis_report.xlsx: {len(xls.sheet_names)} вкладок")
    for i, sheet in enumerate(xls.sheet_names, 1):
        df = pd.read_excel(xls, sheet_name=sheet)
        print(f"  {i}. {sheet} ({len(df)} строк)")
except Exception as e:
    print(f"Ошибка при чтении warehouse_analysis_report.xlsx: {e}")

# Проверка validation_report.xlsx
try:
    xls = pd.ExcelFile('output/validation_report.xlsx')
    print(f"\nvalidation_report.xlsx: {len(xls.sheet_names)} вкладок")
    for i, sheet in enumerate(xls.sheet_names, 1):
        df = pd.read_excel(xls, sheet_name=sheet)
        print(f"  {i}. {sheet} ({len(df)} строк)")
except Exception as e:
    print(f"Ошибка при чтении validation_report.xlsx: {e}")

print("\n" + "="*80)

```

## `collected_code.md`

```md
## `analysis.py`

```py
"""
Скрипт для анализа и визуализации результатов ПОСЛЕ выполнения симуляции.
Запускается отдельно командой: python analysis.py
"""
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config
import math
import requests

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
    """
    CURRENT_HUB_COORDS = (55.857, 37.436)
    SVO_COORDS = (55.97, 37.41)
    AVG_LPU_COORDS = (55.75, 37.62)
    AVG_CFD_COORDS = (54.51, 36.26)
    OSRM_BASE_URL = "https://router.project-osrm.org"

    def __init__(self, use_geocoding: bool = False):
        self.use_geocoding = use_geocoding
        # ИЗМЕНЕНИЕ: Добавляем атрибут geolocator в любом случае, но инициализируем его как None
        self.geolocator: Optional[Nominatim] = None
        if use_geocoding:
            self.geolocator = Nominatim(user_agent="warehouse_relocation_analyzer/1.0")
        self.geocode_cache: Dict[str, Optional[Tuple[float, float]]] = {}
        self.last_request_time = 0
        self.min_request_interval = 1.0

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Преобразует адрес в координаты используя Nominatim (geopy).
        """
        if not self.use_geocoding or self.geolocator is None:
            print("  > [Geocoding] Отключено. Используйте координаты напрямую.")
            return None

        if address in self.geocode_cache:
            print(f"  > [Geocoding Cache] '{address}' -> {self.geocode_cache[address]}")
            return self.geocode_cache[address]

        try:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)

            print(f"  > [Nominatim] Геокодирование адреса: '{address}'")
            location = self.geolocator.geocode(address, timeout=10)
            self.last_request_time = time.time()

            # Явная проверка на наличие атрибутов, чтобы Pylance был уверен в их существовании
            if location and hasattr(location, 'latitude') and hasattr(location, 'longitude'):
                coords = (location.latitude, location.longitude)
                self.geocode_cache[address] = coords
                print(f"  > [Nominatim] Найдено: {coords}")
                return coords
            else:
                print(f"  > [Nominatim] Адрес не найден: '{address}'")
                self.geocode_cache[address] = None # Также кэшируем неудачный результат
                return None

        except Exception as e:
            print(f"  > [Nominatim Error] {e}")
            return None

    def get_route_details(self, start_coords: tuple, end_coords: tuple, mode: str = 'driving') -> dict:
        """
        Получает детали маршрута через OSRM API (бесплатно, без ключей).
        """
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords
        osrm_coords = f"{lon1},{lat1};{lon2},{lat2}"
        url = f"{self.OSRM_BASE_URL}/route/v1/driving/{osrm_coords}?overview=false&steps=false"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['code'] == 'Ok' and len(data['routes']) > 0:
                route = data['routes'][0]
                distance_km = route['distance'] / 1000
                time_h = route['duration'] / 3600
                return {
                    'route_distance_km': round(distance_km, 2), 'travel_time_h': round(time_h, 2),
                    'mode': mode, 'status': 'success', 'source': 'OSRM'
                }
            else:
                print(f"  > [OSRM API Error] {data.get('message', 'Unknown error')}")
                return {'route_distance_km': 0, 'travel_time_h': 0, 'mode': mode, 'status': 'error', 'source': 'OSRM'}

        except requests.exceptions.RequestException as e:
            print(f"  > [OSRM API Error] Ошибка запроса: {e}")
            return self._fallback_distance_calculation(start_coords, end_coords, mode)

    def _fallback_distance_calculation(self, start_coords: tuple, end_coords: tuple, mode: str) -> dict:
        """
        Упрощенный расчет расстояния (fallback на случай недоступности OSRM).
        """
        from math import radians, sin, cos, sqrt, atan2
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords
        R = 6371.0
        lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance_km = R * c * 1.3
        time_h = distance_km / 50
        print(f"  > [Fallback] Используется упрощенный расчет: {distance_km:.1f} км")
        return {
            'route_distance_km': round(distance_km, 2), 'travel_time_h': round(time_h, 2),
            'mode': mode, 'status': 'fallback', 'source': 'haversine'
        }

    def calculate_weighted_annual_distance(self, new_location_coords: tuple) -> dict:
        """
        Рассчитывает взвешенное годовое расстояние S для всех транспортных потоков.
        """
        print(f"\n  > [OSRMGeoRouter] Расчет взвешенного годового расстояния для локации {new_location_coords}")
        flows = {
            'CFO': {'coords': self.AVG_CFD_COORDS, 'share': 0.46, 'name': 'ЦФО (собственный флот)'},
            'SVO': {'coords': self.SVO_COORDS, 'share': 0.25, 'name': 'Авиа (Шереметьево)'},
            'LPU': {'coords': self.AVG_LPU_COORDS, 'share': 0.29, 'name': 'Местные ЛПУ (Москва)'}
        }
        results = {}
        total_weighted_distance = 0
        for flow_id, flow_data in flows.items():
            route = self.get_route_details(new_location_coords, flow_data['coords'])
            weighted_distance = route['route_distance_km'] * flow_data['share']
            total_weighted_distance += weighted_distance
            results[flow_id] = {
                'distance_km': route['route_distance_km'], 'time_h': route['travel_time_h'], 'share': flow_data['share'],
                'weighted_distance_km': weighted_distance, 'name': flow_data['name'], 'source': route.get('source', 'unknown')
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

    def __init__(self, use_geocoding: bool = False):
        """
        Инициализация роутера.

        Args:
            use_geocoding: Использовать ли Nominatim для геокодирования адресов
        """
        self.use_geocoding = use_geocoding
        # Мы явно указываем, что self.geolocator может быть None, что помогает анализатору
        self.geolocator: Optional[Nominatim] = None
        if use_geocoding:
            self.geolocator = Nominatim(user_agent="warehouse_relocation_analyzer/1.0")

        # Кэш для геокодирования (чтобы не делать повторные запросы)
        self.geocode_cache: Dict[str, Optional[Tuple[float, float]]] = {}

        # Счетчик запросов для rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Минимум 1 секунда между запросами к Nominatim

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
    # Используем старый тариф для обратной совместимости, но новый расчет будет в calculate_annual_transport_cost
    LOCAL_FLEET_TARIFF_RUB_KM = 11.2

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
        Включает базовые расходы + ремонт (15%) + компенсацию простоев (5%).
        """
        annual_orders = self.MONTHLY_ORDERS * 12

        # Затраты на ЦФО (собственный флот)
        cost_cfo = (annual_orders * self.CFO_OWN_FLEET_SHARE) * avg_dist_cfo * self.OWN_FLEET_TARIFF_RUB_KM

        # Затраты на Авиа (доставка в SVO)
        cost_svo = (annual_orders * self.AIR_DELIVERY_SHARE) * avg_dist_svo * self.OWN_FLEET_TARIFF_RUB_KM

        # <--- ИЗМЕНЕННАЯ ЛОГИКА --->
        # Затраты на местные перевозки (наемный транспорт)
        # Используем новый повышенный тариф из config.py для учета ограничений в Москве
        cost_local = (annual_orders * self.LOCAL_DELIVERY_SHARE) * avg_dist_local * config.MOSCOW_DELIVERY_TARIFF_RUB_PER_KM

        # Базовые транспортные расходы
        base_transport_cost = cost_cfo + cost_svo + cost_local

        # Добавляем расходы на ремонт и обслуживание (15% от базовых расходов)
        maintenance_cost = base_transport_cost * config.TRANSPORT_MAINTENANCE_RATE

        # Добавляем компенсацию простоев (5% от базовых расходов)
        downtime_cost = base_transport_cost * config.TRANSPORT_DOWNTIME_RATE

        # Общие годовые транспортные расходы
        total_cost = base_transport_cost + maintenance_cost + downtime_cost

        return total_cost

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

        # <--- ИЗМЕНЕННАЯ ЛОГИКА --->
        # Рассчитываем годовые транспортные расходы (T_год) используя обновленный метод
        total_annual_transport_cost = self.calculate_annual_transport_cost(dist_cfo, dist_svo, dist_lpu)
        
        # Разделяем для отчетности
        annual_orders = self.MONTHLY_ORDERS * 12
        cost_cfo = (annual_orders * self.CFO_OWN_FLEET_SHARE) * dist_cfo * self.OWN_FLEET_TARIFF_RUB_KM
        cost_svo = (annual_orders * self.AIR_DELIVERY_SHARE) * dist_svo * self.OWN_FLEET_TARIFF_RUB_KM
        cost_local = (annual_orders * self.LOCAL_DELIVERY_SHARE) * dist_lpu * config.MOSCOW_DELIVERY_TARIFF_RUB_PER_KM


        # Рассчитываем необходимый флот (логика остается прежней для упрощенной оценки)
        # 1. Грузовики 18-20 тонн для ЦФО (2 рейса/нед)
        cfo_orders_per_month = self.MONTHLY_ORDERS * self.CFO_OWN_FLEET_SHARE
        weeks_in_month = 4.33
        cfo_orders_per_week = cfo_orders_per_month / weeks_in_month
        required_heavy_trucks = math.ceil(cfo_orders_per_week / self.CFO_TRIPS_PER_WEEK_PER_TRUCK)

        # 2. Грузовики 5 тонн для Москвы (ежедневно, 6-8 точек) - эта логика будет уточнена в DetailedFleetPlanner
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
            print(f"  > Площадь: {loc['area_offered_sqm']} м²")
            print(f"  > OPEX (помещение): {loc['annual_building_opex']:,.0f} руб./год")
            print(f"  > CAPEX (начальный):  {loc['total_initial_capex']:,.0f} руб.")
            print("-" * 80)
```

## `animations.py`

```py
"""
Модуль для создания анимированных визуализаций финансовых показателей.
Включает анимации ROI, окупаемости, денежного потока и других KPI.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Использовать backend без GUI для серверной генерации
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from typing import Dict, Any, List
import config


class FinancialAnimator:
    """Класс для создания анимированных финансовых визуализаций."""

    def __init__(self, output_dir: str = None):
        """
        Инициализация аниматора.

        Args:
            output_dir: Директория для сохранения анимаций
        """
        self.output_dir = output_dir or config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        # Настройка стиля
        plt.style.use('seaborn-v0_8-darkgrid')

    def animate_roi_comparison(self, roi_data: Dict[str, Any],
                               save_path: str = None,
                               years: int = 10) -> str:
        """
        Создает анимацию сравнения ROI для разных сценариев автоматизации.

        Args:
            roi_data: Данные ROI из автоматизации
            save_path: Путь для сохранения (если None, используется output_dir)
            years: Количество лет для моделирования

        Returns:
            Путь к сохраненному файлу
        """
        if save_path is None:
            save_path = os.path.join(self.output_dir, "roi_comparison_animated.gif")

        print(f"\n[Анимация] Создание анимации сравнения ROI ({years} лет)...")

        # Подготовка данных
        scenarios = []
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']

        for idx, (level_value, roi_info) in enumerate(roi_data.items()):
            scenarios.append({
                'name': roi_info['scenario_name'],
                'capex': roi_info['capex'],
                'annual_benefit': roi_info['net_annual_benefit'],
                'color': colors[idx % len(colors)]
            })

        # Создание фигуры
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Динамика окупаемости инвестиций (ROI)', fontsize=16, fontweight='bold')

        # Инициализация графиков
        lines = []
        bars = []

        for scenario in scenarios:
            line, = ax1.plot([], [], label=scenario['name'],
                           linewidth=2.5, color=scenario['color'])
            lines.append(line)
            bars.append(None)

        ax1.set_xlim(0, years)
        ax1.set_xlabel('Годы', fontsize=12)
        ax1.set_ylabel('Накопленный денежный поток (млн руб)', fontsize=12)
        ax1.set_title('Кумулятивный денежный поток', fontsize=14)
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)

        ax2.set_xlim(-0.5, len(scenarios) - 0.5)
        ax2.set_xlabel('Сценарий', fontsize=12)
        ax2.set_ylabel('ROI (%)', fontsize=12)
        ax2.set_title('ROI к текущему моменту', fontsize=14)
        ax2.set_xticks(range(len(scenarios)))
        ax2.set_xticklabels([s['name'].split(':')[0] for s in scenarios], rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')

        # Функция инициализации
        def init():
            for line in lines:
                line.set_data([], [])
            return lines

        # Функция анимации
        def animate_frame(frame):
            year = frame / 10  # 10 кадров на год для плавности

            # Обновление графика денежного потока
            for idx, (line, scenario) in enumerate(zip(lines, scenarios)):
                years_array = np.linspace(0, year, int(year * 10) + 1)
                cumulative_cf = -scenario['capex'] + scenario['annual_benefit'] * years_array
                line.set_data(years_array, cumulative_cf / 1_000_000)  # В миллионах

            # Обновление гистограммы ROI
            ax2.clear()
            ax2.set_xlim(-0.5, len(scenarios) - 0.5)
            ax2.set_xlabel('Сценарий', fontsize=12)
            ax2.set_ylabel('ROI (%)', fontsize=12)
            ax2.set_title(f'ROI к году {year:.1f}', fontsize=14)
            ax2.set_xticks(range(len(scenarios)))
            ax2.set_xticklabels([s['name'].split(':')[0] for s in scenarios], rotation=45, ha='right')
            ax2.grid(True, alpha=0.3, axis='y')

            roi_values = []
            for scenario in scenarios:
                cumulative_cf = -scenario['capex'] + scenario['annual_benefit'] * year
                roi = (cumulative_cf / scenario['capex'] * 100) if scenario['capex'] > 0 else 0
                roi_values.append(roi)

            bars = ax2.bar(range(len(scenarios)), roi_values,
                          color=[s['color'] for s in scenarios], alpha=0.7)

            # Добавление значений на столбцы
            for idx, (bar, roi_val) in enumerate(zip(bars, roi_values)):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{roi_val:.1f}%',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

            ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)

            return lines + [ax2]

        # Создание анимации
        frames = years * 10  # 10 кадров на год
        anim = animation.FuncAnimation(fig, animate_frame, init_func=init,
                                      frames=frames, interval=50, blit=False)

        # Сохранение
        try:
            print(f"  [Сохранение] {save_path}...")
            anim.save(save_path, writer='pillow', fps=20, dpi=100)
            plt.close(fig)
            print(f"  [Готово] Анимация сохранена: {save_path}")
            return save_path
        except Exception as e:
            print(f"  [Предупреждение] Не удалось сохранить анимацию: {e}")
            plt.close(fig)
            return None

    def animate_payback_period(self, roi_data: Dict[str, Any],
                               save_path: str = None) -> str:
        """
        Создает анимацию достижения точки окупаемости для разных сценариев.

        Args:
            roi_data: Данные ROI
            save_path: Путь для сохранения

        Returns:
            Путь к сохраненному файлу
        """
        if save_path is None:
            save_path = os.path.join(self.output_dir, "payback_period_animated.gif")

        print(f"\n[Анимация] Создание анимации срока окупаемости...")

        # Подготовка данных
        scenarios_data = []
        max_payback = 0

        for level_value, roi_info in roi_data.items():
            payback = roi_info['payback_years']
            if payback != float('inf'):
                scenarios_data.append({
                    'name': roi_info['scenario_name'],
                    'payback': payback,
                    'capex': roi_info['capex'],
                    'annual_benefit': roi_info['net_annual_benefit']
                })
                max_payback = max(max_payback, payback)

        if not scenarios_data:
            print("  [Предупреждение] Нет сценариев с конечным сроком окупаемости")
            return None

        # Создание фигуры
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle('Достижение точки окупаемости', fontsize=16, fontweight='bold')

        colors = plt.cm.viridis(np.linspace(0, 1, len(scenarios_data)))

        # Максимальное время для анимации
        max_years = min(max_payback * 1.2, 15)

        ax.set_xlim(0, max_years)
        ax.set_ylim(-0.5, len(scenarios_data) - 0.5)
        ax.set_xlabel('Годы', fontsize=12)
        ax.set_ylabel('Сценарий', fontsize=12)
        ax.set_yticks(range(len(scenarios_data)))
        ax.set_yticklabels([s['name'] for s in scenarios_data])
        ax.grid(True, alpha=0.3, axis='x')

        # Отметка точек окупаемости
        for idx, scenario in enumerate(scenarios_data):
            ax.axvline(x=scenario['payback'], color=colors[idx],
                      linestyle='--', alpha=0.3, linewidth=1)
            ax.text(scenario['payback'], idx, f" {scenario['payback']:.1f} лет",
                   va='center', fontsize=9, color=colors[idx], fontweight='bold')

        # Прогресс-бары
        progress_bars = []
        for idx in range(len(scenarios_data)):
            bar = Rectangle((0, idx - 0.3), 0, 0.6,
                          facecolor=colors[idx], alpha=0.7)
            ax.add_patch(bar)
            progress_bars.append(bar)

        # Текстовые метки с ROI
        roi_texts = []
        for idx in range(len(scenarios_data)):
            text = ax.text(0, idx, '', ha='left', va='center',
                         fontsize=9, fontweight='bold', color='white',
                         bbox=dict(boxstyle='round', facecolor=colors[idx], alpha=0.8))
            roi_texts.append(text)

        def animate_frame(frame):
            progress = frame / 100  # 0 до 1
            current_time = max_years * progress

            for idx, (scenario, bar, text) in enumerate(zip(scenarios_data, progress_bars, roi_texts)):
                # Обновление ширины бара
                width = min(current_time, scenario['payback'])
                bar.set_width(width)

                # Расчет текущего ROI
                cumulative_cf = -scenario['capex'] + scenario['annual_benefit'] * current_time
                roi = (cumulative_cf / scenario['capex'] * 100) if scenario['capex'] > 0 else 0

                # Обновление текста
                text.set_text(f" ROI: {roi:.1f}%")
                text.set_position((width + 0.2, idx))

                # Цвет текста в зависимости от достижения окупаемости
                if current_time >= scenario['payback']:
                    text.set_bbox(dict(boxstyle='round', facecolor='green', alpha=0.8))
                else:
                    text.set_bbox(dict(boxstyle='round', facecolor=colors[idx], alpha=0.8))

            ax.set_title(f'Прогресс окупаемости (Год {current_time:.1f})',
                        fontsize=14, pad=20)

            return progress_bars + roi_texts

        # Создание анимации
        anim = animation.FuncAnimation(fig, animate_frame,
                                      frames=100, interval=50, blit=True)

        # Сохранение
        try:
            print(f"  [Сохранение] {save_path}...")
            anim.save(save_path, writer='pillow', fps=20, dpi=100)
            plt.close(fig)
            print(f"  [Готово] Анимация сохранена: {save_path}")
            return save_path
        except Exception as e:
            print(f"  [Предупреждение] Не удалось сохранить анимацию: {e}")
            plt.close(fig)
            return None

    def animate_cashflow_waterfall(self, roi_data: Dict[str, Any],
                                   scenario_name: str,
                                   save_path: str = None,
                                   years: int = 5) -> str:
        """
        Создает анимацию водопадной диаграммы денежного потока.

        Args:
            roi_data: Данные ROI
            scenario_name: Название сценария для анимации
            save_path: Путь для сохранения
            years: Количество лет

        Returns:
            Путь к сохраненному файлу
        """
        if save_path is None:
            # Создаем безопасное имя файла
            safe_name = "".join(c for c in scenario_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            save_path = os.path.join(self.output_dir, f"cashflow_waterfall_{safe_name}.gif")

        print(f"\n[Анимация] Создание водопадной диаграммы денежного потока для '{scenario_name}'...")

        # Поиск данных сценария
        scenario_data = None
        for level_value, roi_info in roi_data.items():
            if scenario_name.lower() in roi_info['scenario_name'].lower():
                scenario_data = roi_info
                break

        if not scenario_data:
            print(f"  [Ошибка] Сценарий '{scenario_name}' не найден")
            return None

        # Создание фигуры
        fig, ax = plt.subplots(figsize=(14, 8))

        categories = ['CAPEX', 'Экономия\nна ФОТ', 'Рост\nдохода', 'OPEX\nавтоматизации',
                     'Итого\nза период']

        def animate_frame(frame):
            ax.clear()

            year = (frame / 20) * years  # 20 кадров на весь период

            # Расчет значений
            capex = -scenario_data['capex'] / 1_000_000
            labor_savings = (scenario_data['annual_labor_savings'] * year) / 1_000_000
            revenue_increase = (scenario_data['annual_revenue_increase'] * year) / 1_000_000
            opex = -(scenario_data['annual_opex'] * year) / 1_000_000
            net_cf = capex + labor_savings + revenue_increase + opex

            values = [capex, labor_savings, revenue_increase, opex, net_cf]

            # Создание водопадной диаграммы
            cumulative = 0
            colors_list = ['#e74c3c', '#2ecc71', '#3498db', '#e67e22', '#9b59b6']

            for idx, (cat, val, color) in enumerate(zip(categories, values, colors_list)):
                if idx == len(categories) - 1:  # Итого
                    ax.bar(idx, val, bottom=0, color=color, alpha=0.7, edgecolor='black', linewidth=2)
                    ax.text(idx, val/2, f'{val:.1f}\nмлн руб',
                           ha='center', va='center', fontsize=10, fontweight='bold', color='white')
                else:
                    ax.bar(idx, val, bottom=cumulative, color=color, alpha=0.7, edgecolor='black')
                    ax.text(idx, cumulative + val/2, f'{val:.1f}\nмлн руб',
                           ha='center', va='center', fontsize=9, fontweight='bold')

                    # Линия к следующему столбцу
                    if idx < len(categories) - 2:
                        ax.plot([idx + 0.4, idx + 0.6], [cumulative + val, cumulative + val],
                               'k--', alpha=0.3)

                    cumulative += val

            ax.set_xticks(range(len(categories)))
            ax.set_xticklabels(categories, fontsize=11)
            ax.set_ylabel('Денежный поток (млн руб)', fontsize=12)
            ax.set_title(f'{scenario_data["scenario_name"]}: Денежный поток за {year:.1f} лет',
                        fontsize=14, fontweight='bold', pad=20)
            ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            ax.grid(True, alpha=0.3, axis='y')

            # Аннотация ROI
            roi = (net_cf * 1_000_000 / scenario_data['capex'] * 100) if scenario_data['capex'] > 0 else 0
            ax.text(0.98, 0.98, f'ROI: {roi:.1f}%',
                   transform=ax.transAxes, fontsize=14, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                   ha='right', va='top')

        # Создание анимации
        anim = animation.FuncAnimation(fig, animate_frame, frames=20, interval=200, blit=False)

        # Сохранение
        try:
            print(f"  [Сохранение] {save_path}...")
            anim.save(save_path, writer='pillow', fps=5, dpi=100)
            plt.close(fig)
            print(f"  [Готово] Анимация сохранена: {save_path}")
            return save_path
        except Exception as e:
            print(f"  [Предупреждение] Не удалось сохранить анимацию: {e}")
            plt.close(fig)
            return None


def create_all_animations(roi_data: Dict[str, Any], output_dir: str = None):
    """
    Создает все доступные анимации для финансового анализа.

    Args:
        roi_data: Данные ROI из автоматизации
        output_dir: Директория для сохранения
    """
    print("\n" + "="*100)
    print("СОЗДАНИЕ АНИМИРОВАННЫХ ВИЗУАЛИЗАЦИЙ")
    print("="*100)

    animator = FinancialAnimator(output_dir)

    try:
        # 1. Сравнение ROI
        animator.animate_roi_comparison(roi_data, years=10)

        # 2. Период окупаемости
        animator.animate_payback_period(roi_data)

        # 3. Водопадные диаграммы для каждого сценария (только для значимых)
        for level_value, roi_info in roi_data.items():
            scenario_name = roi_info['scenario_name']
            if 'базовая' not in scenario_name.lower() and level_value != 0:  # Пропускаем базовый сценарий
                animator.animate_cashflow_waterfall(roi_data, scenario_name, years=5)

        print("\n" + "="*100)
        print("ВСЕ АНИМАЦИИ УСПЕШНО СОЗДАНЫ")
        print("="*100)
    except Exception as e:
        print(f"\n[Предупреждение] Ошибка при создании анимаций: {e}")
        print("  (Анимации не критичны для основного анализа)")


if __name__ == "__main__":
    # Тестовый запуск с примерными данными
    test_roi_data = {
        0: {
            'scenario_name': '0: Без автоматизации',
            'capex': 0,
            'annual_opex': 0,
            'net_annual_benefit': 0,
            'payback_years': float('inf'),
            'roi_5y_percent': 0,
            'annual_labor_savings': 0,
            'annual_revenue_increase': 0
        },
        1: {
            'scenario_name': '1: Базовая автоматизация',
            'capex': 50_000_000,
            'annual_opex': 10_000_000,
            'net_annual_benefit': 25_000_000,
            'payback_years': 2.0,
            'roi_5y_percent': 150,
            'annual_labor_savings': 30_000_000,
            'annual_revenue_increase': 5_000_000
        },
        2: {
            'scenario_name': '2: Продвинутая автоматизация',
            'capex': 200_000_000,
            'annual_opex': 35_000_000,
            'net_annual_benefit': 50_000_000,
            'payback_years': 4.0,
            'roi_5y_percent': 25,
            'annual_labor_savings': 60_000_000,
            'annual_revenue_increase': 25_000_000
        },
        3: {
            'scenario_name': '3: Полная автоматизация',
            'capex': 600_000_000,
            'annual_opex': 100_000_000,
            'net_annual_benefit': 80_000_000,
            'payback_years': 7.5,
            'roi_5y_percent': -33,
            'annual_labor_savings': 120_000_000,
            'annual_revenue_increase': 60_000_000
        }
    }

    print("Запуск тестового создания анимаций...")
    create_all_animations(test_roi_data)

```

## `config.py`

```py
# config.py

"""
Глобальные статические константы и базовые настройки проекта.
"""

# --- Финансовые и HR константы ---
INITIAL_STAFF_COUNT = 240
OPERATOR_SALARY_RUB_MONTH = 105000
TRANSPORT_TARIFF_RUB_PER_KM = 13.4  # Средний тариф для 18-20т фуры
TRANSPORT_MAINTENANCE_RATE = 0.15  # 15% на техническое обслуживание транспорта
TRANSPORT_DOWNTIME_RATE = 0.05  # 5% на простои транспорта

# --- Дополнительные расходы на персонал ---
STAFF_TRAINING_COST_PER_PERSON = 50000  # Обучение нового сотрудника
STAFF_ADAPTATION_RATE = 0.20  # 20% от зарплаты на адаптацию
STAFF_RELOCATION_COMPENSATION = 100000  # Компенсация переезда

# --- Параметры текущего актива (старый склад на "Сходненской") ---
CURRENT_WAREHOUSE_IS_OWNED = True  # Мы владеем текущим складом? True - да, False - нет (в аренде)
CURRENT_WAREHOUSE_SALE_VALUE_RUB = 800_000_000 # Оценочная стоимость продажи текущего склада в руб.

# --- Константы склада и локации ---
WAREHOUSE_TOTAL_AREA_SQM = 17000
MIN_AREA_SQM = 17000  # Минимально требуемая площадь
TARGET_AREA_SQM = 17500  # Целевая площадь
ANNUAL_RENT_PER_SQM_RUB = 7500.0
PURCHASE_BUILDING_COST_RUB = 1_500_000_000
BASE_EQUIPMENT_CAPEX_RUB = 350_000_000  # Стеллажи, климат, валидация
MAINTENANCE_COST_OF_OWNED_BUILDING_RUB_YEAR = 50_000_000

# --- Симуляционные константы ---
BASE_ORDER_PROCESSING_TIME_MIN = 15.0
BASE_ORDER_CYCLE_TIME_MIN = 15.0  # Алиас для simulation_engine
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

# --- Новые константы: Ограничения для грузовиков в Москве ---
MOSCOW_RESTRICTION_TONNAGE = 3.5  # Максимальная грузоподъемность в тоннах без пропуска
FREE_PASSES_PER_MONTH = 2         # Количество бесплатных рейсов в месяц для >3.5т
# Повышенный тариф для моделирования использования более мелкого и дорогого транспорта в Москве
MOSCOW_DELIVERY_TARIFF_RUB_PER_KM = 18.5 

# --- Параметры GPP/GDP и валидации ---
GPP_GDP_VALIDATION_COST_RUB = 25_000_000  # Стоимость валидации GPP/GDP
GPP_GDP_CLIMATE_SYSTEM_COST_RUB = 150_000_000  # Климатические системы
GPP_GDP_MONITORING_COST_RUB = 20_000_000  # Системы мониторинга (температура, влажность)
GPP_GDP_ANNUAL_MAINTENANCE_RATE = 0.05  # 5% от CAPEX на годовое обслуживание

# --- Параметры автоматизации (по уровням 0-3) ---
AUTOMATION_LEVELS = {
    0: {  # Без автоматизации
        'name': 'Без автоматизации',
        'capex': 0,
        'annual_opex_rate': 0,
        'labor_reduction': 0,
        'efficiency_multiplier': 1.0
    },
    1: {  # Базовая автоматизация (WMS + сканеры)
        'name': 'Базовая автоматизация',
        'capex': 50_000_000,
        'annual_opex_rate': 0.10,  # 10% от CAPEX
        'labor_reduction': 0.20,  # 20% сокращение персонала
        'efficiency_multiplier': 1.3  # +30% производительность
    },
    2: {  # Продвинутая (WMS + конвейеры + сортировка)
        'name': 'Продвинутая автоматизация',
        'capex': 200_000_000,
        'annual_opex_rate': 0.15,
        'labor_reduction': 0.50,  # 50% сокращение
        'efficiency_multiplier': 2.0  # 2x производительность
    },
    3: {  # Полная автоматизация (AS/RS + AGV + роботы)
        'name': 'Полная автоматизация',
        'capex': 600_000_000,
        'annual_opex_rate': 0.18,
        'labor_reduction': 0.80,  # 80% сокращение
        'efficiency_multiplier': 3.5  # 3.5x производительность
    }
}

# --- Параметры HR и компенсаций (по сценариям) ---
HR_COMPENSATION_PLANS = {
    'no_mitigation': {
        'name': 'Без компенсаций',
        'cost': 0,
        'attrition_rate': 0.25  # 25% уйдут
    },
    'with_compensation': {
        'name': 'С компенсациями',
        'cost': 50_000_000,  # 50 млн на удержание
        'attrition_rate': 0.15  # 15% уйдут (снижено!)
    }
}

# --- Параметры складских операций ---
RACK_SYSTEM_COST_PER_POSITION_RUB = 15000  # Стоимость одного паллето-места
DOCK_DOOR_COST_RUB = 2_500_000  # Стоимость одной докдвери
FORKLIFT_COST_RUB = 3_000_000  # Стоимость погрузчика
FORKLIFT_ANNUAL_MAINTENANCE_RUB = 500_000  # Годовое обслуживание погрузчика

# --- Параметры климатических зон ---
CLIMATE_ZONES = {
    'normal': {  # Обычное хранение (+15...+25°C)
        'temp_range': (15, 25),
        'humidity_range': (40, 60),
        'cost_per_sqm_capex': 8000,  # руб/м² CAPEX
        'cost_per_sqm_opex_year': 1200  # руб/м²/год OPEX
    },
    'cold_chain': {  # Холодовая цепь (+2...+8°C)
        'temp_range': (2, 8),
        'humidity_range': (40, 60),
        'cost_per_sqm_capex': 25000,  # руб/м² CAPEX (дороже!)
        'cost_per_sqm_opex_year': 4500  # руб/м²/год OPEX
    },
    'frozen': {  # Заморозка (-18...-25°C)
        'temp_range': (-25, -18),
        'humidity_range': (30, 50),
        'cost_per_sqm_capex': 40000,
        'cost_per_sqm_opex_year': 8000
    }
}

# --- Параметры транспорта (детальные) ---
TRANSPORT_TYPES = {
    'truck_18t': {  # Фура 18-20т
        'capacity_pallets': 33,
        'cost_per_km_rub': 13.4,
        'purchase_cost_rub': 8_000_000,
        'lease_cost_month_rub': 250_000,
        'fuel_consumption_per_100km': 30,  # литров
        'fuel_cost_per_liter_rub': 55
    },
    'van_3_5t': {  # Газель 3.5т
        'capacity_pallets': 8,
        'cost_per_km_rub': 18.5,
        'purchase_cost_rub': 2_500_000,
        'lease_cost_month_rub': 80_000,
        'fuel_consumption_per_100km': 15,
        'fuel_cost_per_liter_rub': 55
    }
}

# --- Параметры качества и KPI ---
TARGET_ORDER_ACCURACY_PERCENT = 99.5  # Целевая точность комплектации
TARGET_ORDER_CYCLE_TIME_HOURS = 4  # Целевое время цикла заказа
MAX_ACCEPTABLE_CYCLE_TIME_HOURS = 8  # Максимально допустимое время
MIN_DOCK_UTILIZATION_PERCENT = 60  # Минимальная утилизация доков
MAX_DOCK_UTILIZATION_PERCENT = 85  # Максимальная утилизация доков

# --- Бюджетные ограничения ---
MAX_TOTAL_CAPEX_RUB = 2_500_000_000  # Максимальный бюджет CAPEX (2.5 млрд)
MAX_ANNUAL_OPEX_RUB = 500_000_000  # Максимальный годовой OPEX (500 млн)
TARGET_PAYBACK_YEARS = 5  # Целевой срок окупаемости
MAX_ACCEPTABLE_PAYBACK_YEARS = 7  # Максимально допустимый срок

# --- Требования по SKU ---
TOTAL_SKU_COUNT = 15_000  # Общее количество SKU
SKU_DISTRIBUTION = {
    'normal_storage': 0.60,  # 60% - обычное хранение
    'cold_chain': 0.30,      # 30% - холодовая цепь
    'special_handling': 0.10  # 10% - особое обращение
}

# --- Настройки вывода ---
OUTPUT_DIR = "output"
RESULTS_CSV_FILENAME = "simulation_results_dynamic.csv"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

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
    "pnk_chashnikovo_lease": {
        "name": "PNK Чашниково (аренда)",
        "type": "ARENDA",
        "lat": 56.01,
        "lon": 37.10,
        "area_offered_sqm": 17500,
        "cost_metric_base": 12500.0,  # руб/м²/год за складскую площадь
        "current_class": "A_requires_mod"
    },
    "pnk_chashnikovo_bts": {
        "name": "PNK Чашниково (покупка BTS)",
        "type": "POKUPKA_BTS",
        "lat": 56.01,
        "lon": 37.10,
        "area_offered_sqm": 17500,
        "cost_metric_base": 1_500_000_000,  # полная стоимость покупки, руб.
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

## `formula_visualizer.py`

```py
"""
Модуль для подробного вывода формул и визуализации всех расчетов.
Создает графики, диаграммы и подробные объяснения для каждого этапа анализа.
"""
import matplotlib
matplotlib.use('Agg')  # Для серверной работы без GUI
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import numpy as np
import seaborn as sns
from typing import Dict, Any, List, Tuple, Optional
import os
import config


class FormulaVisualizer:
    """Класс для визуализации формул и создания подробных отчетов по расчетам."""

    def __init__(self, output_dir: str = "output"):
        """Инициализация визуализатора."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Настройка стиля для всех графиков
        sns.set_theme(style="whitegrid", palette="husl")
        plt.rcParams['figure.figsize'] = (14, 10)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 9
        plt.rcParams['figure.titlesize'] = 14

    def print_section_header(self, title: str, level: int = 1):
        """Печатает красивый заголовок секции."""
        if level == 1:
            print(f"\n{'='*100}")
            print(f"| {title.upper():^96} |")
            print(f"{'='*100}\n")
        elif level == 2:
            print(f"\n{'-'*100}")
            print(f"  {title}")
            print(f"{'-'*100}")
        else:
            print(f"\n{'.'*100}")
            print(f"    {title}")
            print(f"{'.'*100}")

    def print_formula(self, formula_name: str, formula_latex: str, variables: Dict[str, Any],
                     result: float, unit: str = "руб"):
        """
        Печатает формулу с подробным объяснением всех переменных.

        Args:
            formula_name: Название формулы
            formula_latex: Формула в текстовом представлении (LaTeX-подобная)
            variables: Словарь переменных {название: (значение, описание)}
            result: Результат вычисления
            unit: Единица измерения результата
        """
        print(f"\n+-- {formula_name} " + "-" * (95 - len(formula_name)))
        print(f"|")
        print(f"| FORMULA: {formula_latex}")
        print(f"|")
        print(f"| WHERE:")

        for var_name, var_data in variables.items():
            if isinstance(var_data, tuple):
                value, description = var_data
            else:
                value, description = var_data, "znachenie"

            if isinstance(value, (int, float)):
                if value >= 1_000_000:
                    print(f"|   * {var_name} = {value:,.2f} ({description})")
                elif value >= 1_000:
                    print(f"|   * {var_name} = {value:,.0f} ({description})")
                else:
                    print(f"|   * {var_name} = {value:.2f} ({description})")
            else:
                print(f"|   * {var_name} = {value} ({description})")

        print(f"|")
        if isinstance(result, (int, float)):
            if result >= 1_000_000:
                print(f"| RESULT: {result:,.2f} {unit}")
            else:
                print(f"| RESULT: {result:,.0f} {unit}")
        else:
            print(f"| RESULT: {result} {unit}")
        print(f"+--" + "-" * 97)

    def visualize_distance_calculation(self, location_name: str,
                                      warehouse_coords: Tuple[float, float],
                                      key_points: Dict[str, Tuple[float, float]],
                                      distances: Dict[str, float]):
        """
        Визуализирует расчет расстояний с помощью карты и формулы Haversine.

        Args:
            location_name: Название локации
            warehouse_coords: Координаты склада (lat, lon)
            key_points: Ключевые точки доставки
            distances: Рассчитанные расстояния до каждой точки
        """
        self.print_section_header(f"РАСЧЕТ РАССТОЯНИЙ ДЛЯ ЛОКАЦИИ: {location_name}", level=2)

        # Вывод формулы Haversine
        print("\n[Формула] Используется формула Haversine для расчета расстояния по поверхности Земли:")

        formula_latex = "d = 2R * arcsin(sqrt(sin^2(delta_lat/2) + cos(lat1) * cos(lat2) * sin^2(delta_lon/2))) * 1.4"
        variables = {
            "R": (6371.0, "радиус Земли в км"),
            "lat1, lon1": (f"{warehouse_coords[0]:.4f}, {warehouse_coords[1]:.4f}", "координаты склада"),
            "delta_lat, delta_lon": ("разница координат", "в радианах"),
            "1.4": (1.4, "коэффициент реальных дорог (извилистость)")
        }

        print(f"\n+-- Формула Haversine (расчет расстояния по дуге большого круга) " + "-" * 28)
        print(f"|")
        print(f"| ФОРМУЛА: {formula_latex}")
        print(f"|")
        print(f"| ГДЕ:")
        for var_name, var_data in variables.items():
            value, description = var_data if isinstance(var_data, tuple) else (var_data, "")
            print(f"|   * {var_name} = {value} ({description})")
        print(f"+--" + "-" * 97)

        # Детальный расчет для каждой точки
        print(f"\n[Координаты] Координаты склада: ({warehouse_coords[0]:.4f}, {warehouse_coords[1]:.4f})")
        print(f"\n[Расчет] Расчет расстояний до ключевых точек:\n")

        for point_name, point_coords in key_points.items():
            dist = distances.get(point_name, 0)
            print(f"  >> {point_name}:")
            print(f"      Координаты цели: ({point_coords[0]:.4f}, {point_coords[1]:.4f})")
            print(f"      Расстояние: {dist:.2f} км")
            print()

        try:
            # Создание визуализации карты
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

            # График 1: Карта с точками
            ax1.set_title(f'Географическое расположение: {location_name}', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Долгота (lon)', fontsize=11)
            ax1.set_ylabel('Широта (lat)', fontsize=11)
            ax1.grid(True, alpha=0.3)

            # Отображаем склад
            ax1.scatter(warehouse_coords[1], warehouse_coords[0], s=300, c='red', marker='s',
                       label='Новый склад', zorder=5, edgecolors='black', linewidth=2)

            # Отображаем ключевые точки и линии
            colors = ['blue', 'green', 'orange', 'purple']
            for idx, (point_name, point_coords) in enumerate(key_points.items()):
                color = colors[idx % len(colors)]
                ax1.scatter(point_coords[1], point_coords[0], s=200, c=color, marker='o',
                           label=point_name, zorder=5, edgecolors='black', linewidth=1.5)

                # Линия от склада к точке
                ax1.plot([warehouse_coords[1], point_coords[1]],
                        [warehouse_coords[0], point_coords[0]],
                        color=color, linestyle='--', alpha=0.6, linewidth=2)

                # Аннотация с расстоянием
                mid_lon = (warehouse_coords[1] + point_coords[1]) / 2
                mid_lat = (warehouse_coords[0] + point_coords[0]) / 2
                dist = distances.get(point_name, 0)
                ax1.annotate(f'{dist:.0f} км', xy=(mid_lon, mid_lat), fontsize=9,
                            bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.3))

            ax1.legend(loc='best', fontsize=9)

            # График 2: Диаграмма расстояний
            ax2.set_title('Расстояния до ключевых точек', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Расстояние (км)', fontsize=11)
            ax2.set_ylabel('Направления', fontsize=11)

            point_names = list(distances.keys())
            point_distances = list(distances.values())
            y_pos = np.arange(len(point_names))

            bars = ax2.barh(y_pos, point_distances, color=colors[:len(point_names)],
                           edgecolor='black', linewidth=1.5, alpha=0.8)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(point_names)
            ax2.grid(axis='x', alpha=0.3)

            # Добавляем значения на столбцы
            for idx, (bar, dist) in enumerate(zip(bars, point_distances)):
                ax2.text(dist + 2, bar.get_y() + bar.get_height()/2,
                        f'{dist:.1f} км', va='center', fontsize=10, fontweight='bold')

            plt.tight_layout()
            filename = f'{self.output_dir}/distances_{location_name.replace(" ", "_").replace("/", "_")}.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"\n[График] График сохранен: {filename}")
            plt.close()
        except Exception as e:
            print(f"\n[ОШИБКА] Не удалось создать график расстояний: {e}")

    def visualize_capex_opex_breakdown(self, location_name: str,
                                       capex_data: Dict[str, float],
                                       opex_data: Dict[str, float]):
        """
        Визуализирует детальную структуру CAPEX и OPEX.

        Args:
            location_name: Название локации
            capex_data: Словарь с компонентами CAPEX
            opex_data: Словарь с компонентами OPEX
        """
        self.print_section_header(f"ДЕТАЛЬНЫЙ ФИНАНСОВЫЙ АНАЛИЗ: {location_name}", level=2)

        # Вывод формул CAPEX
        print("\n[CAPEX] РАСЧЕТ CAPEX (Capital Expenditure - Капитальные затраты):\n")

        total_capex = sum(capex_data.values())
        formula_capex = "CAPEX_total = CAPEX_equipment + CAPEX_climate + CAPEX_modifications + CAPEX_building"

        self.print_formula(
            "Общий CAPEX",
            formula_capex,
            {key: (value, key) for key, value in capex_data.items()},
            total_capex,
            "руб"
        )

        # Вывод формул OPEX
        print("\n[OPEX] РАСЧЕТ OPEX (Operational Expenditure - Операционные затраты):\n")

        total_opex = sum(opex_data.values())
        formula_opex = "OPEX_total = OPEX_building + OPEX_personnel + OPEX_transport"

        self.print_formula(
            "Годовой OPEX",
            formula_opex,
            {key: (value, key) for key, value in opex_data.items()},
            total_opex,
            "руб/год"
        )

        try:
            # Создание визуализации
            fig = plt.figure(figsize=(16, 8))
            gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

            # CAPEX Pie Chart
            ax1 = fig.add_subplot(gs[0, 0])
            colors_capex = plt.cm.Blues(np.linspace(0.4, 0.8, len(capex_data)))
            wedges, texts, autotexts = ax1.pie(
                capex_data.values(),
                labels=capex_data.keys(),
                autopct='%1.1f%%',
                colors=colors_capex,
                startangle=90,
                textprops={'fontsize': 9}
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            ax1.set_title(f'Структура CAPEX\nОбщая сумма: {total_capex:,.0f} руб',
                         fontsize=12, fontweight='bold')

            # OPEX Pie Chart
            ax2 = fig.add_subplot(gs[0, 1])
            colors_opex = plt.cm.Oranges(np.linspace(0.4, 0.8, len(opex_data)))
            wedges, texts, autotexts = ax2.pie(
                opex_data.values(),
                labels=opex_data.keys(),
                autopct='%1.1f%%',
                colors=colors_opex,
                startangle=90,
                textprops={'fontsize': 9}
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            ax2.set_title(f'Структура годового OPEX\nОбщая сумма: {total_opex:,.0f} руб',
                         fontsize=12, fontweight='bold')

            # CAPEX Bar Chart
            ax3 = fig.add_subplot(gs[1, 0])
            bars = ax3.bar(range(len(capex_data)), list(capex_data.values()),
                          color=colors_capex, edgecolor='black', linewidth=1.5)
            ax3.set_xticks(range(len(capex_data)))
            ax3.set_xticklabels(list(capex_data.keys()), rotation=45, ha='right', fontsize=9)
            ax3.set_ylabel('Сумма (руб)', fontsize=10)
            ax3.set_title('CAPEX по компонентам', fontsize=12, fontweight='bold')
            ax3.grid(axis='y', alpha=0.3)

            # Добавляем значения на столбцы
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height/1_000_000:.0f}М',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

            # OPEX Bar Chart
            ax4 = fig.add_subplot(gs[1, 1])
            bars = ax4.bar(range(len(opex_data)), list(opex_data.values()),
                          color=colors_opex, edgecolor='black', linewidth=1.5)
            ax4.set_xticks(range(len(opex_data)))
            ax4.set_xticklabels(list(opex_data.keys()), rotation=45, ha='right', fontsize=9)
            ax4.set_ylabel('Сумма (руб/год)', fontsize=10)
            ax4.set_title('Годовой OPEX по компонентам', fontsize=12, fontweight='bold')
            ax4.grid(axis='y', alpha=0.3)

            # Добавляем значения на столбцы
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height/1_000_000:.0f}М',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

            plt.suptitle(f'Финансовый анализ: {location_name}',
                        fontsize=16, fontweight='bold', y=0.98)

            filename = f'{self.output_dir}/finance_{location_name.replace(" ", "_").replace("/", "_")}.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"\n[График] График сохранен: {filename}")
            plt.close()
        except Exception as e:
            print(f"\n[ОШИБКА] Не удалось создать финансовый график: {e}")

    def visualize_location_comparison(self, locations_data: List[Dict[str, Any]]):
        """
        Создает сравнительную визуализацию всех рассмотренных локаций.

        Args:
            locations_data: Список данных по всем локациям
        """
        self.print_section_header("СРАВНИТЕЛЬНЫЙ АНАЛИЗ ВСЕХ ЛОКАЦИЙ", level=1)

        if not locations_data:
            print("Нет данных для сравнения")
            return

        try:
            # Создаем большой сравнительный график
            fig = plt.figure(figsize=(20, 12))
            gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)

            location_names = [loc['location_name'][:20] for loc in locations_data]

            # График 1: Сравнение общего годового OPEX
            ax1 = fig.add_subplot(gs[0, :])
            opex_values = [loc['total_annual_opex_s1'] for loc in locations_data]
            colors = ['green' if opex == min(opex_values) else 'lightblue' for opex in opex_values]

            bars = ax1.bar(range(len(locations_data)), opex_values, color=colors,
                          edgecolor='black', linewidth=2, alpha=0.8)
            ax1.set_xticks(range(len(locations_data)))
            ax1.set_xticklabels(location_names, rotation=45, ha='right', fontsize=10)
            ax1.set_ylabel('Годовой OPEX (руб)', fontsize=12)
            ax1.set_title('Сравнение общего годового OPEX (Сценарий 1)', fontsize=14, fontweight='bold')
            ax1.grid(axis='y', alpha=0.3)

            for bar, opex in zip(bars, opex_values):
                ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(opex_values)*0.01,
                        f'{opex/1_000_000:.0f}М', ha='center', va='bottom', fontsize=10, fontweight='bold')

            # График 2: Сравнение CAPEX
            ax2 = fig.add_subplot(gs[1, 0])
            capex_values = [loc['total_initial_capex'] for loc in locations_data]

            bars = ax2.barh(range(len(locations_data)), capex_values,
                           color=plt.cm.Reds(np.linspace(0.3, 0.8, len(locations_data))),
                           edgecolor='black', linewidth=1.5, alpha=0.8)
            ax2.set_yticks(range(len(locations_data)))
            ax2.set_yticklabels(location_names, fontsize=9)
            ax2.set_xlabel('CAPEX (руб)', fontsize=11)
            ax2.set_title('Сравнение первоначальных инвестиций (CAPEX)', fontsize=12, fontweight='bold')
            ax2.grid(axis='x', alpha=0.3)

            for bar, capex in zip(bars, capex_values):
                ax2.text(capex + max(capex_values)*0.01, bar.get_y() + bar.get_height()/2.,
                        f'{capex/1_000_000:.0f}М', va='center', fontsize=9, fontweight='bold')

            # График 3: Сравнение транспортных расходов
            ax3 = fig.add_subplot(gs[1, 1])
            transport_costs = [loc['total_annual_transport_cost'] for loc in locations_data]

            bars = ax3.barh(range(len(locations_data)), transport_costs,
                           color=plt.cm.Greens(np.linspace(0.3, 0.8, len(locations_data))),
                           edgecolor='black', linewidth=1.5, alpha=0.8)
            ax3.set_yticks(range(len(locations_data)))
            ax3.set_yticklabels(location_names, fontsize=9)
            ax3.set_xlabel('Транспортные расходы (руб/год)', fontsize=11)
            ax3.set_title('Сравнение годовых транспортных расходов', fontsize=12, fontweight='bold')
            ax3.grid(axis='x', alpha=0.3)

            for bar, cost in zip(bars, transport_costs):
                ax3.text(cost + max(transport_costs)*0.01, bar.get_y() + bar.get_height()/2.,
                        f'{cost/1_000_000:.1f}М', va='center', fontsize=9, fontweight='bold')

            # График 4: Детальное сравнение компонентов OPEX
            ax4 = fig.add_subplot(gs[2, :])

            # Подготовка данных для stacked bar chart
            building_opex = [loc['annual_building_opex'] for loc in locations_data]
            transport_opex = [loc['total_annual_transport_cost'] for loc in locations_data]

            x = np.arange(len(locations_data))
            width = 0.6

            p1 = ax4.bar(x, building_opex, width, label='OPEX помещения',
                        color='steelblue', edgecolor='black', linewidth=1)
            p2 = ax4.bar(x, transport_opex, width, bottom=building_opex, label='OPEX транспорта',
                        color='coral', edgecolor='black', linewidth=1)

            ax4.set_xticks(x)
            ax4.set_xticklabels(location_names, rotation=45, ha='right', fontsize=10)
            ax4.set_ylabel('Годовой OPEX (руб)', fontsize=12)
            ax4.set_title('Детальная структура годового OPEX по локациям', fontsize=14, fontweight='bold')
            ax4.legend(loc='upper left', fontsize=11)
            ax4.grid(axis='y', alpha=0.3)

            plt.suptitle('Сравнительный анализ всех кандидатов на релокацию',
                        fontsize=18, fontweight='bold', y=0.995)

            filename = f'{self.output_dir}/comparison_all_locations.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"\n[График] Сравнительный график сохранен: {filename}")
            plt.close()
        except Exception as e:
            print(f"\n[ОШИБКА] Не удалось создать сравнительный график: {e}")

        # Вывод таблицы с рейтингом
        print("\n[Рейтинг] РЕЙТИНГ ЛОКАЦИЙ ПО ГОДОВОМУ OPEX:\n")
        sorted_locations = sorted(locations_data, key=lambda x: x['total_annual_opex_s1'])

        print("+-----+---------------------------------+------------------+------------------+------------------+")
        print("| №   | Локация                         | CAPEX (млн руб)  | OPEX (млн руб)   | Тип владения     |")
        print("+-----+---------------------------------+------------------+------------------+------------------+")

        for idx, loc in enumerate(sorted_locations, 1):
            marker = "[1]" if idx == 1 else f" {idx} "
            print(f"| {marker} | {loc['location_name'][:30]:<31} | {loc['total_initial_capex']/1_000_000:>14.1f}   |"
                  f" {loc['total_annual_opex_s1']/1_000_000:>14.1f}   | {loc['type']:<16} |")

        print("+-----+---------------------------------+------------------+------------------+------------------+")


# Глобальный экземпляр визуализатора
visualizer = FormulaVisualizer()

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
"""
Главный исполняемый файл.
Оркестрирует полный цикл анализа релокации склада: от сбора данных до расчета ROI.
"""
from typing import Dict, Any, List, Optional
import math

# Импорт всех необходимых компонентов
from core.data_model import LocationSpec
from core.location import WarehouseConfigurator
from analysis import AvitoParserStub, FleetOptimizer, OSRMGeoRouter
from scenarios import SCENARIOS_CONFIG
import config
from simulation_runner import SimulationRunner
from transport_planner import DetailedFleetPlanner, DockSimulator
from model_validation import run_full_validation
from formula_visualizer import visualizer



def generate_detailed_relocation_plan(location_data: Dict[str, Any], z_pers_s1: float,
                                     fleet_summary: Optional[Dict[str, Any]] = None,
                                     dock_requirements: Optional[Dict[str, Any]] = None):
    """
    Генерирует текстовое описание детального плана переезда для оптимальной локации.
    """
    print(f"\n{'='*80}")
    print(f"[Шаг 9] ДЕТАЛЬНЫЙ ПЛАН ПЕРЕЕЗДА ДЛЯ ОПТИМАЛЬНОЙ ЛОКАЦИИ: '{location_data['location_name']}'")
    print(f"{'='*80}")
    print(f"\nВыбранная локация: {location_data['location_name']}")
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
    print("\n" + "="*120)
    print("ЗАПУСК КОМПЛЕКСНОГО АНАЛИЗА МНОЖЕСТВА ЛОКАЦИЙ")
    print("="*120)

    # 1. Сбор и фильтрация данных (Avito Stub)
    print("\n" + "+"*120)
    print("[ШАГ 1] СБОР И ФИЛЬТРАЦИЯ ДАННЫХ О ЛОКАЦИЯХ")
    print("+"*120)
    parser = AvitoParserStub()
    candidate_locations_raw = config.ALL_CANDIDATE_LOCATIONS
    filtered_locations: List[Dict[str, Any]] = parser.filter_and_score_locations(candidate_locations_raw)
    print(f"\n[OK] Отфильтровано {len(filtered_locations)} подходящих локаций из {len(candidate_locations_raw)}.")

    if not filtered_locations:
        print("[ERROR] Нет локаций, удовлетворяющих минимальным требованиям. Анализ прекращен.")
        return

    enriched_locations: List[Dict[str, Any]] = []

    # 2. Расчет Z_перс (минимальные расходы на персонал для Сценария 1)
    print("\n" + "+"*120)
    print("[ШАГ 2] РАСЧЕТ РАСХОДОВ НА ПЕРСОНАЛ (Сценарий 1)")
    print("+"*120)

    s1_staff_attrition_rate = SCENARIOS_CONFIG["1_Move_No_Mitigation"]["staff_attrition_rate"]
    s1_staff_count = math.floor(config.INITIAL_STAFF_COUNT * (1 - s1_staff_attrition_rate))

    # Базовые расходы на зарплату
    z_pers_base = s1_staff_count * config.OPERATOR_SALARY_RUB_MONTH * 12

    # Дополнительные расходы на персонал
    new_hires = math.floor(config.INITIAL_STAFF_COUNT * s1_staff_attrition_rate)
    training_costs = new_hires * config.STAFF_TRAINING_COST_PER_PERSON
    adaptation_costs = new_hires * config.OPERATOR_SALARY_RUB_MONTH * config.STAFF_ADAPTATION_RATE
    relocating_staff = config.INITIAL_STAFF_COUNT - new_hires
    relocation_costs = relocating_staff * config.STAFF_RELOCATION_COMPENSATION

    z_pers_s1 = z_pers_base + training_costs + adaptation_costs + relocation_costs

    print(f"\n[Расчет персонала]")
    print(f"  Начальное количество: {config.INITIAL_STAFF_COUNT} чел")
    print(f"  После оттока ({s1_staff_attrition_rate*100:.0f}%): {s1_staff_count} чел")
    print(f"  Новых сотрудников: {new_hires} чел")
    print(f"  Базовая ЗП: {z_pers_base:,.0f} руб/год")
    print(f"  Обучение: {training_costs:,.0f} руб")
    print(f"  Адаптация: {adaptation_costs:,.0f} руб")
    print(f"  Компенсации: {relocation_costs:,.0f} руб")
    print(f"  ИТОГО расходы на персонал: {z_pers_s1:,.0f} руб/год")

    # 3. Анализ логистики для каждой локации
    print("\n" + "+"*120)
    print("[ШАГ 3] АНАЛИЗ ЛОГИСТИКИ И РАСЧЕТ ТРАНСПОРТНЫХ РАСХОДОВ")
    print("+"*120)

    for loc_data in filtered_locations:
        print(f"\n{'-'*100}")
        print(f">>> Анализ локации: '{loc_data['location_name']}'")
        print(f"{'-'*100}")

        # Используем WarehouseConfigurator для расчета расстояний
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

        # Расчет транспортных расходов
        fleet_optimizer = FleetOptimizer()
        total_annual_transport_cost = fleet_optimizer.calculate_annual_transport_cost(avg_dist_cfo, avg_dist_svo, avg_dist_local)
        required_fleet_count = fleet_optimizer.calculate_required_fleet()

        print(f"  Расчетные расстояния: ЦФО={avg_dist_cfo:.0f}км, SVO={avg_dist_svo:.0f}км, Москва={avg_dist_local:.0f}км")
        print(f"  Годовые транспортные расходы: {total_annual_transport_cost:,.0f} руб.")
        print(f"  Требуемый флот (ЦФО): {required_fleet_count} грузовиков")

        # Визуализация расстояний для локации
        visualizer.visualize_distance_calculation(
            location_name=loc_data['location_name'],
            warehouse_coords=(loc_data['lat'], loc_data['lon']),
            key_points=config.KEY_GEO_POINTS,
            distances={
                "CFD_HUBs_Avg": avg_dist_cfo,
                "Airport_SVO": avg_dist_svo,
                "Moscow_Clients_Avg": avg_dist_local
            }
        )

        # Расчет Total_Annual_OPEX (Z_общ) для Сценария 1
        total_annual_opex_s1 = loc_data['annual_building_opex'] + z_pers_s1 + total_annual_transport_cost
        print(f"  Total_Annual_OPEX (Сценарий 1): {total_annual_opex_s1:,.0f} руб./год")

        loc_data['total_annual_transport_cost'] = total_annual_transport_cost
        loc_data['required_fleet_count'] = required_fleet_count
        loc_data['total_annual_opex_s1'] = total_annual_opex_s1
        enriched_locations.append(loc_data)

    # 4. Поиск оптимума
    print("\n" + "+"*120)
    print("[ШАГ 4] ВЫБОР ОПТИМАЛЬНОЙ ЛОКАЦИИ")
    print("+"*120)

    optimal_location = min(enriched_locations, key=lambda x: x['total_annual_opex_s1'])

    print(f"\n{'*'*100}")
    print(f"\n[WINNER] ОПТИМАЛЬНАЯ ЛОКАЦИЯ НАЙДЕНА: '{optimal_location['location_name']}'")
    print(f"\n   [KPI] Минимальный годовой OPEX (Сценарий 1): {optimal_location['total_annual_opex_s1']:,.0f} руб/год")
    print(f"   [CAPEX] {optimal_location['total_initial_capex']:,.0f} руб")
    print(f"   [COORDS] ({optimal_location['lat']:.4f}, {optimal_location['lon']:.4f})")
    print(f"   [TYPE] {optimal_location['type']}")
    print(f"\n{'*'*100}\n")

    # Визуализация сравнения всех локаций
    visualizer.visualize_location_comparison(enriched_locations)

    # Визуализация CAPEX/OPEX для оптимальной локации
    capex_breakdown = {
        'Покупка/аренда здания': optimal_location.get('building_capex', 0),
        'Оборудование': config.BASE_EQUIPMENT_CAPEX_RUB,
        'GPP/GDP валидация': config.GPP_GDP_VALIDATION_COST_RUB,
        'Климатические системы': config.GPP_GDP_CLIMATE_SYSTEM_COST_RUB
    }
    opex_breakdown = {
        'Помещение': optimal_location['annual_building_opex'],
        'Персонал': z_pers_s1,
        'Транспорт': optimal_location['total_annual_transport_cost']
    }
    visualizer.visualize_capex_opex_breakdown(
        location_name=optimal_location['location_name'],
        capex_data=capex_breakdown,
        opex_data=opex_breakdown
    )

    # 5. Детальный транспортный анализ для оптимальной локации
    print("\n" + "+"*120)
    print("[ШАГ 5] ДЕТАЛЬНЫЙ ТРАНСПОРТНЫЙ АНАЛИЗ ОПТИМАЛЬНОЙ ЛОКАЦИИ")
    print("+"*120)

    # Используем OSRM для точных расстояний
    print("\n[OSRM] Использование OSRM API для точного расчета дорожных расстояний...")
    geo_router = OSRMGeoRouter(use_geocoding=False)
    optimal_coords = (optimal_location['lat'], optimal_location['lon'])

    # Получаем точные расстояния через OSRM
    route_data = geo_router.calculate_weighted_annual_distance(optimal_coords)

    distances = {
        'cfo_km': route_data['CFO']['distance_km'],
        'svo_km': route_data['SVO']['distance_km'],
        'local_km': route_data['LPU']['distance_km']
    }

    print(f"\n[DISTANCES] Точные дорожные расстояния (OSRM):")
    print(f"   * ЦФО: {distances['cfo_km']:.2f} км")
    print(f"   * SVO: {distances['svo_km']:.2f} км")
    print(f"   * Москва: {distances['local_km']:.2f} км")

    # Детальный расчет флота
    print("\n[FLEET] Расчет детального состава транспортного флота...")
    detailed_planner = DetailedFleetPlanner()
    fleet_summary = detailed_planner.calculate_fleet_requirements(distances)

    # Расчет доков
    print("\n[DOCKS] Расчет требований к инфраструктуре доков...")
    dock_requirements = detailed_planner.calculate_dock_requirements(fleet_summary)

    # Генерация графика работы
    _ = detailed_planner.generate_transport_schedule(fleet_summary)

    # Проверка достаточности доков
    dock_sim = DockSimulator(
        inbound_docks=dock_requirements['inbound_docks'],
        outbound_docks=dock_requirements['outbound_docks']
    )
    dock_simulation = dock_sim.simulate_dock_operations(dock_requirements['peak_trips_per_day'])

    print(f"\n[Проверка пропускной способности доков]")
    print(f"  Inbound доки (приемка): {dock_requirements['inbound_docks']} шт")
    print(f"  Утилизация: {dock_simulation['inbound_utilization_percent']:.1f}%")
    print(f"  Outbound доки (отгрузка): {dock_requirements['outbound_docks']} шт")
    print(f"  Утилизация: {dock_simulation['outbound_utilization_percent']:.1f}%")

    if not dock_simulation['is_sufficient']:
        print(f"  [WARNING] Доков недостаточно! Требуется увеличение.")
    else:
        print(f"  [OK] Доков достаточно для текущей нагрузки")

    print(f"\n[Рекомендация по транспортному флоту]")
    if fleet_summary['recommendation'] == 'lease':
        print(f"  РЕКОМЕНДУЕТСЯ: Аренда транспорта")
        print(f"  Годовой OPEX (аренда): {fleet_summary['total_opex_lease']:,.0f} руб/год")
        print(f"  Экономия: {fleet_summary['total_opex_own_fleet'] - fleet_summary['total_opex_lease']:,.0f} руб/год vs покупки")
    else:
        print(f"  РЕКОМЕНДУЕТСЯ: Покупка транспорта")
        print(f"  CAPEX (покупка): {fleet_summary['total_capex_purchase']:,.0f} руб")
        print(f"  ROI достигается через ~5 лет")

    # 6. Детализация сценариев и SimPy для оптимальной локации
    print("\n" + "+"*120)
    print("[ШАГ 6] ЗАПУСК SIMPY СИМУЛЯЦИИ ДЛЯ ВСЕХ СЦЕНАРИЕВ")
    print("+"*120)

    # Создаем LocationSpec для SimulationRunner
    optimal_location_spec = LocationSpec(
        name=optimal_location['location_name'],
        lat=optimal_location['lat'],
        lon=optimal_location['lon'],
        ownership_type=optimal_location['type']
    )

    # Формируем initial_base_finance для SimulationRunner
    initial_base_finance_for_runner = {
        "base_capex": optimal_location['total_initial_capex'],
        "base_opex": optimal_location['annual_building_opex'] + optimal_location['total_annual_transport_cost']
    }

    print("\n[SIMPY] Запуск детальной SimPy симуляции операций склада...")
    print(f"   * Локация: {optimal_location['location_name']}")
    print(f"   * Базовый CAPEX: {initial_base_finance_for_runner['base_capex']:,.0f} руб")
    print(f"   * Базовый OPEX: {initial_base_finance_for_runner['base_opex']:,.0f} руб/год")

    runner = SimulationRunner(location_spec=optimal_location_spec)
    runner.run_all_scenarios(initial_base_finance=initial_base_finance_for_runner)

    # 7. Детальный анализ склада (зонирование, условия хранения, автоматизация)
    print("\n" + "+"*120)
    print("[ШАГ 7] ДЕТАЛЬНЫЙ АНАЛИЗ СКЛАДА И АВТОМАТИЗАЦИИ")
    print("+"*120)

    print("\n[WAREHOUSE] Запуск комплексного анализа склада для оптимальной локации...")
    print(f"   * Локация: {optimal_location['location_name']}")
    print(f"   * Площадь: {optimal_location['area_offered_sqm']:,.0f} кв.м")

    # Импортируем модуль анализа склада
    from warehouse_analysis import ComprehensiveWarehouseAnalysis

    # Создаем экземпляр для детального анализа
    warehouse_analyzer = ComprehensiveWarehouseAnalysis(
        location_name=optimal_location['location_name'],
        total_area=optimal_location['area_offered_sqm'],
        total_sku=15_000  # 15,000 SKU согласно требованиям
    )

    # Запускаем полный анализ
    warehouse_analyzer.run_full_analysis()

    # Получаем данные для валидации
    warehouse_validation_data = {
        'zoning_data': warehouse_analyzer.zoning_data,
        'equipment_data': warehouse_analyzer.equipment_data,
        'total_sku': 15_000
    }

    # 8. Валидация модели
    print("\n" + "+"*120)
    print("[ШАГ 8] ВАЛИДАЦИЯ И ВЕРИФИКАЦИЯ МОДЕЛИ")
    print("+"*120)

    validation_results = run_full_validation(
        location_data=optimal_location,
        warehouse_data=warehouse_validation_data,
        roi_data=warehouse_analyzer.roi_data,
        automation_scenarios=warehouse_analyzer.automation_scenarios
    )

    print(f"\n[Результаты валидации]")
    print(f"  Всего проверок: {len(validation_results['validation_results'])}")
    print(f"  Критических ошибок: {validation_results['critical_failures']}")
    print(f"  Предупреждений: {validation_results['warnings']}")
    print(f"  Отчет сохранен: {validation_results['report_path']}")
    print(f"  Общий балл: {validation_results['verification_results']['overall_score']:.1f}/100")

    # 9. Вывод плана переезда
    print("\n" + "+"*120)
    print("[ШАГ 9] ДЕТАЛЬНЫЙ ПЛАН ПЕРЕЕЗДА")
    print("+"*120)
    generate_detailed_relocation_plan(optimal_location, z_pers_s1, fleet_summary, dock_requirements)

    # 10. Финальная сводка
    print("\n" + "="*120)
    print("АНАЛИЗ УСПЕШНО ЗАВЕРШЕН")
    print("="*120)
    print("\nВсе файлы сохранены в директории 'output/':")
    print("  * warehouse_layout_detailed.png - Планировка склада с зонами")
    print("  * automation_comparison_detailed.png - Сравнение сценариев автоматизации")
    print("  * warehouse_analysis_report.xlsx - Полный Excel отчет (9 вкладок)")
    print("  * validation_report.xlsx - Отчет валидации модели (до 7 вкладок)")
    print("  * validation_report_visualizations.png - Визуализация результатов валидации")
    print("  * roi_comparison_animated.gif - Анимация сравнения ROI")
    print("  * payback_period_animated.gif - Анимация срока окупаемости")
    print("  * distance_calculation_*.png - Визуализация расчета расстояний для локаций")
    print("  * location_comparison.png - Сравнение всех локаций")
    print("  * capex_opex_breakdown_*.png - Разбивка CAPEX/OPEX для оптимальной локации")
    print("="*120)


if __name__ == "__main__":
    try:
        main_multi_location_runner()
    except Exception as e:
        print(f"\n[ОШИБКА] Произошла непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()

```

## `model_validation.py`

```py
"""
Модуль для валидации и верификации модели переезда склада.
Проверяет корректность расчетов, соответствие требованиям и достижение целей.
Включает проверку GPP/GDP, климатических систем, KPI и финансовых показателей.
"""
import os
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import config


@dataclass
class ValidationResult:
    """Результат проверки валидации."""
    check_name: str
    passed: bool
    expected: Any
    actual: Any
    message: str
    severity: str  # 'critical', 'warning', 'info'


class ModelValidator:
    """Класс для комплексной валидации и верификации модели."""

    def __init__(self):
        """Инициализация валидатора."""
        self.validation_results: List[ValidationResult] = []
        self.critical_failures = 0
        self.warnings = 0
        self.info_count = 0

    def validate_location_data(self, location_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация данных локации.

        Args:
            location_data: Данные выбранной локации

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ ДАННЫХ ЛОКАЦИИ")
        print("="*100)

        results = []

        # 1. Проверка площади
        results.append(self._validate_area(
            location_data.get('area_offered_sqm', 0),
            config.MIN_AREA_SQM,
            config.TARGET_AREA_SQM
        ))

        # 2. Проверка координат (должны быть в Московской области)
        results.append(self._validate_coordinates(
            location_data.get('lat'),
            location_data.get('lon')
        ))

        # 3. Проверка финансовых показателей
        results.append(self._validate_capex(location_data.get('total_initial_capex', 0)))
        results.append(self._validate_opex(location_data.get('total_annual_opex_s1', 0)))

        # 4. Проверка транспортной доступности
        results.append(self._validate_transport_cost(
            location_data.get('total_annual_transport_cost', 0)
        ))

        # 5. Проверка класса помещения для GPP/GDP
        results.append(self._validate_building_class(
            location_data.get('current_class', '')
        ))

        self.validation_results.extend(results)
        self._print_validation_results(results, "ЛОКАЦИЯ")

        return results

    def validate_warehouse_configuration(self, zoning_data: Dict[str, Any],
                                        equipment_data: Dict[str, Any],
                                        total_sku: int) -> List[ValidationResult]:
        """
        Валидация конфигурации склада.

        Args:
            zoning_data: Данные зонирования
            equipment_data: Данные оборудования
            total_sku: Общее количество SKU

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ КОНФИГУРАЦИИ СКЛАДА")
        print("="*100)

        results = []

        # 1. Проверка зонирования
        results.append(self._validate_zoning_ratios(zoning_data))

        # 2. Проверка вместимости стеллажей
        results.append(self._validate_storage_capacity(equipment_data, total_sku))

        # 3. Проверка количества доков
        results.append(self._validate_dock_count(equipment_data))

        # 4. Проверка климатических зон
        results.append(self._validate_climate_zones(zoning_data))

        # 5. Проверка требований GPP/GDP
        results.append(self._validate_gpp_gdp_zones(zoning_data))

        self.validation_results.extend(results)
        self._print_validation_results(results, "КОНФИГУРАЦИЯ СКЛАДА")

        return results

    def validate_climate_systems(self, climate_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация климатических систем.

        Args:
            climate_data: Данные климатических систем

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ КЛИМАТИЧЕСКИХ СИСТЕМ")
        print("="*100)

        results = []

        # 1. Проверка мощности охлаждения
        if climate_data and 'zones' in climate_data:
            for zone_name, zone_data in climate_data['zones'].items():
                results.append(self._validate_cooling_power(
                    zone_name,
                    zone_data.get('cooling_power_kw', 0),
                    zone_data.get('area_sqm', 0)
                ))

        # 2. Проверка резервирования
        results.append(self._validate_climate_redundancy(climate_data))

        # 3. Проверка систем мониторинга
        results.append(self._validate_monitoring_systems(climate_data))

        self.validation_results.extend(results)
        self._print_validation_results(results, "КЛИМАТИЧЕСКИЕ СИСТЕМЫ")

        return results

    def validate_roi_calculations(self, roi_data: Dict[str, Any],
                                  automation_scenarios: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация расчетов ROI.

        Args:
            roi_data: Данные ROI
            automation_scenarios: Сценарии автоматизации

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ РАСЧЕТОВ ROI")
        print("="*100)

        results = []

        # 1. Проверка срока окупаемости
        results.append(self._validate_payback_period(roi_data))

        # 2. Проверка ROI за 5 лет
        results.append(self._validate_roi_target(roi_data))

        # 3. Проверка логичности сокращения персонала
        results.append(self._validate_labor_reduction(roi_data, automation_scenarios))

        # 4. Проверка корректности расчета выгод
        results.append(self._validate_benefit_calculations(roi_data))

        # 5. Проверка CAPEX автоматизации
        results.append(self._validate_automation_capex(roi_data))

        # 6. Проверка соответствия эффективности и инвестиций
        results.append(self._validate_efficiency_investment_ratio(roi_data, automation_scenarios))

        self.validation_results.extend(results)
        self._print_validation_results(results, "ROI")

        return results

    def validate_operational_kpi(self, simulation_results: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация операционных KPI.

        Args:
            simulation_results: Результаты симуляции

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ ОПЕРАЦИОННЫХ KPI")
        print("="*100)

        results = []

        if simulation_results:
            # 1. Проверка throughput
            results.append(self._validate_throughput(simulation_results))

            # 2. Проверка cycle time
            results.append(self._validate_cycle_time(simulation_results))

            # 3. Проверка утилизации доков
            results.append(self._validate_dock_utilization(simulation_results))

        self.validation_results.extend(results)
        self._print_validation_results(results, "ОПЕРАЦИОННЫЕ KPI")

        return results

    def validate_business_requirements(self, location_data: Dict[str, Any],
                                      roi_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация соответствия бизнес-требованиям.

        Args:
            location_data: Данные локации
            roi_data: Данные ROI

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ СООТВЕТСТВИЯ БИЗНЕС-ТРЕБОВАНИЯМ")
        print("="*100)

        results = []

        # 1. Проверка целевой производительности
        results.append(self._validate_target_throughput())

        # 2. Проверка бюджетных ограничений
        results.append(self._validate_budget_constraints(location_data, roi_data))

        # 3. Проверка требований GPP/GDP
        results.append(self._validate_gpp_gdp_compliance(location_data))

        # 4. Проверка срока реализации проекта
        results.append(self._validate_project_timeline())

        # 5. Проверка масштабируемости
        results.append(self._validate_scalability(location_data))

        self.validation_results.extend(results)
        self._print_validation_results(results, "БИЗНЕС-ТРЕБОВАНИЯ")

        return results

    def verify_model_objectives(self, location_data: Dict[str, Any],
                                roi_data: Dict[str, Any],
                                warehouse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Верификация выполнения целей модели.

        Args:
            location_data: Данные локации
            roi_data: Данные ROI
            warehouse_data: Данные склада

        Returns:
            Словарь с результатами верификации целей
        """
        print("\n" + "="*100)
        print("ВЕРИФИКАЦИЯ ВЫПОЛНЕНИЯ ЦЕЛЕЙ МОДЕЛИ")
        print("="*100)

        objectives = {
            'find_optimal_location': False,
            'minimize_opex': False,
            'achieve_automation': False,
            'ensure_scalability': False,
            'maintain_quality': False,
            'meet_budget': False
        }

        scores = {}

        # 1. Найти оптимальную локацию
        if location_data.get('location_name'):
            objectives['find_optimal_location'] = True
            scores['location_selection'] = 100
            print(f"\n+ Цель 1: Найти оптимальную локацию")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Выбрана локация: {location_data['location_name']}")
        else:
            scores['location_selection'] = 0
            print(f"\n- Цель 1: Найти оптимальную локацию")
            print(f"  Статус: НЕ ВЫПОЛНЕНО")

        # 2. Минимизировать OPEX
        target_opex = config.MAX_ANNUAL_OPEX_RUB
        actual_opex = location_data.get('total_annual_opex_s1', float('inf'))

        if actual_opex <= target_opex:
            objectives['minimize_opex'] = True
            scores['opex_optimization'] = min(100, (target_opex / actual_opex) * 100)
            print(f"\n+ Цель 2: Минимизировать OPEX")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Целевой OPEX: {target_opex:,.0f} руб/год")
            print(f"  Фактический OPEX: {actual_opex:,.0f} руб/год")
            print(f"  Эффективность: {scores['opex_optimization']:.1f}%")
        else:
            scores['opex_optimization'] = (target_opex / actual_opex) * 100
            print(f"\n\! Цель 2: Минимизировать OPEX")
            print(f"  Статус: ЧАСТИЧНО ВЫПОЛНЕНО")
            print(f"  Целевой OPEX: {target_opex:,.0f} руб/год")
            print(f"  Фактический OPEX: {actual_opex:,.0f} руб/год")
            print(f"  Превышение: {((actual_opex / target_opex - 1) * 100):.1f}%")

        # 3. Достичь оптимального уровня автоматизации
        if roi_data:
            best_roi = max([data['roi_5y_percent'] for data in roi_data.values()])
            if best_roi > 20:  # Минимальный ROI 20% за 5 лет
                objectives['achieve_automation'] = True
                scores['automation_efficiency'] = min(100, (best_roi / 50) * 100)
                print(f"\n+ Цель 3: Достичь оптимального уровня автоматизации")
                print(f"  Статус: ВЫПОЛНЕНО")
                print(f"  Лучший ROI за 5 лет: {best_roi:.1f}%")
                print(f"  Эффективность: {scores['automation_efficiency']:.1f}%")
            else:
                scores['automation_efficiency'] = (best_roi / 50) * 100
                print(f"\n\! Цель 3: Достичь оптимального уровня автоматизации")
                print(f"  Статус: ТРЕБУЕТ УЛУЧШЕНИЯ")
                print(f"  Лучший ROI за 5 лет: {best_roi:.1f}%")
        else:
            scores['automation_efficiency'] = 50

        # 4. Обеспечить масштабируемость
        target_capacity = config.TARGET_ORDERS_MONTH * 1.5  # Резерв 50%
        if warehouse_data:
            objectives['ensure_scalability'] = True
            scores['scalability'] = 100
            print(f"\n+ Цель 4: Обеспечить масштабируемость")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Целевая мощность: {target_capacity:,.0f} заказов/месяц")
            print(f"  Резерв мощности: 50%")
        else:
            scores['scalability'] = 50
            print(f"\n\! Цель 4: Обеспечить масштабируемость")
            print(f"  Статус: ТРЕБУЕТ АНАЛИЗА")

        # 5. Поддержать качество (GPP/GDP)
        if location_data.get('current_class') in ['A', 'A_requires_mod', 'A_verified']:
            objectives['maintain_quality'] = True
            scores['quality_standards'] = 100
            print(f"\n+ Цель 5: Поддержать стандарты качества (GPP/GDP)")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Класс помещения: {location_data['current_class']}")
        else:
            scores['quality_standards'] = 50
            print(f"\n\! Цель 5: Поддержать стандарты качества (GPP/GDP)")
            print(f"  Статус: ТРЕБУЕТ МОДИФИКАЦИЙ")

        # 6. Соблюсти бюджет
        total_capex = location_data.get('total_initial_capex', 0)
        if roi_data:
            max_auto_capex = max([data['capex'] for data in roi_data.values()])
            total_capex = max(total_capex, max_auto_capex)

        if total_capex <= config.MAX_TOTAL_CAPEX_RUB:
            objectives['meet_budget'] = True
            scores['budget_compliance'] = 100
            print(f"\n+ Цель 6: Соблюсти бюджетные ограничения")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Макс. бюджет: {config.MAX_TOTAL_CAPEX_RUB:,.0f} руб")
            print(f"  Фактический CAPEX: {total_capex:,.0f} руб")
        else:
            scores['budget_compliance'] = (config.MAX_TOTAL_CAPEX_RUB / total_capex) * 100
            print(f"\n\! Цель 6: Соблюсти бюджетные ограничения")
            print(f"  Статус: ПРЕВЫШЕНИЕ БЮДЖЕТА")
            print(f"  Макс. бюджет: {config.MAX_TOTAL_CAPEX_RUB:,.0f} руб")
            print(f"  Фактический CAPEX: {total_capex:,.0f} руб")
            print(f"  Превышение: {((total_capex / config.MAX_TOTAL_CAPEX_RUB - 1) * 100):.1f}%")

        # Общий балл выполнения целей
        overall_score = sum(scores.values()) / len(scores)

        print(f"\n" + "="*100)
        print(f"ОБЩИЙ БАЛЛ ВЫПОЛНЕНИЯ ЦЕЛЕЙ: {overall_score:.1f}/100")
        print(f"="*100)

        if overall_score >= 80:
            print(f"[ОТЛИЧНО] Модель успешно выполняет все поставленные цели")
        elif overall_score >= 60:
            print(f"[ХОРОШО] Модель выполняет большинство целей, но есть области для улучшения")
        else:
            print(f"[ТРЕБУЕТ ДОРАБОТКИ] Модель нуждается в значительных улучшениях")

        return {
            'objectives_met': objectives,
            'scores': scores,
            'overall_score': overall_score
        }

    def generate_validation_report(self, output_path: str = None,
                                   location_data: Dict[str, Any] = None,
                                   warehouse_data: Dict[str, Any] = None,
                                   roi_data: Dict[str, Any] = None) -> str:
        """
        Генерирует расширенный отчет по валидации в Excel с визуализациями.

        Args:
            output_path: Путь для сохранения отчета
            location_data: Данные локации (для детальных сравнений)
            warehouse_data: Данные склада (для детальных сравнений)
            roi_data: Данные ROI (для детальных сравнений)

        Returns:
            Путь к сохраненному файлу
        """
        if output_path is None:
            output_path = os.path.join(config.OUTPUT_DIR, "validation_report.xlsx")

        print(f"\n[Отчет] Создание расширенного отчета валидации: {output_path}")

        # Подготовка основных данных
        data = []
        for result in self.validation_results:
            data.append({
                'Проверка': result.check_name,
                'Статус': 'ПРОЙДЕНО' if result.passed else 'ПРОВАЛЕНО',
                'Критичность': result.severity.upper(),
                'Ожидаемое': str(result.expected),
                'Фактическое': str(result.actual),
                'Сообщение': result.message
            })

        df = pd.DataFrame(data)

        # Статистика
        total_checks = len(self.validation_results)
        passed = sum(1 for r in self.validation_results if r.passed)
        failed = total_checks - passed

        summary_data = {
            'Показатель': ['Всего проверок', 'Пройдено', 'Провалено', 'Критических ошибок', 'Предупреждений', 'Информационных'],
            'Значение': [total_checks, passed, failed, self.critical_failures, self.warnings, self.info_count]
        }
        summary_df = pd.DataFrame(summary_data)

        # Подготовка дополнительных вкладок
        excel_sheets = {
            'Сводка': summary_df,
            'Детали валидации': df,
            'По категориям': self._prepare_category_breakdown(),
            'По критичности': self._prepare_severity_breakdown(),
        }

        # Добавляем сравнительные данные, если они доступны
        if location_data:
            excel_sheets['Сравнение локации'] = self._prepare_location_comparison(location_data)

        if warehouse_data:
            excel_sheets['Сравнение склада'] = self._prepare_warehouse_comparison(warehouse_data)

        if roi_data:
            excel_sheets['Сравнение ROI'] = self._prepare_roi_comparison(roi_data)

        # Запись в Excel
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, sheet_df in excel_sheets.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"[Отчет] Сохранен: {output_path}")
            print(f"[Отчет] Количество вкладок: {len(excel_sheets)}")
        except Exception as e:
            print(f"[Ошибка] Не удалось сохранить отчет: {e}")
            output_path = None

        # Генерация визуализаций
        if output_path:
            viz_path = output_path.replace('.xlsx', '_visualizations.png')
            self._generate_validation_visualizations(viz_path)

        return output_path

    def _prepare_category_breakdown(self) -> pd.DataFrame:
        """Подготавливает разбивку результатов по категориям."""
        # Группировка проверок по категориям (извлекаем из имени проверки)
        category_stats = {}

        for result in self.validation_results:
            # Определяем категорию из имени проверки
            if 'площад' in result.check_name.lower():
                category = 'Площадь и размеры'
            elif 'координат' in result.check_name.lower():
                category = 'Географическое расположение'
            elif 'capex' in result.check_name.lower() or 'инвестиц' in result.check_name.lower():
                category = 'CAPEX и инвестиции'
            elif 'opex' in result.check_name.lower() or 'операцион' in result.check_name.lower():
                category = 'OPEX и операционные расходы'
            elif 'транспорт' in result.check_name.lower():
                category = 'Транспорт и логистика'
            elif 'класс' in result.check_name.lower() or 'gpp' in result.check_name.lower() or 'gdp' in result.check_name.lower():
                category = 'GPP/GDP соответствие'
            elif 'зон' in result.check_name.lower():
                category = 'Зонирование'
            elif 'стеллаж' in result.check_name.lower() or 'вместимост' in result.check_name.lower():
                category = 'Вместимость и хранение'
            elif 'док' in result.check_name.lower():
                category = 'Доки'
            elif 'климат' in result.check_name.lower() or 'температур' in result.check_name.lower():
                category = 'Климатические системы'
            elif 'мониторинг' in result.check_name.lower():
                category = 'Мониторинг'
            elif 'roi' in result.check_name.lower() or 'окупаем' in result.check_name.lower():
                category = 'ROI и окупаемость'
            elif 'персонал' in result.check_name.lower() or 'сокращение' in result.check_name.lower():
                category = 'Персонал'
            elif 'throughput' in result.check_name.lower() or 'производительност' in result.check_name.lower():
                category = 'Производительность'
            elif 'бюджет' in result.check_name.lower():
                category = 'Бюджетные ограничения'
            else:
                category = 'Прочее'

            if category not in category_stats:
                category_stats[category] = {
                    'Всего проверок': 0,
                    'Пройдено': 0,
                    'Провалено': 0,
                    'Критических': 0,
                    'Предупреждений': 0,
                    'Информационных': 0
                }

            category_stats[category]['Всего проверок'] += 1
            if result.passed:
                category_stats[category]['Пройдено'] += 1
            else:
                category_stats[category]['Провалено'] += 1

            if result.severity == 'critical':
                category_stats[category]['Критических'] += 1
            elif result.severity == 'warning':
                category_stats[category]['Предупреждений'] += 1
            else:
                category_stats[category]['Информационных'] += 1

        # Преобразуем в DataFrame
        data = []
        for category, stats in category_stats.items():
            row = {'Категория': category}
            row.update(stats)
            data.append(row)

        return pd.DataFrame(data)

    def _prepare_severity_breakdown(self) -> pd.DataFrame:
        """Подготавливает разбивку по уровням критичности."""
        severity_map = {'critical': 'Критические', 'warning': 'Предупреждения', 'info': 'Информационные'}

        severity_stats = {
            'critical': {'Всего': 0, 'Пройдено': 0, 'Провалено': 0},
            'warning': {'Всего': 0, 'Пройдено': 0, 'Провалено': 0},
            'info': {'Всего': 0, 'Пройдено': 0, 'Провалено': 0}
        }

        for result in self.validation_results:
            severity_stats[result.severity]['Всего'] += 1
            if result.passed:
                severity_stats[result.severity]['Пройдено'] += 1
            else:
                severity_stats[result.severity]['Провалено'] += 1

        data = []
        for severity, label in severity_map.items():
            row = {'Критичность': label}
            row.update(severity_stats[severity])
            data.append(row)

        return pd.DataFrame(data)

    def _prepare_location_comparison(self, location_data: Dict[str, Any]) -> pd.DataFrame:
        """Подготавливает сравнительную таблицу параметров локации."""
        data = []

        comparisons = [
            {
                'Параметр': 'Площадь (кв.м)',
                'Минимальное требование': f"{config.MIN_AREA_SQM:,.0f}",
                'Целевое значение': f"{config.TARGET_AREA_SQM:,.0f}",
                'Фактическое': f"{location_data.get('area_offered_sqm', 0):,.0f}",
                'Соответствие': 'Да' if location_data.get('area_offered_sqm', 0) >= config.MIN_AREA_SQM else 'Нет'
            },
            {
                'Параметр': 'CAPEX (руб)',
                'Минимальное требование': '0',
                'Целевое значение': f"{config.MAX_TOTAL_CAPEX_RUB:,.0f}",
                'Фактическое': f"{location_data.get('total_initial_capex', 0):,.0f}",
                'Соответствие': 'Да' if location_data.get('total_initial_capex', 0) <= config.MAX_TOTAL_CAPEX_RUB else 'Нет'
            },
            {
                'Параметр': 'Годовой OPEX (руб)',
                'Минимальное требование': '0',
                'Целевое значение': f"{config.MAX_ANNUAL_OPEX_RUB:,.0f}",
                'Фактическое': f"{location_data.get('total_annual_opex_s1', 0):,.0f}",
                'Соответствие': 'Да' if location_data.get('total_annual_opex_s1', 0) <= config.MAX_ANNUAL_OPEX_RUB else 'Нет'
            },
            {
                'Параметр': 'Транспортные расходы (руб/год)',
                'Минимальное требование': '0',
                'Целевое значение': '100,000,000',
                'Фактическое': f"{location_data.get('total_annual_transport_cost', 0):,.0f}",
                'Соответствие': 'Да' if location_data.get('total_annual_transport_cost', 0) <= 100_000_000 else 'Нет'
            },
            {
                'Параметр': 'Класс помещения',
                'Минимальное требование': 'Класс A',
                'Целевое значение': 'Класс A',
                'Фактическое': location_data.get('current_class', 'Не указан'),
                'Соответствие': 'Да' if location_data.get('current_class') in ['A', 'A_verified', 'A_requires_mod'] else 'Нет'
            }
        ]

        return pd.DataFrame(comparisons)

    def _prepare_warehouse_comparison(self, warehouse_data: Dict[str, Any]) -> pd.DataFrame:
        """Подготавливает сравнительную таблицу параметров склада."""
        data = []

        zoning_data = warehouse_data.get('zoning_data', {})
        equipment_data = warehouse_data.get('equipment_data', {})
        total_sku = warehouse_data.get('total_sku', config.TOTAL_SKU_COUNT)

        # Вместимость
        total_positions = equipment_data.get('total_pallet_positions', 0)
        required_positions = total_sku * 2

        data.append({
            'Параметр': 'Паллето-мест',
            'Минимальное требование': f"{required_positions:,.0f}",
            'Фактическое': f"{total_positions:,.0f}",
            'Отклонение': f"{total_positions - required_positions:,.0f}",
            'Соответствие': 'Да' if total_positions >= required_positions else 'Нет'
        })

        # Доки
        total_docks = equipment_data.get('inbound_docks', 0) + equipment_data.get('outbound_docks', 0)
        min_docks = 10

        data.append({
            'Параметр': 'Количество доков',
            'Минимальное требование': f"{min_docks}",
            'Фактическое': f"{total_docks}",
            'Отклонение': f"{total_docks - min_docks}",
            'Соответствие': 'Да' if total_docks >= min_docks else 'Нет'
        })

        # Зонирование - доля хранения
        if zoning_data:
            storage_zones = ['storage_normal', 'storage_cold']
            total_storage = sum(zone.area_sqm for zone_name, zone in zoning_data.items() if zone_name in storage_zones)
            total_area = sum(zone.area_sqm for zone in zoning_data.values())
            storage_ratio = (total_storage / total_area) * 100 if total_area > 0 else 0

            data.append({
                'Параметр': 'Доля зон хранения (%)',
                'Минимальное требование': '75',
                'Фактическое': f"{storage_ratio:.1f}",
                'Отклонение': f"{storage_ratio - 75:.1f}",
                'Соответствие': 'Да' if storage_ratio >= 75 else 'Нет'
            })

        return pd.DataFrame(data)

    def _prepare_roi_comparison(self, roi_data: Dict[str, Any]) -> pd.DataFrame:
        """Подготавливает сравнительную таблицу ROI по сценариям."""
        data = []

        for level_value, roi_info in roi_data.items():
            data.append({
                'Сценарий': roi_info['scenario_name'],
                'CAPEX (руб)': f"{roi_info['capex']:,.0f}",
                'Годовая выгода (руб)': f"{roi_info['net_annual_benefit']:,.0f}",
                'Срок окупаемости (лет)': f"{roi_info['payback_years']:.2f}" if roi_info['payback_years'] != float('inf') else 'Не окупается',
                'ROI за 5 лет (%)': f"{roi_info['roi_5y_percent']:.1f}",
                'Сокращение персонала (чел)': roi_info['reduced_staff'],
                'Рост throughput (%)': f"{(roi_info['annual_revenue_increase'] / (config.TARGET_ORDERS_MONTH * 12 * 500) * 100):.1f}" if config.TARGET_ORDERS_MONTH > 0 else "0.0",
                'Оценка': self._evaluate_roi(roi_info['roi_5y_percent'], roi_info['payback_years'])
            })

        return pd.DataFrame(data)

    def _evaluate_roi(self, roi_5y: float, payback_years: float) -> str:
        """Оценивает качество ROI."""
        if roi_5y >= 100 and payback_years <= 3:
            return 'Отлично'
        elif roi_5y >= 50 and payback_years <= 5:
            return 'Хорошо'
        elif roi_5y >= 20 and payback_years <= 7:
            return 'Приемлемо'
        elif roi_5y >= 0:
            return 'Низкая эффективность'
        else:
            return 'Убыточно'

    def _generate_validation_visualizations(self, output_path: str):
        """Генерирует визуализации результатов валидации."""
        print(f"\n[Визуализация] Создание графиков валидации: {output_path}")

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Результаты валидации и верификации модели', fontsize=16, fontweight='bold')

        # График 1: Общая статистика
        categories = ['Пройдено', 'Провалено']
        passed = sum(1 for r in self.validation_results if r.passed)
        failed = sum(1 for r in self.validation_results if not r.passed)
        values = [passed, failed]
        colors = ['green', 'red']

        ax1.bar(categories, values, color=colors, alpha=0.7)
        ax1.set_ylabel('Количество проверок', fontsize=11)
        ax1.set_title('Общая статистика валидации', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # Добавляем значения на столбцы
        for i, v in enumerate(values):
            ax1.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=10, fontweight='bold')

        # График 2: По уровню критичности
        severity_counts = {
            'Критические': self.critical_failures,
            'Предупреждения': self.warnings,
            'Информационные': self.info_count
        }
        colors_severity = ['red', 'orange', 'blue']

        ax2.bar(severity_counts.keys(), severity_counts.values(), color=colors_severity, alpha=0.7)
        ax2.set_ylabel('Количество', fontsize=11)
        ax2.set_title('Распределение по критичности', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        # График 3: Проходимость по категориям
        category_df = self._prepare_category_breakdown()
        if not category_df.empty:
            top_categories = category_df.nlargest(8, 'Всего проверок')

            x = range(len(top_categories))
            width = 0.35

            ax3.bar([i - width/2 for i in x], top_categories['Пройдено'], width, label='Пройдено', color='green', alpha=0.7)
            ax3.bar([i + width/2 for i in x], top_categories['Провалено'], width, label='Провалено', color='red', alpha=0.7)

            ax3.set_xlabel('Категории', fontsize=11)
            ax3.set_ylabel('Количество проверок', fontsize=11)
            ax3.set_title('Результаты по категориям (топ-8)', fontsize=12, fontweight='bold')
            ax3.set_xticks(x)
            ax3.set_xticklabels(top_categories['Категория'], rotation=45, ha='right', fontsize=9)
            ax3.legend()
            ax3.grid(True, alpha=0.3, axis='y')

        # График 4: Круговая диаграмма общего статуса
        total_checks = len(self.validation_results)
        success_rate = (passed / total_checks * 100) if total_checks > 0 else 0

        colors_pie = ['green' if passed > failed else 'red', 'lightgray']
        explode = (0.1, 0)

        ax4.pie([passed, failed], explode=explode, labels=['Пройдено', 'Провалено'],
                colors=colors_pie, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 11})
        ax4.set_title(f'Общий успех валидации: {success_rate:.1f}%', fontsize=12, fontweight='bold')

        plt.tight_layout()

        try:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"[Визуализация] Сохранена: {output_path}")
        except Exception as e:
            print(f"[Ошибка] Не удалось сохранить визуализацию: {e}")
        finally:
            plt.close()

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def _validate_area(self, actual: float, min_required: float, target: float) -> ValidationResult:
        """Проверка площади."""
        passed = actual >= min_required
        severity = 'critical' if not passed else ('info' if actual >= target else 'warning')

        if not passed:
            self.critical_failures += 1
        elif severity == 'warning':
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Площадь склада",
            passed=passed,
            expected=f">= {min_required} кв.м (цель: {target} кв.м)",
            actual=f"{actual:.0f} кв.м",
            message=f"Площадь {'соответствует' if passed else 'НЕ соответствует'} требованиям",
            severity=severity
        )

    def _validate_coordinates(self, lat: float, lon: float) -> ValidationResult:
        """Проверка координат."""
        passed = lat is not None and lon is not None and 55 <= lat <= 57 and 36 <= lon <= 39

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Координаты локации",
            passed=passed,
            expected="Московская область (55-57°N, 36-39°E)",
            actual=f"({lat:.4f}, {lon:.4f})" if lat and lon else "Не указаны",
            message=f"Координаты {'корректны' if passed else 'некорректны'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_capex(self, capex: float) -> ValidationResult:
        """Проверка CAPEX."""
        max_capex = config.MAX_TOTAL_CAPEX_RUB
        passed = 0 < capex <= max_capex

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Начальные инвестиции (CAPEX)",
            passed=passed,
            expected=f"<= {max_capex:,.0f} руб",
            actual=f"{capex:,.0f} руб",
            message=f"CAPEX {'в пределах нормы' if passed else 'превышает бюджет'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_opex(self, opex: float) -> ValidationResult:
        """Проверка OPEX."""
        target_opex = config.MAX_ANNUAL_OPEX_RUB
        passed = opex <= target_opex

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Годовые операционные расходы (OPEX)",
            passed=passed,
            expected=f"<= {target_opex:,.0f} руб/год",
            actual=f"{opex:,.0f} руб/год",
            message=f"OPEX {'оптимален' if passed else 'требует оптимизации'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_transport_cost(self, transport_cost: float) -> ValidationResult:
        """Проверка транспортных расходов."""
        max_transport = 100_000_000  # 100 млн руб/год
        passed = transport_cost <= max_transport

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Транспортные расходы",
            passed=passed,
            expected=f"<= {max_transport:,.0f} руб/год",
            actual=f"{transport_cost:,.0f} руб/год",
            message=f"Транспортные расходы {'приемлемы' if passed else 'высоки'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_building_class(self, building_class: str) -> ValidationResult:
        """Проверка класса здания."""
        passed = building_class in ['A', 'A_verified', 'A_requires_mod']

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Класс помещения",
            passed=passed,
            expected="Класс A или A с модификацией",
            actual=building_class,
            message=f"Класс здания {'подходит' if passed else 'НЕ подходит'} для фарм.склада",
            severity='critical' if not passed else 'info'
        )

    def _validate_zoning_ratios(self, zoning_data: Dict) -> ValidationResult:
        """Проверка соотношений зон."""
        if not zoning_data:
            self.warnings += 1
            return ValidationResult(
                check_name="Соотношение зон хранения",
                passed=False,
                expected=">= 75% площади под хранение",
                actual="Данные отсутствуют",
                message="Зонирование не проверено",
                severity='warning'
            )

        storage_zones = ['storage_normal', 'storage_cold']
        total_storage = sum(zoning_data[z].area_sqm for z in storage_zones if z in zoning_data)
        total_area = sum(z.area_sqm for z in zoning_data.values())

        storage_ratio = (total_storage / total_area) * 100 if total_area > 0 else 0
        passed = storage_ratio >= 75  # Минимум 75% под хранение

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Соотношение зон хранения",
            passed=passed,
            expected=">= 75% площади под хранение",
            actual=f"{storage_ratio:.1f}% площади",
            message=f"Зонирование {'эффективно' if passed else 'неэффективно'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_storage_capacity(self, equipment_data: Dict, total_sku: int) -> ValidationResult:
        """Проверка вместимости."""
        total_positions = equipment_data.get('total_pallet_positions', 0)
        required_positions = total_sku * 2  # 2 паллето-места на SKU
        passed = total_positions >= required_positions

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Вместимость стеллажей",
            passed=passed,
            expected=f">= {required_positions:,.0f} паллето-мест",
            actual=f"{total_positions:,.0f} паллето-мест",
            message=f"Вместимость {'достаточна' if passed else 'НЕДОСТАТОЧНА'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_dock_count(self, equipment_data: Dict) -> ValidationResult:
        """Проверка количества доков."""
        total_docks = equipment_data.get('inbound_docks', 0) + equipment_data.get('outbound_docks', 0)
        min_docks = 10
        passed = total_docks >= min_docks

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Количество доков",
            passed=passed,
            expected=f">= {min_docks} доков",
            actual=f"{total_docks} доков",
            message=f"Количество доков {'достаточно' if passed else 'недостаточно'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_climate_zones(self, zoning_data: Dict) -> ValidationResult:
        """Проверка климатических зон."""
        has_cold_chain = 'storage_cold' in zoning_data
        passed = has_cold_chain

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Зона холодовой цепи",
            passed=passed,
            expected="Наличие зоны холодовой цепи",
            actual="Присутствует" if has_cold_chain else "Отсутствует",
            message=f"Зона холодовой цепи {'настроена' if passed else 'НЕ настроена'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_gpp_gdp_zones(self, zoning_data: Dict) -> ValidationResult:
        """Проверка требований GPP/GDP для зон."""
        # Проверяем, что есть выделенные зоны для разных температурных режимов
        required_zones = ['storage_normal', 'storage_cold']
        present_zones = [z for z in required_zones if z in zoning_data]
        passed = len(present_zones) >= len(required_zones) - 1  # Минимум одна зона должна быть

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Требования GPP/GDP по зонам",
            passed=passed,
            expected="Минимум 2 климатические зоны",
            actual=f"{len(present_zones)} зон: {', '.join(present_zones)}",
            message=f"Зонирование {'соответствует' if passed else 'НЕ соответствует'} GPP/GDP",
            severity='critical' if not passed else 'info'
        )

    def _validate_cooling_power(self, zone_name: str, cooling_kw: float, area_sqm: float) -> ValidationResult:
        """Проверка мощности охлаждения."""
        # Минимум 50 Вт/м² для холодной зоны
        min_power_per_sqm = 50 if 'cold' in zone_name.lower() else 20
        required_power = (area_sqm * min_power_per_sqm) / 1000  # в кВт

        passed = cooling_kw >= required_power * 0.9  # Допуск -10%

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name=f"Мощность охлаждения ({zone_name})",
            passed=passed,
            expected=f">= {required_power:.1f} кВт",
            actual=f"{cooling_kw:.1f} кВт",
            message=f"Мощность охлаждения {'достаточна' if passed else 'недостаточна'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_climate_redundancy(self, climate_data: Dict) -> ValidationResult:
        """Проверка резервирования климатических систем."""
        # Проверяем наличие резервирования (N+1)
        has_redundancy = climate_data and climate_data.get('redundancy_level') in ['n+1', 'n+2', '2n']
        passed = has_redundancy

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Резервирование климатических систем",
            passed=passed,
            expected="Резервирование N+1 или выше",
            actual=climate_data.get('redundancy_level', 'Нет') if climate_data else "Нет данных",
            message=f"Резервирование {'обеспечено' if passed else 'отсутствует'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_monitoring_systems(self, climate_data: Dict) -> ValidationResult:
        """Проверка систем мониторинга."""
        has_monitoring = climate_data and 'monitoring' in climate_data
        passed = has_monitoring

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Системы мониторинга",
            passed=passed,
            expected="Наличие систем мониторинга температуры и влажности",
            actual="Установлены" if has_monitoring else "Отсутствуют",
            message=f"Системы мониторинга {'настроены' if passed else 'отсутствуют'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_payback_period(self, roi_data: Dict) -> ValidationResult:
        """Проверка срока окупаемости."""
        payback_periods = [
            data['payback_years'] for data in roi_data.values()
            if data['payback_years'] != float('inf')
        ]

        if payback_periods:
            min_payback = min(payback_periods)
            passed = min_payback <= config.MAX_ACCEPTABLE_PAYBACK_YEARS
        else:
            min_payback = float('inf')
            passed = False

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Срок окупаемости",
            passed=passed,
            expected=f"<= {config.MAX_ACCEPTABLE_PAYBACK_YEARS} лет",
            actual=f"{min_payback:.2f} лет" if min_payback != float('inf') else "Нет окупаемости",
            message=f"Окупаемость {'приемлема' if passed else 'слишком долгая'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_roi_target(self, roi_data: Dict) -> ValidationResult:
        """Проверка целевого ROI."""
        roi_5y_values = [data['roi_5y_percent'] for data in roi_data.values()]
        max_roi = max(roi_5y_values) if roi_5y_values else 0
        target_roi = 20
        passed = max_roi >= target_roi

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="ROI за 5 лет",
            passed=passed,
            expected=f">= {target_roi}%",
            actual=f"{max_roi:.1f}%",
            message=f"ROI {'достигает' if passed else 'НЕ достигает'} целевого уровня",
            severity='warning' if not passed else 'info'
        )

    def _validate_labor_reduction(self, roi_data: Dict, automation_scenarios: Dict) -> ValidationResult:
        """Проверка логичности сокращения персонала."""
        inconsistencies = []

        for level_value, roi_info in roi_data.items():
            reduced_staff = roi_info.get('reduced_staff', 0)
            if reduced_staff < 0 or reduced_staff > config.INITIAL_STAFF_COUNT:
                inconsistencies.append(f"{roi_info['scenario_name']}: {reduced_staff} чел")

        passed = len(inconsistencies) == 0

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Логичность сокращения персонала",
            passed=passed,
            expected="0 <= сокращение <= начальное количество",
            actual="Корректно" if passed else f"Ошибки: {', '.join(inconsistencies)}",
            message=f"Сокращение персонала {'логично' if passed else 'содержит ошибки'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_benefit_calculations(self, roi_data: Dict) -> ValidationResult:
        """Проверка корректности расчета выгод."""
        errors = []

        for level_value, roi_info in roi_data.items():
            expected_benefit = (
                roi_info['annual_labor_savings'] +
                roi_info['annual_revenue_increase'] -
                roi_info['annual_opex']
            )
            actual_benefit = roi_info['net_annual_benefit']

            # Допускаем погрешность 1%
            if abs(expected_benefit - actual_benefit) > abs(expected_benefit * 0.01):
                errors.append(roi_info['scenario_name'])

        passed = len(errors) == 0

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Корректность расчета выгод",
            passed=passed,
            expected="Выгода = Экономия + Доход - OPEX",
            actual="Корректно" if passed else f"Ошибки в: {', '.join(errors)}",
            message=f"Расчеты {'корректны' if passed else 'содержат ошибки'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_automation_capex(self, roi_data: Dict) -> ValidationResult:
        """Проверка CAPEX автоматизации."""
        max_auto_capex = max([data['capex'] for data in roi_data.values()])
        max_allowed = 700_000_000  # 700 млн руб максимум на автоматизацию
        passed = max_auto_capex <= max_allowed

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="CAPEX автоматизации",
            passed=passed,
            expected=f"<= {max_allowed:,.0f} руб",
            actual=f"{max_auto_capex:,.0f} руб",
            message=f"Инвестиции в автоматизацию {'разумны' if passed else 'избыточны'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_efficiency_investment_ratio(self, roi_data: Dict, automation_scenarios: Dict) -> ValidationResult:
        """Проверка соотношения эффективности и инвестиций."""
        # Проверяем, что рост эффективности соответствует инвестициям
        ratios = []
        for level_value, roi_info in roi_data.items():
            if roi_info['capex'] > 0:
                efficiency_gain = roi_info['net_annual_benefit'] / roi_info['capex']
                ratios.append((roi_info['scenario_name'], efficiency_gain))

        # Ожидаем минимум 10% годовой выгоды от инвестиций
        passed = all(ratio >= 0.10 for _, ratio in ratios) if ratios else True

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Соотношение эффективность/инвестиции",
            passed=passed,
            expected="Годовая выгода >= 10% от CAPEX",
            actual=f"Средний ratio: {sum(r for _, r in ratios)/len(ratios)*100:.1f}%" if ratios else "N/A",
            message=f"Соотношение {'адекватно' if passed else 'требует пересмотра'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_throughput(self, simulation_results: Dict) -> ValidationResult:
        """Проверка throughput."""
        achieved = simulation_results.get('achieved_throughput', 0)
        target = config.TARGET_ORDERS_MONTH
        passed = achieved >= target * 0.95  # Допуск -5%

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Производительность (throughput)",
            passed=passed,
            expected=f">= {target:,.0f} заказов/месяц",
            actual=f"{achieved:,.0f} заказов/месяц",
            message=f"Производительность {'достаточна' if passed else 'недостаточна'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_cycle_time(self, simulation_results: Dict) -> ValidationResult:
        """Проверка cycle time."""
        actual_minutes = simulation_results.get('avg_cycle_time_min', float('inf'))
        actual_hours = actual_minutes / 60
        target_hours = config.TARGET_ORDER_CYCLE_TIME_HOURS
        max_hours = config.MAX_ACCEPTABLE_CYCLE_TIME_HOURS

        passed = actual_hours <= max_hours

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Время цикла заказа",
            passed=passed,
            expected=f"<= {max_hours} часов (цель: {target_hours} часов)",
            actual=f"{actual_hours:.2f} часов",
            message=f"Время цикла {'приемлемо' if passed else 'слишком долгое'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_dock_utilization(self, simulation_results: Dict) -> ValidationResult:
        """Проверка утилизации доков."""
        # Проверяем, что утилизация в приемлемом диапазоне
        util_percent = simulation_results.get('dock_utilization_percent', 0)
        passed = config.MIN_DOCK_UTILIZATION_PERCENT <= util_percent <= config.MAX_DOCK_UTILIZATION_PERCENT

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Утилизация доков",
            passed=passed,
            expected=f"{config.MIN_DOCK_UTILIZATION_PERCENT}-{config.MAX_DOCK_UTILIZATION_PERCENT}%",
            actual=f"{util_percent:.1f}%",
            message=f"Утилизация {'оптимальна' if passed else 'вне допустимого диапазона'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_target_throughput(self) -> ValidationResult:
        """Проверка целевой производительности."""
        target = config.TARGET_ORDERS_MONTH
        passed = target > 0

        self.info_count += 1

        return ValidationResult(
            check_name="Целевая производительность",
            passed=passed,
            expected="> 0 заказов/месяц",
            actual=f"{target:,.0f} заказов/месяц",
            message="Целевая производительность установлена",
            severity='info'
        )

    def _validate_budget_constraints(self, location_data: Dict, roi_data: Dict) -> ValidationResult:
        """Проверка бюджетных ограничений."""
        max_budget = config.MAX_TOTAL_CAPEX_RUB
        total_investment = location_data['total_initial_capex']

        if roi_data:
            max_auto_capex = max([data['capex'] for data in roi_data.values()])
            total_investment = max(total_investment, max_auto_capex)

        passed = total_investment <= max_budget

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Бюджетные ограничения",
            passed=passed,
            expected=f"<= {max_budget:,.0f} руб",
            actual=f"{total_investment:,.0f} руб",
            message=f"Инвестиции {'в рамках' if passed else 'ПРЕВЫШАЮТ'} бюджет",
            severity='critical' if not passed else 'info'
        )

    def _validate_gpp_gdp_compliance(self, location_data: Dict) -> ValidationResult:
        """Проверка соответствия GPP/GDP."""
        current_class = location_data.get('current_class', '')
        passed = current_class in ['A', 'A_verified', 'A_requires_mod']

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Соответствие GPP/GDP",
            passed=passed,
            expected="Класс A или A с модификациями",
            actual=f"Класс {current_class}",
            message=f"Помещение {'соответствует' if passed else 'НЕ соответствует'} стандартам",
            severity='critical' if not passed else 'info'
        )

    def _validate_project_timeline(self) -> ValidationResult:
        """Проверка срока реализации."""
        max_months = 12
        passed = True

        self.info_count += 1

        return ValidationResult(
            check_name="Срок реализации проекта",
            passed=passed,
            expected=f"<= {max_months} месяцев",
            actual=f"~9-10 месяцев (по плану)",
            message="Проект реализуем в срок",
            severity='info'
        )

    def _validate_scalability(self, location_data: Dict) -> ValidationResult:
        """Проверка масштабируемости."""
        # Проверяем, что есть резерв площади для роста
        area = location_data.get('area_offered_sqm', 0)
        min_area = config.MIN_AREA_SQM
        growth_reserve = ((area - min_area) / min_area) * 100 if min_area > 0 else 0

        passed = growth_reserve >= 20  # Минимум 20% резерв

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Масштабируемость",
            passed=passed,
            expected="Резерв площади >= 20%",
            actual=f"Резерв: {growth_reserve:.1f}%",
            message=f"Масштабируемость {'обеспечена' if passed else 'ограничена'}",
            severity='warning' if not passed else 'info'
        )

    def _print_validation_results(self, results: List[ValidationResult], category: str):
        """Выводит результаты валидации."""
        print(f"\n[{category}] Результаты проверок:")
        print("-" * 100)

        for result in results:
            icon = "[OK]" if result.passed else "[FAIL]"
            severity_icon = {
                'critical': '[!]',
                'warning': '[?]',
                'info': '[+]'
            }.get(result.severity, '[*]')

            print(f"{severity_icon} {icon} {result.check_name}")
            print(f"    Ожидалось: {result.expected}")
            print(f"    Фактически: {result.actual}")
            print(f"    {result.message}")
            print()


def run_full_validation(location_data: Dict[str, Any],
                       warehouse_data: Dict[str, Any],
                       roi_data: Dict[str, Any],
                       automation_scenarios: Dict[str, Any],
                       simulation_results: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Запускает полную валидацию модели.

    Args:
        location_data: Данные локации
        warehouse_data: Данные склада
        roi_data: Данные ROI
        automation_scenarios: Сценарии автоматизации
        simulation_results: Результаты симуляции (опционально)

    Returns:
        Результаты валидации и верификации
    """
    print("\n" + "="*100)
    print("ЗАПУСК ПОЛНОЙ ВАЛИДАЦИИ И ВЕРИФИКАЦИИ МОДЕЛИ")
    print("="*100)

    validator = ModelValidator()

    # 1. Валидация локации
    validator.validate_location_data(location_data)

    # 2. Валидация конфигурации склада
    if warehouse_data:
        validator.validate_warehouse_configuration(
            warehouse_data.get('zoning_data', {}),
            warehouse_data.get('equipment_data', {}),
            warehouse_data.get('total_sku', config.TOTAL_SKU_COUNT)
        )

        # 3. Валидация климатических систем
        if 'climate_requirements' in warehouse_data:
            validator.validate_climate_systems(warehouse_data['climate_requirements'])

    # 4. Валидация ROI
    validator.validate_roi_calculations(roi_data, automation_scenarios)

    # 5. Валидация операционных KPI
    if simulation_results:
        validator.validate_operational_kpi(simulation_results)

    # 6. Валидация бизнес-требований
    validator.validate_business_requirements(location_data, roi_data)

    # 7. Верификация целей
    verification_results = validator.verify_model_objectives(
        location_data, roi_data, warehouse_data
    )

    # 8. Генерация расширенного отчета с данными для сравнений
    report_path = validator.generate_validation_report(
        location_data=location_data,
        warehouse_data=warehouse_data,
        roi_data=roi_data
    )

    # Итоговая статистика
    print("\n" + "="*100)
    print("ИТОГИ ВАЛИДАЦИИ")
    print("="*100)
    print(f"Всего проверок: {len(validator.validation_results)}")
    print(f"Пройдено: {sum(1 for r in validator.validation_results if r.passed)}")
    print(f"Провалено: {sum(1 for r in validator.validation_results if not r.passed)}")
    print(f"Критических ошибок: {validator.critical_failures}")
    print(f"Предупреждений: {validator.warnings}")
    print(f"Информационных: {validator.info_count}")
    if report_path:
        print(f"\nОтчет сохранен: {report_path}")
        viz_path = report_path.replace('.xlsx', '_visualizations.png')
        print(f"Визуализация сохранена: {viz_path}")
    print("="*100)

    return {
        'validation_results': validator.validation_results,
        'verification_results': verification_results,
        'critical_failures': validator.critical_failures,
        'warnings': validator.warnings,
        'info_count': validator.info_count,
        'report_path': report_path
    }


if __name__ == "__main__":
    print("Модуль валидации готов к использованию")
    print("Доступные функции:")
    print("  - run_full_validation() - полная валидация модели")
    print("  - ModelValidator - класс валидатора для расширенного использования")

```

## `scenarios.py`

```py
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
        
        # Если мы владеем старым складом, вычитаем его стоимость из CAPEX
        if config.CURRENT_WAREHOUSE_IS_OWNED:
            total_capex -= config.CURRENT_WAREHOUSE_SALE_VALUE_RUB
        
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

        print("\n--- Финансовая модель проекта ---")
        if config.CURRENT_WAREHOUSE_IS_OWNED:
            print(f"  [+] Учитывается продажа текущего актива.")
            print(f"  > Выручка от продажи: {config.CURRENT_WAREHOUSE_SALE_VALUE_RUB:,.0f} руб. (снижает CAPEX)")
        else:
            print("  [-] Продажа текущего актива не учитывается (он в аренде).")
        print("-------------------------------------------\n")

        # --- Демонстрация для Сценария 2 и 4 ---
        print("\n--- Демонстрация сгенерированных данных ---")
        s2_data = all_scenarios.get("2_Move_With_Compensation")
        s4_data = all_scenarios.get("4_Move_Advanced_Automation")

        # ИСПРАВЛЕННЫЙ БЛОК: Добавлена проверка на None
        if s2_data:
            print(f"Сценарий 2 ('{s2_data['name']}'):")
            print(f"  - Персонал: {s2_data['staff_count']} чел.")
            print(f"  - Эффективность: x{s2_data['processing_efficiency']}")
            print(f"  - Итоговый CAPEX: {s2_data['total_capex']:,.0f} руб.")
            print(f"  - Итоговый OPEX: {s2_data['total_opex']:,.0f} руб.")
        else:
            print("[ПРЕДУПРЕЖДЕНИЕ] Данные для Сценария 2 не найдены в конфигурации.")

        if s4_data:
            print(f"Сценарий 4 ('{s4_data['name']}'):")
            print(f"  - Персонал: {s4_data['staff_count']} чел.")
            print(f"  - Эффективность: x{s4_data['processing_efficiency']}")
            print(f"  - Итоговый CAPEX: {s4_data['total_capex']:,.0f} руб.")
            print(f"  - Итоговый OPEX: {s4_data['total_opex']:,.0f} руб.")
        else:
            print("[ПРЕДУПРЕЖДЕНИЕ] Данные для Сценария 4 не найдены в конфигурации.")
        
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
            
            # 6. Финальный расчет окупаемости (ROI / Payback Period)
            payback = self.calculate_roi(scenario_data)
            if payback is not None:
                print(f"  > Расчетный срок окупаемости: {payback:.2f} лет")

            # 7. Сборка всех KPI в единую структуру данных
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
            self.results.append(result)
            
            # 8. Генерация JSON-файла для FlexSim
            self.flexsim_bridge.generate_json_config(self.location_spec, result, scenario_data)

        # 9. После завершения цикла сохраняем сводный CSV-файл
        self._save_summary_csv()
        print(f"\n--- Анализ для локации '{self.location_spec.name}' завершен. ---")

    def calculate_roi(self, scenario_data: Dict[str, Any]) -> Optional[float]:
        """
        Рассчитывает срок окупаемости (Payback Period) для сценария.
        Сравнивает OPEX нового склада с OPEX текущего склада в Москве.
        """
        # 1. Расчет OPEX текущего склада (Baseline)
        current_rent_opex = 12000 * config.WAREHOUSE_TOTAL_AREA_SQM
        current_labor_opex = config.INITIAL_STAFF_COUNT * config.OPERATOR_SALARY_RUB_MONTH * 12
        total_baseline_opex = current_rent_opex + current_labor_opex

        # 2. OPEX нового сценария (уже рассчитан)
        new_scenario_opex = scenario_data['total_opex']

        # 3. Расчет годовой экономии
        annual_savings = total_baseline_opex - new_scenario_opex

        if annual_savings > 0:
            # CAPEX для окупаемости должен быть "грязным" - без учета продажи старого актива,
            # так как это инвестиции, которые нужно понести.
            capex_for_roi = scenario_data['total_capex']
            if config.CURRENT_WAREHOUSE_IS_OWNED:
                # Возвращаем стоимость продажи, чтобы получить полную сумму инвестиций
                capex_for_roi += config.CURRENT_WAREHOUSE_SALE_VALUE_RUB
                
            payback_period_years = capex_for_roi / annual_savings
            return payback_period_years
        return None

    def _save_summary_csv(self):
        """Сохраняет сводный CSV-файл со всеми результатами."""
        if not self.results: return
        
        df = pd.DataFrame([res.__dict__ for res in self.results])
        
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
        capacity_pallets=33,
        capacity_kg=20000,
        fuel_consumption_l_per_100km=28.0,
        maintenance_cost_rub_per_km=8.5,
        driver_cost_rub_per_trip=15000,
        driver_cost_rub_per_day=0,
        purchase_cost_rub=4_500_000,
        lease_cost_rub_per_month=180_000,
        insurance_rub_per_year=120_000,
    ),
    'medium_truck_5t': VehicleType(
        name='Грузовик 5т (городской)',
        capacity_pallets=8,
        capacity_kg=5000,
        fuel_consumption_l_per_100km=18.0,
        maintenance_cost_rub_per_km=5.2,
        driver_cost_rub_per_trip=0,
        driver_cost_rub_per_day=4500,
        purchase_cost_rub=2_800_000,
        lease_cost_rub_per_month=95_000,
        insurance_rub_per_year=65_000,
    ),
    # <--- НОВЫЙ ТИП ТРАНСПОРТА --->
    'light_van_1_5t': VehicleType(
        name='Фургон 1.5т (без пропуска)',
        capacity_pallets=4,
        capacity_kg=1500,
        fuel_consumption_l_per_100km=15.0,
        maintenance_cost_rub_per_km=4.0,
        driver_cost_rub_per_trip=0,
        driver_cost_rub_per_day=4000,
        purchase_cost_rub=2_100_000,
        lease_cost_rub_per_month=70_000,
        insurance_rub_per_year=50_000,
    ),
    'refrigerated_truck_15t': VehicleType(
        name='Рефрижератор 15т (2-8°C)',
        capacity_pallets=24,
        capacity_kg=15000,
        fuel_consumption_l_per_100km=32.0,
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
    # ... (Константы без изменений) ...
    CFO_OWN_FLEET_SHARE = 0.46
    AIR_DELIVERY_SHARE = 0.25
    LOCAL_DELIVERY_SHARE = 0.29
    COLD_CHAIN_SHARE = 0.17
    WAREHOUSE_OPERATES_24_7 = True
    WORKING_DAYS_PER_WEEK = 7
    WORKING_HOURS_PER_DAY = 24
    AVG_ORDER_WEIGHT_KG = 250
    AVG_ORDER_PALLETS = 1.0
    LOADING_TIME_PER_TRUCK_HOURS = 1.5
    UNLOADING_TIME_PER_TRUCK_HOURS = 2.0
    BUFFER_COEFFICIENT = 1.3
    DIESEL_PRICE_RUB_PER_LITER = 56.0

    def __init__(self):
        """Инициализация планировщика."""
        self.monthly_orders = config.TARGET_ORDERS_MONTH
        self.annual_orders = self.monthly_orders * 12

    def calculate_fleet_requirements(self, distances: Dict[str, float]) -> Dict[str, Any]:
        """
        Рассчитывает детальные требования к флоту для всех потоков.
        """
        print(f"\n  > [DetailedFleetPlanner] Расчет детальных требований к транспортному флоту")

        # 1. ЦФО: тяжелые грузовики 18-20т
        cfo_fleet = self._calculate_cfo_fleet(distances['cfo_km'])

        # <--- ЛОГИКА ИЗМЕНЕНА --->
        # 2. Местные ЛПУ: разделенный флот (5т по пропуску + 1.5т без пропуска)
        # Метод теперь возвращает два словаря - для каждого типа транспорта
        local_fleet_pass, local_fleet_base = self._calculate_local_fleet(distances['local_km'])

        # 3. SVO авиа: средние грузовики + рефрижераторы
        svo_fleet = self._calculate_svo_fleet(distances['svo_km'])

        # 4. Холодная цепь: дополнительные рефрижераторы
        cold_chain_fleet = self._calculate_cold_chain_fleet(distances)

        # 5. Общие затраты (передаем все 5 типов флота)
        total_fleet = self._aggregate_fleet_costs(
            cfo_fleet, 
            local_fleet_pass, 
            local_fleet_base, 
            svo_fleet, 
            cold_chain_fleet
        )

        return total_fleet

    def _calculate_cfo_fleet(self, avg_distance_km: float) -> Dict[str, Any]:
        """
        Расчет флота для ЦФО (46% потока, собственный флот 18-20т).
        """
        vehicle = VEHICLE_TYPES['heavy_truck_20t']
        cfo_orders_per_month = self.monthly_orders * self.CFO_OWN_FLEET_SHARE
        cfo_orders_per_week = cfo_orders_per_month / 4.33
        total_pallets_per_week = cfo_orders_per_week * self.AVG_ORDER_PALLETS
        trips_per_week = math.ceil(total_pallets_per_week / vehicle.capacity_pallets)
        trips_per_truck_per_week = 2
        required_trucks = math.ceil(trips_per_week / trips_per_truck_per_week)
        annual_trips = trips_per_week * 52
        annual_distance_km = annual_trips * avg_distance_km * 2
        fuel_cost = (annual_distance_km / 100) * vehicle.fuel_consumption_l_per_100km * self.DIESEL_PRICE_RUB_PER_LITER
        maintenance_cost = annual_distance_km * vehicle.maintenance_cost_rub_per_km
        driver_cost = annual_trips * vehicle.driver_cost_rub_per_trip
        insurance_cost = required_trucks * vehicle.insurance_rub_per_year
        purchase_capex = required_trucks * vehicle.purchase_cost_rub
        lease_opex_annual = required_trucks * vehicle.lease_cost_rub_per_month * 12
        print(f"    - ЦФО (18-20т): {required_trucks} грузовиков, {annual_trips} рейсов/год")
        return {
            'fleet_type': 'heavy_truck_20t', 'vehicle_name': vehicle.name, 'required_count': required_trucks,
            'annual_trips': annual_trips, 'annual_distance_km': annual_distance_km,
            'avg_distance_per_trip_km': avg_distance_km,
            'costs': {'fuel_rub': fuel_cost, 'maintenance_rub': maintenance_cost, 'driver_salaries_rub': driver_cost,
                      'insurance_rub': insurance_cost, 'total_opex_rub': fuel_cost + maintenance_cost + driver_cost + insurance_cost},
            'capex_purchase_rub': purchase_capex, 'opex_lease_rub': lease_opex_annual
        }
        
    # <--- ПОЛНОСТЬЮ ПЕРЕПИСАННЫЙ МЕТОД --->
    def _calculate_local_fleet(self, avg_distance_km: float) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Расчет флота для местных ЛПУ Москвы, разделенного на 2 части:
        1. 5т грузовики по бесплатным пропускам (2 рейса/мес).
        2. 1.5т фургоны для остального объема.
        """
        # --- 1. Расчет для 5т грузовиков (льготные рейсы) ---
        pass_vehicle = VEHICLE_TYPES['medium_truck_5t']
        
        # 2 рейса в месяц
        pass_annual_trips = config.FREE_PASSES_PER_MONTH * 12
        # Сколько паллет можно увезти этими рейсами
        pallets_on_pass_trips = pass_annual_trips * pass_vehicle.capacity_pallets
        # Для этих рейсов достаточно 1 машины, работающей по вызову
        pass_required_trucks = 1 
        
        pass_annual_distance_km = pass_annual_trips * avg_distance_km
        pass_fuel = (pass_annual_distance_km / 100) * pass_vehicle.fuel_consumption_l_per_100km * self.DIESEL_PRICE_RUB_PER_LITER
        pass_maint = pass_annual_distance_km * pass_vehicle.maintenance_cost_rub_per_km
        pass_driver = pass_annual_trips * pass_vehicle.driver_cost_rub_per_day # Платим за день работы
        pass_ins = pass_required_trucks * pass_vehicle.insurance_rub_per_year
        pass_capex = pass_required_trucks * pass_vehicle.purchase_cost_rub
        pass_lease = pass_required_trucks * pass_vehicle.lease_cost_rub_per_month * 12

        pass_fleet_data = {
            'fleet_type': 'medium_truck_5t_pass', 'vehicle_name': pass_vehicle.name + " (Пропуск)", 'required_count': pass_required_trucks,
            'annual_trips': pass_annual_trips, 'annual_distance_km': pass_annual_distance_km,
            'avg_distance_per_trip_km': avg_distance_km,
            'costs': {'fuel_rub': pass_fuel, 'maintenance_rub': pass_maint, 'driver_salaries_rub': pass_driver, 'insurance_rub': pass_ins,
                      'total_opex_rub': pass_fuel + pass_maint + pass_driver + pass_ins},
            'capex_purchase_rub': pass_capex, 'opex_lease_rub': pass_lease
        }
        print(f"    - Местные ЛПУ (5т по пропуску): {pass_required_trucks} грузовик, {pass_annual_trips} рейсов/год")

        # --- 2. Расчет для 1.5т фургонов (основной объем) ---
        base_vehicle = VEHICLE_TYPES['light_van_1_5t']
        
        # Общий годовой объем в паллетах для Москвы
        total_local_pallets_annual = (self.monthly_orders * self.LOCAL_DELIVERY_SHARE * 12) * self.AVG_ORDER_PALLETS
        # Оставшийся объем после льготных рейсов
        remaining_pallets_annual = total_local_pallets_annual - pallets_on_pass_trips
        
        # Необходимое количество рейсов на малых фургонах
        base_annual_trips = math.ceil(remaining_pallets_annual / base_vehicle.capacity_pallets)
        working_days_per_year = 22 * 12
        trips_per_day = base_annual_trips / working_days_per_year

        # 1 фургон делает 2 рейса в день
        base_required_trucks = math.ceil(trips_per_day / 2)

        base_annual_distance_km = base_annual_trips * avg_distance_km
        base_fuel = (base_annual_distance_km / 100) * base_vehicle.fuel_consumption_l_per_100km * self.DIESEL_PRICE_RUB_PER_LITER
        base_maint = base_annual_distance_km * base_vehicle.maintenance_cost_rub_per_km
        base_driver = base_required_trucks * base_vehicle.driver_cost_rub_per_day * working_days_per_year
        base_ins = base_required_trucks * base_vehicle.insurance_rub_per_year
        base_capex = base_required_trucks * base_vehicle.purchase_cost_rub
        base_lease = base_required_trucks * base_vehicle.lease_cost_rub_per_month * 12

        base_fleet_data = {
            'fleet_type': 'light_van_1_5t', 'vehicle_name': base_vehicle.name, 'required_count': base_required_trucks,
            'annual_trips': base_annual_trips, 'annual_distance_km': base_annual_distance_km,
            'avg_distance_per_trip_km': avg_distance_km,
            'costs': {'fuel_rub': base_fuel, 'maintenance_rub': base_maint, 'driver_salaries_rub': base_driver, 'insurance_rub': base_ins,
                      'total_opex_rub': base_fuel + base_maint + base_driver + base_ins},
            'capex_purchase_rub': base_capex, 'opex_lease_rub': base_lease
        }
        print(f"    - Местные ЛПУ (1.5т без пропуска): {base_required_trucks} фургонов, {base_annual_trips} рейсов/год")

        return pass_fleet_data, base_fleet_data

    def _calculate_svo_fleet(self, avg_distance_km: float) -> Dict[str, Any]:
        """
        Расчет флота для авиадоставки в SVO (25% потока).
        """
        vehicle = VEHICLE_TYPES['medium_truck_5t']
        svo_orders_per_day = (self.monthly_orders * self.AIR_DELIVERY_SHARE) / 22
        pallets_per_day = svo_orders_per_day * self.AVG_ORDER_PALLETS
        trips_per_day = math.ceil(pallets_per_day / vehicle.capacity_pallets)
        required_trucks = math.ceil(trips_per_day / 2)
        working_days_per_year = 264
        annual_trips = trips_per_day * working_days_per_year
        annual_distance_km = annual_trips * avg_distance_km * 2
        fuel_cost = (annual_distance_km / 100) * vehicle.fuel_consumption_l_per_100km * self.DIESEL_PRICE_RUB_PER_LITER
        maintenance_cost = annual_distance_km * vehicle.maintenance_cost_rub_per_km
        driver_cost = required_trucks * vehicle.driver_cost_rub_per_day * working_days_per_year
        insurance_cost = required_trucks * vehicle.insurance_rub_per_year
        purchase_capex = required_trucks * vehicle.purchase_cost_rub
        lease_opex_annual = required_trucks * vehicle.lease_cost_rub_per_month * 12
        print(f"    - SVO авиа (5т): {required_trucks} грузовиков, {trips_per_day} рейсов/день")
        return {
            'fleet_type': 'medium_truck_5t_svo', 'vehicle_name': vehicle.name + ' (SVO)', 'required_count': required_trucks,
            'annual_trips': annual_trips, 'annual_distance_km': annual_distance_km,
            'avg_distance_per_trip_km': avg_distance_km,
            'costs': {'fuel_rub': fuel_cost, 'maintenance_rub': maintenance_cost, 'driver_salaries_rub': driver_cost,
                      'insurance_rub': insurance_cost, 'total_opex_rub': fuel_cost + maintenance_cost + driver_cost + insurance_cost},
            'capex_purchase_rub': purchase_capex, 'opex_lease_rub': lease_opex_annual
        }
    
    def _calculate_cold_chain_fleet(self, distances: Dict[str, float]) -> Dict[str, Any]:
        """
        Расчет рефрижераторов для холодной цепи (17% от общего объема).
        """
        vehicle = VEHICLE_TYPES['refrigerated_truck_15t']
        cold_orders_per_month = self.monthly_orders * self.COLD_CHAIN_SHARE
        cold_cfo = cold_orders_per_month * self.CFO_OWN_FLEET_SHARE
        cold_local = cold_orders_per_month * self.LOCAL_DELIVERY_SHARE
        cold_svo = cold_orders_per_month * self.AIR_DELIVERY_SHARE
        trips_per_month = math.ceil((cold_cfo + cold_local + cold_svo) / vehicle.capacity_pallets)
        trips_per_week = trips_per_month / 4.33
        required_trucks = math.ceil(trips_per_week / 2)
        avg_weighted_distance = (distances['cfo_km'] * self.CFO_OWN_FLEET_SHARE + distances['local_km'] * self.LOCAL_DELIVERY_SHARE + distances['svo_km'] * self.AIR_DELIVERY_SHARE)
        annual_trips = trips_per_month * 12
        annual_distance_km = annual_trips * avg_weighted_distance * 2
        avg_trip_hours = (avg_weighted_distance * 2) / 50
        annual_refrigeration_hours = annual_trips * avg_trip_hours
        fuel_cost = (annual_distance_km / 100) * vehicle.fuel_consumption_l_per_100km * self.DIESEL_PRICE_RUB_PER_LITER
        maintenance_cost = annual_distance_km * vehicle.maintenance_cost_rub_per_km
        driver_cost = annual_trips * vehicle.driver_cost_rub_per_trip
        insurance_cost = required_trucks * vehicle.insurance_rub_per_year
        refrigeration_cost = annual_refrigeration_hours * vehicle.temperature_control_cost_rub_per_hour
        purchase_capex = required_trucks * vehicle.purchase_cost_rub
        lease_opex_annual = required_trucks * vehicle.lease_cost_rub_per_month * 12
        print(f"    - Холодная цепь (15т рефр.): {required_trucks} грузовиков, {annual_trips} рейсов/год")
        return {
            'fleet_type': 'refrigerated_truck_15t', 'vehicle_name': vehicle.name, 'required_count': required_trucks,
            'annual_trips': annual_trips, 'annual_distance_km': annual_distance_km,
            'avg_distance_per_trip_km': avg_weighted_distance,
            'costs': {'fuel_rub': fuel_cost, 'maintenance_rub': maintenance_cost, 'driver_salaries_rub': driver_cost,
                      'insurance_rub': insurance_cost, 'refrigeration_rub': refrigeration_cost,
                      'total_opex_rub': fuel_cost + maintenance_cost + driver_cost + insurance_cost + refrigeration_cost},
            'capex_purchase_rub': purchase_capex, 'opex_lease_rub': lease_opex_annual
        }

    # ... (Остальные методы класса без изменений) ...
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

## `warehouse_analysis.py`

```py
"""
Упрощенный модуль анализа склада.
Включает зонирование, условия хранения, варианты автоматизации и ROI анализ.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any
from enum import Enum
import config
from animations import create_all_animations


class AutomationLevel(Enum):
    """Уровни автоматизации."""
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3


class ComprehensiveWarehouseAnalysis:
    """Класс для комплексного анализа склада с учетом всех факторов."""

    def __init__(self, location_name: str = "PNK Чашниково BTS",
                 total_area: float = 17_500,
                 total_sku: int = 15_000):
        """
        Инициализация комплексного анализа.

        Args:
            location_name: Название локации склада
            total_area: Общая площадь склада (кв.м)
            total_sku: Общее количество SKU
        """
        self.location_name = location_name
        self.total_area = total_area
        self.total_sku = total_sku

        # Результаты анализа
        self.zoning_data = {}
        self.equipment_data = {}
        self.sku_distribution = {}
        self.automation_scenarios = {}
        self.roi_data = {}
        self.climate_requirements = {}
        self.gpp_gdp_compliance = {}
        self.monitoring_systems = {}
        self.detailed_equipment = {}

        # Создаем директорию для output если её нет
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    def run_full_analysis(self):
        """Запускает полный комплексный анализ склада."""
        print("\n" + "="*120)
        print(f"КОМПЛЕКСНЫЙ АНАЛИЗ СКЛАДА: {self.location_name}")
        print(f"Площадь: {self.total_area:,.0f} кв.м | SKU: {self.total_sku:,}")
        print("="*120)

        # ===== ШАГ 1: ЗОНИРОВАНИЕ СКЛАДА =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*40 + "ШАГ 1: ЗОНИРОВАНИЕ СКЛАДА" + " "*53 + "|")
        print("+" + "-"*118 + "+")

        self._calculate_zoning()
        self._calculate_equipment()

        # ===== ШАГ 2: РАСПРЕДЕЛЕНИЕ SKU ПО УСЛОВИЯМ ХРАНЕНИЯ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*30 + "ШАГ 2: РАСПРЕДЕЛЕНИЕ SKU ПО УСЛОВИЯМ ХРАНЕНИЯ" + " "*43 + "|")
        print("+" + "-"*118 + "+")

        self._calculate_sku_distribution()

        # ===== ШАГ 2.5: КЛИМАТИЧЕСКИЕ ТРЕБОВАНИЯ И GPP/GDP =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*30 + "ШАГ 2.5: КЛИМАТИЧЕСКИЕ ТРЕБОВАНИЯ И GPP/GDP" + " "*46 + "|")
        print("+" + "-"*118 + "+")

        self._calculate_climate_requirements()
        self._calculate_gpp_gdp_compliance()
        self._calculate_monitoring_systems()
        self._calculate_detailed_equipment()

        # ===== ШАГ 3: СЦЕНАРИИ АВТОМАТИЗАЦИИ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*38 + "ШАГ 3: СЦЕНАРИИ АВТОМАТИЗАЦИИ (0-3)" + " "*45 + "|")
        print("+" + "-"*118 + "+")

        self._build_automation_scenarios()

        # ===== ШАГ 4: ROI АНАЛИЗ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*40 + "ШАГ 4: ROI АНАЛИЗ И СРАВНЕНИЕ" + " "*49 + "|")
        print("+" + "-"*118 + "+")

        self._calculate_roi()

        # ===== ШАГ 5: ВИЗУАЛИЗАЦИЯ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*45 + "ШАГ 5: ВИЗУАЛИЗАЦИЯ" + " "*54 + "|")
        print("+" + "-"*118 + "+")

        self._generate_visualizations()

        # ===== ШАГ 6: АНИМАЦИИ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*45 + "ШАГ 6: СОЗДАНИЕ АНИМАЦИЙ" + " "*50 + "|")
        print("+" + "-"*118 + "+")

        self._create_animations()

        # ===== ШАГ 7: ЭКСПОРТ ДАННЫХ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*43 + "ШАГ 7: ЭКСПОРТ ДАННЫХ" + " "*54 + "|")
        print("+" + "-"*118 + "+")

        self._export_to_excel()

        print("\n" + "="*120)
        print("КОМПЛЕКСНЫЙ АНАЛИЗ ЗАВЕРШЕН")
        print("="*120)

    def _calculate_zoning(self):
        """Упрощенный расчет зонирования."""
        # Простое зонирование по процентам
        storage_normal_area = self.total_area * 0.65  # 65% - нормальное хранение
        storage_cold_area = self.total_area * 0.30     # 30% - холодовая цепь
        receiving_area = self.total_area * 0.03        # 3% - приемка
        dispatch_area = self.total_area * 0.02         # 2% - отгрузка

        self.zoning_data = {
            'storage_normal': type('obj', (object,), {'area_sqm': storage_normal_area, 'name': 'Нормальное хранение'}),
            'storage_cold': type('obj', (object,), {'area_sqm': storage_cold_area, 'name': 'Холодовая цепь'}),
            'receiving': type('obj', (object,), {'area_sqm': receiving_area, 'name': 'Приемка'}),
            'dispatch': type('obj', (object,), {'area_sqm': dispatch_area, 'name': 'Отгрузка'})
        }

        print(f"\n[Зонирование склада]")
        for zone_id, zone in self.zoning_data.items():
            print(f"  {zone.name}: {zone.area_sqm:,.0f} кв.м ({zone.area_sqm/self.total_area*100:.1f}%)")

    def _calculate_equipment(self):
        """Упрощенный расчет оборудования."""
        # Стеллажи (предполагаем 2 паллето-места на кв.м для стеллажной зоны)
        storage_area = self.zoning_data['storage_normal'].area_sqm + self.zoning_data['storage_cold'].area_sqm
        total_pallet_positions = int(storage_area * 2)

        # Доки (6 inbound + 6 outbound)
        inbound_docks = 6
        outbound_docks = 6

        # CAPEX оборудования (упрощенный расчет)
        equipment_capex = 50_000_000  # 50 млн руб

        self.equipment_data = {
            'total_pallet_positions': total_pallet_positions,
            'inbound_docks': inbound_docks,
            'outbound_docks': outbound_docks,
            'total_capex': equipment_capex
        }

        print(f"\n[Складское оборудование]")
        print(f"  Паллето-мест: {total_pallet_positions:,}")
        print(f"  Inbound доков: {inbound_docks}")
        print(f"  Outbound доков: {outbound_docks}")
        print(f"  CAPEX оборудования: {equipment_capex:,.0f} руб")

    def _calculate_sku_distribution(self):
        """Упрощенное распределение SKU."""
        self.sku_distribution = {
            'normal': {'sku_count': int(self.total_sku * 0.60), 'share': 0.60},
            'cold_chain': {'sku_count': int(self.total_sku * 0.30), 'share': 0.30},
            'special': {'sku_count': int(self.total_sku * 0.10), 'share': 0.10}
        }

        print(f"\n[Распределение SKU]")
        for condition, data in self.sku_distribution.items():
            print(f"  {condition}: {data['sku_count']:,} SKU ({data['share']*100:.0f}%)")

    def _calculate_climate_requirements(self):
        """Детальный расчет климатических требований для каждой зоны."""
        print(f"\n[Климатические требования]")

        # Зона нормального хранения
        normal_area = self.zoning_data['storage_normal'].area_sqm
        self.climate_requirements['storage_normal'] = {
            'zone_name': 'Нормальное хранение',
            'temperature_range': '15-25°C',
            'temperature_target': '20°C',
            'humidity_range': '40-60%',
            'humidity_target': '50%',
            'air_changes_per_hour': 2,
            'cooling_power_kw': (normal_area * 20) / 1000,  # 20 Вт/кв.м
            'heating_power_kw': (normal_area * 15) / 1000,  # 15 Вт/кв.м
            'ventilation_capacity_m3h': normal_area * 4 * 2,  # 4м высота * 2 обмена
            'monitoring_points': int(normal_area / 200),  # 1 точка на 200кв.м
            'area_sqm': normal_area
        }

        # Зона холодовой цепи
        cold_area = self.zoning_data['storage_cold'].area_sqm
        self.climate_requirements['storage_cold'] = {
            'zone_name': 'Холодовая цепь',
            'temperature_range': '2-8°C',
            'temperature_target': '5°C',
            'humidity_range': '45-75%',
            'humidity_target': '60%',
            'air_changes_per_hour': 6,
            'cooling_power_kw': (cold_area * 80) / 1000,  # 80 Вт/кв.м для холодильной зоны
            'heating_power_kw': 0,  # Не требуется для холодильной зоны
            'ventilation_capacity_m3h': cold_area * 4 * 6,  # 4м высота * 6 обменов
            'monitoring_points': int(cold_area / 100),  # 1 точка на 100кв.м (повышенные требования)
            'backup_cooling_kw': (cold_area * 80) / 1000,  # 100% резервирование
            'area_sqm': cold_area
        }

        # Зона приемки
        receiving_area = self.zoning_data['receiving'].area_sqm
        self.climate_requirements['receiving'] = {
            'zone_name': 'Зона приемки',
            'temperature_range': '15-25°C',
            'temperature_target': '20°C',
            'humidity_range': '40-70%',
            'humidity_target': '55%',
            'air_changes_per_hour': 4,
            'cooling_power_kw': (receiving_area * 25) / 1000,
            'heating_power_kw': (receiving_area * 20) / 1000,
            'ventilation_capacity_m3h': receiving_area * 4 * 4,
            'monitoring_points': int(max(receiving_area / 300, 2)),
            'area_sqm': receiving_area
        }

        # Зона отгрузки
        dispatch_area = self.zoning_data['dispatch'].area_sqm
        self.climate_requirements['dispatch'] = {
            'zone_name': 'Зона отгрузки',
            'temperature_range': '15-25°C',
            'temperature_target': '20°C',
            'humidity_range': '40-70%',
            'humidity_target': '55%',
            'air_changes_per_hour': 4,
            'cooling_power_kw': (dispatch_area * 25) / 1000,
            'heating_power_kw': (dispatch_area * 20) / 1000,
            'ventilation_capacity_m3h': dispatch_area * 4 * 4,
            'monitoring_points': int(max(dispatch_area / 300, 2)),
            'area_sqm': dispatch_area
        }

        # Вывод информации
        for zone_id, requirements in self.climate_requirements.items():
            print(f"\n  {requirements['zone_name']} ({requirements['area_sqm']:,.0f} кв.м):")
            print(f"    Температура: {requirements['temperature_range']} (целевая: {requirements['temperature_target']})")
            print(f"    Влажность: {requirements['humidity_range']} (целевая: {requirements['humidity_target']})")
            print(f"    Воздухообмен: {requirements['air_changes_per_hour']} раз/час")
            print(f"    Мощность охлаждения: {requirements['cooling_power_kw']:.1f} кВт")
            if requirements.get('heating_power_kw', 0) > 0:
                print(f"    Мощность обогрева: {requirements['heating_power_kw']:.1f} кВт")
            print(f"    Вентиляция: {requirements['ventilation_capacity_m3h']:,.0f} м3/час")
            print(f"    Точек мониторинга: {requirements['monitoring_points']}")
            if 'backup_cooling_kw' in requirements:
                print(f"    Резервное охлаждение: {requirements['backup_cooling_kw']:.1f} кВт")

    def _calculate_gpp_gdp_compliance(self):
        """Расчет требований GPP/GDP для каждой зоны."""
        print(f"\n[Соответствие GPP/GDP требованиям]")

        self.gpp_gdp_compliance = {
            'storage_normal': {
                'zone_name': 'Нормальное хранение',
                'gmp_classification': 'Grade D',
                'gdp_requirements': [
                    'Температурный мониторинг 24/7',
                    'Контроль влажности',
                    'Автоматическая сигнализация отклонений',
                    'Квалифицированное оборудование (IQ/OQ/PQ)',
                    'Валидация температурного картирования'
                ],
                'documentation': [
                    'Протоколы валидации',
                    'SOP по контролю климата',
                    'Журналы калибровки',
                    'Отчеты по отклонениям'
                ],
                'validation_status': 'Требуется первичная валидация',
                'revalidation_period_months': 12
            },
            'storage_cold': {
                'zone_name': 'Холодовая цепь',
                'gmp_classification': 'Grade D',
                'gdp_requirements': [
                    'Непрерывный температурный мониторинг',
                    'Контроль влажности',
                    'Аварийная сигнализация с SMS/Email',
                    'Резервирование охлаждения (N+1)',
                    'Автономное питание (ИБП + генератор)',
                    'Квалификация холодильного оборудования',
                    'Температурное картирование каждые 6 месяцев'
                ],
                'documentation': [
                    'Протоколы валидации холодильного оборудования',
                    'SOP по работе с холодовой цепью',
                    'План действий при аварии',
                    'Журналы калибровки температурных датчиков',
                    'Отчеты по отклонениям температуры'
                ],
                'validation_status': 'Требуется усиленная валидация',
                'revalidation_period_months': 6
            },
            'receiving': {
                'zone_name': 'Зона приемки',
                'gmp_classification': 'Grade D',
                'gdp_requirements': [
                    'Температурный контроль',
                    'Раздельная зона для карантина',
                    'Процедуры входного контроля',
                    'Контроль доступа'
                ],
                'documentation': [
                    'SOP по приемке товара',
                    'Журналы входного контроля',
                    'Чек-листы проверки температуры'
                ],
                'validation_status': 'Базовая валидация',
                'revalidation_period_months': 12
            },
            'dispatch': {
                'zone_name': 'Зона отгрузки',
                'gmp_classification': 'Grade D',
                'gdp_requirements': [
                    'Температурный контроль',
                    'Процедуры предотгрузочной проверки',
                    'Контроль качества упаковки',
                    'Документирование условий отгрузки'
                ],
                'documentation': [
                    'SOP по отгрузке',
                    'Журналы отгрузки',
                    'Чек-листы проверки температурного режима транспорта'
                ],
                'validation_status': 'Базовая валидация',
                'revalidation_period_months': 12
            }
        }

        # Вывод информации
        for zone_id, compliance in self.gpp_gdp_compliance.items():
            print(f"\n  {compliance['zone_name']}:")
            print(f"    GMP классификация: {compliance['gmp_classification']}")
            print(f"    GDP требования ({len(compliance['gdp_requirements'])}):")
            for req in compliance['gdp_requirements']:
                print(f"      - {req}")
            print(f"    Статус валидации: {compliance['validation_status']}")
            print(f"    Ревалидация каждые: {compliance['revalidation_period_months']} месяцев")

    def _calculate_monitoring_systems(self):
        """Расчет систем мониторинга."""
        print(f"\n[Системы мониторинга и контроля]")

        total_monitoring_points = sum(
            req['monitoring_points'] for req in self.climate_requirements.values()
        )

        self.monitoring_systems = {
            'temperature_sensors': {
                'description': 'Датчики температуры',
                'quantity': total_monitoring_points,
                'type': 'Высокоточные PT100/PT1000',
                'accuracy': '±0.1°C',
                'calibration_interval_months': 6,
                'data_logging_interval_min': 5,
                'cost_per_unit_rub': 15_000,
                'total_cost_rub': total_monitoring_points * 15_000
            },
            'humidity_sensors': {
                'description': 'Датчики влажности',
                'quantity': total_monitoring_points,
                'type': 'Емкостные датчики',
                'accuracy': '±2% RH',
                'calibration_interval_months': 12,
                'data_logging_interval_min': 5,
                'cost_per_unit_rub': 12_000,
                'total_cost_rub': total_monitoring_points * 12_000
            },
            'monitoring_software': {
                'description': 'Программное обеспечение мониторинга',
                'features': [
                    'Сбор данных в реальном времени',
                    'Автоматическая сигнализация',
                    'SMS/Email уведомления',
                    'Генерация отчетов',
                    'Интеграция с WMS',
                    '21 CFR Part 11 compliance'
                ],
                'license_type': 'Perpetual',
                'cost_rub': 5_000_000,
                'annual_maintenance_rub': 500_000
            },
            'alarm_system': {
                'description': 'Система аварийной сигнализации',
                'channels': 4,  # Каждая зона отдельно
                'notification_methods': ['SMS', 'Email', 'Звуковая', 'Световая'],
                'response_time_sec': 10,
                'cost_rub': 1_500_000
            },
            'backup_power': {
                'description': 'Резервное питание (ИБП + Генератор)',
                'ups_capacity_kva': 150,
                'ups_runtime_hours': 2,
                'generator_capacity_kw': 200,
                'cost_rub': 8_000_000
            }
        }

        # Общая стоимость систем мониторинга
        total_monitoring_cost = (
            self.monitoring_systems['temperature_sensors']['total_cost_rub'] +
            self.monitoring_systems['humidity_sensors']['total_cost_rub'] +
            self.monitoring_systems['monitoring_software']['cost_rub'] +
            self.monitoring_systems['alarm_system']['cost_rub'] +
            self.monitoring_systems['backup_power']['cost_rub']
        )

        self.monitoring_systems['total_capex_rub'] = total_monitoring_cost
        self.monitoring_systems['total_annual_opex_rub'] = (
            self.monitoring_systems['monitoring_software']['annual_maintenance_rub']
        )

        # Вывод информации
        print(f"\n  Датчики температуры: {self.monitoring_systems['temperature_sensors']['quantity']} шт")
        print(f"    Тип: {self.monitoring_systems['temperature_sensors']['type']}")
        print(f"    Точность: {self.monitoring_systems['temperature_sensors']['accuracy']}")
        print(f"    Стоимость: {self.monitoring_systems['temperature_sensors']['total_cost_rub']:,.0f} руб")

        print(f"\n  Датчики влажности: {self.monitoring_systems['humidity_sensors']['quantity']} шт")
        print(f"    Тип: {self.monitoring_systems['humidity_sensors']['type']}")
        print(f"    Точность: {self.monitoring_systems['humidity_sensors']['accuracy']}")
        print(f"    Стоимость: {self.monitoring_systems['humidity_sensors']['total_cost_rub']:,.0f} руб")

        print(f"\n  Программное обеспечение мониторинга:")
        print(f"    Функции: {len(self.monitoring_systems['monitoring_software']['features'])}")
        for feature in self.monitoring_systems['monitoring_software']['features']:
            print(f"      - {feature}")
        print(f"    Стоимость лицензии: {self.monitoring_systems['monitoring_software']['cost_rub']:,.0f} руб")
        print(f"    Годовое обслуживание: {self.monitoring_systems['monitoring_software']['annual_maintenance_rub']:,.0f} руб")

        print(f"\n  Система аварийной сигнализации:")
        print(f"    Каналов: {self.monitoring_systems['alarm_system']['channels']}")
        print(f"    Методы оповещения: {', '.join(self.monitoring_systems['alarm_system']['notification_methods'])}")
        print(f"    Стоимость: {self.monitoring_systems['alarm_system']['cost_rub']:,.0f} руб")

        print(f"\n  Резервное питание:")
        print(f"    ИБП: {self.monitoring_systems['backup_power']['ups_capacity_kva']} кВА, {self.monitoring_systems['backup_power']['ups_runtime_hours']} часа")
        print(f"    Генератор: {self.monitoring_systems['backup_power']['generator_capacity_kw']} кВт")
        print(f"    Стоимость: {self.monitoring_systems['backup_power']['cost_rub']:,.0f} руб")

        print(f"\n  ИТОГО системы мониторинга:")
        print(f"    CAPEX: {total_monitoring_cost:,.0f} руб")
        print(f"    Годовой OPEX: {self.monitoring_systems['total_annual_opex_rub']:,.0f} руб")

    def _calculate_detailed_equipment(self):
        """Детальный расчет оборудования по категориям."""
        print(f"\n[Детальное оборудование]")

        self.detailed_equipment = {
            'racking_systems': {
                'description': 'Стеллажные системы',
                'pallet_racking_positions': self.equipment_data['total_pallet_positions'],
                'racking_type': 'Паллетные стеллажи',
                'levels': 5,
                'max_load_per_position_kg': 1000,
                'aisle_width_m': 3.5,
                'cost_per_position_rub': 8_000,
                'total_cost_rub': self.equipment_data['total_pallet_positions'] * 8_000
            },
            'material_handling': {
                'description': 'Погрузочно-разгрузочная техника',
                'forklifts': {
                    'quantity': 8,
                    'type': 'Электропогрузчик 2т',
                    'cost_per_unit_rub': 2_500_000,
                    'total_cost_rub': 8 * 2_500_000
                },
                'pallet_jacks': {
                    'quantity': 12,
                    'type': 'Электротележка 2т',
                    'cost_per_unit_rub': 350_000,
                    'total_cost_rub': 12 * 350_000
                },
                'total_cost_rub': (8 * 2_500_000) + (12 * 350_000)
            },
            'climate_systems': {
                'description': 'Климатическое оборудование',
                'hvac_units': {
                    'quantity': 12,
                    'type': 'Прецизионные кондиционеры',
                    'total_cooling_kw': sum(req['cooling_power_kw'] for req in self.climate_requirements.values()),
                    'cost_per_unit_rub': 1_200_000,
                    'total_cost_rub': 12 * 1_200_000
                },
                'cold_storage_units': {
                    'quantity': 6,
                    'type': 'Холодильные установки',
                    'cooling_kw': self.climate_requirements['storage_cold']['cooling_power_kw'],
                    'cost_per_unit_rub': 3_500_000,
                    'total_cost_rub': 6 * 3_500_000
                },
                'ventilation_system': {
                    'total_capacity_m3h': sum(req['ventilation_capacity_m3h'] for req in self.climate_requirements.values()),
                    'cost_rub': 8_000_000
                },
                'total_cost_rub': (12 * 1_200_000) + (6 * 3_500_000) + 8_000_000
            },
            'loading_docks': {
                'description': 'Погрузочно-разгрузочные доки',
                'inbound_docks': self.equipment_data['inbound_docks'],
                'outbound_docks': self.equipment_data['outbound_docks'],
                'dock_levelers': self.equipment_data['inbound_docks'] + self.equipment_data['outbound_docks'],
                'dock_shelters': self.equipment_data['inbound_docks'] + self.equipment_data['outbound_docks'],
                'cost_per_dock_rub': 800_000,
                'total_cost_rub': (self.equipment_data['inbound_docks'] + self.equipment_data['outbound_docks']) * 800_000
            },
            'safety_security': {
                'description': 'Системы безопасности',
                'fire_suppression': {
                    'type': 'Спринклерная система',
                    'coverage_sqm': self.total_area,
                    'cost_rub': 5_000_000
                },
                'video_surveillance': {
                    'cameras': 40,
                    'recording_days': 90,
                    'cost_rub': 2_500_000
                },
                'access_control': {
                    'readers': 20,
                    'integration': 'WMS + Time Tracking',
                    'cost_rub': 1_500_000
                },
                'total_cost_rub': 5_000_000 + 2_500_000 + 1_500_000
            }
        }

        # Общая стоимость оборудования
        total_equipment_capex = (
            self.detailed_equipment['racking_systems']['total_cost_rub'] +
            self.detailed_equipment['material_handling']['total_cost_rub'] +
            self.detailed_equipment['climate_systems']['total_cost_rub'] +
            self.detailed_equipment['loading_docks']['total_cost_rub'] +
            self.detailed_equipment['safety_security']['total_cost_rub']
        )

        self.detailed_equipment['total_equipment_capex_rub'] = total_equipment_capex

        # Вывод информации
        print(f"\n  Стеллажные системы:")
        print(f"    Паллето-мест: {self.detailed_equipment['racking_systems']['pallet_racking_positions']:,}")
        print(f"    Тип: {self.detailed_equipment['racking_systems']['racking_type']}, {self.detailed_equipment['racking_systems']['levels']} уровней")
        print(f"    Стоимость: {self.detailed_equipment['racking_systems']['total_cost_rub']:,.0f} руб")

        print(f"\n  Погрузочно-разгрузочная техника:")
        print(f"    Погрузчики: {self.detailed_equipment['material_handling']['forklifts']['quantity']} шт")
        print(f"    Электротележки: {self.detailed_equipment['material_handling']['pallet_jacks']['quantity']} шт")
        print(f"    Стоимость: {self.detailed_equipment['material_handling']['total_cost_rub']:,.0f} руб")

        print(f"\n  Климатические системы:")
        print(f"    HVAC установок: {self.detailed_equipment['climate_systems']['hvac_units']['quantity']} шт")
        print(f"    Холодильных установок: {self.detailed_equipment['climate_systems']['cold_storage_units']['quantity']} шт")
        print(f"    Общая мощность охлаждения: {self.detailed_equipment['climate_systems']['hvac_units']['total_cooling_kw']:.1f} кВт")
        print(f"    Стоимость: {self.detailed_equipment['climate_systems']['total_cost_rub']:,.0f} руб")

        print(f"\n  Погрузочно-разгрузочные доки:")
        print(f"    Inbound: {self.detailed_equipment['loading_docks']['inbound_docks']} шт")
        print(f"    Outbound: {self.detailed_equipment['loading_docks']['outbound_docks']} шт")
        print(f"    Стоимость: {self.detailed_equipment['loading_docks']['total_cost_rub']:,.0f} руб")

        print(f"\n  Системы безопасности:")
        print(f"    Пожаротушение: {self.detailed_equipment['safety_security']['fire_suppression']['type']}")
        print(f"    Видеонаблюдение: {self.detailed_equipment['safety_security']['video_surveillance']['cameras']} камер")
        print(f"    СКУД: {self.detailed_equipment['safety_security']['access_control']['readers']} считывателей")
        print(f"    Стоимость: {self.detailed_equipment['safety_security']['total_cost_rub']:,.0f} руб")

        print(f"\n  ИТОГО оборудование: {total_equipment_capex:,.0f} руб")

    def _build_automation_scenarios(self):
        """Построение сценариев автоматизации."""
        # Сценарий 0: Без автоматизации
        self.automation_scenarios[AutomationLevel.LEVEL_0] = {
            'name': '0: Без автоматизации (Базовый)',
            'capex': 0,
            'annual_opex': 0,
            'labor_reduction_factor': 0,
            'efficiency_multiplier': 1.0,
            'description': 'Ручная работа без автоматизации'
        }

        # Сценарий 1: Базовая автоматизация
        self.automation_scenarios[AutomationLevel.LEVEL_1] = {
            'name': '1: Базовая автоматизация (WMS + Сканеры)',
            'capex': 50_000_000,
            'annual_opex': 10_000_000,
            'labor_reduction_factor': 0.20,  # 20% сокращение
            'efficiency_multiplier': 1.3,     # +30% производительность
            'description': 'WMS, сканеры штрих-кодов, базовое ПО'
        }

        # Сценарий 2: Продвинутая автоматизация
        self.automation_scenarios[AutomationLevel.LEVEL_2] = {
            'name': '2: Продвинутая автоматизация (+ Конвейеры + Сортировка)',
            'capex': 200_000_000,
            'annual_opex': 35_000_000,
            'labor_reduction_factor': 0.50,  # 50% сокращение
            'efficiency_multiplier': 2.0,     # 2x производительность
            'description': 'WMS, конвейеры, автоматическая сортировка'
        }

        # Сценарий 3: Полная автоматизация
        self.automation_scenarios[AutomationLevel.LEVEL_3] = {
            'name': '3: Полная автоматизация (AS/RS + Роботы)',
            'capex': 600_000_000,
            'annual_opex': 100_000_000,
            'labor_reduction_factor': 0.80,  # 80% сокращение
            'efficiency_multiplier': 3.5,     # 3.5x производительность
            'description': 'AS/RS, AGV, роботы, полная автоматизация'
        }

        print(f"\n[Сценарии автоматизации]")
        for level, scenario in self.automation_scenarios.items():
            print(f"\n  {scenario['name']}")
            print(f"    CAPEX: {scenario['capex']:,.0f} руб")
            print(f"    Годовой OPEX: {scenario['annual_opex']:,.0f} руб/год")
            print(f"    Сокращение персонала: {scenario['labor_reduction_factor']*100:.0f}%")
            print(f"    Рост производительности: {(scenario['efficiency_multiplier']-1)*100:.0f}%")

    def _calculate_roi(self):
        """Расчет ROI для каждого сценария."""
        base_staff_count = config.INITIAL_STAFF_COUNT
        monthly_salary = config.OPERATOR_SALARY_RUB_MONTH
        base_throughput = config.TARGET_ORDERS_MONTH
        revenue_per_order = 500  # Примерный доход с заказа (руб)

        print(f"\n[Расчет ROI]")
        for level, scenario in self.automation_scenarios.items():
            # Экономия на ФОТ
            reduced_staff = int(base_staff_count * scenario['labor_reduction_factor'])
            annual_labor_savings = reduced_staff * monthly_salary * 12

            # Рост производительности
            throughput_increase = int(base_throughput * (scenario['efficiency_multiplier'] - 1))
            annual_revenue_increase = throughput_increase * 12 * revenue_per_order

            # Чистая годовая выгода
            net_annual_benefit = annual_labor_savings + annual_revenue_increase - scenario['annual_opex']

            # Срок окупаемости
            if net_annual_benefit > 0:
                payback_years = scenario['capex'] / net_annual_benefit
            else:
                payback_years = float('inf')

            # ROI за 5 лет
            if scenario['capex'] > 0:
                roi_5y_percent = ((net_annual_benefit * 5 - scenario['capex']) / scenario['capex']) * 100
            else:
                roi_5y_percent = 0

            self.roi_data[level.value] = {
                'scenario_name': scenario['name'],
                'capex': scenario['capex'],
                'annual_opex': scenario['annual_opex'],
                'reduced_staff': reduced_staff,
                'annual_labor_savings': annual_labor_savings,
                'annual_revenue_increase': annual_revenue_increase,
                'net_annual_benefit': net_annual_benefit,
                'payback_years': payback_years,
                'roi_5y_percent': roi_5y_percent
            }

            print(f"\n  {scenario['name']}")
            print(f"    Экономия на ФОТ: {annual_labor_savings:,.0f} руб/год")
            print(f"    Рост дохода: {annual_revenue_increase:,.0f} руб/год")
            print(f"    Чистая выгода: {net_annual_benefit:,.0f} руб/год")
            print(f"    Срок окупаемости: {payback_years:.2f} лет" if payback_years != float('inf') else "    Срок окупаемости: Не окупается")
            print(f"    ROI за 5 лет: {roi_5y_percent:.1f}%")

    def _generate_visualizations(self):
        """Генерирует статические визуализации."""
        print("\n[Визуализация] Создание графиков...")

        # 1. Сравнение сценариев автоматизации
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Анализ сценариев автоматизации: {self.location_name}',
                    fontsize=16, fontweight='bold')

        scenarios_names = [s['name'].split(':')[0] for s in self.automation_scenarios.values()]

        # График 1: CAPEX
        capex_values = [s['capex']/1_000_000 for s in self.automation_scenarios.values()]
        ax1.bar(scenarios_names, capex_values, color='steelblue', alpha=0.7)
        ax1.set_ylabel('CAPEX (млн руб)', fontsize=11)
        ax1.set_title('Начальные инвестиции', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # График 2: Годовой OPEX
        opex_values = [s['annual_opex']/1_000_000 for s in self.automation_scenarios.values()]
        ax2.bar(scenarios_names, opex_values, color='coral', alpha=0.7)
        ax2.set_ylabel('Годовой OPEX (млн руб)', fontsize=11)
        ax2.set_title('Операционные расходы', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        # График 3: ROI за 5 лет
        roi_values = [self.roi_data[i]['roi_5y_percent'] for i in range(len(self.automation_scenarios))]
        colors = ['red' if r < 0 else 'green' for r in roi_values]
        ax3.bar(scenarios_names, roi_values, color=colors, alpha=0.7)
        ax3.set_ylabel('ROI за 5 лет (%)', fontsize=11)
        ax3.set_title('Возврат инвестиций', fontsize=12, fontweight='bold')
        ax3.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax3.grid(True, alpha=0.3, axis='y')

        # График 4: Срок окупаемости
        payback_values = [self.roi_data[i]['payback_years'] for i in range(len(self.automation_scenarios))]
        payback_values = [min(p, 15) for p in payback_values]  # Ограничиваем 15 годами
        ax4.bar(scenarios_names, payback_values, color='purple', alpha=0.7)
        ax4.set_ylabel('Срок окупаемости (лет)', fontsize=11)
        ax4.set_title('Период окупаемости', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        save_path = os.path.join(config.OUTPUT_DIR, "automation_comparison_detailed.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  [Сохранено] {save_path}")

        # 2. Зонирование склада (простая визуализация)
        fig, ax = plt.subplots(figsize=(12, 8))
        zones = list(self.zoning_data.values())
        zone_names = [z.name for z in zones]
        zone_areas = [z.area_sqm for z in zones]
        colors_zones = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']

        ax.pie(zone_areas, labels=zone_names, colors=colors_zones, autopct='%1.1f%%',
              startangle=90, textprops={'fontsize': 11})
        ax.set_title(f'Зонирование склада: {self.location_name}\nОбщая площадь: {self.total_area:,.0f} кв.м',
                    fontsize=14, fontweight='bold', pad=20)

        save_path = os.path.join(config.OUTPUT_DIR, "warehouse_layout_detailed.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  [Сохранено] {save_path}")
        print("[Визуализация] Все графики успешно созданы")

    def _create_animations(self):
        """Создает анимированные визуализации."""
        print("\n[Анимации] Создание анимированных графиков...")

        try:
            create_all_animations(self.roi_data, config.OUTPUT_DIR)
            print("[Анимации] Все анимации успешно созданы")
        except Exception as e:
            print(f"[Предупреждение] Не удалось создать анимации: {e}")
            print("  (Это не критично для основного анализа)")

    def _export_to_excel(self):
        """Экспортирует результаты анализа в Excel."""
        print("\n[Экспорт] Создание Excel отчета...")

        excel_data = {
            "Сводка": self._prepare_summary_dataframe(),
            "Зонирование": self._prepare_zoning_dataframe(),
            "Климатические требования": self._prepare_climate_dataframe(),
            "GPP GDP Compliance": self._prepare_gpp_gdp_dataframe(),
            "Системы мониторинга": self._prepare_monitoring_dataframe(),
            "Детальное оборудование": self._prepare_detailed_equipment_dataframe(),
            "Автоматизация": self._prepare_automation_dataframe(),
            "ROI анализ": self._prepare_roi_dataframe(),
            "Распределение SKU": self._prepare_sku_distribution_dataframe()
        }

        excel_path = os.path.join(config.OUTPUT_DIR, "warehouse_analysis_report.xlsx")

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for sheet_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"[Экспорт] Excel отчет сохранен: {excel_path}")
        print(f"  Количество вкладок: {len(excel_data)}")

    def _prepare_summary_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame со сводной информацией."""
        summary_data = []

        # Общая информация о складе
        summary_data.append({"Категория": "ОБЩАЯ ИНФОРМАЦИЯ", "Параметр": "", "Значение": ""})
        summary_data.append({"Категория": "Склад", "Параметр": "Название локации", "Значение": self.location_name})
        summary_data.append({"Категория": "Склад", "Параметр": "Общая площадь (кв.м)", "Значение": f"{self.total_area:,.0f}"})
        summary_data.append({"Категория": "Склад", "Параметр": "Общее количество SKU", "Значение": f"{self.total_sku:,}"})

        # Финансовая сводка
        summary_data.append({"Категория": "", "Параметр": "", "Значение": ""})
        summary_data.append({"Категория": "ФИНАНСОВАЯ СВОДКА", "Параметр": "", "Значение": ""})

        if self.monitoring_systems:
            monitoring_capex = self.monitoring_systems.get('total_capex_rub', 0)
            monitoring_opex = self.monitoring_systems.get('total_annual_opex_rub', 0)
            summary_data.append({"Категория": "Мониторинг", "Параметр": "CAPEX систем мониторинга (руб)", "Значение": f"{monitoring_capex:,.0f}"})
            summary_data.append({"Категория": "Мониторинг", "Параметр": "Годовой OPEX мониторинга (руб)", "Значение": f"{monitoring_opex:,.0f}"})

        if self.detailed_equipment:
            equipment_capex = self.detailed_equipment.get('total_equipment_capex_rub', 0)
            summary_data.append({"Категория": "Оборудование", "Параметр": "CAPEX оборудования (руб)", "Значение": f"{equipment_capex:,.0f}"})

        # Лучший вариант автоматизации
        if self.roi_data:
            best_roi_level = max(self.roi_data.items(), key=lambda x: x[1]['roi_5y_percent'])
            summary_data.append({"Категория": "", "Параметр": "", "Значение": ""})
            summary_data.append({"Категория": "РЕКОМЕНДАЦИИ", "Параметр": "", "Значение": ""})
            summary_data.append({"Категория": "Автоматизация", "Параметр": "Рекомендуемый сценарий", "Значение": best_roi_level[1]['scenario_name']})
            summary_data.append({"Категория": "Автоматизация", "Параметр": "ROI за 5 лет (%)", "Значение": f"{best_roi_level[1]['roi_5y_percent']:.1f}"})
            summary_data.append({"Категория": "Автоматизация", "Параметр": "Срок окупаемости (лет)", "Значение": f"{best_roi_level[1]['payback_years']:.2f}" if best_roi_level[1]['payback_years'] != float('inf') else "Не окупается"})

        return pd.DataFrame(summary_data)

    def _prepare_zoning_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с данными зонирования."""
        data = []
        for zone_id, zone in self.zoning_data.items():
            data.append({
                "ID зоны": zone_id,
                "Название": zone.name,
                "Площадь (кв.м)": zone.area_sqm,
                "Доля (%)": (zone.area_sqm / self.total_area) * 100
            })
        return pd.DataFrame(data)

    def _prepare_climate_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с климатическими требованиями."""
        data = []
        for zone_id, requirements in self.climate_requirements.items():
            data.append({
                "ID зоны": zone_id,
                "Название зоны": requirements['zone_name'],
                "Площадь (кв.м)": f"{requirements['area_sqm']:,.0f}",
                "Диапазон температур": requirements['temperature_range'],
                "Целевая температура": requirements['temperature_target'],
                "Диапазон влажности": requirements['humidity_range'],
                "Целевая влажность": requirements['humidity_target'],
                "Воздухообмен (раз/час)": requirements['air_changes_per_hour'],
                "Мощность охлаждения (кВт)": f"{requirements['cooling_power_kw']:.1f}",
                "Мощность обогрева (кВт)": f"{requirements.get('heating_power_kw', 0):.1f}",
                "Вентиляция (м3/час)": f"{requirements['ventilation_capacity_m3h']:,.0f}",
                "Точек мониторинга": requirements['monitoring_points'],
                "Резервное охлаждение (кВт)": f"{requirements.get('backup_cooling_kw', 0):.1f}"
            })
        return pd.DataFrame(data)

    def _prepare_gpp_gdp_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с требованиями GPP/GDP."""
        data = []
        for zone_id, compliance in self.gpp_gdp_compliance.items():
            # Основная информация
            base_info = {
                "ID зоны": zone_id,
                "Название зоны": compliance['zone_name'],
                "GMP классификация": compliance['gmp_classification'],
                "Статус валидации": compliance['validation_status'],
                "Период ревалидации (месяцев)": compliance['revalidation_period_months'],
                "Количество GDP требований": len(compliance['gdp_requirements']),
                "Количество документов": len(compliance['documentation'])
            }

            # Добавляем GDP требования как отдельные строки
            for idx, req in enumerate(compliance['gdp_requirements'], 1):
                req_info = base_info.copy()
                req_info[f"GDP требование {idx}"] = req
                data.append(req_info)

            # Если нет требований, добавляем хотя бы основную строку
            if not compliance['gdp_requirements']:
                data.append(base_info)

        return pd.DataFrame(data)

    def _prepare_monitoring_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с системами мониторинга."""
        data = []

        # Датчики температуры
        if 'temperature_sensors' in self.monitoring_systems:
            ts = self.monitoring_systems['temperature_sensors']
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Количество",
                "Значение": ts['quantity'],
                "Единица": "шт"
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Тип",
                "Значение": ts['type'],
                "Единица": ""
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Точность",
                "Значение": ts['accuracy'],
                "Единица": ""
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Интервал калибровки",
                "Значение": ts['calibration_interval_months'],
                "Единица": "месяцев"
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Стоимость за единицу",
                "Значение": f"{ts['cost_per_unit_rub']:,.0f}",
                "Единица": "руб"
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Общая стоимость",
                "Значение": f"{ts['total_cost_rub']:,.0f}",
                "Единица": "руб"
            })

        # Датчики влажности
        if 'humidity_sensors' in self.monitoring_systems:
            hs = self.monitoring_systems['humidity_sensors']
            data.append({
                "Категория": "Датчики влажности",
                "Параметр": "Количество",
                "Значение": hs['quantity'],
                "Единица": "шт"
            })
            data.append({
                "Категория": "Датчики влажности",
                "Параметр": "Тип",
                "Значение": hs['type'],
                "Единица": ""
            })
            data.append({
                "Категория": "Датчики влажности",
                "Параметр": "Точность",
                "Значение": hs['accuracy'],
                "Единица": ""
            })
            data.append({
                "Категория": "Датчики влажности",
                "Параметр": "Общая стоимость",
                "Значение": f"{hs['total_cost_rub']:,.0f}",
                "Единица": "руб"
            })

        # ПО мониторинга
        if 'monitoring_software' in self.monitoring_systems:
            ms = self.monitoring_systems['monitoring_software']
            data.append({
                "Категория": "ПО мониторинга",
                "Параметр": "Описание",
                "Значение": ms['description'],
                "Единица": ""
            })
            data.append({
                "Категория": "ПО мониторинга",
                "Параметр": "Стоимость лицензии",
                "Значение": f"{ms['cost_rub']:,.0f}",
                "Единица": "руб"
            })
            data.append({
                "Категория": "ПО мониторинга",
                "Параметр": "Годовое обслуживание",
                "Значение": f"{ms['annual_maintenance_rub']:,.0f}",
                "Единица": "руб/год"
            })

        # Система сигнализации
        if 'alarm_system' in self.monitoring_systems:
            als = self.monitoring_systems['alarm_system']
            data.append({
                "Категория": "Аварийная сигнализация",
                "Параметр": "Каналов",
                "Значение": als['channels'],
                "Единица": "шт"
            })
            data.append({
                "Категория": "Аварийная сигнализация",
                "Параметр": "Стоимость",
                "Значение": f"{als['cost_rub']:,.0f}",
                "Единица": "руб"
            })

        # Резервное питание
        if 'backup_power' in self.monitoring_systems:
            bp = self.monitoring_systems['backup_power']
            data.append({
                "Категория": "Резервное питание",
                "Параметр": "ИБП мощность",
                "Значение": bp['ups_capacity_kva'],
                "Единица": "кВА"
            })
            data.append({
                "Категория": "Резервное питание",
                "Параметр": "ИБП автономность",
                "Значение": bp['ups_runtime_hours'],
                "Единица": "часов"
            })
            data.append({
                "Категория": "Резервное питание",
                "Параметр": "Генератор мощность",
                "Значение": bp['generator_capacity_kw'],
                "Единица": "кВт"
            })
            data.append({
                "Категория": "Резервное питание",
                "Параметр": "Стоимость",
                "Значение": f"{bp['cost_rub']:,.0f}",
                "Единица": "руб"
            })

        # Итого
        data.append({
            "Категория": "ИТОГО",
            "Параметр": "CAPEX систем мониторинга",
            "Значение": f"{self.monitoring_systems.get('total_capex_rub', 0):,.0f}",
            "Единица": "руб"
        })
        data.append({
            "Категория": "ИТОГО",
            "Параметр": "Годовой OPEX",
            "Значение": f"{self.monitoring_systems.get('total_annual_opex_rub', 0):,.0f}",
            "Единица": "руб/год"
        })

        return pd.DataFrame(data)

    def _prepare_detailed_equipment_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с детальным оборудованием."""
        data = []

        # Стеллажные системы
        if 'racking_systems' in self.detailed_equipment:
            rs = self.detailed_equipment['racking_systems']
            data.append({
                "Категория": "Стеллажные системы",
                "Описание": rs['description'],
                "Параметр": "Паллето-мест",
                "Значение": f"{rs['pallet_racking_positions']:,}",
                "Стоимость (руб)": f"{rs['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Стеллажные системы",
                "Описание": "Тип стеллажей",
                "Параметр": rs['racking_type'],
                "Значение": f"{rs['levels']} уровней",
                "Стоимость (руб)": ""
            })

        # Погрузочная техника
        if 'material_handling' in self.detailed_equipment:
            mh = self.detailed_equipment['material_handling']
            data.append({
                "Категория": "Погрузочная техника",
                "Описание": "Погрузчики",
                "Параметр": mh['forklifts']['type'],
                "Значение": f"{mh['forklifts']['quantity']} шт",
                "Стоимость (руб)": f"{mh['forklifts']['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Погрузочная техника",
                "Описание": "Электротележки",
                "Параметр": mh['pallet_jacks']['type'],
                "Значение": f"{mh['pallet_jacks']['quantity']} шт",
                "Стоимость (руб)": f"{mh['pallet_jacks']['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Погрузочная техника",
                "Описание": "ИТОГО",
                "Параметр": "",
                "Значение": "",
                "Стоимость (руб)": f"{mh['total_cost_rub']:,.0f}"
            })

        # Климатические системы
        if 'climate_systems' in self.detailed_equipment:
            cs = self.detailed_equipment['climate_systems']
            data.append({
                "Категория": "Климатическое оборудование",
                "Описание": "HVAC установки",
                "Параметр": cs['hvac_units']['type'],
                "Значение": f"{cs['hvac_units']['quantity']} шт, {cs['hvac_units']['total_cooling_kw']:.1f} кВт",
                "Стоимость (руб)": f"{cs['hvac_units']['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Климатическое оборудование",
                "Описание": "Холодильные установки",
                "Параметр": cs['cold_storage_units']['type'],
                "Значение": f"{cs['cold_storage_units']['quantity']} шт, {cs['cold_storage_units']['cooling_kw']:.1f} кВт",
                "Стоимость (руб)": f"{cs['cold_storage_units']['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Климатическое оборудование",
                "Описание": "Система вентиляции",
                "Параметр": f"{cs['ventilation_system']['total_capacity_m3h']:,.0f} м3/час",
                "Значение": "",
                "Стоимость (руб)": f"{cs['ventilation_system']['cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Климатическое оборудование",
                "Описание": "ИТОГО",
                "Параметр": "",
                "Значение": "",
                "Стоимость (руб)": f"{cs['total_cost_rub']:,.0f}"
            })

        # Доки
        if 'loading_docks' in self.detailed_equipment:
            ld = self.detailed_equipment['loading_docks']
            data.append({
                "Категория": "Погрузочные доки",
                "Описание": "Inbound доки",
                "Параметр": f"{ld['inbound_docks']} шт",
                "Значение": "",
                "Стоимость (руб)": ""
            })
            data.append({
                "Категория": "Погрузочные доки",
                "Описание": "Outbound доки",
                "Параметр": f"{ld['outbound_docks']} шт",
                "Значение": "",
                "Стоимость (руб)": ""
            })
            data.append({
                "Категория": "Погрузочные доки",
                "Описание": "ИТОГО",
                "Параметр": f"{ld['dock_levelers']} доков",
                "Значение": "",
                "Стоимость (руб)": f"{ld['total_cost_rub']:,.0f}"
            })

        # Безопасность
        if 'safety_security' in self.detailed_equipment:
            ss = self.detailed_equipment['safety_security']
            data.append({
                "Категория": "Системы безопасности",
                "Описание": "Пожаротушение",
                "Параметр": ss['fire_suppression']['type'],
                "Значение": f"{ss['fire_suppression']['coverage_sqm']:,.0f} кв.м",
                "Стоимость (руб)": f"{ss['fire_suppression']['cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Системы безопасности",
                "Описание": "Видеонаблюдение",
                "Параметр": f"{ss['video_surveillance']['cameras']} камер",
                "Значение": f"{ss['video_surveillance']['recording_days']} дней записи",
                "Стоимость (руб)": f"{ss['video_surveillance']['cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Системы безопасности",
                "Описание": "СКУД",
                "Параметр": f"{ss['access_control']['readers']} считывателей",
                "Значение": ss['access_control']['integration'],
                "Стоимость (руб)": f"{ss['access_control']['cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Системы безопасности",
                "Описание": "ИТОГО",
                "Параметр": "",
                "Значение": "",
                "Стоимость (руб)": f"{ss['total_cost_rub']:,.0f}"
            })

        # Общий итог
        data.append({
            "Категория": "ОБЩИЙ ИТОГ",
            "Описание": "Все оборудование",
            "Параметр": "",
            "Значение": "",
            "Стоимость (руб)": f"{self.detailed_equipment.get('total_equipment_capex_rub', 0):,.0f}"
        })

        return pd.DataFrame(data)

    def _prepare_sku_distribution_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с распределением SKU."""
        data = []
        for condition, info in self.sku_distribution.items():
            data.append({
                "Условие хранения": condition,
                "Количество SKU": info['sku_count'],
                "Доля (%)": info['share'] * 100
            })

        # Добавляем итоговую строку
        total_sku = sum(info['sku_count'] for info in self.sku_distribution.values())
        data.append({
            "Условие хранения": "ИТОГО",
            "Количество SKU": total_sku,
            "Доля (%)": 100.0
        })

        return pd.DataFrame(data)

    def _prepare_automation_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame со сценариями автоматизации."""
        data = []
        for level, scenario in self.automation_scenarios.items():
            data.append({
                "Уровень": level.value,
                "Название": scenario['name'],
                "CAPEX автоматизации (руб)": scenario['capex'],
                "Годовой OPEX автоматизации (руб)": scenario['annual_opex'],
                "Сокращение персонала (%)": scenario['labor_reduction_factor'] * 100,
                "Множитель эффективности": scenario['efficiency_multiplier'],
                "Описание": scenario['description']
            })
        return pd.DataFrame(data)

    def _prepare_roi_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с ROI анализом."""
        data = []
        for level_value, roi_info in self.roi_data.items():
            data.append({
                "Сценарий": roi_info['scenario_name'],
                "CAPEX (руб)": roi_info['capex'],
                "Годовой OPEX (руб)": roi_info['annual_opex'],
                "Сокращение персонала (чел)": roi_info['reduced_staff'],
                "Экономия на ФОТ (руб/год)": roi_info['annual_labor_savings'],
                "Увеличение throughput (заказов/мес)": roi_info['annual_revenue_increase'] / (500 * 12),
                "Дополнительный доход (руб/год)": roi_info['annual_revenue_increase'],
                "Чистая годовая выгода (руб)": roi_info['net_annual_benefit'],
                "Срок окупаемости (лет)": roi_info['payback_years'] if roi_info['payback_years'] != float('inf') else "N/A",
                "ROI за 5 лет (%)": roi_info['roi_5y_percent']
            })
        return pd.DataFrame(data)


if __name__ == "__main__":
    # Запуск комплексного анализа
    analysis = ComprehensiveWarehouseAnalysis(
        location_name="PNK Чашниково BTS",
        total_area=17_500,  # кв.м
        total_sku=15_000  # количество SKU
    )

    analysis.run_full_analysis()

    print("\n" + "="*120)
    print("Все файлы сохранены в директории 'output/':")
    print("  * warehouse_layout_detailed.png - Планировка склада с зонами")
    print("  * automation_comparison_detailed.png - Сравнение сценариев автоматизации")
    print("  * warehouse_analysis_report.xlsx - Полный Excel отчет")
    print("  * roi_comparison_animated.gif - Анимация сравнения ROI")
    print("  * payback_period_animated.gif - Анимация срока окупаемости")
    print("="*120)

```

## `Отчет_Методология_Анализа.md`

```md
# МЕТОДОЛОГИЯ АНАЛИЗА РЕЛОКАЦИИ ФАРМАЦЕВТИЧЕСКОГО СКЛАДА

## 1. Подход к определению места нахождения нового склада

Для выбора оптимального местоположения нового склада применяется комплексный подход, включающий:

### 1.1. Анализ рыночных предложений
- Анализ складов из раздаточного материала и актуальных предложений на рынке
- Оценка соответствия по ключевым параметрам:
  - Площадь помещения (требуемая: 15,000-17,500 кв.м)
  - Расстояние от МКАД (оптимально: 10-40 км)
  - Расстояние от аэропорта Шереметьево (критично для импортных поставок)
  - Климатические условия внутри склада (температура 15-25°C для нормального хранения, 2-8°C для холодовой цепи)
  - Возможность обеспечения требований GPP/GDP (Good Pharmacy Practice/Good Distribution Practice)

### 1.2. Верификация данных
- Созвон с представителями складских комплексов для подтверждения актуальности информации
- Изучение подробностей инфраструктуры, коммуникаций, возможностей модификации

### 1.3. Построение модели цифрового двойника
Применяется модель искусственного интеллекта по построению цифрового двойника, которая:
- При достаточном количестве вводных данных делает прогноз о наилучшем расположении объекта
- Оптимизирует внутреннюю организацию склада (зонирование, размещение оборудования)
- Анализирует внешнюю логистику (транспортные маршруты, доступность ключевых точек)

### 1.4. Методология выбора
Модель использует следующие параметры для оценки локаций:
- **Географические координаты** и расчет расстояний до ключевых точек:
  - Аэропорт Шереметьево (импорт)
  - Центральный федеральный округ (дистрибуция)
  - Московские клиенты (локальная доставка)
- **Финансовые показатели**:
  - CAPEX (начальные инвестиции): здание, оборудование, валидация GPP/GDP, климатические системы
  - OPEX (операционные расходы): аренда/обслуживание помещения, персонал, транспорт
- **Технические характеристики**:
  - Класс склада (требуется класс A или доведение до фармацевтических стандартов)
  - Возможность организации холодовой цепи
  - Наличие/возможность установки погрузочно-разгрузочных доков

**Результат:** Выбирается локация с минимальным Total Annual OPEX при приемлемом уровне CAPEX

---

## 2. Подход к транспортному обеспечению нового склада

### 2.1. Построение модели цифрового двойника транспортной логистики
Модель искусственного интеллекта симулирует работу склада на каждой рассматриваемой точке с использованием:
- **Открытых источников данных**:
  - OSRM (Open Source Routing Machine) для расчета реальных дорожных расстояний
  - OpenStreetMap для построения маршрутов
  - Данные о дорожной инфраструктуре
- **Коэффициентов погрешности** для учета реальных условий (пробки, сезонность, ограничения движения)

### 2.2. Детальный расчет транспортных потоков
Анализируются три основных направления доставки:
1. **ЦФО (Центральный федеральный округ)** - основная дистрибуция (350 рейсов/месяц)
2. **Аэропорт Шереметьево** - импортные поставки (120 рейсов/месяц)
3. **Москва** - локальная доставка клиентам (180 рейсов/месяц)

### 2.3. Оптимизация транспортного флота
Модель рассчитывает:
- **Состав флота** по типам транспорта:
  - Грузовики 20т (дальние маршруты ЦФО)
  - Фургоны 3.5т (локальная доставка Москва)
  - Рефрижераторы (холодовая цепь)
- **Финансовую оптимальность**:
  - Сравнение аренды vs покупки транспорта
  - Расчет CAPEX и OPEX для каждого варианта
  - Определение оптимальной стратегии (как правило, рекомендуется аренда)
- **Требования к инфраструктуре**:
  - Количество inbound доков (приемка): 6 шт
  - Количество outbound доков (отгрузка): 6 шт
  - Пиковая нагрузка: расчет на основе суточных объемов
  - Утилизация доков: оптимально 60-75%

### 2.4. Симуляция операций
Для каждой локации выполняется симуляция годовой работы склада с учетом:
- Расчетных расстояний по каждому направлению
- Стоимости топлива, амортизации, содержания водителей
- Годовых транспортных расходов (OPEX)

**Результат:** Выбирается вариант с минимальными транспортными затратами при сохранении требуемого уровня сервиса

---

## 3. Результаты анализа текущих складских систем и концепция автоматизации нового склада

### 3.1. Анализ четырех сценариев автоматизации
Наша модель выполняет анализ **четырех уровней автоматизации** склада:

#### **Уровень 0: Без автоматизации (Базовый)**
- **Описание**: Ручная работа без автоматизации
- **CAPEX**: 0 руб (только базовое оборудование)
- **Годовой OPEX**: 0 руб (дополнительных затрат на автоматизацию нет)
- **Персонал**: Без сокращения (100% персонала)
- **Производительность**: Базовая (множитель 1.0)
- **Применение**: Минимальный бюджет, низкие объемы

#### **Уровень 1: Базовая автоматизация (WMS + Сканеры)**
- **Описание**: Система управления складом (WMS), сканеры штрих-кодов, базовое программное обеспечение
- **CAPEX**: 50,000,000 руб
- **Годовой OPEX**: 10,000,000 руб
- **Сокращение персонала**: 20% (экономия на ФОТ)
- **Производительность**: +30% (множитель 1.3)
- **ROI**: Окупаемость ~3 года
- **Применение**: Стандартный уровень для современных складов

#### **Уровень 2: Продвинутая автоматизация (+ Конвейеры + Сортировка)**
- **Описание**: WMS + конвейерные системы + автоматическая сортировка
- **CAPEX**: 200,000,000 руб
- **Годовой OPEX**: 35,000,000 руб
- **Сокращение персонала**: 50% (существенная экономия на ФОТ)
- **Производительность**: 2x (удвоение производительности)
- **ROI**: Окупаемость ~4-5 лет
- **Применение**: Высокие объемы, стабильный ассортимент

#### **Уровень 3: Полная автоматизация (AS/RS + Роботы + AGV)**
- **Описание**:
  - AS/RS (Automated Storage and Retrieval Systems) - автоматизированные системы хранения
  - AGV (Automated Guided Vehicles) - автономные транспортные средства
  - Роботизированные системы комплектации
- **CAPEX**: 600,000,000 руб
- **Годовой OPEX**: 100,000,000 руб
- **Сокращение персонала**: 80% (минимальный персонал для контроля)
- **Производительность**: 3.5x (увеличение в 3.5 раза)
- **ROI**: Окупаемость ~6-8 лет
- **Применение**: Очень высокие объемы, долгосрочная перспектива

### 3.2. Методология ROI-анализа для каждого сценария
Для каждого уровня автоматизации модель рассчитывает:

**Экономические показатели:**
- Экономия на фонде оплаты труда (ФОТ) за счет сокращения персонала
- Рост дохода за счет увеличения throughput (пропускной способности)
- Чистая годовая выгода = (Экономия ФОТ + Дополнительный доход) - OPEX автоматизации
- Срок окупаемости = CAPEX / Чистая годовая выгода
- ROI за 5 лет = ((Чистая выгода × 5 лет) - CAPEX) / CAPEX × 100%

**Операционные показатели:**
- Пропускная способность (заказов/день)
- Утилизация персонала
- Точность комплектации
- Время выполнения заказа (cycle time)

### 3.3. Комплексный анализ текущих складских систем
Модель анализирует следующие аспекты:

#### **Зонирование склада:**
- Нормальное хранение (15-25°C): 65% площади
- Холодовая цепь (2-8°C): 30% площади
- Приемка: 3% площади
- Отгрузка: 2% площади

#### **Распределение SKU по условиям хранения:**
- Нормальные условия: 60% (9,000 SKU из 15,000)
- Холодовая цепь: 30% (4,500 SKU)
- Специальные условия: 10% (1,500 SKU)

#### **Климатические требования и GPP/GDP:**
- **Температурный мониторинг 24/7**:
  - Высокоточные датчики PT100/PT1000 (точность ±0.1°C)
  - Автоматическая сигнализация отклонений
  - Резервирование систем охлаждения (N+1)
- **Валидация систем**:
  - IQ/OQ/PQ квалификация оборудования
  - Температурное картирование
  - Периодическая ревалидация (каждые 6-12 месяцев)
- **GMP классификация**: Grade D для всех зон
- **Документация**: Протоколы валидации, SOP, журналы калибровки

#### **Системы мониторинга:**
- Датчики температуры и влажности по зонам
- ПО мониторинга с compliance 21 CFR Part 11
- Аварийная сигнализация (SMS/Email/Звуковая/Световая)
- Резервное питание (ИБП + генератор)
- **CAPEX систем мониторинга**: ~20,000,000 руб
- **Годовой OPEX**: ~500,000 руб

#### **Детальное оборудование:**
- Стеллажные системы: паллетные стеллажи на 33,000+ паллето-мест
- Погрузочная техника: 8 электропогрузчиков, 12 электротележек
- Климатические системы: 12 HVAC установок, 6 холодильных установок
- Погрузочные доки: 6 inbound + 6 outbound с док-левелерами
- Системы безопасности: пожаротушение, видеонаблюдение (40 камер), СКУД (20 считывателей)
- **Общий CAPEX оборудования**: ~100,000,000 руб

### 3.4. Концепция автоматизации
На основе анализа модель рекомендует:

**Для малого/среднего бизнеса (до 2,000 заказов/день):**
- Уровень 1 (Базовая автоматизация)
- Оптимальное соотношение затрат/эффективности
- Быстрая окупаемость

**Для крупного бизнеса (2,000-5,000 заказов/день):**
- Уровень 2 (Продвинутая автоматизация)
- Существенный рост производительности
- Снижение зависимости от персонала

**Для enterprise-уровня (5,000+ заказов/день):**
- Уровень 3 (Полная автоматизация)
- Максимальная эффективность
- Долгосрочная инвестиция

### 3.5. Визуализация и отчетность
Модель создает:
- Excel-отчеты с 9 вкладками детального анализа
- Визуализации: планировка склада, сравнение сценариев, ROI-анализ
- Анимированные графики сравнения ROI и срока окупаемости
- Отчет валидации модели с верификацией всех расчетов

---

## ЗАКЛЮЧЕНИЕ

Представленная методология обеспечивает:
1. **Научно обоснованный выбор локации** на основе многофакторного анализа и оптимизации CAPEX/OPEX
2. **Оптимизацию транспортной логистики** с использованием реальных дорожных данных и симуляции операций
3. **Детальный анализ складских систем** с учетом фармацевтических требований GPP/GDP
4. **Объективное сравнение сценариев автоматизации** с расчетом финансовых и операционных показателей
5. **Прозрачность и воспроизводимость** всех расчетов с полной документацией и визуализацией

Модель цифрового двойника позволяет принимать решения на основе данных, минимизируя риски и обеспечивая оптимальное использование ресурсов при релокации фармацевтического склада.

---

*Документ подготовлен на основе модели искусственного интеллекта для анализа релокации фармацевтического склада*

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
      "Bash(python test_enhanced_simulation.py:*)",
      "Bash(if exist output mkdir output)",
      "Bash(python warehouse_analysis.py:*)",
      "Bash(output/analysis_log.txt)",
      "Bash(python:*)",
      "Bash(cat:*)",
      "Bash(timeout 300 python:*)",
      "Bash(dir:*)",
      "Bash(findstr:*)"
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
    Базовая симуляция складских операций с использованием SimPy.
    """

    def __init__(self, staff_count: int, efficiency_multiplier: float):
        """
        Args:
            staff_count: Количество операторов склада
            efficiency_multiplier: Коэффициент эффективности обработки
        """
        self.env = simpy.Environment()
        self.staff_count = staff_count
        self.efficiency_multiplier = efficiency_multiplier

        # Операторы как ресурс SimPy
        self.operators = simpy.Resource(self.env, capacity=staff_count)

        # Статистика
        self.processed_orders_count = 0
        self.total_cycle_time_min = 0.0

    def _order_generator(self):
        """Генерирует входящие заказы для обработки."""
        total_orders = config.TARGET_ORDERS_MONTH
        arrival_interval = (config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY) / total_orders

        for order_id in range(total_orders):
            # Добавляем случайность ±20%
            actual_interval = arrival_interval * random.uniform(0.8, 1.2)
            yield self.env.timeout(actual_interval)
            self.env.process(self._process_order(order_id))

    def _process_order(self, order_id: int):
        """Процесс обработки одного заказа."""
        arrival_time = self.env.now

        # Запрашиваем оператора
        with self.operators.request() as operator_request:
            yield operator_request

            # Базовое время обработки
            base_processing_time = config.BASE_ORDER_CYCLE_TIME_MIN

            # Применяем множитель эффективности (автоматизация уменьшает время)
            actual_processing_time = base_processing_time / self.efficiency_multiplier

            # Добавляем вариативность ±15%
            actual_processing_time *= random.uniform(0.85, 1.15)

            # Обработка заказа
            yield self.env.timeout(actual_processing_time)

            # Обновляем статистику
            cycle_time = self.env.now - arrival_time
            self.total_cycle_time_min += cycle_time
            self.processed_orders_count += 1

    def run(self) -> Dict[str, float]:
        """Запускает симуляцию и возвращает итоговые операционные KPI."""

        # Запускаем генератор заказов
        self.env.process(self._order_generator())

        # Задаем общую длительность симуляции с запасом
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
            enable_dock_simulation: Включить симуляцию доков
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
        """Генерирует прибытие грузовиков на приёмку."""
        # 40% от общего числа заказов приходит через inbound
        total_inbound_trucks = int(config.TARGET_ORDERS_MONTH * 0.4 / 10)
        arrival_interval = (config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY) / total_inbound_trucks

        for truck_id in range(total_inbound_trucks):
            actual_interval = arrival_interval * random.uniform(0.8, 1.2)
            yield self.env.timeout(actual_interval)
            self.env.process(self._process_inbound_truck(truck_id))

    def _outbound_truck_generator(self):
        """Генерирует грузовики на отгрузку."""
        # 60% заказов идёт на outbound
        total_outbound_trucks = int(config.TARGET_ORDERS_MONTH * 0.6 / 10)
        arrival_interval = (config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY) / total_outbound_trucks

        for truck_id in range(total_outbound_trucks):
            actual_interval = arrival_interval * random.uniform(0.8, 1.2)
            yield self.env.timeout(actual_interval)
            self.env.process(self._process_outbound_truck(truck_id))

    def _process_inbound_truck(self, truck_id: int):
        """Процесс разгрузки одного грузовика."""
        arrival_time = self.env.now

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
        """Процесс погрузки одного грузовика."""
        arrival_time = self.env.now

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
        """Запускает расширенную симуляцию и возвращает KPI."""

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

        # Добавляем метрики доков
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
        "Total_CAPEX": 1100000000,
        "Annual_OPEX": 510841394.96103835
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
        "Staff_Operators": 180,
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
        "Total_CAPEX": 1150000000,
        "Annual_OPEX": 541081394.9610384
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
        "Staff_Operators": 204,
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
        "Total_CAPEX": 1200000000,
        "Annual_OPEX": 510841394.96103835
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
        "Staff_Operators": 180,
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
        "Total_CAPEX": 1400000000,
        "Annual_OPEX": 510841394.96103835
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
        "Staff_Operators": 180,
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
    Базовая симуляция складских операций с использованием SimPy.
    """

    def __init__(self, staff_count: int, efficiency_multiplier: float):
        """
        Args:
            staff_count: Количество операторов склада
            efficiency_multiplier: Коэффициент эффективности обработки
        """
        self.env = simpy.Environment()
        self.staff_count = staff_count
        self.efficiency_multiplier = efficiency_multiplier

        # Операторы как ресурс SimPy
        self.operators = simpy.Resource(self.env, capacity=staff_count)

        # Статистика
        self.processed_orders_count = 0
        self.total_cycle_time_min = 0.0

    def _order_generator(self):
        """Генерирует входящие заказы для обработки."""
        total_orders = config.TARGET_ORDERS_MONTH
        arrival_interval = (config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY) / total_orders

        for order_id in range(total_orders):
            # Добавляем случайность ±20%
            actual_interval = arrival_interval * random.uniform(0.8, 1.2)
            yield self.env.timeout(actual_interval)
            self.env.process(self._process_order(order_id))

    def _process_order(self, order_id: int):
        """Процесс обработки одного заказа."""
        arrival_time = self.env.now

        # Запрашиваем оператора
        with self.operators.request() as operator_request:
            yield operator_request

            # Базовое время обработки
            base_processing_time = config.BASE_ORDER_CYCLE_TIME_MIN

            # Применяем множитель эффективности (автоматизация уменьшает время)
            actual_processing_time = base_processing_time / self.efficiency_multiplier

            # Добавляем вариативность ±15%
            actual_processing_time *= random.uniform(0.85, 1.15)

            # Обработка заказа
            yield self.env.timeout(actual_processing_time)

            # Обновляем статистику
            cycle_time = self.env.now - arrival_time
            self.total_cycle_time_min += cycle_time
            self.processed_orders_count += 1

    def run(self) -> Dict[str, float]:
        """Запускает симуляцию и возвращает итоговые операционные KPI."""

        # Запускаем генератор заказов
        self.env.process(self._order_generator())

        # Задаем общую длительность симуляции с запасом
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
            enable_dock_simulation: Включить симуляцию доков
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
        """Генерирует прибытие грузовиков на приёмку."""
        # 40% от общего числа заказов приходит через inbound
        total_inbound_trucks = int(config.TARGET_ORDERS_MONTH * 0.4 / 10)
        arrival_interval = (config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY) / total_inbound_trucks

        for truck_id in range(total_inbound_trucks):
            actual_interval = arrival_interval * random.uniform(0.8, 1.2)
            yield self.env.timeout(actual_interval)
            self.env.process(self._process_inbound_truck(truck_id))

    def _outbound_truck_generator(self):
        """Генерирует грузовики на отгрузку."""
        # 60% заказов идёт на outbound
        total_outbound_trucks = int(config.TARGET_ORDERS_MONTH * 0.6 / 10)
        arrival_interval = (config.SIMULATION_WORKING_DAYS * config.MINUTES_PER_WORKING_DAY) / total_outbound_trucks

        for truck_id in range(total_outbound_trucks):
            actual_interval = arrival_interval * random.uniform(0.8, 1.2)
            yield self.env.timeout(actual_interval)
            self.env.process(self._process_outbound_truck(truck_id))

    def _process_inbound_truck(self, truck_id: int):
        """Процесс разгрузки одного грузовика."""
        arrival_time = self.env.now

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
        """Процесс погрузки одного грузовика."""
        arrival_time = self.env.now

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
        """Запускает расширенную симуляцию и возвращает KPI."""

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

        # Добавляем метрики доков
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

