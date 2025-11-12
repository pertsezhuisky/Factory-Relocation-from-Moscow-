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
from formula_visualizer import visualizer

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
    visualizer.print_section_header("ЗАПУСК КОМПЛЕКСНОГО АНАЛИЗА МНОЖЕСТВА ЛОКАЦИЙ", level=1)

    # 1. Сбор и фильтрация данных (Avito Stub)
    visualizer.print_section_header("ШАГ 1: СБОР И ФИЛЬТРАЦИЯ ДАННЫХ О ЛОКАЦИЯХ", level=2)
    parser = AvitoParserStub()
    candidate_locations_raw = config.ALL_CANDIDATE_LOCATIONS
    filtered_locations: List[Dict[str, Any]] = parser.filter_and_score_locations(candidate_locations_raw)
    print(f"\n[OK] Otfiltrovano {len(filtered_locations)} podhodyashchih lokatsiy iz {len(candidate_locations_raw)}.")

    if not filtered_locations:
        print("[ERROR] Net lokatsiy, udovletvoryayushchih minimal'nym trebovaniyam. Analiz prekrashchen.")
        return

    enriched_locations: List[Dict[str, Any]] = []

    # Расчет Z_перс (минимальные расходы на персонал для Сценария 1)
    visualizer.print_section_header("ШАГ 2: РАСЧЕТ РАСХОДОВ НА ПЕРСОНАЛ (Сценарий 1)", level=2)

    s1_staff_attrition_rate = SCENARIOS_CONFIG["1_Move_No_Mitigation"]["staff_attrition_rate"]
    s1_staff_count = math.floor(config.INITIAL_STAFF_COUNT * (1 - s1_staff_attrition_rate))

    # Базовые расходы на зарплату
    z_pers_base = s1_staff_count * config.OPERATOR_SALARY_RUB_MONTH * 12

    # Дополнительные расходы на персонал
    # 1. Обучение новых сотрудников (единоразово в первый год)
    new_hires = math.floor(config.INITIAL_STAFF_COUNT * s1_staff_attrition_rate)  # Количество новых сотрудников
    training_costs = new_hires * config.STAFF_TRAINING_COST_PER_PERSON

    # 2. Адаптация (20% от зарплаты в первый месяц для новых сотрудников)
    adaptation_costs = new_hires * config.OPERATOR_SALARY_RUB_MONTH * config.STAFF_ADAPTATION_RATE

    # 3. Компенсация при переезде (для сотрудников, которые переезжают с компанией)
    relocating_staff = config.INITIAL_STAFF_COUNT - new_hires
    relocation_costs = relocating_staff * config.STAFF_RELOCATION_COMPENSATION

    # Общие годовые расходы на персонал (включая единоразовые затраты в первый год)
    z_pers_s1 = z_pers_base + training_costs + adaptation_costs + relocation_costs

    # Подробный вывод формулы расчета персонала
    visualizer.print_formula(
        "Raschet polnyh rashodov na personal (s uchetom obucheniya i kompensatsiy)",
        "Z_pers = Zarplaty + Obuchenie + Adaptatsiya + Kompensatsii",
        {
            "N_nachal'noe": (config.INITIAL_STAFF_COUNT, "nachal'noe kolichestvo sotrudnikov"),
            "Koeff_ottoka": (s1_staff_attrition_rate, "koeffitsient ottoka personala (Stsenariy 1)"),
            "N_sotrudnikov": (s1_staff_count, f"floor({config.INITIAL_STAFF_COUNT} * (1 - {s1_staff_attrition_rate}))"),
            "N_novyh": (new_hires, "kolichestvo novyh sotrudnikov"),
            "Zarplata_mesyats": (config.OPERATOR_SALARY_RUB_MONTH, "srednyaya zarplata operatora v mesyats, rub"),
            "Zarplaty_god": (z_pers_base, f"{s1_staff_count} * {config.OPERATOR_SALARY_RUB_MONTH} * 12"),
            "Obuchenie": (training_costs, f"{new_hires} * {config.STAFF_TRAINING_COST_PER_PERSON}"),
            "Adaptatsiya": (adaptation_costs, f"{new_hires} * {config.OPERATOR_SALARY_RUB_MONTH} * {config.STAFF_ADAPTATION_RATE}"),
            "Kompensatsii": (relocation_costs, f"{relocating_staff} * {config.STAFF_RELOCATION_COMPENSATION}")
        },
        z_pers_s1,
        "rub (pervyy god)"
    )

    visualizer.print_section_header("ШАГ 3: АНАЛИЗ ЛОГИСТИКИ И РАСЧЕТ ТРАНСПОРТНЫХ РАСХОДОВ", level=2)

    for loc_data in filtered_locations:
        print(f"\n{'-'*100}")
        print(f">>> Analiz lokatsii: '{loc_data['location_name']}'")
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

        # Визуализация расчета расстояний
        key_points = {
            "ЦФО (хабы)": config.KEY_GEO_POINTS["CFD_HUBs_Avg"],
            "SVO (аэропорт)": config.KEY_GEO_POINTS["Airport_SVO"],
            "Москва (ЛПУ)": config.KEY_GEO_POINTS["Moscow_Clients_Avg"]
        }
        distances = {
            "ЦФО (хабы)": avg_dist_cfo,
            "SVO (аэропорт)": avg_dist_svo,
            "Москва (ЛПУ)": avg_dist_local
        }
        visualizer.visualize_distance_calculation(
            loc_data['location_name'],
            (loc_data['lat'], loc_data['lon']),
            key_points,
            distances
        )

        # Расчет транспортных расходов
        fleet_optimizer = FleetOptimizer()
        total_annual_transport_cost = fleet_optimizer.calculate_annual_transport_cost(avg_dist_cfo, avg_dist_svo, avg_dist_local)
        required_fleet_count = fleet_optimizer.calculate_required_fleet()

        # Подробный вывод формулы транспортных расходов
        annual_orders = config.TARGET_ORDERS_MONTH * 12
        cost_cfo = annual_orders * fleet_optimizer.CFO_OWN_FLEET_SHARE * avg_dist_cfo * config.TRANSPORT_TARIFF_RUB_PER_KM
        cost_svo = annual_orders * fleet_optimizer.AIR_DELIVERY_SHARE * avg_dist_svo * config.TRANSPORT_TARIFF_RUB_PER_KM
        cost_local = annual_orders * fleet_optimizer.LOCAL_DELIVERY_SHARE * avg_dist_local * config.MOSCOW_DELIVERY_TARIFF_RUB_PER_KM

        visualizer.print_formula(
            "Raschet godovyh transportnyh rashodov",
            "T_god = T_TsFO + T_SVO + T_Moskva",
            {
                "Zakazov/god": (annual_orders, f"{config.TARGET_ORDERS_MONTH} * 12"),
                "Dolya_TsFO": (fleet_optimizer.CFO_OWN_FLEET_SHARE, "dolya zakazov v TsFO"),
                "Dolya_SVO": (fleet_optimizer.AIR_DELIVERY_SHARE, "dolya aviado stavki"),
                "Dolya_Moskva": (fleet_optimizer.LOCAL_DELIVERY_SHARE, "dolya mestnoy dostavki"),
                "Rasst_TsFO": (avg_dist_cfo, "rasstoyanie do TsFO, km"),
                "Rasst_SVO": (avg_dist_svo, "rasstoyanie do SVO, km"),
                "Rasst_Moskva": (avg_dist_local, "rasstoyanie do Moskvy, km"),
                "Tarif_standart": (config.TRANSPORT_TARIFF_RUB_PER_KM, "tarif 18-20t, rub/km"),
                "Tarif_Moskva": (config.MOSCOW_DELIVERY_TARIFF_RUB_PER_KM, "tarif Moskva, rub/km"),
                "T_TsFO": (cost_cfo, f"{annual_orders} * {fleet_optimizer.CFO_OWN_FLEET_SHARE} * {avg_dist_cfo:.0f} * {config.TRANSPORT_TARIFF_RUB_PER_KM}"),
                "T_SVO": (cost_svo, f"{annual_orders} * {fleet_optimizer.AIR_DELIVERY_SHARE} * {avg_dist_svo:.0f} * {config.TRANSPORT_TARIFF_RUB_PER_KM}"),
                "T_Moskva": (cost_local, f"{annual_orders} * {fleet_optimizer.LOCAL_DELIVERY_SHARE} * {avg_dist_local:.0f} * {config.MOSCOW_DELIVERY_TARIFF_RUB_PER_KM}")
            },
            total_annual_transport_cost,
            "rub/god"
        )

        # Расчет Total_Annual_OPEX (Z_общ) для Сценария 1
        total_annual_opex_s1 = loc_data['annual_building_opex'] + z_pers_s1 + total_annual_transport_cost

        visualizer.print_formula(
            "Raschet obshchego godovogo OPEX (Stsenariy 1)",
            "OPEX_obshchiy = OPEX_pomeshchenie + OPEX_personal + OPEX_transport",
            {
                "OPEX_pomeshchenie": (loc_data['annual_building_opex'], "rashody na pomeshchenie"),
                "OPEX_personal": (z_pers_s1, "rashody na personal"),
                "OPEX_transport": (total_annual_transport_cost, "transportnye rashody")
            },
            total_annual_opex_s1,
            "rub/god"
        )

        # Визуализация финансовой структуры
        capex_data = {
            "Оборудование": float(50_000_000),
            "Климат GPP/GDP": float(250_000_000),
            "Модификации": float(100_000_000 if loc_data['current_class'] == 'A_requires_mod' else 0)
        }
        if loc_data['type'] == 'POKUPKA_BTS':
            capex_data["Покупка здания"] = float(loc_data['total_initial_capex'] - sum(capex_data.values()))

        opex_data = {
            "OPEX помещения": float(loc_data['annual_building_opex']),
            "OPEX персонала": float(z_pers_s1),
            "OPEX транспорта": float(total_annual_transport_cost)
        }

        visualizer.visualize_capex_opex_breakdown(
            loc_data['location_name'],
            capex_data,
            opex_data
        )

        loc_data['total_annual_transport_cost'] = total_annual_transport_cost
        loc_data['required_fleet_count'] = required_fleet_count
        loc_data['total_annual_opex_s1'] = total_annual_opex_s1
        enriched_locations.append(loc_data)

    # 4. Поиск Оптимума и сравнение всех локаций
    visualizer.print_section_header("ШАГ 4: ВЫБОР ОПТИМАЛЬНОЙ ЛОКАЦИИ", level=2)

    # Создаем сравнительную визуализацию всех локаций
    visualizer.visualize_location_comparison(enriched_locations)

    optimal_location = min(enriched_locations, key=lambda x: x['total_annual_opex_s1'])

    print(f"\n{'*'*100}")
    print(f"\n[WINNER] OPTIMAL'NAYA LOKATSIYA NAYDENA: '{optimal_location['location_name']}'")
    print(f"\n   [KPI] Minimal'nyy godovoy OPEX (Stsenariy 1): {optimal_location['total_annual_opex_s1']:,.0f} rub/god")
    print(f"   [CAPEX] {optimal_location['total_initial_capex']:,.0f} rub")
    print(f"   [COORDS] ({optimal_location['lat']:.4f}, {optimal_location['lon']:.4f})")
    print(f"   [TYPE] {optimal_location['type']}")
    print(f"\n{'*'*100}\n")

    # 5. Детальный транспортный анализ для оптимальной локации
    visualizer.print_section_header("ШАГ 5: ДЕТАЛЬНЫЙ ТРАНСПОРТНЫЙ АНАЛИЗ ОПТИМАЛЬНОЙ ЛОКАЦИИ", level=2)

    # Используем OSRM для точных расстояний
    print("\n[OSRM] Ispol'zuetsya OSRM API dlya tochnogo rascheta dorozhnyh rasstoyaniy...")
    geo_router = OSRMGeoRouter(use_geocoding=False)
    optimal_coords = (optimal_location['lat'], optimal_location['lon'])

    # Получаем точные расстояния через OSRM
    route_data = geo_router.calculate_weighted_annual_distance(optimal_coords)

    distances = {
        'cfo_km': route_data['CFO']['distance_km'],
        'svo_km': route_data['SVO']['distance_km'],
        'local_km': route_data['LPU']['distance_km']
    }

    print(f"\n[DISTANCES] Tochnye dorozhnye rasstoyaniya (OSRM):")
    print(f"   * TsFO: {distances['cfo_km']:.2f} km")
    print(f"   * SVO: {distances['svo_km']:.2f} km")
    print(f"   * Moskva: {distances['local_km']:.2f} km")

    # Детальный расчет флота
    print("\n[FLEET] Raschet detal'nogo sostava transportnogo flota...")
    detailed_planner = DetailedFleetPlanner()
    fleet_summary = detailed_planner.calculate_fleet_requirements(distances)

    # Визуализация транспортных расходов
    visualizer.visualize_transport_costs(
        optimal_location['location_name'],
        fleet_summary['fleet_breakdown'],
        {
            'total_vehicles': fleet_summary['total_vehicles'],
            'total_opex': fleet_summary['total_opex_own_fleet'],
            'total_capex': fleet_summary['total_capex_purchase'],
            'total_lease': fleet_summary['total_opex_lease']
        }
    )

    # Расчет доков
    print("\n[DOCKS] Raschet trebovaniy k infrastrukture dokov...")
    dock_requirements = detailed_planner.calculate_dock_requirements(fleet_summary)

    # Генерация графика работы
    _ = detailed_planner.generate_transport_schedule(fleet_summary)

    # Проверка достаточности доков
    dock_sim = DockSimulator(
        inbound_docks=dock_requirements['inbound_docks'],
        outbound_docks=dock_requirements['outbound_docks']
    )
    dock_simulation = dock_sim.simulate_dock_operations(dock_requirements['peak_trips_per_day'])

    print(f"\n+-- Proverka propusknoy sposobnosti dokov " + "-" * 60)
    print(f"|")
    print(f"|  [+] Inbound doki (priemka): {dock_requirements['inbound_docks']} sht")
    print(f"|      Utilizatsiya: {dock_simulation['inbound_utilization_percent']:.1f}%")
    print(f"|")
    print(f"|  [+] Outbound doki (otgruzka): {dock_requirements['outbound_docks']} sht")
    print(f"|      Utilizatsiya: {dock_simulation['outbound_utilization_percent']:.1f}%")
    print(f"|")
    if not dock_simulation['is_sufficient']:
        print(f"|  [WARNING] Dokov nedostatochno! Trebuetsya uvelichenie.")
    else:
        print(f"|  [OK] Dokov dostatochno dlya tekushchey nagruzki")
    print(f"+--" + "-" * 97)

    print(f"\n+-- Rekomendatsiya po transportnomu flotu " + "-" * 56)
    print(f"|")
    if fleet_summary['recommendation'] == 'lease':
        print(f"|  [RECOMMENDATION] Arenda transporta")
        print(f"|     * Godovoy OPEX (arenda): {fleet_summary['total_opex_lease']:,.0f} rub/god")
        print(f"|     * Godovoy OPEX (sobstvennyy): {fleet_summary['total_opex_own_fleet']:,.0f} rub/god")
        print(f"|     * Ekonomiya: {fleet_summary['total_opex_own_fleet'] - fleet_summary['total_opex_lease']:,.0f} rub/god")
    else:
        print(f"|  [RECOMMENDATION] Pokupka transporta")
        print(f"|     * CAPEX (pokupka): {fleet_summary['total_capex_purchase']:,.0f} rub")
        print(f"|     * Godovoy OPEX: {fleet_summary['total_opex_own_fleet']:,.0f} rub/god")
        print(f"|     * ROI dostigaetsya cherez ~5 let")
    print(f"+--" + "-" * 97)

    # 6. Детализация Сценариев и SimPy для Оптимальной Локации
    visualizer.print_section_header("ШАГ 6: ЗАПУСК SIMPY СИМУЛЯЦИИ ДЛЯ ВСЕХ СЦЕНАРИЕВ", level=2)

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

    print("\n[SIMPY] Zapusk detal'noy SimPy simulyatsii operatsiy sklada...")
    print(f"   * Lokatsiya: {optimal_location['location_name']}")
    print(f"   * Bazovyy CAPEX: {initial_base_finance_for_runner['base_capex']:,.0f} rub")
    print(f"   * Bazovyy OPEX: {initial_base_finance_for_runner['base_opex']:,.0f} rub/god")

    runner = SimulationRunner(location_spec=optimal_location_spec)
    runner.run_all_scenarios(initial_base_finance=initial_base_finance_for_runner)

    # 7. Создание итогового dashboard
    visualizer.print_section_header("ШАГ 7: СОЗДАНИЕ ИТОГОВОГО DASHBOARD", level=2)

    print("\n[DASHBOARD] Generatsiya itogo dashboard s vizualizatsiey vseh klyuchevyh pokazateley...")
    visualizer.create_dashboard(optimal_location, fleet_summary, dock_requirements)

    # 8. Детальный анализ склада (зонирование, условия хранения, автоматизация)
    visualizer.print_section_header("ШАГ 8: ДЕТАЛЬНЫЙ АНАЛИЗ СКЛАДА И АВТОМАТИЗАЦИИ", level=2)

    print("\n[WAREHOUSE] Zapusk kompleksnogo analiza sklada dlya optimal'noy lokatsii...")
    print(f"   * Lokatsiya: {optimal_location['location_name']}")
    print(f"   * Ploshchad': {optimal_location['area_offered_sqm']:,.0f} kv.m")

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

    # 9. Вывод Плана Переезда
    visualizer.print_section_header("ШАГ 9: ДЕТАЛЬНЫЙ ПЛАН ПЕРЕЕЗДА", level=2)
    generate_detailed_relocation_plan(optimal_location, z_pers_s1, fleet_summary, dock_requirements)

if __name__ == "__main__":
    try:
        main_multi_location_runner()
    except Exception as e:
        print(f"\n[ОШИБКА] Произошла непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()