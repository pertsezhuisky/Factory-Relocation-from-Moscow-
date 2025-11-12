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