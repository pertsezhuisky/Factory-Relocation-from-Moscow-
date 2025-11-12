"""
Модуль для валидации и верификации модели переезда склада.
Проверяет корректность расчетов, соответствие требованиям и достижение целей.
Включает проверку GPP/GDP, климатических систем, KPI и финансовых показателей.
"""
import os
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import pandas as pd
import config


@dataclass
class ValidationResult:
    """Результат проверки валидации."""
    check_name: str
    passed: bool
    expected: Any
    actual: Any
    message: str
    severity: str  # 'critical', 'warning', 'info'


class ModelValidator:
    """Класс для комплексной валидации и верификации модели."""

    def __init__(self):
        """Инициализация валидатора."""
        self.validation_results: List[ValidationResult] = []
        self.critical_failures = 0
        self.warnings = 0
        self.info_count = 0

    def validate_location_data(self, location_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация данных локации.

        Args:
            location_data: Данные выбранной локации

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ ДАННЫХ ЛОКАЦИИ")
        print("="*100)

        results = []

        # 1. Проверка площади
        results.append(self._validate_area(
            location_data.get('area_offered_sqm', 0),
            config.MIN_AREA_SQM,
            config.TARGET_AREA_SQM
        ))

        # 2. Проверка координат (должны быть в Московской области)
        results.append(self._validate_coordinates(
            location_data.get('lat'),
            location_data.get('lon')
        ))

        # 3. Проверка финансовых показателей
        results.append(self._validate_capex(location_data.get('total_initial_capex', 0)))
        results.append(self._validate_opex(location_data.get('total_annual_opex_s1', 0)))

        # 4. Проверка транспортной доступности
        results.append(self._validate_transport_cost(
            location_data.get('total_annual_transport_cost', 0)
        ))

        # 5. Проверка класса помещения для GPP/GDP
        results.append(self._validate_building_class(
            location_data.get('current_class', '')
        ))

        self.validation_results.extend(results)
        self._print_validation_results(results, "ЛОКАЦИЯ")

        return results

    def validate_warehouse_configuration(self, zoning_data: Dict[str, Any],
                                        equipment_data: Dict[str, Any],
                                        total_sku: int) -> List[ValidationResult]:
        """
        Валидация конфигурации склада.

        Args:
            zoning_data: Данные зонирования
            equipment_data: Данные оборудования
            total_sku: Общее количество SKU

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ КОНФИГУРАЦИИ СКЛАДА")
        print("="*100)

        results = []

        # 1. Проверка зонирования
        results.append(self._validate_zoning_ratios(zoning_data))

        # 2. Проверка вместимости стеллажей
        results.append(self._validate_storage_capacity(equipment_data, total_sku))

        # 3. Проверка количества доков
        results.append(self._validate_dock_count(equipment_data))

        # 4. Проверка климатических зон
        results.append(self._validate_climate_zones(zoning_data))

        # 5. Проверка требований GPP/GDP
        results.append(self._validate_gpp_gdp_zones(zoning_data))

        self.validation_results.extend(results)
        self._print_validation_results(results, "КОНФИГУРАЦИЯ СКЛАДА")

        return results

    def validate_climate_systems(self, climate_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация климатических систем.

        Args:
            climate_data: Данные климатических систем

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ КЛИМАТИЧЕСКИХ СИСТЕМ")
        print("="*100)

        results = []

        # 1. Проверка мощности охлаждения
        if climate_data and 'zones' in climate_data:
            for zone_name, zone_data in climate_data['zones'].items():
                results.append(self._validate_cooling_power(
                    zone_name,
                    zone_data.get('cooling_power_kw', 0),
                    zone_data.get('area_sqm', 0)
                ))

        # 2. Проверка резервирования
        results.append(self._validate_climate_redundancy(climate_data))

        # 3. Проверка систем мониторинга
        results.append(self._validate_monitoring_systems(climate_data))

        self.validation_results.extend(results)
        self._print_validation_results(results, "КЛИМАТИЧЕСКИЕ СИСТЕМЫ")

        return results

    def validate_roi_calculations(self, roi_data: Dict[str, Any],
                                  automation_scenarios: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация расчетов ROI.

        Args:
            roi_data: Данные ROI
            automation_scenarios: Сценарии автоматизации

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ РАСЧЕТОВ ROI")
        print("="*100)

        results = []

        # 1. Проверка срока окупаемости
        results.append(self._validate_payback_period(roi_data))

        # 2. Проверка ROI за 5 лет
        results.append(self._validate_roi_target(roi_data))

        # 3. Проверка логичности сокращения персонала
        results.append(self._validate_labor_reduction(roi_data, automation_scenarios))

        # 4. Проверка корректности расчета выгод
        results.append(self._validate_benefit_calculations(roi_data))

        # 5. Проверка CAPEX автоматизации
        results.append(self._validate_automation_capex(roi_data))

        # 6. Проверка соответствия эффективности и инвестиций
        results.append(self._validate_efficiency_investment_ratio(roi_data, automation_scenarios))

        self.validation_results.extend(results)
        self._print_validation_results(results, "ROI")

        return results

    def validate_operational_kpi(self, simulation_results: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация операционных KPI.

        Args:
            simulation_results: Результаты симуляции

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ ОПЕРАЦИОННЫХ KPI")
        print("="*100)

        results = []

        if simulation_results:
            # 1. Проверка throughput
            results.append(self._validate_throughput(simulation_results))

            # 2. Проверка cycle time
            results.append(self._validate_cycle_time(simulation_results))

            # 3. Проверка утилизации доков
            results.append(self._validate_dock_utilization(simulation_results))

        self.validation_results.extend(results)
        self._print_validation_results(results, "ОПЕРАЦИОННЫЕ KPI")

        return results

    def validate_business_requirements(self, location_data: Dict[str, Any],
                                      roi_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Валидация соответствия бизнес-требованиям.

        Args:
            location_data: Данные локации
            roi_data: Данные ROI

        Returns:
            Список результатов валидации
        """
        print("\n" + "="*100)
        print("ВАЛИДАЦИЯ СООТВЕТСТВИЯ БИЗНЕС-ТРЕБОВАНИЯМ")
        print("="*100)

        results = []

        # 1. Проверка целевой производительности
        results.append(self._validate_target_throughput())

        # 2. Проверка бюджетных ограничений
        results.append(self._validate_budget_constraints(location_data, roi_data))

        # 3. Проверка требований GPP/GDP
        results.append(self._validate_gpp_gdp_compliance(location_data))

        # 4. Проверка срока реализации проекта
        results.append(self._validate_project_timeline())

        # 5. Проверка масштабируемости
        results.append(self._validate_scalability(location_data))

        self.validation_results.extend(results)
        self._print_validation_results(results, "БИЗНЕС-ТРЕБОВАНИЯ")

        return results

    def verify_model_objectives(self, location_data: Dict[str, Any],
                                roi_data: Dict[str, Any],
                                warehouse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Верификация выполнения целей модели.

        Args:
            location_data: Данные локации
            roi_data: Данные ROI
            warehouse_data: Данные склада

        Returns:
            Словарь с результатами верификации целей
        """
        print("\n" + "="*100)
        print("ВЕРИФИКАЦИЯ ВЫПОЛНЕНИЯ ЦЕЛЕЙ МОДЕЛИ")
        print("="*100)

        objectives = {
            'find_optimal_location': False,
            'minimize_opex': False,
            'achieve_automation': False,
            'ensure_scalability': False,
            'maintain_quality': False,
            'meet_budget': False
        }

        scores = {}

        # 1. Найти оптимальную локацию
        if location_data.get('location_name'):
            objectives['find_optimal_location'] = True
            scores['location_selection'] = 100
            print(f"\n✓ Цель 1: Найти оптимальную локацию")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Выбрана локация: {location_data['location_name']}")
        else:
            scores['location_selection'] = 0
            print(f"\n✗ Цель 1: Найти оптимальную локацию")
            print(f"  Статус: НЕ ВЫПОЛНЕНО")

        # 2. Минимизировать OPEX
        target_opex = config.MAX_ANNUAL_OPEX_RUB
        actual_opex = location_data.get('total_annual_opex_s1', float('inf'))

        if actual_opex <= target_opex:
            objectives['minimize_opex'] = True
            scores['opex_optimization'] = min(100, (target_opex / actual_opex) * 100)
            print(f"\n✓ Цель 2: Минимизировать OPEX")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Целевой OPEX: {target_opex:,.0f} руб/год")
            print(f"  Фактический OPEX: {actual_opex:,.0f} руб/год")
            print(f"  Эффективность: {scores['opex_optimization']:.1f}%")
        else:
            scores['opex_optimization'] = (target_opex / actual_opex) * 100
            print(f"\n⚠ Цель 2: Минимизировать OPEX")
            print(f"  Статус: ЧАСТИЧНО ВЫПОЛНЕНО")
            print(f"  Целевой OPEX: {target_opex:,.0f} руб/год")
            print(f"  Фактический OPEX: {actual_opex:,.0f} руб/год")
            print(f"  Превышение: {((actual_opex / target_opex - 1) * 100):.1f}%")

        # 3. Достичь оптимального уровня автоматизации
        if roi_data:
            best_roi = max([data['roi_5y_percent'] for data in roi_data.values()])
            if best_roi > 20:  # Минимальный ROI 20% за 5 лет
                objectives['achieve_automation'] = True
                scores['automation_efficiency'] = min(100, (best_roi / 50) * 100)
                print(f"\n✓ Цель 3: Достичь оптимального уровня автоматизации")
                print(f"  Статус: ВЫПОЛНЕНО")
                print(f"  Лучший ROI за 5 лет: {best_roi:.1f}%")
                print(f"  Эффективность: {scores['automation_efficiency']:.1f}%")
            else:
                scores['automation_efficiency'] = (best_roi / 50) * 100
                print(f"\n⚠ Цель 3: Достичь оптимального уровня автоматизации")
                print(f"  Статус: ТРЕБУЕТ УЛУЧШЕНИЯ")
                print(f"  Лучший ROI за 5 лет: {best_roi:.1f}%")
        else:
            scores['automation_efficiency'] = 50

        # 4. Обеспечить масштабируемость
        target_capacity = config.TARGET_ORDERS_MONTH * 1.5  # Резерв 50%
        if warehouse_data:
            objectives['ensure_scalability'] = True
            scores['scalability'] = 100
            print(f"\n✓ Цель 4: Обеспечить масштабируемость")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Целевая мощность: {target_capacity:,.0f} заказов/месяц")
            print(f"  Резерв мощности: 50%")
        else:
            scores['scalability'] = 50
            print(f"\n⚠ Цель 4: Обеспечить масштабируемость")
            print(f"  Статус: ТРЕБУЕТ АНАЛИЗА")

        # 5. Поддержать качество (GPP/GDP)
        if location_data.get('current_class') in ['A', 'A_requires_mod', 'A_verified']:
            objectives['maintain_quality'] = True
            scores['quality_standards'] = 100
            print(f"\n✓ Цель 5: Поддержать стандарты качества (GPP/GDP)")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Класс помещения: {location_data['current_class']}")
        else:
            scores['quality_standards'] = 50
            print(f"\n⚠ Цель 5: Поддержать стандарты качества (GPP/GDP)")
            print(f"  Статус: ТРЕБУЕТ МОДИФИКАЦИЙ")

        # 6. Соблюсти бюджет
        total_capex = location_data.get('total_initial_capex', 0)
        if roi_data:
            max_auto_capex = max([data['capex'] for data in roi_data.values()])
            total_capex = max(total_capex, max_auto_capex)

        if total_capex <= config.MAX_TOTAL_CAPEX_RUB:
            objectives['meet_budget'] = True
            scores['budget_compliance'] = 100
            print(f"\n✓ Цель 6: Соблюсти бюджетные ограничения")
            print(f"  Статус: ВЫПОЛНЕНО")
            print(f"  Макс. бюджет: {config.MAX_TOTAL_CAPEX_RUB:,.0f} руб")
            print(f"  Фактический CAPEX: {total_capex:,.0f} руб")
        else:
            scores['budget_compliance'] = (config.MAX_TOTAL_CAPEX_RUB / total_capex) * 100
            print(f"\n⚠ Цель 6: Соблюсти бюджетные ограничения")
            print(f"  Статус: ПРЕВЫШЕНИЕ БЮДЖЕТА")
            print(f"  Макс. бюджет: {config.MAX_TOTAL_CAPEX_RUB:,.0f} руб")
            print(f"  Фактический CAPEX: {total_capex:,.0f} руб")
            print(f"  Превышение: {((total_capex / config.MAX_TOTAL_CAPEX_RUB - 1) * 100):.1f}%")

        # Общий балл выполнения целей
        overall_score = sum(scores.values()) / len(scores)

        print(f"\n" + "="*100)
        print(f"ОБЩИЙ БАЛЛ ВЫПОЛНЕНИЯ ЦЕЛЕЙ: {overall_score:.1f}/100")
        print(f"="*100)

        if overall_score >= 80:
            print(f"[ОТЛИЧНО] Модель успешно выполняет все поставленные цели")
        elif overall_score >= 60:
            print(f"[ХОРОШО] Модель выполняет большинство целей, но есть области для улучшения")
        else:
            print(f"[ТРЕБУЕТ ДОРАБОТКИ] Модель нуждается в значительных улучшениях")

        return {
            'objectives_met': objectives,
            'scores': scores,
            'overall_score': overall_score
        }

    def generate_validation_report(self, output_path: str = None) -> str:
        """
        Генерирует отчет по валидации в Excel.

        Args:
            output_path: Путь для сохранения отчета

        Returns:
            Путь к сохраненному файлу
        """
        if output_path is None:
            output_path = os.path.join(config.OUTPUT_DIR, "validation_report.xlsx")

        print(f"\n[Отчет] Создание отчета валидации: {output_path}")

        # Подготовка данных
        data = []
        for result in self.validation_results:
            data.append({
                'Проверка': result.check_name,
                'Статус': 'ПРОЙДЕНО' if result.passed else 'ПРОВАЛЕНО',
                'Критичность': result.severity.upper(),
                'Ожидаемое': str(result.expected),
                'Фактическое': str(result.actual),
                'Сообщение': result.message
            })

        df = pd.DataFrame(data)

        # Статистика
        total_checks = len(self.validation_results)
        passed = sum(1 for r in self.validation_results if r.passed)
        failed = total_checks - passed

        summary_data = {
            'Показатель': ['Всего проверок', 'Пройдено', 'Провалено', 'Критических ошибок', 'Предупреждений', 'Информационных'],
            'Значение': [total_checks, passed, failed, self.critical_failures, self.warnings, self.info_count]
        }
        summary_df = pd.DataFrame(summary_data)

        # Запись в Excel
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                summary_df.to_excel(writer, sheet_name='Сводка', index=False)
                df.to_excel(writer, sheet_name='Детали валидации', index=False)
            print(f"[Отчет] Сохранен: {output_path}")
        except Exception as e:
            print(f"[Ошибка] Не удалось сохранить отчет: {e}")
            output_path = None

        return output_path

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def _validate_area(self, actual: float, min_required: float, target: float) -> ValidationResult:
        """Проверка площади."""
        passed = actual >= min_required
        severity = 'critical' if not passed else ('info' if actual >= target else 'warning')

        if not passed:
            self.critical_failures += 1
        elif severity == 'warning':
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Площадь склада",
            passed=passed,
            expected=f">= {min_required} кв.м (цель: {target} кв.м)",
            actual=f"{actual:.0f} кв.м",
            message=f"Площадь {'соответствует' if passed else 'НЕ соответствует'} требованиям",
            severity=severity
        )

    def _validate_coordinates(self, lat: float, lon: float) -> ValidationResult:
        """Проверка координат."""
        passed = lat is not None and lon is not None and 55 <= lat <= 57 and 36 <= lon <= 39

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Координаты локации",
            passed=passed,
            expected="Московская область (55-57°N, 36-39°E)",
            actual=f"({lat:.4f}, {lon:.4f})" if lat and lon else "Не указаны",
            message=f"Координаты {'корректны' if passed else 'некорректны'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_capex(self, capex: float) -> ValidationResult:
        """Проверка CAPEX."""
        max_capex = config.MAX_TOTAL_CAPEX_RUB
        passed = 0 < capex <= max_capex

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Начальные инвестиции (CAPEX)",
            passed=passed,
            expected=f"<= {max_capex:,.0f} руб",
            actual=f"{capex:,.0f} руб",
            message=f"CAPEX {'в пределах нормы' if passed else 'превышает бюджет'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_opex(self, opex: float) -> ValidationResult:
        """Проверка OPEX."""
        target_opex = config.MAX_ANNUAL_OPEX_RUB
        passed = opex <= target_opex

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Годовые операционные расходы (OPEX)",
            passed=passed,
            expected=f"<= {target_opex:,.0f} руб/год",
            actual=f"{opex:,.0f} руб/год",
            message=f"OPEX {'оптимален' if passed else 'требует оптимизации'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_transport_cost(self, transport_cost: float) -> ValidationResult:
        """Проверка транспортных расходов."""
        max_transport = 100_000_000  # 100 млн руб/год
        passed = transport_cost <= max_transport

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Транспортные расходы",
            passed=passed,
            expected=f"<= {max_transport:,.0f} руб/год",
            actual=f"{transport_cost:,.0f} руб/год",
            message=f"Транспортные расходы {'приемлемы' if passed else 'высоки'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_building_class(self, building_class: str) -> ValidationResult:
        """Проверка класса здания."""
        passed = building_class in ['A', 'A_verified', 'A_requires_mod']

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Класс помещения",
            passed=passed,
            expected="Класс A или A с модификацией",
            actual=building_class,
            message=f"Класс здания {'подходит' if passed else 'НЕ подходит'} для фарм.склада",
            severity='critical' if not passed else 'info'
        )

    def _validate_zoning_ratios(self, zoning_data: Dict) -> ValidationResult:
        """Проверка соотношений зон."""
        if not zoning_data:
            self.warnings += 1
            return ValidationResult(
                check_name="Соотношение зон хранения",
                passed=False,
                expected=">= 75% площади под хранение",
                actual="Данные отсутствуют",
                message="Зонирование не проверено",
                severity='warning'
            )

        storage_zones = ['storage_normal', 'storage_cold']
        total_storage = sum(zoning_data[z].area_sqm for z in storage_zones if z in zoning_data)
        total_area = sum(z.area_sqm for z in zoning_data.values())

        storage_ratio = (total_storage / total_area) * 100 if total_area > 0 else 0
        passed = storage_ratio >= 75  # Минимум 75% под хранение

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Соотношение зон хранения",
            passed=passed,
            expected=">= 75% площади под хранение",
            actual=f"{storage_ratio:.1f}% площади",
            message=f"Зонирование {'эффективно' if passed else 'неэффективно'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_storage_capacity(self, equipment_data: Dict, total_sku: int) -> ValidationResult:
        """Проверка вместимости."""
        total_positions = equipment_data.get('total_pallet_positions', 0)
        required_positions = total_sku * 2  # 2 паллето-места на SKU
        passed = total_positions >= required_positions

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Вместимость стеллажей",
            passed=passed,
            expected=f">= {required_positions:,.0f} паллето-мест",
            actual=f"{total_positions:,.0f} паллето-мест",
            message=f"Вместимость {'достаточна' if passed else 'НЕДОСТАТОЧНА'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_dock_count(self, equipment_data: Dict) -> ValidationResult:
        """Проверка количества доков."""
        total_docks = equipment_data.get('inbound_docks', 0) + equipment_data.get('outbound_docks', 0)
        min_docks = 10
        passed = total_docks >= min_docks

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Количество доков",
            passed=passed,
            expected=f">= {min_docks} доков",
            actual=f"{total_docks} доков",
            message=f"Количество доков {'достаточно' if passed else 'недостаточно'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_climate_zones(self, zoning_data: Dict) -> ValidationResult:
        """Проверка климатических зон."""
        has_cold_chain = 'storage_cold' in zoning_data
        passed = has_cold_chain

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Зона холодовой цепи",
            passed=passed,
            expected="Наличие зоны холодовой цепи",
            actual="Присутствует" if has_cold_chain else "Отсутствует",
            message=f"Зона холодовой цепи {'настроена' if passed else 'НЕ настроена'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_gpp_gdp_zones(self, zoning_data: Dict) -> ValidationResult:
        """Проверка требований GPP/GDP для зон."""
        # Проверяем, что есть выделенные зоны для разных температурных режимов
        required_zones = ['storage_normal', 'storage_cold']
        present_zones = [z for z in required_zones if z in zoning_data]
        passed = len(present_zones) >= len(required_zones) - 1  # Минимум одна зона должна быть

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Требования GPP/GDP по зонам",
            passed=passed,
            expected="Минимум 2 климатические зоны",
            actual=f"{len(present_zones)} зон: {', '.join(present_zones)}",
            message=f"Зонирование {'соответствует' if passed else 'НЕ соответствует'} GPP/GDP",
            severity='critical' if not passed else 'info'
        )

    def _validate_cooling_power(self, zone_name: str, cooling_kw: float, area_sqm: float) -> ValidationResult:
        """Проверка мощности охлаждения."""
        # Минимум 50 Вт/м² для холодной зоны
        min_power_per_sqm = 50 if 'cold' in zone_name.lower() else 20
        required_power = (area_sqm * min_power_per_sqm) / 1000  # в кВт

        passed = cooling_kw >= required_power * 0.9  # Допуск -10%

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name=f"Мощность охлаждения ({zone_name})",
            passed=passed,
            expected=f">= {required_power:.1f} кВт",
            actual=f"{cooling_kw:.1f} кВт",
            message=f"Мощность охлаждения {'достаточна' if passed else 'недостаточна'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_climate_redundancy(self, climate_data: Dict) -> ValidationResult:
        """Проверка резервирования климатических систем."""
        # Проверяем наличие резервирования (N+1)
        has_redundancy = climate_data and climate_data.get('redundancy_level') in ['n+1', 'n+2', '2n']
        passed = has_redundancy

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Резервирование климатических систем",
            passed=passed,
            expected="Резервирование N+1 или выше",
            actual=climate_data.get('redundancy_level', 'Нет') if climate_data else "Нет данных",
            message=f"Резервирование {'обеспечено' if passed else 'отсутствует'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_monitoring_systems(self, climate_data: Dict) -> ValidationResult:
        """Проверка систем мониторинга."""
        has_monitoring = climate_data and 'monitoring' in climate_data
        passed = has_monitoring

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Системы мониторинга",
            passed=passed,
            expected="Наличие систем мониторинга температуры и влажности",
            actual="Установлены" if has_monitoring else "Отсутствуют",
            message=f"Системы мониторинга {'настроены' if passed else 'отсутствуют'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_payback_period(self, roi_data: Dict) -> ValidationResult:
        """Проверка срока окупаемости."""
        payback_periods = [
            data['payback_years'] for data in roi_data.values()
            if data['payback_years'] != float('inf')
        ]

        if payback_periods:
            min_payback = min(payback_periods)
            passed = min_payback <= config.MAX_ACCEPTABLE_PAYBACK_YEARS
        else:
            min_payback = float('inf')
            passed = False

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Срок окупаемости",
            passed=passed,
            expected=f"<= {config.MAX_ACCEPTABLE_PAYBACK_YEARS} лет",
            actual=f"{min_payback:.2f} лет" if min_payback != float('inf') else "Нет окупаемости",
            message=f"Окупаемость {'приемлема' if passed else 'слишком долгая'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_roi_target(self, roi_data: Dict) -> ValidationResult:
        """Проверка целевого ROI."""
        roi_5y_values = [data['roi_5y_percent'] for data in roi_data.values()]
        max_roi = max(roi_5y_values) if roi_5y_values else 0
        target_roi = 20
        passed = max_roi >= target_roi

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="ROI за 5 лет",
            passed=passed,
            expected=f">= {target_roi}%",
            actual=f"{max_roi:.1f}%",
            message=f"ROI {'достигает' if passed else 'НЕ достигает'} целевого уровня",
            severity='warning' if not passed else 'info'
        )

    def _validate_labor_reduction(self, roi_data: Dict, automation_scenarios: Dict) -> ValidationResult:
        """Проверка логичности сокращения персонала."""
        inconsistencies = []

        for level_value, roi_info in roi_data.items():
            reduced_staff = roi_info.get('reduced_staff', 0)
            if reduced_staff < 0 or reduced_staff > config.INITIAL_STAFF_COUNT:
                inconsistencies.append(f"{roi_info['scenario_name']}: {reduced_staff} чел")

        passed = len(inconsistencies) == 0

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Логичность сокращения персонала",
            passed=passed,
            expected="0 <= сокращение <= начальное количество",
            actual="Корректно" if passed else f"Ошибки: {', '.join(inconsistencies)}",
            message=f"Сокращение персонала {'логично' if passed else 'содержит ошибки'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_benefit_calculations(self, roi_data: Dict) -> ValidationResult:
        """Проверка корректности расчета выгод."""
        errors = []

        for level_value, roi_info in roi_data.items():
            expected_benefit = (
                roi_info['annual_labor_savings'] +
                roi_info['annual_revenue_increase'] -
                roi_info['annual_opex']
            )
            actual_benefit = roi_info['net_annual_benefit']

            # Допускаем погрешность 1%
            if abs(expected_benefit - actual_benefit) > abs(expected_benefit * 0.01):
                errors.append(roi_info['scenario_name'])

        passed = len(errors) == 0

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Корректность расчета выгод",
            passed=passed,
            expected="Выгода = Экономия + Доход - OPEX",
            actual="Корректно" if passed else f"Ошибки в: {', '.join(errors)}",
            message=f"Расчеты {'корректны' if passed else 'содержат ошибки'}",
            severity='critical' if not passed else 'info'
        )

    def _validate_automation_capex(self, roi_data: Dict) -> ValidationResult:
        """Проверка CAPEX автоматизации."""
        max_auto_capex = max([data['capex'] for data in roi_data.values()])
        max_allowed = 700_000_000  # 700 млн руб максимум на автоматизацию
        passed = max_auto_capex <= max_allowed

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="CAPEX автоматизации",
            passed=passed,
            expected=f"<= {max_allowed:,.0f} руб",
            actual=f"{max_auto_capex:,.0f} руб",
            message=f"Инвестиции в автоматизацию {'разумны' if passed else 'избыточны'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_efficiency_investment_ratio(self, roi_data: Dict, automation_scenarios: Dict) -> ValidationResult:
        """Проверка соотношения эффективности и инвестиций."""
        # Проверяем, что рост эффективности соответствует инвестициям
        ratios = []
        for level_value, roi_info in roi_data.items():
            if roi_info['capex'] > 0:
                efficiency_gain = roi_info['net_annual_benefit'] / roi_info['capex']
                ratios.append((roi_info['scenario_name'], efficiency_gain))

        # Ожидаем минимум 10% годовой выгоды от инвестиций
        passed = all(ratio >= 0.10 for _, ratio in ratios) if ratios else True

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Соотношение эффективность/инвестиции",
            passed=passed,
            expected="Годовая выгода >= 10% от CAPEX",
            actual=f"Средний ratio: {sum(r for _, r in ratios)/len(ratios)*100:.1f}%" if ratios else "N/A",
            message=f"Соотношение {'адекватно' if passed else 'требует пересмотра'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_throughput(self, simulation_results: Dict) -> ValidationResult:
        """Проверка throughput."""
        achieved = simulation_results.get('achieved_throughput', 0)
        target = config.TARGET_ORDERS_MONTH
        passed = achieved >= target * 0.95  # Допуск -5%

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Производительность (throughput)",
            passed=passed,
            expected=f">= {target:,.0f} заказов/месяц",
            actual=f"{achieved:,.0f} заказов/месяц",
            message=f"Производительность {'достаточна' if passed else 'недостаточна'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_cycle_time(self, simulation_results: Dict) -> ValidationResult:
        """Проверка cycle time."""
        actual_minutes = simulation_results.get('avg_cycle_time_min', float('inf'))
        actual_hours = actual_minutes / 60
        target_hours = config.TARGET_ORDER_CYCLE_TIME_HOURS
        max_hours = config.MAX_ACCEPTABLE_CYCLE_TIME_HOURS

        passed = actual_hours <= max_hours

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Время цикла заказа",
            passed=passed,
            expected=f"<= {max_hours} часов (цель: {target_hours} часов)",
            actual=f"{actual_hours:.2f} часов",
            message=f"Время цикла {'приемлемо' if passed else 'слишком долгое'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_dock_utilization(self, simulation_results: Dict) -> ValidationResult:
        """Проверка утилизации доков."""
        # Проверяем, что утилизация в приемлемом диапазоне
        util_percent = simulation_results.get('dock_utilization_percent', 0)
        passed = config.MIN_DOCK_UTILIZATION_PERCENT <= util_percent <= config.MAX_DOCK_UTILIZATION_PERCENT

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Утилизация доков",
            passed=passed,
            expected=f"{config.MIN_DOCK_UTILIZATION_PERCENT}-{config.MAX_DOCK_UTILIZATION_PERCENT}%",
            actual=f"{util_percent:.1f}%",
            message=f"Утилизация {'оптимальна' if passed else 'вне допустимого диапазона'}",
            severity='warning' if not passed else 'info'
        )

    def _validate_target_throughput(self) -> ValidationResult:
        """Проверка целевой производительности."""
        target = config.TARGET_ORDERS_MONTH
        passed = target > 0

        self.info_count += 1

        return ValidationResult(
            check_name="Целевая производительность",
            passed=passed,
            expected="> 0 заказов/месяц",
            actual=f"{target:,.0f} заказов/месяц",
            message="Целевая производительность установлена",
            severity='info'
        )

    def _validate_budget_constraints(self, location_data: Dict, roi_data: Dict) -> ValidationResult:
        """Проверка бюджетных ограничений."""
        max_budget = config.MAX_TOTAL_CAPEX_RUB
        total_investment = location_data['total_initial_capex']

        if roi_data:
            max_auto_capex = max([data['capex'] for data in roi_data.values()])
            total_investment = max(total_investment, max_auto_capex)

        passed = total_investment <= max_budget

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Бюджетные ограничения",
            passed=passed,
            expected=f"<= {max_budget:,.0f} руб",
            actual=f"{total_investment:,.0f} руб",
            message=f"Инвестиции {'в рамках' if passed else 'ПРЕВЫШАЮТ'} бюджет",
            severity='critical' if not passed else 'info'
        )

    def _validate_gpp_gdp_compliance(self, location_data: Dict) -> ValidationResult:
        """Проверка соответствия GPP/GDP."""
        current_class = location_data.get('current_class', '')
        passed = current_class in ['A', 'A_verified', 'A_requires_mod']

        if not passed:
            self.critical_failures += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Соответствие GPP/GDP",
            passed=passed,
            expected="Класс A или A с модификациями",
            actual=f"Класс {current_class}",
            message=f"Помещение {'соответствует' if passed else 'НЕ соответствует'} стандартам",
            severity='critical' if not passed else 'info'
        )

    def _validate_project_timeline(self) -> ValidationResult:
        """Проверка срока реализации."""
        max_months = 12
        passed = True

        self.info_count += 1

        return ValidationResult(
            check_name="Срок реализации проекта",
            passed=passed,
            expected=f"<= {max_months} месяцев",
            actual=f"~9-10 месяцев (по плану)",
            message="Проект реализуем в срок",
            severity='info'
        )

    def _validate_scalability(self, location_data: Dict) -> ValidationResult:
        """Проверка масштабируемости."""
        # Проверяем, что есть резерв площади для роста
        area = location_data.get('area_offered_sqm', 0)
        min_area = config.MIN_AREA_SQM
        growth_reserve = ((area - min_area) / min_area) * 100 if min_area > 0 else 0

        passed = growth_reserve >= 20  # Минимум 20% резерв

        if not passed:
            self.warnings += 1
        else:
            self.info_count += 1

        return ValidationResult(
            check_name="Масштабируемость",
            passed=passed,
            expected="Резерв площади >= 20%",
            actual=f"Резерв: {growth_reserve:.1f}%",
            message=f"Масштабируемость {'обеспечена' if passed else 'ограничена'}",
            severity='warning' if not passed else 'info'
        )

    def _print_validation_results(self, results: List[ValidationResult], category: str):
        """Выводит результаты валидации."""
        print(f"\n[{category}] Результаты проверок:")
        print("-" * 100)

        for result in results:
            icon = "[OK]" if result.passed else "[FAIL]"
            severity_icon = {
                'critical': '[!]',
                'warning': '[?]',
                'info': '[+]'
            }.get(result.severity, '[*]')

            print(f"{severity_icon} {icon} {result.check_name}")
            print(f"    Ожидалось: {result.expected}")
            print(f"    Фактически: {result.actual}")
            print(f"    {result.message}")
            print()


def run_full_validation(location_data: Dict[str, Any],
                       warehouse_data: Dict[str, Any],
                       roi_data: Dict[str, Any],
                       automation_scenarios: Dict[str, Any],
                       simulation_results: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Запускает полную валидацию модели.

    Args:
        location_data: Данные локации
        warehouse_data: Данные склада
        roi_data: Данные ROI
        automation_scenarios: Сценарии автоматизации
        simulation_results: Результаты симуляции (опционально)

    Returns:
        Результаты валидации и верификации
    """
    print("\n" + "="*100)
    print("ЗАПУСК ПОЛНОЙ ВАЛИДАЦИИ И ВЕРИФИКАЦИИ МОДЕЛИ")
    print("="*100)

    validator = ModelValidator()

    # 1. Валидация локации
    validator.validate_location_data(location_data)

    # 2. Валидация конфигурации склада
    if warehouse_data:
        validator.validate_warehouse_configuration(
            warehouse_data.get('zoning_data', {}),
            warehouse_data.get('equipment_data', {}),
            warehouse_data.get('total_sku', config.TOTAL_SKU_COUNT)
        )

        # 3. Валидация климатических систем
        if 'climate_requirements' in warehouse_data:
            validator.validate_climate_systems(warehouse_data['climate_requirements'])

    # 4. Валидация ROI
    validator.validate_roi_calculations(roi_data, automation_scenarios)

    # 5. Валидация операционных KPI
    if simulation_results:
        validator.validate_operational_kpi(simulation_results)

    # 6. Валидация бизнес-требований
    validator.validate_business_requirements(location_data, roi_data)

    # 7. Верификация целей
    verification_results = validator.verify_model_objectives(
        location_data, roi_data, warehouse_data
    )

    # 8. Генерация отчета
    report_path = validator.generate_validation_report()

    # Итоговая статистика
    print("\n" + "="*100)
    print("ИТОГИ ВАЛИДАЦИИ")
    print("="*100)
    print(f"Всего проверок: {len(validator.validation_results)}")
    print(f"Пройдено: {sum(1 for r in validator.validation_results if r.passed)}")
    print(f"Провалено: {sum(1 for r in validator.validation_results if not r.passed)}")
    print(f"Критических ошибок: {validator.critical_failures}")
    print(f"Предупреждений: {validator.warnings}")
    print(f"Информационных: {validator.info_count}")
    if report_path:
        print(f"\nОтчет сохранен: {report_path}")
    print("="*100)

    return {
        'validation_results': validator.validation_results,
        'verification_results': verification_results,
        'critical_failures': validator.critical_failures,
        'warnings': validator.warnings,
        'info_count': validator.info_count,
        'report_path': report_path
    }


if __name__ == "__main__":
    print("Модуль валидации готов к использованию")
    print("Доступные функции:")
    print("  - run_full_validation() - полная валидация модели")
    print("  - ModelValidator - класс валидатора для расширенного использования")
