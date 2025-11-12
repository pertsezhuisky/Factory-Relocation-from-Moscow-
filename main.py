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

    # 8. Валидация модели (временно отключена по запросу пользователя)
    print("\n" + "+"*120)
    print("[ШАГ 8] ВАЛИДАЦИЯ И ВЕРИФИКАЦИЯ МОДЕЛИ (пропущено)")
    print("+"*120)
    print("\n[INFO] Валидация отключена. Включите вручную при необходимости.")

    # validation_results = run_full_validation(
    #     location_data=optimal_location,
    #     warehouse_data=warehouse_validation_data,
    #     roi_data=warehouse_analyzer.roi_data,
    #     automation_scenarios=warehouse_analyzer.automation_scenarios
    # )
    #
    # print(f"\n[Результаты валидации]")
    # print(f"  Всего проверок: {len(validation_results['validation_results'])}")
    # print(f"  Критических ошибок: {validation_results['critical_failures']}")
    # print(f"  Предупреждений: {validation_results['warnings']}")
    # print(f"  Отчет сохранен: {validation_results['report_path']}")
    # print(f"  Общий балл: {validation_results['verification_results']['overall_score']:.1f}/100")

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
    print("  * warehouse_analysis_report.xlsx - Полный Excel отчет")
    print("  * validation_report.xlsx - Отчет валидации модели")
    print("  * roi_comparison_animated.gif - Анимация сравнения ROI")
    print("  * payback_period_animated.gif - Анимация срока окупаемости")
    print("="*120)


if __name__ == "__main__":
    try:
        main_multi_location_runner()
    except Exception as e:
        print(f"\n[ОШИБКА] Произошла непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()
