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
            total_area: Общая площадь склада (кв.м)
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
        self.climate_requirements = {}
        self.gpp_gdp_compliance = {}
        self.monitoring_systems = {}
        self.detailed_equipment = {}

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

        # ===== ШАГ 2.5: КЛИМАТИЧЕСКИЕ ТРЕБОВАНИЯ И GPP/GDP =====
        print("\n" + "+" + "-"*118 + "+")
        print("|" + " "*30 + "ШАГ 2.5: КЛИМАТИЧЕСКИЕ ТРЕБОВАНИЯ И GPP/GDP" + " "*46 + "|")
        print("+" + "-"*118 + "+")

        self._calculate_climate_requirements()
        self._calculate_gpp_gdp_compliance()
        self._calculate_monitoring_systems()
        self._calculate_detailed_equipment()

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

    def _calculate_climate_requirements(self):
        """Детальный расчет климатических требований для каждой зоны."""
        print(f"\n[Климатические требования]")

        # Зона нормального хранения
        normal_area = self.zoning_data['storage_normal'].area_sqm
        self.climate_requirements['storage_normal'] = {
            'zone_name': 'Нормальное хранение',
            'temperature_range': '15-25°C',
            'temperature_target': '20°C',
            'humidity_range': '40-60%',
            'humidity_target': '50%',
            'air_changes_per_hour': 2,
            'cooling_power_kw': (normal_area * 20) / 1000,  # 20 Вт/кв.м
            'heating_power_kw': (normal_area * 15) / 1000,  # 15 Вт/кв.м
            'ventilation_capacity_m3h': normal_area * 4 * 2,  # 4м высота * 2 обмена
            'monitoring_points': int(normal_area / 200),  # 1 точка на 200кв.м
            'area_sqm': normal_area
        }

        # Зона холодовой цепи
        cold_area = self.zoning_data['storage_cold'].area_sqm
        self.climate_requirements['storage_cold'] = {
            'zone_name': 'Холодовая цепь',
            'temperature_range': '2-8°C',
            'temperature_target': '5°C',
            'humidity_range': '45-75%',
            'humidity_target': '60%',
            'air_changes_per_hour': 6,
            'cooling_power_kw': (cold_area * 80) / 1000,  # 80 Вт/кв.м для холодильной зоны
            'heating_power_kw': 0,  # Не требуется для холодильной зоны
            'ventilation_capacity_m3h': cold_area * 4 * 6,  # 4м высота * 6 обменов
            'monitoring_points': int(cold_area / 100),  # 1 точка на 100кв.м (повышенные требования)
            'backup_cooling_kw': (cold_area * 80) / 1000,  # 100% резервирование
            'area_sqm': cold_area
        }

        # Зона приемки
        receiving_area = self.zoning_data['receiving'].area_sqm
        self.climate_requirements['receiving'] = {
            'zone_name': 'Зона приемки',
            'temperature_range': '15-25°C',
            'temperature_target': '20°C',
            'humidity_range': '40-70%',
            'humidity_target': '55%',
            'air_changes_per_hour': 4,
            'cooling_power_kw': (receiving_area * 25) / 1000,
            'heating_power_kw': (receiving_area * 20) / 1000,
            'ventilation_capacity_m3h': receiving_area * 4 * 4,
            'monitoring_points': int(max(receiving_area / 300, 2)),
            'area_sqm': receiving_area
        }

        # Зона отгрузки
        dispatch_area = self.zoning_data['dispatch'].area_sqm
        self.climate_requirements['dispatch'] = {
            'zone_name': 'Зона отгрузки',
            'temperature_range': '15-25°C',
            'temperature_target': '20°C',
            'humidity_range': '40-70%',
            'humidity_target': '55%',
            'air_changes_per_hour': 4,
            'cooling_power_kw': (dispatch_area * 25) / 1000,
            'heating_power_kw': (dispatch_area * 20) / 1000,
            'ventilation_capacity_m3h': dispatch_area * 4 * 4,
            'monitoring_points': int(max(dispatch_area / 300, 2)),
            'area_sqm': dispatch_area
        }

        # Вывод информации
        for zone_id, requirements in self.climate_requirements.items():
            print(f"\n  {requirements['zone_name']} ({requirements['area_sqm']:,.0f} кв.м):")
            print(f"    Температура: {requirements['temperature_range']} (целевая: {requirements['temperature_target']})")
            print(f"    Влажность: {requirements['humidity_range']} (целевая: {requirements['humidity_target']})")
            print(f"    Воздухообмен: {requirements['air_changes_per_hour']} раз/час")
            print(f"    Мощность охлаждения: {requirements['cooling_power_kw']:.1f} кВт")
            if requirements.get('heating_power_kw', 0) > 0:
                print(f"    Мощность обогрева: {requirements['heating_power_kw']:.1f} кВт")
            print(f"    Вентиляция: {requirements['ventilation_capacity_m3h']:,.0f} м3/час")
            print(f"    Точек мониторинга: {requirements['monitoring_points']}")
            if 'backup_cooling_kw' in requirements:
                print(f"    Резервное охлаждение: {requirements['backup_cooling_kw']:.1f} кВт")

    def _calculate_gpp_gdp_compliance(self):
        """Расчет требований GPP/GDP для каждой зоны."""
        print(f"\n[Соответствие GPP/GDP требованиям]")

        self.gpp_gdp_compliance = {
            'storage_normal': {
                'zone_name': 'Нормальное хранение',
                'gmp_classification': 'Grade D',
                'gdp_requirements': [
                    'Температурный мониторинг 24/7',
                    'Контроль влажности',
                    'Автоматическая сигнализация отклонений',
                    'Квалифицированное оборудование (IQ/OQ/PQ)',
                    'Валидация температурного картирования'
                ],
                'documentation': [
                    'Протоколы валидации',
                    'SOP по контролю климата',
                    'Журналы калибровки',
                    'Отчеты по отклонениям'
                ],
                'validation_status': 'Требуется первичная валидация',
                'revalidation_period_months': 12
            },
            'storage_cold': {
                'zone_name': 'Холодовая цепь',
                'gmp_classification': 'Grade D',
                'gdp_requirements': [
                    'Непрерывный температурный мониторинг',
                    'Контроль влажности',
                    'Аварийная сигнализация с SMS/Email',
                    'Резервирование охлаждения (N+1)',
                    'Автономное питание (ИБП + генератор)',
                    'Квалификация холодильного оборудования',
                    'Температурное картирование каждые 6 месяцев'
                ],
                'documentation': [
                    'Протоколы валидации холодильного оборудования',
                    'SOP по работе с холодовой цепью',
                    'План действий при аварии',
                    'Журналы калибровки температурных датчиков',
                    'Отчеты по отклонениям температуры'
                ],
                'validation_status': 'Требуется усиленная валидация',
                'revalidation_period_months': 6
            },
            'receiving': {
                'zone_name': 'Зона приемки',
                'gmp_classification': 'Grade D',
                'gdp_requirements': [
                    'Температурный контроль',
                    'Раздельная зона для карантина',
                    'Процедуры входного контроля',
                    'Контроль доступа'
                ],
                'documentation': [
                    'SOP по приемке товара',
                    'Журналы входного контроля',
                    'Чек-листы проверки температуры'
                ],
                'validation_status': 'Базовая валидация',
                'revalidation_period_months': 12
            },
            'dispatch': {
                'zone_name': 'Зона отгрузки',
                'gmp_classification': 'Grade D',
                'gdp_requirements': [
                    'Температурный контроль',
                    'Процедуры предотгрузочной проверки',
                    'Контроль качества упаковки',
                    'Документирование условий отгрузки'
                ],
                'documentation': [
                    'SOP по отгрузке',
                    'Журналы отгрузки',
                    'Чек-листы проверки температурного режима транспорта'
                ],
                'validation_status': 'Базовая валидация',
                'revalidation_period_months': 12
            }
        }

        # Вывод информации
        for zone_id, compliance in self.gpp_gdp_compliance.items():
            print(f"\n  {compliance['zone_name']}:")
            print(f"    GMP классификация: {compliance['gmp_classification']}")
            print(f"    GDP требования ({len(compliance['gdp_requirements'])}):")
            for req in compliance['gdp_requirements']:
                print(f"      - {req}")
            print(f"    Статус валидации: {compliance['validation_status']}")
            print(f"    Ревалидация каждые: {compliance['revalidation_period_months']} месяцев")

    def _calculate_monitoring_systems(self):
        """Расчет систем мониторинга."""
        print(f"\n[Системы мониторинга и контроля]")

        total_monitoring_points = sum(
            req['monitoring_points'] for req in self.climate_requirements.values()
        )

        self.monitoring_systems = {
            'temperature_sensors': {
                'description': 'Датчики температуры',
                'quantity': total_monitoring_points,
                'type': 'Высокоточные PT100/PT1000',
                'accuracy': '±0.1°C',
                'calibration_interval_months': 6,
                'data_logging_interval_min': 5,
                'cost_per_unit_rub': 15_000,
                'total_cost_rub': total_monitoring_points * 15_000
            },
            'humidity_sensors': {
                'description': 'Датчики влажности',
                'quantity': total_monitoring_points,
                'type': 'Емкостные датчики',
                'accuracy': '±2% RH',
                'calibration_interval_months': 12,
                'data_logging_interval_min': 5,
                'cost_per_unit_rub': 12_000,
                'total_cost_rub': total_monitoring_points * 12_000
            },
            'monitoring_software': {
                'description': 'Программное обеспечение мониторинга',
                'features': [
                    'Сбор данных в реальном времени',
                    'Автоматическая сигнализация',
                    'SMS/Email уведомления',
                    'Генерация отчетов',
                    'Интеграция с WMS',
                    '21 CFR Part 11 compliance'
                ],
                'license_type': 'Perpetual',
                'cost_rub': 5_000_000,
                'annual_maintenance_rub': 500_000
            },
            'alarm_system': {
                'description': 'Система аварийной сигнализации',
                'channels': 4,  # Каждая зона отдельно
                'notification_methods': ['SMS', 'Email', 'Звуковая', 'Световая'],
                'response_time_sec': 10,
                'cost_rub': 1_500_000
            },
            'backup_power': {
                'description': 'Резервное питание (ИБП + Генератор)',
                'ups_capacity_kva': 150,
                'ups_runtime_hours': 2,
                'generator_capacity_kw': 200,
                'cost_rub': 8_000_000
            }
        }

        # Общая стоимость систем мониторинга
        total_monitoring_cost = (
            self.monitoring_systems['temperature_sensors']['total_cost_rub'] +
            self.monitoring_systems['humidity_sensors']['total_cost_rub'] +
            self.monitoring_systems['monitoring_software']['cost_rub'] +
            self.monitoring_systems['alarm_system']['cost_rub'] +
            self.monitoring_systems['backup_power']['cost_rub']
        )

        self.monitoring_systems['total_capex_rub'] = total_monitoring_cost
        self.monitoring_systems['total_annual_opex_rub'] = (
            self.monitoring_systems['monitoring_software']['annual_maintenance_rub']
        )

        # Вывод информации
        print(f"\n  Датчики температуры: {self.monitoring_systems['temperature_sensors']['quantity']} шт")
        print(f"    Тип: {self.monitoring_systems['temperature_sensors']['type']}")
        print(f"    Точность: {self.monitoring_systems['temperature_sensors']['accuracy']}")
        print(f"    Стоимость: {self.monitoring_systems['temperature_sensors']['total_cost_rub']:,.0f} руб")

        print(f"\n  Датчики влажности: {self.monitoring_systems['humidity_sensors']['quantity']} шт")
        print(f"    Тип: {self.monitoring_systems['humidity_sensors']['type']}")
        print(f"    Точность: {self.monitoring_systems['humidity_sensors']['accuracy']}")
        print(f"    Стоимость: {self.monitoring_systems['humidity_sensors']['total_cost_rub']:,.0f} руб")

        print(f"\n  Программное обеспечение мониторинга:")
        print(f"    Функции: {len(self.monitoring_systems['monitoring_software']['features'])}")
        for feature in self.monitoring_systems['monitoring_software']['features']:
            print(f"      - {feature}")
        print(f"    Стоимость лицензии: {self.monitoring_systems['monitoring_software']['cost_rub']:,.0f} руб")
        print(f"    Годовое обслуживание: {self.monitoring_systems['monitoring_software']['annual_maintenance_rub']:,.0f} руб")

        print(f"\n  Система аварийной сигнализации:")
        print(f"    Каналов: {self.monitoring_systems['alarm_system']['channels']}")
        print(f"    Методы оповещения: {', '.join(self.monitoring_systems['alarm_system']['notification_methods'])}")
        print(f"    Стоимость: {self.monitoring_systems['alarm_system']['cost_rub']:,.0f} руб")

        print(f"\n  Резервное питание:")
        print(f"    ИБП: {self.monitoring_systems['backup_power']['ups_capacity_kva']} кВА, {self.monitoring_systems['backup_power']['ups_runtime_hours']} часа")
        print(f"    Генератор: {self.monitoring_systems['backup_power']['generator_capacity_kw']} кВт")
        print(f"    Стоимость: {self.monitoring_systems['backup_power']['cost_rub']:,.0f} руб")

        print(f"\n  ИТОГО системы мониторинга:")
        print(f"    CAPEX: {total_monitoring_cost:,.0f} руб")
        print(f"    Годовой OPEX: {self.monitoring_systems['total_annual_opex_rub']:,.0f} руб")

    def _calculate_detailed_equipment(self):
        """Детальный расчет оборудования по категориям."""
        print(f"\n[Детальное оборудование]")

        self.detailed_equipment = {
            'racking_systems': {
                'description': 'Стеллажные системы',
                'pallet_racking_positions': self.equipment_data['total_pallet_positions'],
                'racking_type': 'Паллетные стеллажи',
                'levels': 5,
                'max_load_per_position_kg': 1000,
                'aisle_width_m': 3.5,
                'cost_per_position_rub': 8_000,
                'total_cost_rub': self.equipment_data['total_pallet_positions'] * 8_000
            },
            'material_handling': {
                'description': 'Погрузочно-разгрузочная техника',
                'forklifts': {
                    'quantity': 8,
                    'type': 'Электропогрузчик 2т',
                    'cost_per_unit_rub': 2_500_000,
                    'total_cost_rub': 8 * 2_500_000
                },
                'pallet_jacks': {
                    'quantity': 12,
                    'type': 'Электротележка 2т',
                    'cost_per_unit_rub': 350_000,
                    'total_cost_rub': 12 * 350_000
                },
                'total_cost_rub': (8 * 2_500_000) + (12 * 350_000)
            },
            'climate_systems': {
                'description': 'Климатическое оборудование',
                'hvac_units': {
                    'quantity': 12,
                    'type': 'Прецизионные кондиционеры',
                    'total_cooling_kw': sum(req['cooling_power_kw'] for req in self.climate_requirements.values()),
                    'cost_per_unit_rub': 1_200_000,
                    'total_cost_rub': 12 * 1_200_000
                },
                'cold_storage_units': {
                    'quantity': 6,
                    'type': 'Холодильные установки',
                    'cooling_kw': self.climate_requirements['storage_cold']['cooling_power_kw'],
                    'cost_per_unit_rub': 3_500_000,
                    'total_cost_rub': 6 * 3_500_000
                },
                'ventilation_system': {
                    'total_capacity_m3h': sum(req['ventilation_capacity_m3h'] for req in self.climate_requirements.values()),
                    'cost_rub': 8_000_000
                },
                'total_cost_rub': (12 * 1_200_000) + (6 * 3_500_000) + 8_000_000
            },
            'loading_docks': {
                'description': 'Погрузочно-разгрузочные доки',
                'inbound_docks': self.equipment_data['inbound_docks'],
                'outbound_docks': self.equipment_data['outbound_docks'],
                'dock_levelers': self.equipment_data['inbound_docks'] + self.equipment_data['outbound_docks'],
                'dock_shelters': self.equipment_data['inbound_docks'] + self.equipment_data['outbound_docks'],
                'cost_per_dock_rub': 800_000,
                'total_cost_rub': (self.equipment_data['inbound_docks'] + self.equipment_data['outbound_docks']) * 800_000
            },
            'safety_security': {
                'description': 'Системы безопасности',
                'fire_suppression': {
                    'type': 'Спринклерная система',
                    'coverage_sqm': self.total_area,
                    'cost_rub': 5_000_000
                },
                'video_surveillance': {
                    'cameras': 40,
                    'recording_days': 90,
                    'cost_rub': 2_500_000
                },
                'access_control': {
                    'readers': 20,
                    'integration': 'WMS + Time Tracking',
                    'cost_rub': 1_500_000
                },
                'total_cost_rub': 5_000_000 + 2_500_000 + 1_500_000
            }
        }

        # Общая стоимость оборудования
        total_equipment_capex = (
            self.detailed_equipment['racking_systems']['total_cost_rub'] +
            self.detailed_equipment['material_handling']['total_cost_rub'] +
            self.detailed_equipment['climate_systems']['total_cost_rub'] +
            self.detailed_equipment['loading_docks']['total_cost_rub'] +
            self.detailed_equipment['safety_security']['total_cost_rub']
        )

        self.detailed_equipment['total_equipment_capex_rub'] = total_equipment_capex

        # Вывод информации
        print(f"\n  Стеллажные системы:")
        print(f"    Паллето-мест: {self.detailed_equipment['racking_systems']['pallet_racking_positions']:,}")
        print(f"    Тип: {self.detailed_equipment['racking_systems']['racking_type']}, {self.detailed_equipment['racking_systems']['levels']} уровней")
        print(f"    Стоимость: {self.detailed_equipment['racking_systems']['total_cost_rub']:,.0f} руб")

        print(f"\n  Погрузочно-разгрузочная техника:")
        print(f"    Погрузчики: {self.detailed_equipment['material_handling']['forklifts']['quantity']} шт")
        print(f"    Электротележки: {self.detailed_equipment['material_handling']['pallet_jacks']['quantity']} шт")
        print(f"    Стоимость: {self.detailed_equipment['material_handling']['total_cost_rub']:,.0f} руб")

        print(f"\n  Климатические системы:")
        print(f"    HVAC установок: {self.detailed_equipment['climate_systems']['hvac_units']['quantity']} шт")
        print(f"    Холодильных установок: {self.detailed_equipment['climate_systems']['cold_storage_units']['quantity']} шт")
        print(f"    Общая мощность охлаждения: {self.detailed_equipment['climate_systems']['hvac_units']['total_cooling_kw']:.1f} кВт")
        print(f"    Стоимость: {self.detailed_equipment['climate_systems']['total_cost_rub']:,.0f} руб")

        print(f"\n  Погрузочно-разгрузочные доки:")
        print(f"    Inbound: {self.detailed_equipment['loading_docks']['inbound_docks']} шт")
        print(f"    Outbound: {self.detailed_equipment['loading_docks']['outbound_docks']} шт")
        print(f"    Стоимость: {self.detailed_equipment['loading_docks']['total_cost_rub']:,.0f} руб")

        print(f"\n  Системы безопасности:")
        print(f"    Пожаротушение: {self.detailed_equipment['safety_security']['fire_suppression']['type']}")
        print(f"    Видеонаблюдение: {self.detailed_equipment['safety_security']['video_surveillance']['cameras']} камер")
        print(f"    СКУД: {self.detailed_equipment['safety_security']['access_control']['readers']} считывателей")
        print(f"    Стоимость: {self.detailed_equipment['safety_security']['total_cost_rub']:,.0f} руб")

        print(f"\n  ИТОГО оборудование: {total_equipment_capex:,.0f} руб")

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
            "Сводка": self._prepare_summary_dataframe(),
            "Зонирование": self._prepare_zoning_dataframe(),
            "Климатические требования": self._prepare_climate_dataframe(),
            "GPP GDP Compliance": self._prepare_gpp_gdp_dataframe(),
            "Системы мониторинга": self._prepare_monitoring_dataframe(),
            "Детальное оборудование": self._prepare_detailed_equipment_dataframe(),
            "Автоматизация": self._prepare_automation_dataframe(),
            "ROI анализ": self._prepare_roi_dataframe(),
            "Распределение SKU": self._prepare_sku_distribution_dataframe()
        }

        excel_path = os.path.join(config.OUTPUT_DIR, "warehouse_analysis_report.xlsx")

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for sheet_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"[Экспорт] Excel отчет сохранен: {excel_path}")
        print(f"  Количество вкладок: {len(excel_data)}")

    def _prepare_summary_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame со сводной информацией."""
        summary_data = []

        # Общая информация о складе
        summary_data.append({"Категория": "ОБЩАЯ ИНФОРМАЦИЯ", "Параметр": "", "Значение": ""})
        summary_data.append({"Категория": "Склад", "Параметр": "Название локации", "Значение": self.location_name})
        summary_data.append({"Категория": "Склад", "Параметр": "Общая площадь (кв.м)", "Значение": f"{self.total_area:,.0f}"})
        summary_data.append({"Категория": "Склад", "Параметр": "Общее количество SKU", "Значение": f"{self.total_sku:,}"})

        # Финансовая сводка
        summary_data.append({"Категория": "", "Параметр": "", "Значение": ""})
        summary_data.append({"Категория": "ФИНАНСОВАЯ СВОДКА", "Параметр": "", "Значение": ""})

        if self.monitoring_systems:
            monitoring_capex = self.monitoring_systems.get('total_capex_rub', 0)
            monitoring_opex = self.monitoring_systems.get('total_annual_opex_rub', 0)
            summary_data.append({"Категория": "Мониторинг", "Параметр": "CAPEX систем мониторинга (руб)", "Значение": f"{monitoring_capex:,.0f}"})
            summary_data.append({"Категория": "Мониторинг", "Параметр": "Годовой OPEX мониторинга (руб)", "Значение": f"{monitoring_opex:,.0f}"})

        if self.detailed_equipment:
            equipment_capex = self.detailed_equipment.get('total_equipment_capex_rub', 0)
            summary_data.append({"Категория": "Оборудование", "Параметр": "CAPEX оборудования (руб)", "Значение": f"{equipment_capex:,.0f}"})

        # Лучший вариант автоматизации
        if self.roi_data:
            best_roi_level = max(self.roi_data.items(), key=lambda x: x[1]['roi_5y_percent'])
            summary_data.append({"Категория": "", "Параметр": "", "Значение": ""})
            summary_data.append({"Категория": "РЕКОМЕНДАЦИИ", "Параметр": "", "Значение": ""})
            summary_data.append({"Категория": "Автоматизация", "Параметр": "Рекомендуемый сценарий", "Значение": best_roi_level[1]['scenario_name']})
            summary_data.append({"Категория": "Автоматизация", "Параметр": "ROI за 5 лет (%)", "Значение": f"{best_roi_level[1]['roi_5y_percent']:.1f}"})
            summary_data.append({"Категория": "Автоматизация", "Параметр": "Срок окупаемости (лет)", "Значение": f"{best_roi_level[1]['payback_years']:.2f}" if best_roi_level[1]['payback_years'] != float('inf') else "Не окупается"})

        return pd.DataFrame(summary_data)

    def _prepare_zoning_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с данными зонирования."""
        data = []
        for zone_id, zone in self.zoning_data.items():
            data.append({
                "ID зоны": zone_id,
                "Название": zone.name,
                "Площадь (кв.м)": zone.area_sqm,
                "Доля (%)": (zone.area_sqm / self.total_area) * 100
            })
        return pd.DataFrame(data)

    def _prepare_climate_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с климатическими требованиями."""
        data = []
        for zone_id, requirements in self.climate_requirements.items():
            data.append({
                "ID зоны": zone_id,
                "Название зоны": requirements['zone_name'],
                "Площадь (кв.м)": f"{requirements['area_sqm']:,.0f}",
                "Диапазон температур": requirements['temperature_range'],
                "Целевая температура": requirements['temperature_target'],
                "Диапазон влажности": requirements['humidity_range'],
                "Целевая влажность": requirements['humidity_target'],
                "Воздухообмен (раз/час)": requirements['air_changes_per_hour'],
                "Мощность охлаждения (кВт)": f"{requirements['cooling_power_kw']:.1f}",
                "Мощность обогрева (кВт)": f"{requirements.get('heating_power_kw', 0):.1f}",
                "Вентиляция (м3/час)": f"{requirements['ventilation_capacity_m3h']:,.0f}",
                "Точек мониторинга": requirements['monitoring_points'],
                "Резервное охлаждение (кВт)": f"{requirements.get('backup_cooling_kw', 0):.1f}"
            })
        return pd.DataFrame(data)

    def _prepare_gpp_gdp_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с требованиями GPP/GDP."""
        data = []
        for zone_id, compliance in self.gpp_gdp_compliance.items():
            # Основная информация
            base_info = {
                "ID зоны": zone_id,
                "Название зоны": compliance['zone_name'],
                "GMP классификация": compliance['gmp_classification'],
                "Статус валидации": compliance['validation_status'],
                "Период ревалидации (месяцев)": compliance['revalidation_period_months'],
                "Количество GDP требований": len(compliance['gdp_requirements']),
                "Количество документов": len(compliance['documentation'])
            }

            # Добавляем GDP требования как отдельные строки
            for idx, req in enumerate(compliance['gdp_requirements'], 1):
                req_info = base_info.copy()
                req_info[f"GDP требование {idx}"] = req
                data.append(req_info)

            # Если нет требований, добавляем хотя бы основную строку
            if not compliance['gdp_requirements']:
                data.append(base_info)

        return pd.DataFrame(data)

    def _prepare_monitoring_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с системами мониторинга."""
        data = []

        # Датчики температуры
        if 'temperature_sensors' in self.monitoring_systems:
            ts = self.monitoring_systems['temperature_sensors']
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Количество",
                "Значение": ts['quantity'],
                "Единица": "шт"
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Тип",
                "Значение": ts['type'],
                "Единица": ""
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Точность",
                "Значение": ts['accuracy'],
                "Единица": ""
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Интервал калибровки",
                "Значение": ts['calibration_interval_months'],
                "Единица": "месяцев"
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Стоимость за единицу",
                "Значение": f"{ts['cost_per_unit_rub']:,.0f}",
                "Единица": "руб"
            })
            data.append({
                "Категория": "Датчики температуры",
                "Параметр": "Общая стоимость",
                "Значение": f"{ts['total_cost_rub']:,.0f}",
                "Единица": "руб"
            })

        # Датчики влажности
        if 'humidity_sensors' in self.monitoring_systems:
            hs = self.monitoring_systems['humidity_sensors']
            data.append({
                "Категория": "Датчики влажности",
                "Параметр": "Количество",
                "Значение": hs['quantity'],
                "Единица": "шт"
            })
            data.append({
                "Категория": "Датчики влажности",
                "Параметр": "Тип",
                "Значение": hs['type'],
                "Единица": ""
            })
            data.append({
                "Категория": "Датчики влажности",
                "Параметр": "Точность",
                "Значение": hs['accuracy'],
                "Единица": ""
            })
            data.append({
                "Категория": "Датчики влажности",
                "Параметр": "Общая стоимость",
                "Значение": f"{hs['total_cost_rub']:,.0f}",
                "Единица": "руб"
            })

        # ПО мониторинга
        if 'monitoring_software' in self.monitoring_systems:
            ms = self.monitoring_systems['monitoring_software']
            data.append({
                "Категория": "ПО мониторинга",
                "Параметр": "Описание",
                "Значение": ms['description'],
                "Единица": ""
            })
            data.append({
                "Категория": "ПО мониторинга",
                "Параметр": "Стоимость лицензии",
                "Значение": f"{ms['cost_rub']:,.0f}",
                "Единица": "руб"
            })
            data.append({
                "Категория": "ПО мониторинга",
                "Параметр": "Годовое обслуживание",
                "Значение": f"{ms['annual_maintenance_rub']:,.0f}",
                "Единица": "руб/год"
            })

        # Система сигнализации
        if 'alarm_system' in self.monitoring_systems:
            als = self.monitoring_systems['alarm_system']
            data.append({
                "Категория": "Аварийная сигнализация",
                "Параметр": "Каналов",
                "Значение": als['channels'],
                "Единица": "шт"
            })
            data.append({
                "Категория": "Аварийная сигнализация",
                "Параметр": "Стоимость",
                "Значение": f"{als['cost_rub']:,.0f}",
                "Единица": "руб"
            })

        # Резервное питание
        if 'backup_power' in self.monitoring_systems:
            bp = self.monitoring_systems['backup_power']
            data.append({
                "Категория": "Резервное питание",
                "Параметр": "ИБП мощность",
                "Значение": bp['ups_capacity_kva'],
                "Единица": "кВА"
            })
            data.append({
                "Категория": "Резервное питание",
                "Параметр": "ИБП автономность",
                "Значение": bp['ups_runtime_hours'],
                "Единица": "часов"
            })
            data.append({
                "Категория": "Резервное питание",
                "Параметр": "Генератор мощность",
                "Значение": bp['generator_capacity_kw'],
                "Единица": "кВт"
            })
            data.append({
                "Категория": "Резервное питание",
                "Параметр": "Стоимость",
                "Значение": f"{bp['cost_rub']:,.0f}",
                "Единица": "руб"
            })

        # Итого
        data.append({
            "Категория": "ИТОГО",
            "Параметр": "CAPEX систем мониторинга",
            "Значение": f"{self.monitoring_systems.get('total_capex_rub', 0):,.0f}",
            "Единица": "руб"
        })
        data.append({
            "Категория": "ИТОГО",
            "Параметр": "Годовой OPEX",
            "Значение": f"{self.monitoring_systems.get('total_annual_opex_rub', 0):,.0f}",
            "Единица": "руб/год"
        })

        return pd.DataFrame(data)

    def _prepare_detailed_equipment_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с детальным оборудованием."""
        data = []

        # Стеллажные системы
        if 'racking_systems' in self.detailed_equipment:
            rs = self.detailed_equipment['racking_systems']
            data.append({
                "Категория": "Стеллажные системы",
                "Описание": rs['description'],
                "Параметр": "Паллето-мест",
                "Значение": f"{rs['pallet_racking_positions']:,}",
                "Стоимость (руб)": f"{rs['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Стеллажные системы",
                "Описание": "Тип стеллажей",
                "Параметр": rs['racking_type'],
                "Значение": f"{rs['levels']} уровней",
                "Стоимость (руб)": ""
            })

        # Погрузочная техника
        if 'material_handling' in self.detailed_equipment:
            mh = self.detailed_equipment['material_handling']
            data.append({
                "Категория": "Погрузочная техника",
                "Описание": "Погрузчики",
                "Параметр": mh['forklifts']['type'],
                "Значение": f"{mh['forklifts']['quantity']} шт",
                "Стоимость (руб)": f"{mh['forklifts']['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Погрузочная техника",
                "Описание": "Электротележки",
                "Параметр": mh['pallet_jacks']['type'],
                "Значение": f"{mh['pallet_jacks']['quantity']} шт",
                "Стоимость (руб)": f"{mh['pallet_jacks']['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Погрузочная техника",
                "Описание": "ИТОГО",
                "Параметр": "",
                "Значение": "",
                "Стоимость (руб)": f"{mh['total_cost_rub']:,.0f}"
            })

        # Климатические системы
        if 'climate_systems' in self.detailed_equipment:
            cs = self.detailed_equipment['climate_systems']
            data.append({
                "Категория": "Климатическое оборудование",
                "Описание": "HVAC установки",
                "Параметр": cs['hvac_units']['type'],
                "Значение": f"{cs['hvac_units']['quantity']} шт, {cs['hvac_units']['total_cooling_kw']:.1f} кВт",
                "Стоимость (руб)": f"{cs['hvac_units']['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Климатическое оборудование",
                "Описание": "Холодильные установки",
                "Параметр": cs['cold_storage_units']['type'],
                "Значение": f"{cs['cold_storage_units']['quantity']} шт, {cs['cold_storage_units']['cooling_kw']:.1f} кВт",
                "Стоимость (руб)": f"{cs['cold_storage_units']['total_cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Климатическое оборудование",
                "Описание": "Система вентиляции",
                "Параметр": f"{cs['ventilation_system']['total_capacity_m3h']:,.0f} м3/час",
                "Значение": "",
                "Стоимость (руб)": f"{cs['ventilation_system']['cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Климатическое оборудование",
                "Описание": "ИТОГО",
                "Параметр": "",
                "Значение": "",
                "Стоимость (руб)": f"{cs['total_cost_rub']:,.0f}"
            })

        # Доки
        if 'loading_docks' in self.detailed_equipment:
            ld = self.detailed_equipment['loading_docks']
            data.append({
                "Категория": "Погрузочные доки",
                "Описание": "Inbound доки",
                "Параметр": f"{ld['inbound_docks']} шт",
                "Значение": "",
                "Стоимость (руб)": ""
            })
            data.append({
                "Категория": "Погрузочные доки",
                "Описание": "Outbound доки",
                "Параметр": f"{ld['outbound_docks']} шт",
                "Значение": "",
                "Стоимость (руб)": ""
            })
            data.append({
                "Категория": "Погрузочные доки",
                "Описание": "ИТОГО",
                "Параметр": f"{ld['dock_levelers']} доков",
                "Значение": "",
                "Стоимость (руб)": f"{ld['total_cost_rub']:,.0f}"
            })

        # Безопасность
        if 'safety_security' in self.detailed_equipment:
            ss = self.detailed_equipment['safety_security']
            data.append({
                "Категория": "Системы безопасности",
                "Описание": "Пожаротушение",
                "Параметр": ss['fire_suppression']['type'],
                "Значение": f"{ss['fire_suppression']['coverage_sqm']:,.0f} кв.м",
                "Стоимость (руб)": f"{ss['fire_suppression']['cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Системы безопасности",
                "Описание": "Видеонаблюдение",
                "Параметр": f"{ss['video_surveillance']['cameras']} камер",
                "Значение": f"{ss['video_surveillance']['recording_days']} дней записи",
                "Стоимость (руб)": f"{ss['video_surveillance']['cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Системы безопасности",
                "Описание": "СКУД",
                "Параметр": f"{ss['access_control']['readers']} считывателей",
                "Значение": ss['access_control']['integration'],
                "Стоимость (руб)": f"{ss['access_control']['cost_rub']:,.0f}"
            })
            data.append({
                "Категория": "Системы безопасности",
                "Описание": "ИТОГО",
                "Параметр": "",
                "Значение": "",
                "Стоимость (руб)": f"{ss['total_cost_rub']:,.0f}"
            })

        # Общий итог
        data.append({
            "Категория": "ОБЩИЙ ИТОГ",
            "Описание": "Все оборудование",
            "Параметр": "",
            "Значение": "",
            "Стоимость (руб)": f"{self.detailed_equipment.get('total_equipment_capex_rub', 0):,.0f}"
        })

        return pd.DataFrame(data)

    def _prepare_sku_distribution_dataframe(self) -> pd.DataFrame:
        """Подготавливает DataFrame с распределением SKU."""
        data = []
        for condition, info in self.sku_distribution.items():
            data.append({
                "Условие хранения": condition,
                "Количество SKU": info['sku_count'],
                "Доля (%)": info['share'] * 100
            })

        # Добавляем итоговую строку
        total_sku = sum(info['sku_count'] for info in self.sku_distribution.values())
        data.append({
            "Условие хранения": "ИТОГО",
            "Количество SKU": total_sku,
            "Доля (%)": 100.0
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
        total_area=17_500,  # кв.м
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
