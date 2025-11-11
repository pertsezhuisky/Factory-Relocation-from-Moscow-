"""
Скрипт для анализа и визуализации результатов ПОСЛЕ выполнения симуляции.
Запускается отдельно командой: python analysis.py
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config
import math

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
                "total_initial_capex": total_initial_capex
            })

        return scored_locations

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