"""
Модуль для управления условиями хранения фармацевтической продукции.
Поддерживает различные температурные режимы, контроль влажности и особый контроль.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TemperatureRegime(Enum):
    """Температурные режимы хранения фармацевтической продукции."""
    NORMAL = "normal"  # +15...+25°C
    COLD_CHAIN = "cold_chain"  # +2...+8°C
    FROZEN = "frozen"  # -18...-25°C (на будущее, если потребуется)
    ROOM_TEMP = "room_temp"  # Без строгого контроля


class HumidityControl(Enum):
    """Уровни контроля влажности."""
    STRICT = "strict"  # 40-60% RH (строгий контроль)
    MODERATE = "moderate"  # 30-70% RH (умеренный контроль)
    NONE = "none"  # Без контроля


class SpecialControl(Enum):
    """Типы особого контроля для специальных категорий товаров."""
    NARCOTIC = "narcotic"  # Наркотические вещества
    PSYCHOTROPIC = "psychotropic"  # Психотропные вещества
    HIGH_RISK = "high_risk"  # Высокорисковые препараты
    NONE = "none"  # Без особого контроля


@dataclass
class StorageCondition:
    """Класс, описывающий условия хранения для SKU или зоны."""
    temperature_regime: TemperatureRegime
    humidity_control: HumidityControl
    special_control: SpecialControl
    rf_id_tracking: bool = True  # Все SKU имеют RF ID

    def get_temperature_range(self) -> tuple:
        """Возвращает диапазон температур для режима."""
        ranges = {
            TemperatureRegime.NORMAL: (15, 25),
            TemperatureRegime.COLD_CHAIN: (2, 8),
            TemperatureRegime.FROZEN: (-25, -18),
            TemperatureRegime.ROOM_TEMP: (10, 30)
        }
        return ranges.get(self.temperature_regime, (15, 25))

    def get_humidity_range(self) -> tuple:
        """Возвращает диапазон влажности (%)."""
        ranges = {
            HumidityControl.STRICT: (40, 60),
            HumidityControl.MODERATE: (30, 70),
            HumidityControl.NONE: (0, 100)
        }
        return ranges.get(self.humidity_control, (40, 60))

    def requires_validation(self) -> bool:
        """Проверяет, требуется ли валидация GPP/GDP для этих условий."""
        return self.temperature_regime in [TemperatureRegime.NORMAL, TemperatureRegime.COLD_CHAIN]

    def requires_special_security(self) -> bool:
        """Проверяет, требуется ли особая безопасность (для НС, ПС)."""
        return self.special_control != SpecialControl.NONE


class StorageConditionManager:
    """Менеджер условий хранения для склада."""

    def __init__(self):
        """Инициализация менеджера условий хранения."""
        self.conditions: Dict[str, StorageCondition] = {}
        self._initialize_default_conditions()

    def _initialize_default_conditions(self):
        """Создает типовые условия хранения."""
        # Обычные условия (большинство товаров)
        self.conditions['normal'] = StorageCondition(
            temperature_regime=TemperatureRegime.NORMAL,
            humidity_control=HumidityControl.STRICT,
            special_control=SpecialControl.NONE,
            rf_id_tracking=True
        )

        # Холодовая цепь
        self.conditions['cold_chain'] = StorageCondition(
            temperature_regime=TemperatureRegime.COLD_CHAIN,
            humidity_control=HumidityControl.STRICT,
            special_control=SpecialControl.NONE,
            rf_id_tracking=True
        )

        # Обычные с особым контролем (НС/ПС)
        self.conditions['normal_controlled'] = StorageCondition(
            temperature_regime=TemperatureRegime.NORMAL,
            humidity_control=HumidityControl.STRICT,
            special_control=SpecialControl.NARCOTIC,
            rf_id_tracking=True
        )

        # Холодовая цепь с особым контролем
        self.conditions['cold_controlled'] = StorageCondition(
            temperature_regime=TemperatureRegime.COLD_CHAIN,
            humidity_control=HumidityControl.STRICT,
            special_control=SpecialControl.HIGH_RISK,
            rf_id_tracking=True
        )

    def get_condition(self, condition_id: str) -> Optional[StorageCondition]:
        """Получает условия хранения по ID."""
        return self.conditions.get(condition_id)

    def add_custom_condition(self, condition_id: str, condition: StorageCondition):
        """Добавляет пользовательские условия хранения."""
        self.conditions[condition_id] = condition

    def get_all_conditions(self) -> Dict[str, StorageCondition]:
        """Возвращает все доступные условия хранения."""
        return self.conditions.copy()

    def calculate_sku_distribution(self, total_sku: int,
                                   distribution_profile: str = "balanced") -> Dict[str, Dict[str, Any]]:
        """
        Рассчитывает распределение SKU по условиям хранения.

        Args:
            total_sku: Общее количество SKU
            distribution_profile: Профиль распределения ("balanced", "cold_heavy", "normal_heavy")

        Returns:
            Словарь с распределением SKU по условиям
        """
        profiles = {
            "balanced": {
                "normal": 0.65,  # 65% обычные условия
                "cold_chain": 0.30,  # 30% холодовая цепь
                "normal_controlled": 0.03,  # 3% НС/ПС обычные
                "cold_controlled": 0.02  # 2% холодовая с особым контролем
            },
            "cold_heavy": {
                "normal": 0.50,
                "cold_chain": 0.45,
                "normal_controlled": 0.03,
                "cold_controlled": 0.02
            },
            "normal_heavy": {
                "normal": 0.75,
                "cold_chain": 0.20,
                "normal_controlled": 0.03,
                "cold_controlled": 0.02
            }
        }

        profile = profiles.get(distribution_profile, profiles["balanced"])
        distribution = {}

        for condition_id, share in profile.items():
            condition = self.conditions.get(condition_id)
            if condition:
                sku_count = int(total_sku * share)
                distribution[condition_id] = {
                    "sku_count": sku_count,
                    "share": share,
                    "condition": condition,
                    "temperature_range": condition.get_temperature_range(),
                    "humidity_range": condition.get_humidity_range(),
                    "requires_validation": condition.requires_validation(),
                    "requires_special_security": condition.requires_special_security()
                }

        return distribution

    def print_distribution_summary(self, distribution: Dict[str, Dict[str, Any]]):
        """Выводит сводку по распределению SKU."""
        print("\n" + "="*80)
        print("РАСПРЕДЕЛЕНИЕ SKU ПО УСЛОВИЯМ ХРАНЕНИЯ")
        print("="*80)

        total_sku = sum(d["sku_count"] for d in distribution.values())

        for condition_id, data in distribution.items():
            condition = data["condition"]
            temp_range = data["temperature_range"]
            humidity_range = data["humidity_range"]

            print(f"\n[{condition_id.upper()}]")
            print(f"  SKU: {data['sku_count']:,} ({data['share']*100:.1f}%)")
            print(f"  Температура: {temp_range[0]}°C...{temp_range[1]}°C")
            print(f"  Влажность: {humidity_range[0]}%...{humidity_range[1]}% RH")
            print(f"  Валидация GPP/GDP: {'Требуется' if data['requires_validation'] else 'Не требуется'}")
            print(f"  Особый контроль: {'Требуется' if data['requires_special_security'] else 'Не требуется'}")

        print(f"\nИтого SKU: {total_sku:,}")
        print("="*80)


class ClimateSystemCalculator:
    """Калькулятор для расчета требований к климатическим системам."""

    # Константы для расчета мощности климатических систем
    COOLING_POWER_PER_SQM = {
        TemperatureRegime.NORMAL: 120,  # Вт/кв.м для обычных условий
        TemperatureRegime.COLD_CHAIN: 250,  # Вт/кв.м для холодовой цепи
        TemperatureRegime.FROZEN: 400  # Вт/кв.м для заморозки (на будущее)
    }

    # Стоимость оборудования (руб/кв.м)
    EQUIPMENT_COST_PER_SQM = {
        TemperatureRegime.NORMAL: 8_000,  # руб/кв.м для обычных условий
        TemperatureRegime.COLD_CHAIN: 25_000,  # руб/кв.м для холодовой цепи
        TemperatureRegime.FROZEN: 45_000  # руб/кв.м для заморозки
    }

    # Годовые эксплуатационные расходы (% от стоимости оборудования)
    ANNUAL_MAINTENANCE_RATE = 0.12  # 12% от CAPEX в год

    # Стоимость электроэнергии (руб/кВт·ч)
    ELECTRICITY_COST_RUB_PER_KWH = 6.5

    # Часы работы в год
    OPERATING_HOURS_PER_YEAR = 8760  # 24/7/365

    def calculate_climate_requirements(self, zone_areas: Dict[TemperatureRegime, float]) -> Dict[str, Any]:
        """
        Рассчитывает требования к климатическим системам для зон склада.

        Args:
            zone_areas: Словарь {TemperatureRegime: площадь_кв.м}

        Returns:
            Словарь с требованиями и стоимостью
        """
        results = {
            "zones": {},
            "total_capex": 0,
            "total_annual_opex": 0,
            "total_cooling_power_kw": 0
        }

        for regime, area in zone_areas.items():
            # Расчет мощности охлаждения
            cooling_power_w = area * self.COOLING_POWER_PER_SQM.get(regime, 120)
            cooling_power_kw = cooling_power_w / 1000

            # CAPEX на оборудование
            equipment_capex = area * self.EQUIPMENT_COST_PER_SQM.get(regime, 8_000)

            # Годовой OPEX (обслуживание + электроэнергия)
            maintenance_opex = equipment_capex * self.ANNUAL_MAINTENANCE_RATE
            electricity_opex = cooling_power_kw * self.OPERATING_HOURS_PER_YEAR * self.ELECTRICITY_COST_RUB_PER_KWH * 0.6  # 60% load factor
            annual_opex = maintenance_opex + electricity_opex

            results["zones"][regime.value] = {
                "area_sqm": area,
                "cooling_power_kw": cooling_power_kw,
                "equipment_capex": equipment_capex,
                "annual_maintenance_opex": maintenance_opex,
                "annual_electricity_opex": electricity_opex,
                "total_annual_opex": annual_opex
            }

            results["total_capex"] += equipment_capex
            results["total_annual_opex"] += annual_opex
            results["total_cooling_power_kw"] += cooling_power_kw

        return results

    def calculate_redundancy_requirements(self, climate_requirements: Dict[str, Any],
                                         redundancy_level: str = "n+1") -> Dict[str, Any]:
        """
        Рассчитывает требования к резервированию систем.

        Args:
            climate_requirements: Результат calculate_climate_requirements
            redundancy_level: Уровень резервирования ("n+1", "2n", "n+2")

        Returns:
            Обновленные требования с учетом резервирования
        """
        redundancy_multipliers = {
            "n+1": 1.5,  # 50% дополнительной мощности
            "2n": 2.0,   # 100% резерв (полное дублирование)
            "n+2": 1.7   # 70% дополнительной мощности
        }

        multiplier = redundancy_multipliers.get(redundancy_level, 1.5)

        redundant_capex = climate_requirements["total_capex"] * (multiplier - 1.0)
        redundant_opex = climate_requirements["total_annual_opex"] * (multiplier - 1.0) * 0.3  # 30% от OPEX на резерв

        return {
            "redundancy_level": redundancy_level,
            "additional_capex": redundant_capex,
            "additional_annual_opex": redundant_opex,
            "total_capex_with_redundancy": climate_requirements["total_capex"] + redundant_capex,
            "total_opex_with_redundancy": climate_requirements["total_annual_opex"] + redundant_opex
        }

    def print_climate_summary(self, climate_requirements: Dict[str, Any],
                             redundancy_requirements: Optional[Dict[str, Any]] = None):
        """Выводит сводку по климатическим системам."""
        print("\n" + "="*80)
        print("ТРЕБОВАНИЯ К КЛИМАТИЧЕСКИМ СИСТЕМАМ")
        print("="*80)

        for zone_name, data in climate_requirements["zones"].items():
            print(f"\n[ЗОНА: {zone_name.upper()}]")
            print(f"  Площадь: {data['area_sqm']:,.0f} кв.м")
            print(f"  Мощность охлаждения: {data['cooling_power_kw']:.1f} кВт")
            print(f"  CAPEX (оборудование): {data['equipment_capex']:,.0f} руб")
            print(f"  Годовой OPEX (обслуживание): {data['annual_maintenance_opex']:,.0f} руб")
            print(f"  Годовой OPEX (электричество): {data['annual_electricity_opex']:,.0f} руб")
            print(f"  Итого годовой OPEX: {data['total_annual_opex']:,.0f} руб")

        print(f"\n{'-'*80}")
        print(f"ИТОГО (без резервирования):")
        print(f"  Общая мощность: {climate_requirements['total_cooling_power_kw']:.1f} кВт")
        print(f"  Общий CAPEX: {climate_requirements['total_capex']:,.0f} руб")
        print(f"  Общий годовой OPEX: {climate_requirements['total_annual_opex']:,.0f} руб")

        if redundancy_requirements:
            print(f"\n{'-'*80}")
            print(f"С УЧЕТОМ РЕЗЕРВИРОВАНИЯ ({redundancy_requirements['redundancy_level'].upper()}):")
            print(f"  Дополнительный CAPEX: {redundancy_requirements['additional_capex']:,.0f} руб")
            print(f"  Дополнительный годовой OPEX: {redundancy_requirements['additional_annual_opex']:,.0f} руб")
            print(f"  ИТОГО CAPEX: {redundancy_requirements['total_capex_with_redundancy']:,.0f} руб")
            print(f"  ИТОГО годовой OPEX: {redundancy_requirements['total_opex_with_redundancy']:,.0f} руб")

        print("="*80)


class MonitoringSystemCalculator:
    """Калькулятор для систем мониторинга температуры и влажности."""

    # Стоимость датчиков (руб/шт)
    SENSOR_COST_TEMP_HUMIDITY = 15_000  # Датчик температуры и влажности
    SENSOR_COST_RF_ID_READER = 50_000  # RF ID ридер

    # Стоимость центральной системы мониторинга
    CENTRAL_SYSTEM_COST = 2_500_000  # Сервер + ПО + интеграция

    # Датчики на кв.м
    SENSORS_PER_SQM = 0.02  # 1 датчик на 50 кв.м
    RF_ID_READERS_PER_SQM = 0.005  # 1 ридер на 200 кв.м

    # Годовое обслуживание (% от CAPEX)
    ANNUAL_MAINTENANCE_RATE = 0.15  # 15% от CAPEX

    def calculate_monitoring_system(self, total_area: float,
                                   zone_areas: Dict[TemperatureRegime, float]) -> Dict[str, Any]:
        """
        Рассчитывает требования к системе мониторинга.

        Args:
            total_area: Общая площадь склада
            zone_areas: Словарь {TemperatureRegime: площадь_кв.м}

        Returns:
            Словарь с требованиями к мониторингу
        """
        # Расчет количества датчиков
        temp_humidity_sensors = int(total_area * self.SENSORS_PER_SQM)
        rf_id_readers = int(total_area * self.RF_ID_READERS_PER_SQM)

        # CAPEX
        sensors_capex = temp_humidity_sensors * self.SENSOR_COST_TEMP_HUMIDITY
        readers_capex = rf_id_readers * self.SENSOR_COST_RF_ID_READER
        total_capex = sensors_capex + readers_capex + self.CENTRAL_SYSTEM_COST

        # Годовой OPEX (обслуживание + калибровка)
        annual_opex = total_capex * self.ANNUAL_MAINTENANCE_RATE

        return {
            "temp_humidity_sensors": temp_humidity_sensors,
            "rf_id_readers": rf_id_readers,
            "sensors_capex": sensors_capex,
            "readers_capex": readers_capex,
            "central_system_capex": self.CENTRAL_SYSTEM_COST,
            "total_capex": total_capex,
            "annual_opex": annual_opex
        }

    def print_monitoring_summary(self, monitoring_system: Dict[str, Any]):
        """Выводит сводку по системе мониторинга."""
        print("\n" + "="*80)
        print("СИСТЕМА МОНИТОРИНГА ТЕМПЕРАТУРЫ И ВЛАЖНОСТИ")
        print("="*80)

        print(f"\nОборудование:")
        print(f"  Датчики температуры/влажности: {monitoring_system['temp_humidity_sensors']} шт")
        print(f"  RF ID ридеры: {monitoring_system['rf_id_readers']} шт")
        print(f"  Центральная система мониторинга: 1 комплект")

        print(f"\nСтоимость:")
        print(f"  CAPEX (датчики): {monitoring_system['sensors_capex']:,.0f} руб")
        print(f"  CAPEX (ридеры): {monitoring_system['readers_capex']:,.0f} руб")
        print(f"  CAPEX (центральная система): {monitoring_system['central_system_capex']:,.0f} руб")
        print(f"  ИТОГО CAPEX: {monitoring_system['total_capex']:,.0f} руб")
        print(f"  Годовой OPEX (обслуживание + калибровка): {monitoring_system['annual_opex']:,.0f} руб")

        print("="*80)


if __name__ == "__main__":
    # Демонстрация работы модуля
    print("\n" + "="*100)
    print("ДЕМОНСТРАЦИЯ МОДУЛЯ STORAGE_CONDITIONS")
    print("="*100)

    # 1. Создание менеджера условий хранения
    manager = StorageConditionManager()

    # 2. Распределение SKU (пример с 15,000 SKU)
    total_sku = 15_000
    distribution = manager.calculate_sku_distribution(total_sku, "balanced")
    manager.print_distribution_summary(distribution)

    # 3. Расчет климатических систем для склада 17,500 кв.м
    # Предполагаемое распределение площадей по зонам
    zone_areas = {
        TemperatureRegime.NORMAL: 11_500,  # 65% площади
        TemperatureRegime.COLD_CHAIN: 5_250,  # 30% площади
    }

    climate_calc = ClimateSystemCalculator()
    climate_req = climate_calc.calculate_climate_requirements(zone_areas)
    redundancy_req = climate_calc.calculate_redundancy_requirements(climate_req, "n+1")
    climate_calc.print_climate_summary(climate_req, redundancy_req)

    # 4. Расчет системы мониторинга
    monitoring_calc = MonitoringSystemCalculator()
    monitoring_system = monitoring_calc.calculate_monitoring_system(17_500, zone_areas)
    monitoring_calc.print_monitoring_summary(monitoring_system)

    print("\n" + "="*100)
    print("ИТОГОВАЯ СВОДКА ПО УСЛОВИЯМ ХРАНЕНИЯ")
    print("="*100)
    print(f"\nИтого CAPEX (климат + мониторинг с резервированием):")
    print(f"  {redundancy_req['total_capex_with_redundancy'] + monitoring_system['total_capex']:,.0f} руб")
    print(f"\nИтого годовой OPEX:")
    print(f"  {redundancy_req['total_opex_with_redundancy'] + monitoring_system['annual_opex']:,.0f} руб")
    print("="*100)
