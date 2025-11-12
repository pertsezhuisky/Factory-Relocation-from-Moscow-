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
