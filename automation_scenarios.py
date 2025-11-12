"""
Модуль для детальных сценариев автоматизации склада (Уровни 0-3).
Включает расчет стоимости оборудования, влияния на эффективность и ROI.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np


class AutomationLevel(Enum):
    """Уровни автоматизации склада."""
    LEVEL_0 = "level_0"  # Без автоматизации (только имеющееся)
    LEVEL_1 = "level_1"  # Гибридная (базовая)
    LEVEL_2 = "level_2"  # Гибридная (средняя)
    LEVEL_3 = "level_3"  # Полная автоматизация


@dataclass
class AutomationEquipment:
    """Класс для описания единицы оборудования автоматизации."""
    name: str
    category: str  # "WMS", "Conveyor", "AGV", "Robotics", "AutoStore", etc.
    quantity: int
    unit_price: float
    installation_cost_multiplier: float = 0.15  # 15% от стоимости оборудования
    annual_maintenance_rate: float = 0.12  # 12% от CAPEX в год
    labor_reduction_factor: float = 0.0  # Сокращение персонала (0-1)
    efficiency_boost: float = 0.0  # Повышение эффективности (0-1)

    def get_total_capex(self) -> float:
        """Рассчитывает общий CAPEX для оборудования."""
        equipment_cost = self.quantity * self.unit_price
        installation_cost = equipment_cost * self.installation_cost_multiplier
        return equipment_cost + installation_cost

    def get_annual_opex(self) -> float:
        """Рассчитывает годовой OPEX для оборудования."""
        return self.get_total_capex() * self.annual_maintenance_rate


class AutomationScenario:
    """Класс для описания сценария автоматизации."""

    def __init__(self, level: AutomationLevel, name: str, description: str):
        """
        Инициализация сценария автоматизации.

        Args:
            level: Уровень автоматизации
            name: Название сценария
            description: Описание сценария
        """
        self.level = level
        self.name = name
        self.description = description
        self.equipment: List[AutomationEquipment] = []
        self.total_capex = 0.0
        self.total_annual_opex = 0.0
        self.labor_reduction_factor = 0.0
        self.efficiency_multiplier = 1.0

    def add_equipment(self, equipment: AutomationEquipment):
        """Добавляет оборудование в сценарий."""
        self.equipment.append(equipment)

    def calculate_totals(self):
        """Рассчитывает итоговые показатели сценария."""
        self.total_capex = sum(eq.get_total_capex() for eq in self.equipment)
        self.total_annual_opex = sum(eq.get_annual_opex() for eq in self.equipment)

        # Средневзвешенное сокращение персонала
        if self.equipment:
            total_capex_weight = sum(eq.get_total_capex() for eq in self.equipment)
            weighted_labor_reduction = sum(
                eq.labor_reduction_factor * eq.get_total_capex()
                for eq in self.equipment
            )
            self.labor_reduction_factor = weighted_labor_reduction / total_capex_weight if total_capex_weight > 0 else 0.0

            # Средневзвешенный буст эффективности
            weighted_efficiency = sum(
                eq.efficiency_boost * eq.get_total_capex()
                for eq in self.equipment
            )
            avg_efficiency_boost = weighted_efficiency / total_capex_weight if total_capex_weight > 0 else 0.0
            self.efficiency_multiplier = 1.0 + avg_efficiency_boost

    def print_summary(self):
        """Выводит сводку по сценарию."""
        print(f"\n{'='*100}")
        print(f"[{self.level.value.upper()}] {self.name}")
        print(f"{'='*100}")
        print(f"Описание: {self.description}")
        print(f"\nОборудование:")

        for eq in self.equipment:
            print(f"  • {eq.name} ({eq.category})")
            print(f"    Количество: {eq.quantity} шт")
            print(f"    Цена за единицу: {eq.unit_price:,.0f} руб")
            print(f"    CAPEX (с установкой): {eq.get_total_capex():,.0f} руб")
            print(f"    Годовой OPEX (обслуживание): {eq.get_annual_opex():,.0f} руб")
            print(f"    Сокращение персонала: {eq.labor_reduction_factor*100:.1f}%")
            print(f"    Повышение эффективности: {eq.efficiency_boost*100:.1f}%")
            print()

        print(f"{'-'*100}")
        print(f"ИТОГО:")
        print(f"  Общий CAPEX автоматизации: {self.total_capex:,.0f} руб")
        print(f"  Общий годовой OPEX автоматизации: {self.total_annual_opex:,.0f} руб")
        print(f"  Средневзвешенное сокращение персонала: {self.labor_reduction_factor*100:.1f}%")
        print(f"  Множитель эффективности: x{self.efficiency_multiplier:.2f}")
        print(f"{'='*100}")


class AutomationScenarioBuilder:
    """Построитель сценариев автоматизации склада."""

    def __init__(self):
        """Инициализация построителя."""
        self.scenarios: Dict[AutomationLevel, AutomationScenario] = {}

    def build_level_0_scenario(self) -> AutomationScenario:
        """
        Уровень 0: Без практической автоматизации (только имеющееся оборудование).

        Оборудование:
        - Базовая WMS (система управления складом)
        - Ручные сканеры штрих-кодов
        - Ручные тележки и паллетные тележки
        """
        scenario = AutomationScenario(
            level=AutomationLevel.LEVEL_0,
            name="Без автоматизации (базовая WMS)",
            description="Минимальная автоматизация: базовая WMS, ручные сканеры, без конвейеров и роботов"
        )

        # 1. Базовая WMS (Warehouse Management System)
        scenario.add_equipment(AutomationEquipment(
            name="Базовая WMS (лицензии + внедрение)",
            category="WMS",
            quantity=1,
            unit_price=15_000_000,  # 15 млн руб за систему
            installation_cost_multiplier=0.20,  # 20% на внедрение и обучение
            annual_maintenance_rate=0.15,  # 15% на поддержку и обновления
            labor_reduction_factor=0.0,  # Не сокращает персонал
            efficiency_boost=0.05  # +5% эффективности за счет учета
        ))

        # 2. Ручные сканеры штрих-кодов и RF ID
        scenario.add_equipment(AutomationEquipment(
            name="Ручные сканеры (штрих-коды + RF ID)",
            category="Scanning",
            quantity=100,  # 100 сканеров для персонала
            unit_price=50_000,  # 50 тыс руб за сканер
            installation_cost_multiplier=0.05,
            annual_maintenance_rate=0.10,
            labor_reduction_factor=0.0,
            efficiency_boost=0.03  # +3% за счет точности
        ))

        # 3. Ручные паллетные тележки
        scenario.add_equipment(AutomationEquipment(
            name="Ручные паллетные тележки",
            category="Material Handling",
            quantity=30,
            unit_price=35_000,  # 35 тыс руб за тележку
            installation_cost_multiplier=0.0,
            annual_maintenance_rate=0.08,
            labor_reduction_factor=0.0,
            efficiency_boost=0.0
        ))

        scenario.calculate_totals()
        return scenario

    def build_level_1_scenario(self) -> AutomationScenario:
        """
        Уровень 1: Гибридная автоматизация (базовая).

        Дополнительно к уровню 0:
        - Продвинутая WMS с интеграцией
        - Конвейеры для сортировки
        - Электрические тележки
        """
        scenario = AutomationScenario(
            level=AutomationLevel.LEVEL_1,
            name="Гибридная автоматизация (базовая)",
            description="Базовая автоматизация: продвинутая WMS, конвейеры для сортировки, электротележки"
        )

        # Все оборудование из уровня 0
        level_0 = self.build_level_0_scenario()
        for eq in level_0.equipment:
            scenario.add_equipment(eq)

        # 4. Конвейеры для сортировки (в зонах приемки и отгрузки)
        scenario.add_equipment(AutomationEquipment(
            name="Конвейеры для сортировки",
            category="Conveyor",
            quantity=4,  # 2 для приемки, 2 для отгрузки
            unit_price=3_500_000,  # 3.5 млн руб за линию
            installation_cost_multiplier=0.25,
            annual_maintenance_rate=0.12,
            labor_reduction_factor=0.08,  # -8% персонала
            efficiency_boost=0.12  # +12% эффективности
        ))

        # 5. Электрические паллетные тележки (частичная замена ручных)
        scenario.add_equipment(AutomationEquipment(
            name="Электрические паллетные тележки",
            category="Material Handling",
            quantity=15,
            unit_price=250_000,  # 250 тыс руб за тележку
            installation_cost_multiplier=0.05,
            annual_maintenance_rate=0.10,
            labor_reduction_factor=0.05,  # -5% персонала
            efficiency_boost=0.08  # +8% эффективности
        ))

        # 6. Pick-to-Light система (подсветка для комплектации)
        scenario.add_equipment(AutomationEquipment(
            name="Pick-to-Light система",
            category="Picking Assist",
            quantity=50,  # 50 станций
            unit_price=150_000,  # 150 тыс руб за станцию
            installation_cost_multiplier=0.15,
            annual_maintenance_rate=0.10,
            labor_reduction_factor=0.03,
            efficiency_boost=0.10  # +10% скорости комплектации
        ))

        scenario.calculate_totals()
        return scenario

    def build_level_2_scenario(self) -> AutomationScenario:
        """
        Уровень 2: Гибридная автоматизация (средняя).

        Дополнительно к уровню 1:
        - AGV (автономные роботы)
        - Автоматические системы комплектации
        - Вертикальные лифты (VLM)
        """
        scenario = AutomationScenario(
            level=AutomationLevel.LEVEL_2,
            name="Гибридная автоматизация (средняя)",
            description="Средняя автоматизация: AGV, автоматическая комплектация, вертикальные лифты"
        )

        # Все оборудование из уровня 1
        level_1 = self.build_level_1_scenario()
        for eq in level_1.equipment:
            scenario.add_equipment(eq)

        # 7. AGV (Automated Guided Vehicles) - автономные роботы
        scenario.add_equipment(AutomationEquipment(
            name="AGV (автономные роботы)",
            category="AGV",
            quantity=10,  # 10 роботов
            unit_price=4_500_000,  # 4.5 млн руб за робота
            installation_cost_multiplier=0.20,  # Требуется настройка навигации
            annual_maintenance_rate=0.15,
            labor_reduction_factor=0.15,  # -15% персонала (замена грузчиков)
            efficiency_boost=0.18  # +18% эффективности
        ))

        # 8. Вертикальные лифты (VLM - Vertical Lift Modules)
        scenario.add_equipment(AutomationEquipment(
            name="Вертикальные лифты (VLM)",
            category="Storage & Retrieval",
            quantity=6,  # 6 лифтов
            unit_price=8_000_000,  # 8 млн руб за лифт
            installation_cost_multiplier=0.15,
            annual_maintenance_rate=0.12,
            labor_reduction_factor=0.10,  # -10% персонала
            efficiency_boost=0.15  # +15% эффективности
        ))

        # 9. Автоматическая система сортировки (расширенная)
        scenario.add_equipment(AutomationEquipment(
            name="Автоматическая система сортировки (расширенная)",
            category="Sorting",
            quantity=2,  # 2 системы
            unit_price=12_000_000,  # 12 млн руб за систему
            installation_cost_multiplier=0.25,
            annual_maintenance_rate=0.12,
            labor_reduction_factor=0.12,
            efficiency_boost=0.20  # +20% эффективности
        ))

        scenario.calculate_totals()
        return scenario

    def build_level_3_scenario(self) -> AutomationScenario:
        """
        Уровень 3: Полная автоматизация.

        Дополнительно к уровню 2:
        - AutoStore (роботизированная система хранения)
        - Роботизированная комплектация
        - Автоматические dock doors
        - Полная интеграция с ERP
        """
        scenario = AutomationScenario(
            level=AutomationLevel.LEVEL_3,
            name="Полная автоматизация",
            description="Максимальная автоматизация: AutoStore, роботизированная комплектация, полная интеграция"
        )

        # Все оборудование из уровня 2
        level_2 = self.build_level_2_scenario()
        for eq in level_2.equipment:
            scenario.add_equipment(eq)

        # 10. AutoStore (роботизированная система хранения и комплектации)
        scenario.add_equipment(AutomationEquipment(
            name="AutoStore (роботизированная система)",
            category="AutoStore",
            quantity=1,  # 1 система (включает роботов, контейнеры, грид)
            unit_price=150_000_000,  # 150 млн руб за систему
            installation_cost_multiplier=0.30,  # Требуется сложная установка
            annual_maintenance_rate=0.15,
            labor_reduction_factor=0.25,  # -25% персонала
            efficiency_boost=0.40  # +40% эффективности
        ))

        # 11. Роботизированная комплектация (роботы-манипуляторы)
        scenario.add_equipment(AutomationEquipment(
            name="Роботы-манипуляторы для комплектации",
            category="Robotics",
            quantity=8,  # 8 роботов
            unit_price=15_000_000,  # 15 млн руб за робота
            installation_cost_multiplier=0.25,
            annual_maintenance_rate=0.15,
            labor_reduction_factor=0.20,  # -20% персонала
            efficiency_boost=0.35  # +35% эффективности
        ))

        # 12. Автоматические dock doors (ворота)
        scenario.add_equipment(AutomationEquipment(
            name="Автоматические dock doors",
            category="Infrastructure",
            quantity=10,  # 10 автоматических ворот
            unit_price=800_000,  # 800 тыс руб за ворота
            installation_cost_multiplier=0.10,
            annual_maintenance_rate=0.10,
            labor_reduction_factor=0.05,
            efficiency_boost=0.08  # +8% за счет скорости обработки
        ))

        # 13. Интеграция с ERP и расширенная аналитика
        scenario.add_equipment(AutomationEquipment(
            name="ERP интеграция и AI-аналитика",
            category="Software",
            quantity=1,
            unit_price=20_000_000,  # 20 млн руб
            installation_cost_multiplier=0.30,
            annual_maintenance_rate=0.18,
            labor_reduction_factor=0.08,  # -8% (оптимизация процессов)
            efficiency_boost=0.15  # +15% за счет оптимизации
        ))

        scenario.calculate_totals()
        return scenario

    def build_all_scenarios(self) -> Dict[AutomationLevel, AutomationScenario]:
        """Создает все сценарии автоматизации."""
        self.scenarios = {
            AutomationLevel.LEVEL_0: self.build_level_0_scenario(),
            AutomationLevel.LEVEL_1: self.build_level_1_scenario(),
            AutomationLevel.LEVEL_2: self.build_level_2_scenario(),
            AutomationLevel.LEVEL_3: self.build_level_3_scenario()
        }
        return self.scenarios

    def print_all_scenarios_summary(self):
        """Выводит сводку по всем сценариям."""
        print("\n" + "="*100)
        print("СЦЕНАРИИ АВТОМАТИЗАЦИИ СКЛАДА PNK ЧАШНИКОВО BTS")
        print("="*100)

        for level, scenario in self.scenarios.items():
            scenario.print_summary()

    def compare_scenarios(self) -> Dict[str, Any]:
        """
        Сравнивает все сценарии автоматизации.

        Returns:
            Словарь с данными для сравнения
        """
        comparison = {
            "levels": [],
            "capex": [],
            "annual_opex": [],
            "labor_reduction": [],
            "efficiency_multiplier": [],
            "names": []
        }

        for level, scenario in sorted(self.scenarios.items(), key=lambda x: x[0].value):
            comparison["levels"].append(level.value)
            comparison["capex"].append(scenario.total_capex)
            comparison["annual_opex"].append(scenario.total_annual_opex)
            comparison["labor_reduction"].append(scenario.labor_reduction_factor * 100)
            comparison["efficiency_multiplier"].append(scenario.efficiency_multiplier)
            comparison["names"].append(scenario.name)

        return comparison

    def visualize_comparison(self, save_path: Optional[str] = None, show: bool = True):
        """
        Визуализирует сравнение сценариев.

        Args:
            save_path: Путь для сохранения изображения
            show: Показать ли изображение
        """
        comparison = self.compare_scenarios()

        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        fig.suptitle('Сравнение сценариев автоматизации склада', fontsize=18, weight='bold')

        # График 1: CAPEX
        ax1 = axes[0, 0]
        colors = ['#90EE90', '#FFD700', '#FFA500', '#FF6347']
        bars1 = ax1.bar(comparison["names"], np.array(comparison["capex"]) / 1_000_000, color=colors)
        ax1.set_ylabel('CAPEX (млн руб)', fontsize=12)
        ax1.set_title('Инвестиционные затраты (CAPEX)', fontsize=14, weight='bold')
        ax1.tick_params(axis='x', rotation=15)
        ax1.grid(axis='y', alpha=0.3)

        # Добавляем значения на столбцы
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=10, weight='bold')

        # График 2: Годовой OPEX
        ax2 = axes[0, 1]
        bars2 = ax2.bar(comparison["names"], np.array(comparison["annual_opex"]) / 1_000_000, color=colors)
        ax2.set_ylabel('Годовой OPEX (млн руб)', fontsize=12)
        ax2.set_title('Эксплуатационные расходы (годовой OPEX)', fontsize=14, weight='bold')
        ax2.tick_params(axis='x', rotation=15)
        ax2.grid(axis='y', alpha=0.3)

        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=10, weight='bold')

        # График 3: Сокращение персонала
        ax3 = axes[1, 0]
        bars3 = ax3.bar(comparison["names"], comparison["labor_reduction"], color=colors)
        ax3.set_ylabel('Сокращение персонала (%)', fontsize=12)
        ax3.set_title('Потенциальное сокращение персонала', fontsize=14, weight='bold')
        ax3.tick_params(axis='x', rotation=15)
        ax3.grid(axis='y', alpha=0.3)

        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=10, weight='bold')

        # График 4: Множитель эффективности
        ax4 = axes[1, 1]
        bars4 = ax4.bar(comparison["names"], comparison["efficiency_multiplier"], color=colors)
        ax4.set_ylabel('Множитель эффективности', fontsize=12)
        ax4.set_title('Повышение эффективности операций', fontsize=14, weight='bold')
        ax4.tick_params(axis='x', rotation=15)
        ax4.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Базовая эффективность')
        ax4.grid(axis='y', alpha=0.3)
        ax4.legend()

        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'x{height:.2f}', ha='center', va='bottom', fontsize=10, weight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"[Automation] Сравнительный график сохранен: {save_path}")

        if show:
            plt.show()

        return fig, axes

    def calculate_roi_analysis(self, base_staff_count: int = 100,
                               monthly_salary: float = 105_000,
                               base_throughput: int = 10_000) -> Dict[str, Any]:
        """
        Рассчитывает ROI для каждого сценария автоматизации.

        Args:
            base_staff_count: Базовое количество персонала
            monthly_salary: Средняя месячная зарплата
            base_throughput: Базовая пропускная способность (заказов/месяц)

        Returns:
            Словарь с данными ROI для каждого сценария
        """
        roi_data = {}

        for level, scenario in self.scenarios.items():
            # Расчет экономии на персонале
            reduced_staff = int(base_staff_count * scenario.labor_reduction_factor)
            annual_labor_savings = reduced_staff * monthly_salary * 12

            # Расчет увеличения throughput
            new_throughput = int(base_throughput * scenario.efficiency_multiplier)
            throughput_increase = new_throughput - base_throughput

            # Расчет дохода от увеличенного throughput (условно: 500 руб прибыли с заказа)
            profit_per_order = 500
            annual_revenue_increase = throughput_increase * 12 * profit_per_order

            # Общая годовая экономия/выгода
            total_annual_benefit = annual_labor_savings + annual_revenue_increase

            # Чистая годовая выгода (за вычетом OPEX автоматизации)
            net_annual_benefit = total_annual_benefit - scenario.total_annual_opex

            # Срок окупаемости (payback period)
            payback_years = scenario.total_capex / net_annual_benefit if net_annual_benefit > 0 else float('inf')

            # ROI за 5 лет
            total_benefit_5y = net_annual_benefit * 5
            roi_5y = ((total_benefit_5y - scenario.total_capex) / scenario.total_capex * 100) if scenario.total_capex > 0 else 0

            roi_data[level.value] = {
                "scenario_name": scenario.name,
                "capex": scenario.total_capex,
                "annual_opex": scenario.total_annual_opex,
                "reduced_staff": reduced_staff,
                "annual_labor_savings": annual_labor_savings,
                "throughput_increase": throughput_increase,
                "annual_revenue_increase": annual_revenue_increase,
                "total_annual_benefit": total_annual_benefit,
                "net_annual_benefit": net_annual_benefit,
                "payback_years": payback_years,
                "roi_5y_percent": roi_5y
            }

        return roi_data

    def print_roi_summary(self, roi_data: Dict[str, Any]):
        """Выводит сводку ROI для всех сценариев."""
        print("\n" + "="*100)
        print("ROI АНАЛИЗ СЦЕНАРИЕВ АВТОМАТИЗАЦИИ")
        print("="*100)

        for level_value, data in roi_data.items():
            print(f"\n[{level_value.upper()}] {data['scenario_name']}")
            print(f"{'-'*100}")
            print(f"  CAPEX (инвестиции):                {data['capex']:>20,.0f} руб")
            print(f"  Годовой OPEX (обслуживание):       {data['annual_opex']:>20,.0f} руб")
            print(f"\n  Сокращение персонала:              {data['reduced_staff']:>20} чел")
            print(f"  Экономия на ФОТ (годовая):         {data['annual_labor_savings']:>20,.0f} руб")
            print(f"  Увеличение throughput:             {data['throughput_increase']:>20,} заказов/мес")
            print(f"  Дополнительный доход (годовой):    {data['annual_revenue_increase']:>20,.0f} руб")
            print(f"\n  Общая годовая выгода:              {data['total_annual_benefit']:>20,.0f} руб")
            print(f"  Чистая годовая выгода (после OPEX):{data['net_annual_benefit']:>20,.0f} руб")
            print(f"\n  Срок окупаемости:                  {data['payback_years']:>20.2f} лет")
            print(f"  ROI за 5 лет:                      {data['roi_5y_percent']:>19.1f}%")

        print("\n" + "="*100)


if __name__ == "__main__":
    # Демонстрация работы модуля
    print("\n" + "="*100)
    print("ДЕМОНСТРАЦИЯ МОДУЛЯ AUTOMATION_SCENARIOS")
    print("="*100)

    # 1. Создание всех сценариев автоматизации
    builder = AutomationScenarioBuilder()
    scenarios = builder.build_all_scenarios()

    # 2. Вывод сводки по всем сценариям
    builder.print_all_scenarios_summary()

    # 3. Расчет и вывод ROI анализа
    roi_data = builder.calculate_roi_analysis(
        base_staff_count=100,
        monthly_salary=105_000,
        base_throughput=10_000
    )
    builder.print_roi_summary(roi_data)

    # 4. Визуализация сравнения сценариев
    print("\n[Визуализация] Создание сравнительных графиков...")
    builder.visualize_comparison(save_path="output/automation_comparison.png", show=False)

    print("\n" + "="*100)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*100)
