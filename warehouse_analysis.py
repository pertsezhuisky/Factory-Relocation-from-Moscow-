"""
Главный скрипт для комплексного анализа склада PNK Чашниково BTS.
Включает зонирование, условия хранения, варианты автоматизации и ROI анализ.
"""
import os
from typing import Dict, Any
import matplotlib.pyplot as plt
import pandas as pd

# Импорт всех созданных модулей
from warehouse_zoning import WarehouseZoning
from storage_conditions import (
    StorageConditionManager,
    ClimateSystemCalculator,
    MonitoringSystemCalculator,
    TemperatureRegime
)
from automation_scenarios import (
    AutomationScenarioBuilder,
    AutomationLevel
)
import config


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

        # Инициализация модулей
        self.warehouse_zoning = WarehouseZoning(total_area, location_name)
        self.storage_manager = StorageConditionManager()
        self.climate_calculator = ClimateSystemCalculator()
        self.monitoring_calculator = MonitoringSystemCalculator()
        self.automation_builder = AutomationScenarioBuilder()

        # Результаты анализа
        self.zoning_data = None
        self.equipment_data = None
        self.sku_distribution = None
        self.climate_requirements = None
        self.monitoring_system = None
        self.automation_scenarios = None
        self.roi_data = None

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

        self.zoning_data = self.warehouse_zoning.calculate_standard_zoning(
            normal_storage_ratio=0.65,
            cold_chain_ratio=0.30
        )
        self.warehouse_zoning.print_zoning_summary()

        # Расчет складского оборудования
        self.equipment_data = self.warehouse_zoning.calculate_equipment_requirements()
        self.warehouse_zoning.print_equipment_summary(self.equipment_data)

        # ===== ШАГ 2: РАСПРЕДЕЛЕНИЕ SKU ПО УСЛОВИЯМ ХРАНЕНИЯ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*30 + "ШАГ 2: РАСПРЕДЕЛЕНИЕ SKU ПО УСЛОВИЯМ ХРАНЕНИЯ" + " "*43 + "|")
        print("+" + "-"*118 + "+")

        self.sku_distribution = self.storage_manager.calculate_sku_distribution(
            self.total_sku,
            distribution_profile="balanced"
        )
        self.storage_manager.print_distribution_summary(self.sku_distribution)

        # ===== ШАГ 3: РАСЧЕТ КЛИМАТИЧЕСКИХ СИСТЕМ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*35 + "ШАГ 3: КЛИМАТИЧЕСКИЕ СИСТЕМЫ И МОНИТОРИНГ" + " "*42 + "|")
        print("+" + "-"*118 + "+")

        # Подготовка данных о зонах для расчета климата
        zone_areas = {
            TemperatureRegime.NORMAL: self.zoning_data['storage_normal'].area_sqm,
            TemperatureRegime.COLD_CHAIN: self.zoning_data['storage_cold'].area_sqm
        }

        # Расчет климатических систем
        self.climate_requirements = self.climate_calculator.calculate_climate_requirements(zone_areas)
        redundancy_requirements = self.climate_calculator.calculate_redundancy_requirements(
            self.climate_requirements,
            redundancy_level="n+1"
        )
        self.climate_calculator.print_climate_summary(self.climate_requirements, redundancy_requirements)

        # Расчет систем мониторинга
        self.monitoring_system = self.monitoring_calculator.calculate_monitoring_system(
            self.total_area,
            zone_areas
        )
        self.monitoring_calculator.print_monitoring_summary(self.monitoring_system)

        # ===== ШАГ 4: СЦЕНАРИИ АВТОМАТИЗАЦИИ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*38 + "ШАГ 4: СЦЕНАРИИ АВТОМАТИЗАЦИИ (0-3)" + " "*45 + "|")
        print("+" + "-"*118 + "+")

        self.automation_scenarios = self.automation_builder.build_all_scenarios()
        self.automation_builder.print_all_scenarios_summary()

        # ===== ШАГ 5: ROI АНАЛИЗ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*40 + "ШАГ 5: ROI АНАЛИЗ И СРАВНЕНИЕ" + " "*49 + "|")
        print("+" + "-"*118 + "+")

        self.roi_data = self.automation_builder.calculate_roi_analysis(
            base_staff_count=config.INITIAL_STAFF_COUNT,
            monthly_salary=config.OPERATOR_SALARY_RUB_MONTH,
            base_throughput=config.TARGET_ORDERS_MONTH
        )
        self.automation_builder.print_roi_summary(self.roi_data)

        # ===== ШАГ 6: ВИЗУАЛИЗАЦИЯ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*45 + "ШАГ 6: ВИЗУАЛИЗАЦИЯ" + " "*54 + "|")
        print("+" + "-"*118 + "+")

        self._generate_visualizations()

        # ===== ШАГ 7: ИТОГОВАЯ СВОДКА =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*42 + "ШАГ 7: ИТОГОВАЯ СВОДКА" + " "*53 + "|")
        print("+" + "-"*118 + "+")

        self._print_final_summary(redundancy_requirements)

        # ===== ШАГ 8: ЭКСПОРТ ДАННЫХ =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*43 + "ШАГ 8: ЭКСПОРТ ДАННЫХ" + " "*54 + "|")
        print("+" + "-"*118 + "+")

        self._export_to_excel()

        print("\n" + "="*120)
        print("КОМПЛЕКСНЫЙ АНАЛИЗ ЗАВЕРШЕН")
        print("="*120)

    def _generate_visualizations(self):
        """Генерирует все визуализации."""
        print("\n[Визуализация] Генерация графиков и диаграмм...")

        # 1. Планировка склада
        print("  [1/2] Создание планировки склада с зонами...")
        self.warehouse_zoning.visualize_warehouse_layout(
            save_path=os.path.join(config.OUTPUT_DIR, "warehouse_layout_detailed.png"),
            show=False
        )

        # 2. Сравнение сценариев автоматизации
        print("  [2/2] Создание сравнительных графиков автоматизации...")
        self.automation_builder.visualize_comparison(
            save_path=os.path.join(config.OUTPUT_DIR, "automation_comparison_detailed.png"),
            show=False
        )

        print("[Визуализация] Все графики успешно сохранены в директорию 'output/'")

    def _print_final_summary(self, redundancy_requirements: Dict[str, Any]):
        """Выводит итоговую финансовую сводку."""
        print("\n" + "="*120)
        print("ИТОГОВАЯ ФИНАНСОВАЯ СВОДКА ПО СКЛАДУ PNK ЧАШНИКОВО BTS")
        print("="*120)

        # Базовые инвестиции (без автоматизации)
        base_capex = self.equipment_data['total_capex']  # Складское оборудование
        climate_capex = redundancy_requirements['total_capex_with_redundancy']  # Климат с резервированием
        monitoring_capex = self.monitoring_system['total_capex']  # Мониторинг

        total_base_capex = base_capex + climate_capex + monitoring_capex

        # Базовый OPEX (без автоматизации)
        climate_opex = redundancy_requirements['total_opex_with_redundancy']
        monitoring_opex = self.monitoring_system['annual_opex']

        total_base_opex = climate_opex + monitoring_opex

        print(f"\n[БАЗОВЫЕ ИНВЕСТИЦИИ (без учета автоматизации)]")
        print(f"  Складское оборудование (стеллажи, доки):     {base_capex:>25,.0f} руб")
        print(f"  Климатические системы (с резервированием):   {climate_capex:>25,.0f} руб")
        print(f"  Системы мониторинга (темп., влажность, RF):  {monitoring_capex:>25,.0f} руб")
        print(f"  {'-'*80}")
        print(f"  ИТОГО базовый CAPEX:                         {total_base_capex:>25,.0f} руб")

        print(f"\n[БАЗОВЫЙ ГОДОВОЙ OPEX (без учета автоматизации)]")
        print(f"  Обслуживание климатических систем:           {climate_opex:>25,.0f} руб/год")
        print(f"  Обслуживание систем мониторинга:             {monitoring_opex:>25,.0f} руб/год")
        print(f"  {'-'*80}")
        print(f"  ИТОГО базовый OPEX:                          {total_base_opex:>25,.0f} руб/год")

        # Сценарии автоматизации
        print(f"\n[ВАРИАНТЫ АВТОМАТИЗАЦИИ И ИТОГОВЫЕ ИНВЕСТИЦИИ]")
        print(f"\n{'Уровень':<25} {'CAPEX авт.':<20} {'OPEX авт.':<20} {'Итого CAPEX':<20} {'Итого OPEX':<20} {'ROI 5 лет':<15}")
        print(f"{'-'*120}")

        for level, scenario in self.automation_scenarios.items():
            roi_info = self.roi_data.get(level.value, {})

            total_capex_with_auto = total_base_capex + scenario.total_capex
            total_opex_with_auto = total_base_opex + scenario.total_annual_opex

            roi_5y = roi_info.get('roi_5y_percent', 0)

            print(f"{scenario.name:<25} "
                  f"{scenario.total_capex:>18,.0f} "
                  f"{scenario.total_annual_opex:>18,.0f} "
                  f"{total_capex_with_auto:>18,.0f} "
                  f"{total_opex_with_auto:>18,.0f} "
                  f"{roi_5y:>13.1f}%")

        # Рекомендация
        print(f"\n{'='*120}")
        print(f"[РЕКОМЕНДАЦИЯ]")

        # Находим оптимальный сценарий по ROI 5 лет
        best_roi_level = max(self.roi_data.items(), key=lambda x: x[1]['roi_5y_percent'])
        best_scenario_name = self.automation_scenarios[AutomationLevel(best_roi_level[0])].name
        best_roi_value = best_roi_level[1]['roi_5y_percent']
        best_payback = best_roi_level[1]['payback_years']

        print(f"  Оптимальный сценарий по ROI: {best_scenario_name}")
        print(f"  ROI за 5 лет: {best_roi_value:.1f}%")
        print(f"  Срок окупаемости: {best_payback:.2f} лет")

        # Находим сценарий с минимальным сроком окупаемости
        min_payback_level = min(
            [(k, v) for k, v in self.roi_data.items() if v['payback_years'] != float('inf')],
            key=lambda x: x[1]['payback_years']
        )
        min_payback_scenario = self.automation_scenarios[AutomationLevel(min_payback_level[0])].name
        min_payback_value = min_payback_level[1]['payback_years']

        print(f"\n  Сценарий с минимальным сроком окупаемости: {min_payback_scenario}")
        print(f"  Срок окупаемости: {min_payback_value:.2f} лет")

        print(f"{'='*120}")

    def _export_to_excel(self):
        """Экспортирует результаты анализа в Excel."""
        print("\n[Экспорт] Создание Excel отчета...")

        # Подготовка данных для экспорта
        excel_data = {
            "Зонирование": self._prepare_zoning_dataframe(),
            "Условия хранения": self._prepare_storage_conditions_dataframe(),
            "Климатические системы": self._prepare_climate_dataframe(),
            "Автоматизация": self._prepare_automation_dataframe(),
            "ROI анализ": self._prepare_roi_dataframe()
        }

        # Запись в Excel
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
                "Доля (%)": (zone.area_sqm / self.total_area) * 100,
                "Температурный режим": zone.temperature_regime.value if zone.temperature_regime else "N/A",
                "Описание": zone.description
            })
        return pd.DataFrame(data)

    def _prepare_storage_conditions_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с условиями хранения."""
        data = []
        for condition_id, condition_data in self.sku_distribution.items():
            temp_range = condition_data['temperature_range']
            humidity_range = condition_data['humidity_range']
            data.append({
                "Условие": condition_id,
                "Количество SKU": condition_data['sku_count'],
                "Доля (%)": condition_data['share'] * 100,
                "Температура (°C)": f"{temp_range[0]}...{temp_range[1]}",
                "Влажность (% RH)": f"{humidity_range[0]}-{humidity_range[1]}",
                "Валидация GPP/GDP": "Да" if condition_data['requires_validation'] else "Нет",
                "Особый контроль": "Да" if condition_data['requires_special_security'] else "Нет"
            })
        return pd.DataFrame(data)

    def _prepare_climate_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с данными климатических систем."""
        data = []
        for zone_name, zone_data in self.climate_requirements['zones'].items():
            data.append({
                "Зона": zone_name,
                "Площадь (м²)": zone_data['area_sqm'],
                "Мощность охлаждения (кВт)": zone_data['cooling_power_kw'],
                "CAPEX оборудования (руб)": zone_data['equipment_capex'],
                "Годовой OPEX обслуживания (руб)": zone_data['annual_maintenance_opex'],
                "Годовой OPEX электроэнергии (руб)": zone_data['annual_electricity_opex'],
                "Итого годовой OPEX (руб)": zone_data['total_annual_opex']
            })
        return pd.DataFrame(data)

    def _prepare_automation_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame со сценариями автоматизации."""
        data = []
        for level, scenario in self.automation_scenarios.items():
            data.append({
                "Уровень": level.value,
                "Название": scenario.name,
                "CAPEX автоматизации (руб)": scenario.total_capex,
                "Годовой OPEX автоматизации (руб)": scenario.total_annual_opex,
                "Сокращение персонала (%)": scenario.labor_reduction_factor * 100,
                "Множитель эффективности": scenario.efficiency_multiplier,
                "Описание": scenario.description
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
                "Увеличение throughput (заказов/мес)": roi_info['throughput_increase'],
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
    print("="*120)
