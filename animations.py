"""
Модуль для создания анимированных визуализаций финансовых показателей.
Включает анимации ROI, окупаемости, денежного потока и других KPI.
"""
import os
import numpy as np
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
        ax2.set_xticklabels([s['name'].split()[0] for s in scenarios], rotation=45, ha='right')
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
            ax2.set_xticklabels([s['name'].split()[0] for s in scenarios], rotation=45, ha='right')
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
        print(f"  [Сохранение] {save_path}...")
        anim.save(save_path, writer='pillow', fps=20, dpi=100)
        plt.close(fig)

        print(f"  [Готово] Анимация сохранена: {save_path}")
        return save_path

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
        print(f"  [Сохранение] {save_path}...")
        anim.save(save_path, writer='pillow', fps=20, dpi=100)
        plt.close(fig)

        print(f"  [Готово] Анимация сохранена: {save_path}")
        return save_path

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
            save_path = os.path.join(self.output_dir, f"cashflow_waterfall_{scenario_name}.gif")

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
        print(f"  [Сохранение] {save_path}...")
        anim.save(save_path, writer='pillow', fps=5, dpi=100)
        plt.close(fig)

        print(f"  [Готово] Анимация сохранена: {save_path}")
        return save_path


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

    # 1. Сравнение ROI
    animator.animate_roi_comparison(roi_data, years=10)

    # 2. Период окупаемости
    animator.animate_payback_period(roi_data)

    # 3. Водопадные диаграммы для каждого сценария (только для значимых)
    for level_value, roi_info in roi_data.items():
        scenario_name = roi_info['scenario_name']
        if 'базовая' not in scenario_name.lower():  # Пропускаем базовый сценарий
            animator.animate_cashflow_waterfall(roi_data, scenario_name, years=5)

    print("\n" + "="*100)
    print("ВСЕ АНИМАЦИИ УСПЕШНО СОЗДАНЫ")
    print("="*100)


if __name__ == "__main__":
    # Тестовый запуск с примерными данными
    test_roi_data = {
        '0': {
            'scenario_name': '0: Без автоматизации',
            'capex': 400_000_000,
            'annual_opex': 50_000_000,
            'net_annual_benefit': 0,
            'payback_years': float('inf'),
            'roi_5y_percent': 0,
            'annual_labor_savings': 0,
            'annual_revenue_increase': 0
        },
        '1': {
            'scenario_name': '1: Базовая автоматизация',
            'capex': 500_000_000,
            'annual_opex': 55_000_000,
            'net_annual_benefit': 25_000_000,
            'payback_years': 4.0,
            'roi_5y_percent': 25,
            'annual_labor_savings': 30_000_000,
            'annual_revenue_increase': 50_000_000
        },
        '2': {
            'scenario_name': '2: Продвинутая автоматизация',
            'capex': 700_000_000,
            'annual_opex': 65_000_000,
            'net_annual_benefit': 50_000_000,
            'payback_years': 5.5,
            'roi_5y_percent': 36,
            'annual_labor_savings': 60_000_000,
            'annual_revenue_increase': 100_000_000
        }
    }

    create_all_animations(test_roi_data)
