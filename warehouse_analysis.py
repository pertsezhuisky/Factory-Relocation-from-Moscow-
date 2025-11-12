"""
Упрощенный модуль анализа склада.
Включает зонирование, условия хранения, варианты автоматизации и ROI анализ.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any
from enum import Enum
import config
from animations import create_all_animations


class AutomationLevel(Enum):
    """Уровни автоматизации."""
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3


class ComprehensiveWarehouseAnalysis:
    """Класс для комплексного анализа склада с учетом всех факторов."""

    def __init__(self, location_name: str = "PNK Чашниково BTS",
                 total_area: float = 17_500,
                 total_sku: int = 15_000):
        """
        Инициализация комплексного анализа.

        Args:
            location_name: Название локации склада
            total_area: Общая площадь склада (м²)
            total_sku: Общее количество SKU
        """
        self.location_name = location_name
        self.total_area = total_area
        self.total_sku = total_sku

        # Результаты анализа
        self.zoning_data = {}
        self.equipment_data = {}
        self.sku_distribution = {}
        self.automation_scenarios = {}
        self.roi_data = {}

        # Создаем директорию для output если её нет
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    def run_full_analysis(self):
        """Запускает полный комплексный анализ склада."""
        print("\n" + "="*120)
        print(f"КОМПЛЕКСНЫЙ АНАЛИЗ СКЛАДА: {self.location_name}")
        print(f"Площадь: {self.total_area:,.0f} кв.м | SKU: {self.total_sku:,}")
        print("="*120)

        # ===== ШАГ 1: ЗОНИРОВАНИЕ СКЛАДА =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*40 + "ШАГ 1: ЗОНИРОВАНИЕ СКЛАДА" + " "*53 + "|")
        print("+" + "-"*118 + "+")

        self._calculate_zoning()
        self._calculate_equipment()

        # ===== ШАГ 2: РАСПРЕДЕЛЕНИЕ SKU ПО УСЛОВИЯМ ХРАНЕНИЯ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*30 + "ШАГ 2: РАСПРЕДЕЛЕНИЕ SKU ПО УСЛОВИЯМ ХРАНЕНИЯ" + " "*43 + "|")
        print("+" + "-"*118 + "+")

        self._calculate_sku_distribution()

        # ===== ШАГ 3: СЦЕНАРИИ АВТОМАТИЗАЦИИ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*38 + "ШАГ 3: СЦЕНАРИИ АВТОМАТИЗАЦИИ (0-3)" + " "*45 + "|")
        print("+" + "-"*118 + "+")

        self._build_automation_scenarios()

        # ===== ШАГ 4: ROI АНАЛИЗ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*40 + "ШАГ 4: ROI АНАЛИЗ И СРАВНЕНИЕ" + " "*49 + "|")
        print("+" + "-"*118 + "+")

        self._calculate_roi()

        # ===== ШАГ 5: ВИЗУАЛИЗАЦИЯ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*45 + "ШАГ 5: ВИЗУАЛИЗАЦИЯ" + " "*54 + "|")
        print("+" + "-"*118 + "+")

        self._generate_visualizations()

        # ===== ШАГ 6: АНИМАЦИИ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*45 + "ШАГ 6: СОЗДАНИЕ АНИМАЦИЙ" + " "*50 + "|")
        print("+" + "-"*118 + "+")

        self._create_animations()

        # ===== ШАГ 7: ЭКСПОРТ ДАННЫХ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*43 + "ШАГ 7: ЭКСПОРТ ДАННЫХ" + " "*54 + "|")
        print("+" + "-"*118 + "+")

        self._export_to_excel()

        print("\n" + "="*120)
        print("КОМПЛЕКСНЫЙ АНАЛИЗ ЗАВЕРШЕН")
        print("="*120)

    def _calculate_zoning(self):
        """Упрощенный расчет зонирования."""
        # Простое зонирование по процентам
        storage_normal_area = self.total_area * 0.65  # 65% - нормальное хранение
        storage_cold_area = self.total_area * 0.30     # 30% - холодовая цепь
        receiving_area = self.total_area * 0.03        # 3% - приемка
        dispatch_area = self.total_area * 0.02         # 2% - отгрузка

        self.zoning_data = {
            'storage_normal': type('obj', (object,), {'area_sqm': storage_normal_area, 'name': 'Нормальное хранение'}),
            'storage_cold': type('obj', (object,), {'area_sqm': storage_cold_area, 'name': 'Холодовая цепь'}),
            'receiving': type('obj', (object,), {'area_sqm': receiving_area, 'name': 'Приемка'}),
            'dispatch': type('obj', (object,), {'area_sqm': dispatch_area, 'name': 'Отгрузка'})
        }

        print(f"\n[Зонирование склада]")
        for zone_id, zone in self.zoning_data.items():
            print(f"  {zone.name}: {zone.area_sqm:,.0f} кв.м ({zone.area_sqm/self.total_area*100:.1f}%)")

    def _calculate_equipment(self):
        """Упрощенный расчет оборудования."""
        # Стеллажи (предполагаем 2 паллето-места на кв.м для стеллажной зоны)
        storage_area = self.zoning_data['storage_normal'].area_sqm + self.zoning_data['storage_cold'].area_sqm
        total_pallet_positions = int(storage_area * 2)

        # Доки (6 inbound + 6 outbound)
        inbound_docks = 6
        outbound_docks = 6

        # CAPEX оборудования (упрощенный расчет)
        equipment_capex = 50_000_000  # 50 млн руб

        self.equipment_data = {
            'total_pallet_positions': total_pallet_positions,
            'inbound_docks': inbound_docks,
            'outbound_docks': outbound_docks,
            'total_capex': equipment_capex
        }

        print(f"\n[Складское оборудование]")
        print(f"  Паллето-мест: {total_pallet_positions:,}")
        print(f"  Inbound доков: {inbound_docks}")
        print(f"  Outbound доков: {outbound_docks}")
        print(f"  CAPEX оборудования: {equipment_capex:,.0f} руб")

    def _calculate_sku_distribution(self):
        """Упрощенное распределение SKU."""
        self.sku_distribution = {
            'normal': {'sku_count': int(self.total_sku * 0.60), 'share': 0.60},
            'cold_chain': {'sku_count': int(self.total_sku * 0.30), 'share': 0.30},
            'special': {'sku_count': int(self.total_sku * 0.10), 'share': 0.10}
        }

        print(f"\n[Распределение SKU]")
        for condition, data in self.sku_distribution.items():
            print(f"  {condition}: {data['sku_count']:,} SKU ({data['share']*100:.0f}%)")

    def _build_automation_scenarios(self):
        """Построение сценариев автоматизации."""
        # Сценарий 0: Без автоматизации
        self.automation_scenarios[AutomationLevel.LEVEL_0] = {
            'name': '0: Без автоматизации (Базовый)',
            'capex': 0,
            'annual_opex': 0,
            'labor_reduction_factor': 0,
            'efficiency_multiplier': 1.0,
            'description': 'Ручная работа без автоматизации'
        }

        # Сценарий 1: Базовая автоматизация
        self.automation_scenarios[AutomationLevel.LEVEL_1] = {
            'name': '1: Базовая автоматизация (WMS + Сканеры)',
            'capex': 50_000_000,
            'annual_opex': 10_000_000,
            'labor_reduction_factor': 0.20,  # 20% сокращение
            'efficiency_multiplier': 1.3,     # +30% производительность
            'description': 'WMS, сканеры штрих-кодов, базовое ПО'
        }

        # Сценарий 2: Продвинутая автоматизация
        self.automation_scenarios[AutomationLevel.LEVEL_2] = {
            'name': '2: Продвинутая автоматизация (+ Конвейеры + Сортировка)',
            'capex': 200_000_000,
            'annual_opex': 35_000_000,
            'labor_reduction_factor': 0.50,  # 50% сокращение
            'efficiency_multiplier': 2.0,     # 2x производительность
            'description': 'WMS, конвейеры, автоматическая сортировка'
        }

        # Сценарий 3: Полная автоматизация
        self.automation_scenarios[AutomationLevel.LEVEL_3] = {
            'name': '3: Полная автоматизация (AS/RS + Роботы)',
            'capex': 600_000_000,
            'annual_opex': 100_000_000,
            'labor_reduction_factor': 0.80,  # 80% сокращение
            'efficiency_multiplier': 3.5,     # 3.5x производительность
            'description': 'AS/RS, AGV, роботы, полная автоматизация'
        }

        print(f"\n[Сценарии автоматизации]")
        for level, scenario in self.automation_scenarios.items():
            print(f"\n  {scenario['name']}")
            print(f"    CAPEX: {scenario['capex']:,.0f} руб")
            print(f"    Годовой OPEX: {scenario['annual_opex']:,.0f} руб/год")
            print(f"    Сокращение персонала: {scenario['labor_reduction_factor']*100:.0f}%")
            print(f"    Рост производительности: {(scenario['efficiency_multiplier']-1)*100:.0f}%")

    def _calculate_roi(self):
        """Расчет ROI для каждого сценария."""
        base_staff_count = config.INITIAL_STAFF_COUNT
        monthly_salary = config.OPERATOR_SALARY_RUB_MONTH
        base_throughput = config.TARGET_ORDERS_MONTH
        revenue_per_order = 500  # Примерный доход с заказа (руб)

        print(f"\n[Расчет ROI]")
        for level, scenario in self.automation_scenarios.items():
            # Экономия на ФОТ
            reduced_staff = int(base_staff_count * scenario['labor_reduction_factor'])
            annual_labor_savings = reduced_staff * monthly_salary * 12

            # Рост производительности
            throughput_increase = int(base_throughput * (scenario['efficiency_multiplier'] - 1))
            annual_revenue_increase = throughput_increase * 12 * revenue_per_order

            # Чистая годовая выгода
            net_annual_benefit = annual_labor_savings + annual_revenue_increase - scenario['annual_opex']

            # Срок окупаемости
            if net_annual_benefit > 0:
                payback_years = scenario['capex'] / net_annual_benefit
            else:
                payback_years = float('inf')

            # ROI за 5 лет
            if scenario['capex'] > 0:
                roi_5y_percent = ((net_annual_benefit * 5 - scenario['capex']) / scenario['capex']) * 100
            else:
                roi_5y_percent = 0

            self.roi_data[level.value] = {
                'scenario_name': scenario['name'],
                'capex': scenario['capex'],
                'annual_opex': scenario['annual_opex'],
                'reduced_staff': reduced_staff,
                'annual_labor_savings': annual_labor_savings,
                'annual_revenue_increase': annual_revenue_increase,
                'net_annual_benefit': net_annual_benefit,
                'payback_years': payback_years,
                'roi_5y_percent': roi_5y_percent
            }

            print(f"\n  {scenario['name']}")
            print(f"    Экономия на ФОТ: {annual_labor_savings:,.0f} руб/год")
            print(f"    Рост дохода: {annual_revenue_increase:,.0f} руб/год")
            print(f"    Чистая выгода: {net_annual_benefit:,.0f} руб/год")
            print(f"    Срок окупаемости: {payback_years:.2f} лет" if payback_years != float('inf') else "    Срок окупаемости: Не окупается")
            print(f"    ROI за 5 лет: {roi_5y_percent:.1f}%")

    def _generate_visualizations(self):
        """Генерирует статические визуализации."""
        print("\n[Визуализация] Создание графиков...")

        # 1. Сравнение сценариев автоматизации
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Анализ сценариев автоматизации: {self.location_name}',
                    fontsize=16, fontweight='bold')

        scenarios_names = [s['name'].split(':')[0] for s in self.automation_scenarios.values()]

        # График 1: CAPEX
        capex_values = [s['capex']/1_000_000 for s in self.automation_scenarios.values()]
        ax1.bar(scenarios_names, capex_values, color='steelblue', alpha=0.7)
        ax1.set_ylabel('CAPEX (млн руб)', fontsize=11)
        ax1.set_title('Начальные инвестиции', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # График 2: Годовой OPEX
        opex_values = [s['annual_opex']/1_000_000 for s in self.automation_scenarios.values()]
        ax2.bar(scenarios_names, opex_values, color='coral', alpha=0.7)
        ax2.set_ylabel('Годовой OPEX (млн руб)', fontsize=11)
        ax2.set_title('Операционные расходы', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        # График 3: ROI за 5 лет
        roi_values = [self.roi_data[i]['roi_5y_percent'] for i in range(len(self.automation_scenarios))]
        colors = ['red' if r < 0 else 'green' for r in roi_values]
        ax3.bar(scenarios_names, roi_values, color=colors, alpha=0.7)
        ax3.set_ylabel('ROI за 5 лет (%)', fontsize=11)
        ax3.set_title('Возврат инвестиций', fontsize=12, fontweight='bold')
        ax3.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax3.grid(True, alpha=0.3, axis='y')

        # График 4: Срок окупаемости
        payback_values = [self.roi_data[i]['payback_years'] for i in range(len(self.automation_scenarios))]
        payback_values = [min(p, 15) for p in payback_values]  # Ограничиваем 15 годами
        ax4.bar(scenarios_names, payback_values, color='purple', alpha=0.7)
        ax4.set_ylabel('Срок окупаемости (лет)', fontsize=11)
        ax4.set_title('Период окупаемости', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        save_path = os.path.join(config.OUTPUT_DIR, "automation_comparison_detailed.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  [Сохранено] {save_path}")

        # 2. Зонирование склада (простая визуализация)
        fig, ax = plt.subplots(figsize=(12, 8))
        zones = list(self.zoning_data.values())
        zone_names = [z.name for z in zones]
        zone_areas = [z.area_sqm for z in zones]
        colors_zones = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']

        ax.pie(zone_areas, labels=zone_names, colors=colors_zones, autopct='%1.1f%%',
              startangle=90, textprops={'fontsize': 11})
        ax.set_title(f'Зонирование склада: {self.location_name}\nОбщая площадь: {self.total_area:,.0f} кв.м',
                    fontsize=14, fontweight='bold', pad=20)

        save_path = os.path.join(config.OUTPUT_DIR, "warehouse_layout_detailed.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  [Сохранено] {save_path}")
        print("[Визуализация] Все графики успешно созданы")

    def _create_animations(self):
        """Создает анимированные визуализации."""
        print("\n[Анимации] Создание анимированных графиков...")

        try:
            create_all_animations(self.roi_data, config.OUTPUT_DIR)
            print("[Анимации] Все анимации успешно созданы")
        except Exception as e:
            print(f"[Предупреждение] Не удалось создать анимации: {e}")
            print("  (Это не критично для основного анализа)")

    def _export_to_excel(self):
        """Экспортирует результаты анализа в Excel."""
        print("\n[Экспорт] Создание Excel отчета...")

        excel_data = {
            "Зонирование": self._prepare_zoning_dataframe(),
            "Автоматизация": self._prepare_automation_dataframe(),
            "ROI анализ": self._prepare_roi_dataframe()
        }

        excel_path = os.path.join(config.OUTPUT_DIR, "warehouse_analysis_report.xlsx")

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for sheet_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"[Экспорт] Excel отчет сохранен: {excel_path}")

    def _prepare_zoning_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с данными зонирования."""
        data = []
        for zone_id, zone in self.zoning_data.items():
            data.append({
                "ID зоны": zone_id,
                "Название": zone.name,
                "Площадь (м²)": zone.area_sqm,
                "Доля (%)": (zone.area_sqm / self.total_area) * 100
            })
        return pd.DataFrame(data)

    def _prepare_automation_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame со сценариями автоматизации."""
        data = []
        for level, scenario in self.automation_scenarios.items():
            data.append({
                "Уровень": level.value,
                "Название": scenario['name'],
                "CAPEX автоматизации (руб)": scenario['capex'],
                "Годовой OPEX автоматизации (руб)": scenario['annual_opex'],
                "Сокращение персонала (%)": scenario['labor_reduction_factor'] * 100,
                "Множитель эффективности": scenario['efficiency_multiplier'],
                "Описание": scenario['description']
            })
        return pd.DataFrame(data)

    def _prepare_roi_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с ROI анализом."""
        data = []
        for level_value, roi_info in self.roi_data.items():
            data.append({
                "Сценарий": roi_info['scenario_name'],
                "CAPEX (руб)": roi_info['capex'],
                "Годовой OPEX (руб)": roi_info['annual_opex'],
                "Сокращение персонала (чел)": roi_info['reduced_staff'],
                "Экономия на ФОТ (руб/год)": roi_info['annual_labor_savings'],
                "Увеличение throughput (заказов/мес)": roi_info['annual_revenue_increase'] / (500 * 12),
                "Дополнительный доход (руб/год)": roi_info['annual_revenue_increase'],
                "Чистая годовая выгода (руб)": roi_info['net_annual_benefit'],
                "Срок окупаемости (лет)": roi_info['payback_years'] if roi_info['payback_years'] != float('inf') else "N/A",
                "ROI за 5 лет (%)": roi_info['roi_5y_percent']
            })
        return pd.DataFrame(data)


if __name__ == "__main__":
    # Запуск комплексного анализа
    analysis = ComprehensiveWarehouseAnalysis(
        location_name="PNK Чашниково BTS",
        total_area=17_500,  # м²
        total_sku=15_000  # количество SKU
    )

    analysis.run_full_analysis()

    print("\n" + "="*120)
    print("Все файлы сохранены в директории 'output/':")
    print("  * warehouse_layout_detailed.png - Планировка склада с зонами")
    print("  * automation_comparison_detailed.png - Сравнение сценариев автоматизации")
    print("  * warehouse_analysis_report.xlsx - Полный Excel отчет")
    print("  * roi_comparison_animated.gif - Анимация сравнения ROI")
    print("  * payback_period_animated.gif - Анимация срока окупаемости")
    print("="*120)
