"""
Модуль для подробного вывода формул и визуализации всех расчетов.
Создает графики, диаграммы и подробные объяснения для каждого этапа анализа.
"""
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
        print("\n[FORMULA] Ispol'zuetsya formula Haversine dlya rascheta rasstoyaniya po poverhnosti Zemli:")

        formula_latex = "d = 2R x arcsin(sqrt(sin^2(Deltalat/2) + cos(lat_1) x cos(lat_2) x sin^2(Deltalon/2))) x 1.4"
        variables = {
            "R": (6371.0, "радиус Земли в км"),
            "lat_1, lon_1": (f"{warehouse_coords[0]:.4f}, {warehouse_coords[1]:.4f}", "координаты склада"),
            "Deltalat, Deltalon": ("разница координат", "в радианах"),
            "1.4": (1.4, "коэффициент реальных дорог (извилистость)")
        }

        print(f"\n+- Формула Haversine (расчет расстояния по дуге большого круга) " + "-" * 28)
        print(f"|")
        print(f"| ФОРМУЛА: {formula_latex}")
        print(f"|")
        print(f"| ГДЕ:")
        for var_name, var_data in variables.items():
            value, description = var_data if isinstance(var_data, tuple) else (var_data, "")
            print(f"|    {var_name} = {value} ({description})")
        print(f"+" + "-" * 99)

        # Детальный расчет для каждой точки
        print(f"\n[LOC] Координаты склада: ({warehouse_coords[0]:.4f}, {warehouse_coords[1]:.4f})")
        print(f"\n[CHART] Расчет расстояний до ключевых точек:\n")

        for point_name, point_coords in key_points.items():
            dist = distances.get(point_name, 0)
            print(f"  > {point_name}:")
            print(f"      Координаты цели: ({point_coords[0]:.4f}, {point_coords[1]:.4f})")
            print(f"      Расстояние: {dist:.2f} км")
            print()

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
        filename = f'{self.output_dir}/distances_{location_name.replace(" ", "_")}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n[SAVE] График сохранен: {filename}")
        plt.close()

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
        print("\n РАСЧЕТ CAPEX (Capital Expenditure - Капитальные затраты):\n")

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
        print("\n РАСЧЕТ OPEX (Operational Expenditure - Операционные затраты):\n")

        total_opex = sum(opex_data.values())
        formula_opex = "OPEX_total = OPEX_building + OPEX_personnel + OPEX_transport"

        self.print_formula(
            "Годовой OPEX",
            formula_opex,
            {key: (value, key) for key, value in opex_data.items()},
            total_opex,
            "руб/год"
        )

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

        filename = f'{self.output_dir}/finance_{location_name.replace(" ", "_")}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n[SAVE] График сохранен: {filename}")
        plt.close()

    def visualize_transport_costs(self, location_name: str,
                                  fleet_data: List[Dict[str, Any]],
                                  total_summary: Dict[str, float]):
        """
        Визуализирует детальные транспортные расходы и состав флота.

        Args:
            location_name: Название локации
            fleet_data: Список с данными по каждому типу транспорта
            total_summary: Общие итоги по транспорту
        """
        self.print_section_header(f"ДЕТАЛЬНЫЙ ТРАНСПОРТНЫЙ АНАЛИЗ: {location_name}", level=2)

        # Вывод формул расчета транспортных расходов
        print("\n[TRUCK] РАСЧЕТ ТРАНСПОРТНЫХ РАСХОДОВ:\n")

        for fleet in fleet_data:
            print(f"\n+- {fleet['vehicle_name']} " + "-" * (95 - len(fleet['vehicle_name'])))
            print(f"|")
            print(f"| Количество: {fleet['required_count']} единиц")
            print(f"| Рейсов в год: {fleet['annual_trips']:,}")
            print(f"| Километраж в год: {fleet['annual_distance_km']:,.0f} км")
            print(f"|")
            print(f"| ДЕТАЛИЗАЦИЯ РАСХОДОВ:")
            for cost_name, cost_value in fleet['costs'].items():
                if cost_name != 'total_opex_rub':
                    print(f"|    {cost_name}: {cost_value:,.0f} руб")
            print(f"|")
            print(f"| === ИТОГО OPEX: {fleet['costs']['total_opex_rub']:,.0f} руб/год ===")
            print(f"| === CAPEX (покупка): {fleet['capex_purchase_rub']:,.0f} руб ===")
            print(f"| === OPEX (аренда): {fleet['opex_lease_rub']:,.0f} руб/год ===")
            print(f"+" + "-" * 99)

        # Создание визуализации
        fig = plt.figure(figsize=(18, 12))
        gs = GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.3)

        # График 1: Состав флота
        ax1 = fig.add_subplot(gs[0, :])
        vehicle_names = [f"{f['vehicle_name']}\n({f['required_count']} ед.)" for f in fleet_data]
        vehicle_counts = [f['required_count'] for f in fleet_data]
        colors = plt.cm.tab20(np.linspace(0, 1, len(fleet_data)))

        bars = ax1.bar(range(len(fleet_data)), vehicle_counts, color=colors,
                      edgecolor='black', linewidth=2, alpha=0.8)
        ax1.set_xticks(range(len(fleet_data)))
        ax1.set_xticklabels(vehicle_names, fontsize=9)
        ax1.set_ylabel('Количество единиц техники', fontsize=11)
        ax1.set_title('Состав транспортного флота', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

        for bar, count in zip(bars, vehicle_counts):
            ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                    f'{count}', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # График 2: Распределение годового километража
        ax2 = fig.add_subplot(gs[1, 0])
        distances = [f['annual_distance_km'] for f in fleet_data]
        vehicle_labels = [f['vehicle_name'].split('(')[0][:20] for f in fleet_data]

        wedges, texts, autotexts = ax2.pie(
            distances,
            labels=vehicle_labels,
            autopct=lambda pct: f'{pct:.1f}%\n({pct*sum(distances)/100:,.0f} км)',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 8}
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(7)
        ax2.set_title(f'Распределение километража\nОбщий годовой пробег: {sum(distances):,.0f} км',
                     fontsize=12, fontweight='bold')

        # График 3: Сравнение OPEX по типам транспорта
        ax3 = fig.add_subplot(gs[1, 1])
        opex_values = [f['costs']['total_opex_rub'] for f in fleet_data]

        bars = ax3.barh(range(len(fleet_data)), opex_values, color=colors,
                       edgecolor='black', linewidth=1.5, alpha=0.8)
        ax3.set_yticks(range(len(fleet_data)))
        ax3.set_yticklabels(vehicle_labels, fontsize=9)
        ax3.set_xlabel('Годовой OPEX (руб)', fontsize=11)
        ax3.set_title('OPEX по типам транспорта (собственный флот)', fontsize=12, fontweight='bold')
        ax3.grid(axis='x', alpha=0.3)

        for bar, opex in zip(bars, opex_values):
            ax3.text(opex + opex*0.02, bar.get_y() + bar.get_height()/2.,
                    f'{opex/1_000_000:.1f}М', va='center', fontsize=9, fontweight='bold')

        # График 4: Структура расходов для каждого типа транспорта
        ax4 = fig.add_subplot(gs[2, :])

        # Подготовка данных для stacked bar chart
        cost_categories = ['fuel_rub', 'maintenance_rub', 'driver_salaries_rub', 'insurance_rub']
        cost_labels = ['Топливо', 'Обслуживание', 'Зарплаты водителей', 'Страхование']

        # Проверяем наличие refrigeration_rub
        if any('refrigeration_rub' in f['costs'] for f in fleet_data):
            cost_categories.append('refrigeration_rub')
            cost_labels.append('Охлаждение')

        cost_data = []
        for category in cost_categories:
            category_values = []
            for fleet in fleet_data:
                category_values.append(fleet['costs'].get(category, 0))
            cost_data.append(category_values)

        x = np.arange(len(fleet_data))
        width = 0.6
        bottom = np.zeros(len(fleet_data))

        cost_colors = plt.cm.Set3(np.linspace(0, 1, len(cost_categories)))

        for idx, (category_values, label) in enumerate(zip(cost_data, cost_labels)):
            ax4.bar(x, category_values, width, label=label, bottom=bottom,
                   color=cost_colors[idx], edgecolor='black', linewidth=0.5)
            bottom += category_values

        ax4.set_xticks(x)
        ax4.set_xticklabels(vehicle_labels, rotation=45, ha='right', fontsize=9)
        ax4.set_ylabel('Расходы (руб/год)', fontsize=11)
        ax4.set_title('Детальная структура расходов по типам транспорта', fontsize=14, fontweight='bold')
        ax4.legend(loc='upper left', fontsize=9)
        ax4.grid(axis='y', alpha=0.3)

        plt.suptitle(f'Транспортный анализ: {location_name}',
                    fontsize=16, fontweight='bold', y=0.995)

        filename = f'{self.output_dir}/transport_{location_name.replace(" ", "_")}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n[SAVE] График сохранен: {filename}")
        plt.close()

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
        print(f"\n[SAVE] Сравнительный график сохранен: {filename}")
        plt.close()

        # Вывод таблицы с рейтингом
        print("\n[CHART] РЕЙТИНГ ЛОКАЦИЙ ПО ГОДОВОМУ OPEX:\n")
        sorted_locations = sorted(locations_data, key=lambda x: x['total_annual_opex_s1'])

        print("+-----+---------------------------------+------------------+------------------+------------------+")
        print("|  | Локация                         | CAPEX (млн руб)  | OPEX (млн руб)   | Тип владения     |")
        print("+-----+---------------------------------+------------------+------------------+------------------+")

        for idx, loc in enumerate(sorted_locations, 1):
            marker = "[WIN]" if idx == 1 else f" {idx} "
            print(f"| {marker} | {loc['location_name'][:30]:<31} | {loc['total_initial_capex']/1_000_000:>14.1f}   |"
                  f" {loc['total_annual_opex_s1']/1_000_000:>14.1f}   | {loc['type']:<16} |")

        print("+-----+---------------------------------+------------------+------------------+------------------+")

    def create_dashboard(self, optimal_location: Dict[str, Any],
                        fleet_summary: Dict[str, Any],
                        dock_requirements: Dict[str, Any]):
        """
        Создает итоговый dashboard с ключевыми показателями оптимальной локации.

        Args:
            optimal_location: Данные оптимальной локации
            fleet_summary: Данные по флоту
            dock_requirements: Требования к докам
        """
        self.print_section_header("ИТОГОВЫЙ DASHBOARD - ОПТИМАЛЬНАЯ ЛОКАЦИЯ", level=1)

        fig = plt.figure(figsize=(20, 14))
        gs = GridSpec(4, 3, figure=fig, hspace=0.4, wspace=0.35)

        # Заголовок с основной информацией
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')

        title_text = f"ОПТИМАЛЬНАЯ ЛОКАЦИЯ: {optimal_location['location_name']}\n"
        title_text += f"Координаты: ({optimal_location['lat']:.4f}, {optimal_location['lon']:.4f})\n"
        title_text += f"Площадь: {optimal_location['area_offered_sqm']:,} м^2 | "
        title_text += f"Тип: {optimal_location['type']}"

        ax_title.text(0.5, 0.5, title_text, ha='center', va='center',
                     fontsize=16, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=1', facecolor='lightblue', alpha=0.8))

        # КПИ блоки
        kpi_data = [
            ("CAPEX", f"{optimal_location['total_initial_capex']/1_000_000:.0f}М руб", "Первоначальные инвестиции", 'Blues'),
            ("Годовой OPEX", f"{optimal_location['total_annual_opex_s1']/1_000_000:.0f}М руб/год", "Операционные расходы", 'Oranges'),
            ("Транспорт", f"{fleet_summary['total_vehicles']} единиц", f"Рекомендация: {fleet_summary['recommendation']}", 'Greens'),
        ]

        for idx, (title, value, subtitle, cmap) in enumerate(kpi_data):
            ax = fig.add_subplot(gs[1, idx])
            ax.axis('off')

            color = plt.cm.get_cmap(cmap)(0.6)
            rect = patches.FancyBboxPatch((0.1, 0.2), 0.8, 0.6,
                                         boxstyle="round,pad=0.05",
                                         facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(rect)

            ax.text(0.5, 0.7, title, ha='center', va='center',
                   fontsize=12, fontweight='bold', transform=ax.transAxes)
            ax.text(0.5, 0.5, value, ha='center', va='center',
                   fontsize=18, fontweight='bold', transform=ax.transAxes)
            ax.text(0.5, 0.3, subtitle, ha='center', va='center',
                   fontsize=9, style='italic', transform=ax.transAxes)

        # График флота
        ax2 = fig.add_subplot(gs[2, :2])
        fleet_names = [f['vehicle_name'].split('(')[0][:25] for f in fleet_summary['fleet_breakdown']]
        fleet_counts = [f['required_count'] for f in fleet_summary['fleet_breakdown']]

        colors = plt.cm.tab10(np.linspace(0, 1, len(fleet_summary['fleet_breakdown'])))
        bars = ax2.barh(range(len(fleet_names)), fleet_counts, color=colors,
                       edgecolor='black', linewidth=1.5, alpha=0.8)
        ax2.set_yticks(range(len(fleet_names)))
        ax2.set_yticklabels(fleet_names, fontsize=9)
        ax2.set_xlabel('Количество единиц', fontsize=11)
        ax2.set_title('Состав транспортного флота', fontsize=13, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)

        for bar, count in zip(bars, fleet_counts):
            ax2.text(count + 0.1, bar.get_y() + bar.get_height()/2.,
                    f'{count}', va='center', fontsize=10, fontweight='bold')

        # График доков
        ax3 = fig.add_subplot(gs[2, 2])
        dock_labels = ['Inbound\n(приемка)', 'Outbound\n(отгрузка)']
        dock_values = [dock_requirements['inbound_docks'], dock_requirements['outbound_docks']]

        bars = ax3.bar(range(2), dock_values, color=['#4CAF50', '#FF9800'],
                      edgecolor='black', linewidth=2, alpha=0.8, width=0.6)
        ax3.set_xticks(range(2))
        ax3.set_xticklabels(dock_labels, fontsize=10)
        ax3.set_ylabel('Количество доков', fontsize=11)
        ax3.set_title(f'Требования к докам\nУтилизация: {dock_requirements["dock_utilization_percent"]:.1f}%',
                     fontsize=12, fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)

        for bar, value in zip(bars, dock_values):
            ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
                    f'{value}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        # Структура OPEX
        ax4 = fig.add_subplot(gs[3, :])

        opex_components = {
            'OPEX помещения': optimal_location['annual_building_opex'],
            'OPEX транспорта': optimal_location['total_annual_transport_cost']
        }

        colors_opex = ['#2196F3', '#FFC107']
        wedges, texts, autotexts = ax4.pie(
            opex_components.values(),
            labels=opex_components.keys(),
            autopct=lambda pct: f'{pct:.1f}%\n{pct*sum(opex_components.values())/100/1_000_000:.1f}М руб',
            colors=colors_opex,
            startangle=90,
            textprops={'fontsize': 11}
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax4.set_title(f'Структура годового OPEX\nОбщая сумма: {sum(opex_components.values())/1_000_000:.0f}М руб',
                     fontsize=13, fontweight='bold')

        plt.suptitle('ИТОГОВЫЙ DASHBOARD - РЕЗУЛЬТАТЫ АНАЛИЗА',
                    fontsize=18, fontweight='bold', y=0.98)

        filename = f'{self.output_dir}/dashboard_optimal_location.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n[SAVE] Dashboard сохранен: {filename}")
        plt.close()


# Глобальный экземпляр визуализатора
visualizer = FormulaVisualizer()
