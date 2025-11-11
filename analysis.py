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
    # Этот блок теперь может выполнять разные задачи.
    # Для построения графика по-прежнему вызываем plot_results()
    # plot_results()

    # Демонстрация работы FleetOptimizer
    print("\n" + "="*80)
    print("ЗАПУСК АНАЛИЗА ТРАНСПОРТНЫХ ПОТОКОВ (FleetOptimizer)")
    print("="*80)
    optimizer = FleetOptimizer()

    # 5. Заглушка для расстояний (Логопарк Север-2)
    dist_cfo = 400  # км
    dist_svo = 30   # км
    dist_local = 60 # км

    required_fleet = optimizer.calculate_required_fleet()
    annual_cost = optimizer.calculate_annual_transport_cost(dist_cfo, dist_svo, dist_local)

    print(f"Расчет для новой локации (расстояния: ЦФО={dist_cfo}км, SVO={dist_svo}км, Local={dist_local}км):\n")
    print(f"  > Минимально необходимое количество грузовиков для ЦФО: {required_fleet} шт.")
    print(f"  > Прогнозируемые годовые транспортные расходы: {annual_cost:,.2f} руб.")
    print("="*80)