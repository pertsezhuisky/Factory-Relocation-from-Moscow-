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