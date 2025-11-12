"""
Модуль для детального зонирования фармацевтического склада PNK Чашниково BTS.
Включает расчет площадей зон, планировку и визуализацию.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from storage_conditions import TemperatureRegime, StorageConditionManager


@dataclass
class ZoneSpec:
    """Спецификация зоны склада."""
    name: str
    area_sqm: float
    temperature_regime: Optional[TemperatureRegime]
    description: str
    color: str  # Цвет для визуализации
    position: Optional[Tuple[float, float, float, float]] = None  # (x, y, width, height) для визуализации


class WarehouseZoning:
    """Класс для зонирования склада с учетом фармацевтических требований."""

    def __init__(self, total_area: float, location_name: str = "PNK Чашниково BTS"):
        """
        Инициализация зонирования склада.

        Args:
            total_area: Общая площадь склада (кв.м)
            location_name: Название локации
        """
        self.total_area = total_area
        self.location_name = location_name
        self.zones: Dict[str, ZoneSpec] = {}
        self.storage_manager = StorageConditionManager()

    def calculate_standard_zoning(self, normal_storage_ratio: float = 0.65,
                                 cold_chain_ratio: float = 0.30) -> Dict[str, ZoneSpec]:
        """
        Рассчитывает стандартное зонирование склада.

        Args:
            normal_storage_ratio: Доля площади для обычного хранения (0-1)
            cold_chain_ratio: Доля площади для холодовой цепи (0-1)

        Returns:
            Словарь зон склада
        """
        # Проверка корректности входных данных
        if normal_storage_ratio + cold_chain_ratio > 0.95:
            raise ValueError("Сумма долей хранения не должна превышать 95% (остальное - техн. зоны)")

        # === ЗОНА ПРИЕМКИ (Inbound) ===
        receiving_area = self.total_area * 0.08  # 8% от общей площади
        self.zones['receiving'] = ZoneSpec(
            name="Зона приемки (Inbound)",
            area_sqm=receiving_area,
            temperature_regime=TemperatureRegime.NORMAL,
            description="Разгрузка, первичная приемка, входной контроль",
            color="#FFE5CC",
            position=None
        )

        # === ЗОНА КАРАНТИНА ===
        quarantine_area = self.total_area * 0.05  # 5% от общей площади
        self.zones['quarantine'] = ZoneSpec(
            name="Зона карантина",
            area_sqm=quarantine_area,
            temperature_regime=TemperatureRegime.NORMAL,
            description="Временное хранение до прохождения контроля качества",
            color="#FFF4CC",
            position=None
        )

        # === ОСНОВНАЯ ЗОНА ХРАНЕНИЯ (ОБЫЧНЫЕ УСЛОВИЯ) ===
        normal_storage_area = self.total_area * normal_storage_ratio
        self.zones['storage_normal'] = ZoneSpec(
            name="Зона хранения (обычные условия +15...+25°C)",
            area_sqm=normal_storage_area,
            temperature_regime=TemperatureRegime.NORMAL,
            description="Основная зона хранения фармацевтической продукции",
            color="#CCE5FF",
            position=None
        )

        # === ЗОНА ХРАНЕНИЯ (ХОЛОДОВАЯ ЦЕПЬ) ===
        cold_chain_area = self.total_area * cold_chain_ratio
        self.zones['storage_cold'] = ZoneSpec(
            name="Зона хранения (холодовая цепь +2...+8°C)",
            area_sqm=cold_chain_area,
            temperature_regime=TemperatureRegime.COLD_CHAIN,
            description="Холодовая камера для препаратов, требующих низких температур",
            color="#CCF2FF",
            position=None
        )

        # === ЗОНА ОСОБОГО КОНТРОЛЯ (НС/ПС) ===
        controlled_area = self.total_area * 0.03  # 3% для НС/ПС
        self.zones['controlled'] = ZoneSpec(
            name="Зона особого контроля (НС/ПС)",
            area_sqm=controlled_area,
            temperature_regime=TemperatureRegime.NORMAL,
            description="Хранение наркотических и психотропных веществ (усиленная охрана)",
            color="#FFCCCC",
            position=None
        )

        # === ЗОНА КОМПЛЕКТАЦИИ (Picking) ===
        picking_area = self.total_area * 0.12  # 12% от общей площади
        self.zones['picking'] = ZoneSpec(
            name="Зона комплектации (Picking)",
            area_sqm=picking_area,
            temperature_regime=TemperatureRegime.NORMAL,
            description="Зона сборки заказов, подготовки к отгрузке",
            color="#E5CCFF",
            position=None
        )

        # === ЗОНА ЭКСПЕДИЦИИ (Staging/Dispatch) ===
        dispatch_area = self.total_area * 0.06  # 6% от общей площади
        self.zones['dispatch'] = ZoneSpec(
            name="Зона экспедиции (Dispatch)",
            area_sqm=dispatch_area,
            temperature_regime=TemperatureRegime.NORMAL,
            description="Временное хранение перед отгрузкой, консолидация заказов",
            color="#CCFFCC",
            position=None
        )

        # === ЗОНА КРОСС-ДОКИНГА ===
        crossdock_area = self.total_area * 0.04  # 4% от общей площади
        self.zones['crossdock'] = ZoneSpec(
            name="Зона кросс-докинга",
            area_sqm=crossdock_area,
            temperature_regime=TemperatureRegime.NORMAL,
            description="Прямая перегрузка без размещения на хранение",
            color="#FFFFCC",
            position=None
        )

        # === ЗОНА БРАКА И ВОЗВРАТОВ ===
        returns_area = self.total_area * 0.02  # 2% от общей площади
        self.zones['returns'] = ZoneSpec(
            name="Зона брака и возвратов",
            area_sqm=returns_area,
            temperature_regime=TemperatureRegime.NORMAL,
            description="Обработка бракованной продукции и возвратов",
            color="#FFD9CC",
            position=None
        )

        # === ТЕХНИЧЕСКИЕ И АДМИНИСТРАТИВНЫЕ ЗОНЫ ===
        technical_area = self.total_area * 0.03  # 3% от общей площади
        self.zones['technical'] = ZoneSpec(
            name="Технические помещения",
            area_sqm=technical_area,
            temperature_regime=None,
            description="Серверная, электрощитовая, вентиляция",
            color="#D9D9D9",
            position=None
        )

        office_area = self.total_area * 0.02  # 2% от общей площади
        self.zones['office'] = ZoneSpec(
            name="Административная зона",
            area_sqm=office_area,
            temperature_regime=None,
            description="Офисы, комната отдыха персонала",
            color="#F2F2F2",
            position=None
        )

        return self.zones

    def calculate_positions_for_visualization(self):
        """
        Рассчитывает позиции зон для 2D визуализации.
        Предполагается прямоугольная планировка склада.
        """
        # Предполагаем склад 140м x 125м (примерно 17,500 кв.м)
        warehouse_width = 140
        warehouse_height = 125

        # Определяем позиции зон (x, y, width, height)
        # Схема: Receiving (верх слева) -> Storage (центр) -> Dispatch (верх справа)
        positions = {
            'receiving': (0, 100, 35, 25),  # Верхний левый угол
            'quarantine': (35, 100, 25, 25),  # Рядом с приемкой
            'storage_normal': (0, 20, 90, 80),  # Основная зона (большая)
            'storage_cold': (90, 50, 50, 50),  # Холодовая камера (правый блок)
            'controlled': (90, 100, 25, 25),  # Особый контроль (отдельно, охрана)
            'picking': (0, 0, 90, 20),  # Зона комплектации (низ, вдоль длины)
            'dispatch': (115, 100, 25, 25),  # Экспедиция (верхний правый угол)
            'crossdock': (60, 100, 30, 25),  # Кросс-докинг (между receiving и dispatch)
            'returns': (90, 0, 25, 20),  # Зона брака (низ справа)
            'technical': (115, 0, 25, 20),  # Технические помещения (низ, правый край)
            'office': (90, 20, 50, 30)  # Офисы (справа, над технической зоной)
        }

        for zone_id, position in positions.items():
            if zone_id in self.zones:
                self.zones[zone_id].position = position

    def visualize_warehouse_layout(self, save_path: Optional[str] = None, show: bool = True):
        """
        Визуализирует планировку склада в 2D.

        Args:
            save_path: Путь для сохранения изображения
            show: Показать ли изображение
        """
        self.calculate_positions_for_visualization()

        fig, ax = plt.subplots(figsize=(16, 12))

        # Рисуем зоны
        for zone_id, zone in self.zones.items():
            if zone.position:
                x, y, width, height = zone.position
                rect = patches.Rectangle(
                    (x, y), width, height,
                    linewidth=2,
                    edgecolor='black',
                    facecolor=zone.color,
                    alpha=0.7
                )
                ax.add_patch(rect)

                # Добавляем текст с названием зоны
                text_x = x + width / 2
                text_y = y + height / 2
                fontsize = 8 if width < 30 or height < 30 else 10

                ax.text(
                    text_x, text_y,
                    f"{zone.name}\n{zone.area_sqm:.0f} кв.м",
                    ha='center', va='center',
                    fontsize=fontsize,
                    weight='bold',
                    wrap=True
                )

        # Настройка осей и заголовка
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 125)
        ax.set_aspect('equal')
        ax.set_xlabel('Ширина (м)', fontsize=12)
        ax.set_ylabel('Длина (м)', fontsize=12)
        ax.set_title(
            f'Планировка склада: {self.location_name}\nОбщая площадь: {self.total_area:,.0f} кв.м',
            fontsize=16,
            weight='bold',
            pad=20
        )
        ax.grid(True, alpha=0.3)

        # Добавляем легенду
        legend_elements = []
        for zone_id, zone in self.zones.items():
            if zone.temperature_regime:
                temp_range = self.storage_manager.conditions.get(zone_id.replace('storage_', ''))
                if temp_range:
                    temp_info = f" ({temp_range.get_temperature_range()[0]}°C...{temp_range.get_temperature_range()[1]}°C)"
                else:
                    temp_info = ""
            else:
                temp_info = ""

            legend_elements.append(
                patches.Patch(
                    facecolor=zone.color,
                    edgecolor='black',
                    label=f"{zone.name}{temp_info}"
                )
            )

        ax.legend(
            handles=legend_elements,
            loc='upper left',
            bbox_to_anchor=(1.02, 1),
            fontsize=9,
            framealpha=0.9
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"[Zoning] Планировка сохранена: {save_path}")

        if show:
            plt.show()

        return fig, ax

    def print_zoning_summary(self):
        """Выводит детальную сводку по зонированию."""
        print("\n" + "="*100)
        print(f"ЗОНИРОВАНИЕ СКЛАДА: {self.location_name}")
        print(f"Общая площадь: {self.total_area:,.0f} кв.м")
        print("="*100)

        # Группируем зоны по типу
        storage_zones = []
        operational_zones = []
        support_zones = []

        for zone_id, zone in self.zones.items():
            if 'storage' in zone_id or 'controlled' in zone_id or 'quarantine' in zone_id:
                storage_zones.append(zone)
            elif 'technical' in zone_id or 'office' in zone_id:
                support_zones.append(zone)
            else:
                operational_zones.append(zone)

        # Зоны хранения
        print("\n[ЗОНЫ ХРАНЕНИЯ]")
        storage_total = 0
        for zone in storage_zones:
            temp_info = ""
            if zone.temperature_regime:
                condition_id = 'normal' if zone.temperature_regime == TemperatureRegime.NORMAL else 'cold_chain'
                condition = self.storage_manager.get_condition(condition_id)
                if condition:
                    temp_range = condition.get_temperature_range()
                    humidity_range = condition.get_humidity_range()
                    temp_info = f" | {temp_range[0]}°C...{temp_range[1]}°C, {humidity_range[0]}-{humidity_range[1]}% RH"

            print(f"  • {zone.name}: {zone.area_sqm:,.0f} кв.м ({zone.area_sqm/self.total_area*100:.1f}%){temp_info}")
            print(f"    {zone.description}")
            storage_total += zone.area_sqm

        print(f"\n  ИТОГО зон хранения: {storage_total:,.0f} кв.м ({storage_total/self.total_area*100:.1f}%)")

        # Операционные зоны
        print("\n[ОПЕРАЦИОННЫЕ ЗОНЫ]")
        operational_total = 0
        for zone in operational_zones:
            print(f"  • {zone.name}: {zone.area_sqm:,.0f} кв.м ({zone.area_sqm/self.total_area*100:.1f}%)")
            print(f"    {zone.description}")
            operational_total += zone.area_sqm

        print(f"\n  ИТОГО операционных зон: {operational_total:,.0f} кв.м ({operational_total/self.total_area*100:.1f}%)")

        # Вспомогательные зоны
        print("\n[ВСПОМОГАТЕЛЬНЫЕ ЗОНЫ]")
        support_total = 0
        for zone in support_zones:
            print(f"  • {zone.name}: {zone.area_sqm:,.0f} кв.м ({zone.area_sqm/self.total_area*100:.1f}%)")
            print(f"    {zone.description}")
            support_total += zone.area_sqm

        print(f"\n  ИТОГО вспомогательных зон: {support_total:,.0f} кв.м ({support_total/self.total_area*100:.1f}%)")

        # Общая проверка
        total_allocated = storage_total + operational_total + support_total
        print("\n" + "-"*100)
        print(f"ИТОГО распределенной площади: {total_allocated:,.0f} кв.м ({total_allocated/self.total_area*100:.1f}%)")
        unallocated = self.total_area - total_allocated
        print(f"Нераспределенная площадь (проходы, коридоры): {unallocated:,.0f} кв.м ({unallocated/self.total_area*100:.1f}%)")
        print("="*100)

    def export_zoning_data(self) -> Dict[str, Any]:
        """
        Экспортирует данные зонирования для использования в других модулях.

        Returns:
            Словарь с данными зонирования
        """
        export_data = {
            "location_name": self.location_name,
            "total_area": self.total_area,
            "zones": {}
        }

        for zone_id, zone in self.zones.items():
            export_data["zones"][zone_id] = {
                "name": zone.name,
                "area_sqm": zone.area_sqm,
                "share": zone.area_sqm / self.total_area,
                "temperature_regime": zone.temperature_regime.value if zone.temperature_regime else None,
                "description": zone.description
            }

        return export_data

    def calculate_equipment_requirements(self) -> Dict[str, Any]:
        """
        Рассчитывает требования к складскому оборудованию для каждой зоны.

        Returns:
            Словарь с требованиями к оборудованию
        """
        # Константы для расчета оборудования
        PALLET_RACK_COST_PER_SQM = 2_500  # руб/кв.м для паллетных стеллажей
        SHELVING_COST_PER_SQM = 3_500  # руб/кв.м для полочных стеллажей
        PICKING_EQUIPMENT_COST = 1_500_000  # стоимость оборудования для picking зоны
        DOCK_DOOR_COST = 500_000  # стоимость одних ворот (dock door)

        equipment = {
            "racking_systems": {},
            "picking_equipment": {},
            "dock_doors": {},
            "total_capex": 0
        }

        # Стеллажи для зон хранения
        for zone_id in ['storage_normal', 'storage_cold', 'controlled', 'quarantine']:
            if zone_id in self.zones:
                zone = self.zones[zone_id]
                # Используем 80% площади под стеллажи (20% - проходы)
                usable_area = zone.area_sqm * 0.8

                if zone_id in ['storage_normal', 'storage_cold']:
                    # Паллетные стеллажи для основного хранения
                    racking_capex = usable_area * PALLET_RACK_COST_PER_SQM
                    rack_type = "Паллетные стеллажи"
                else:
                    # Полочные стеллажи для контролируемых зон
                    racking_capex = usable_area * SHELVING_COST_PER_SQM
                    rack_type = "Полочные стеллажи"

                equipment["racking_systems"][zone_id] = {
                    "zone_name": zone.name,
                    "type": rack_type,
                    "usable_area_sqm": usable_area,
                    "capex": racking_capex
                }
                equipment["total_capex"] += racking_capex

        # Оборудование для комплектации
        equipment["picking_equipment"] = {
            "description": "Тележки, сканеры, терминалы для picking",
            "capex": PICKING_EQUIPMENT_COST
        }
        equipment["total_capex"] += PICKING_EQUIPMENT_COST

        # Dock doors (ворота для приемки и отгрузки)
        # Расчет: 1 dock door на каждые 2,000 кв.м складской площади (минимум 4-6 для приемки, 4-6 для отгрузки)
        inbound_docks = max(4, int((self.zones.get('receiving', ZoneSpec("", 0, None, "", "")).area_sqm / 2000) * 2))
        outbound_docks = max(4, int((self.zones.get('dispatch', ZoneSpec("", 0, None, "", "")).area_sqm / 2000) * 2))

        equipment["dock_doors"] = {
            "inbound_docks": inbound_docks,
            "outbound_docks": outbound_docks,
            "capex_per_door": DOCK_DOOR_COST,
            "total_capex": (inbound_docks + outbound_docks) * DOCK_DOOR_COST
        }
        equipment["total_capex"] += equipment["dock_doors"]["total_capex"]

        return equipment

    def print_equipment_summary(self, equipment: Dict[str, Any]):
        """Выводит сводку по складскому оборудованию."""
        print("\n" + "="*100)
        print("СКЛАДСКОЕ ОБОРУДОВАНИЕ")
        print("="*100)

        print("\n[СТЕЛЛАЖНЫЕ СИСТЕМЫ]")
        for zone_id, data in equipment["racking_systems"].items():
            print(f"  • {data['zone_name']}")
            print(f"    Тип: {data['type']}")
            print(f"    Используемая площадь: {data['usable_area_sqm']:,.0f} кв.м")
            print(f"    CAPEX: {data['capex']:,.0f} руб")

        print("\n[ОБОРУДОВАНИЕ ДЛЯ КОМПЛЕКТАЦИИ]")
        print(f"  • {equipment['picking_equipment']['description']}")
        print(f"    CAPEX: {equipment['picking_equipment']['capex']:,.0f} руб")

        print("\n[DOCK DOORS (ВОРОТА)]")
        print(f"  • Inbound docks (приемка): {equipment['dock_doors']['inbound_docks']} шт")
        print(f"  • Outbound docks (отгрузка): {equipment['dock_doors']['outbound_docks']} шт")
        print(f"  • Стоимость 1 dock door: {equipment['dock_doors']['capex_per_door']:,.0f} руб")
        print(f"  • ИТОГО CAPEX: {equipment['dock_doors']['total_capex']:,.0f} руб")

        print("\n" + "-"*100)
        print(f"ИТОГО CAPEX (складское оборудование): {equipment['total_capex']:,.0f} руб")
        print("="*100)


if __name__ == "__main__":
    # Демонстрация работы модуля
    print("\n" + "="*100)
    print("ДЕМОНСТРАЦИЯ МОДУЛЯ WAREHOUSE_ZONING")
    print("="*100)

    # 1. Создание зонирования для склада PNK Чашниково BTS (17,500 кв.м)
    warehouse = WarehouseZoning(total_area=17_500, location_name="PNK Чашниково BTS")

    # 2. Расчет стандартного зонирования
    zones = warehouse.calculate_standard_zoning(normal_storage_ratio=0.65, cold_chain_ratio=0.30)

    # 3. Вывод детальной сводки
    warehouse.print_zoning_summary()

    # 4. Расчет требований к оборудованию
    equipment = warehouse.calculate_equipment_requirements()
    warehouse.print_equipment_summary(equipment)

    # 5. Визуализация планировки
    print("\n[Визуализация] Создание 2D планировки склада...")
    warehouse.visualize_warehouse_layout(save_path="output/warehouse_layout.png", show=False)

    # 6. Экспорт данных
    export_data = warehouse.export_zoning_data()
    print(f"\n[Экспорт] Данные зонирования экспортированы: {len(export_data['zones'])} зон")

    print("\n" + "="*100)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*100)
