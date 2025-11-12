"""
Тестовый скрипт для проверки расширенной SimPy симуляции с доками.
"""
from core.simulation_engine import WarehouseSimulator, EnhancedWarehouseSimulator

print("="*80)
print("ТЕСТИРОВАНИЕ РАСШИРЕННОЙ SIMPY СИМУЛЯЦИИ")
print("="*80)

# Тест 1: Базовая симуляция (без доков)
print("\n[Тест 1] Базовая симуляция (только обработка заказов)")
print("-"*80)
basic_sim = WarehouseSimulator(staff_count=75, efficiency_multiplier=1.0)
basic_results = basic_sim.run()

print(f"Обработано заказов: {basic_results['achieved_throughput']}")
print(f"Среднее время цикла: {basic_results['avg_cycle_time_min']} мин")

# Тест 2: Расширенная симуляция С доками
print("\n[Тест 2] Расширенная симуляция (с моделированием доков)")
print("-"*80)
enhanced_sim = EnhancedWarehouseSimulator(
    staff_count=75,
    efficiency_multiplier=1.0,
    inbound_docks=4,
    outbound_docks=4,
    enable_dock_simulation=True
)
enhanced_results = enhanced_sim.run()

print(f"Обработано заказов: {enhanced_results['achieved_throughput']}")
print(f"Среднее время цикла: {enhanced_results['avg_cycle_time_min']} мин")
print(f"\nМетрики доков:")
print(f"  - Inbound грузовиков обслужено: {enhanced_results['inbound_trucks_served']}")
print(f"  - Outbound грузовиков обслужено: {enhanced_results['outbound_trucks_served']}")
print(f"  - Среднее время ожидания inbound: {enhanced_results['avg_inbound_wait_min']:.2f} мин")
print(f"  - Среднее время ожидания outbound: {enhanced_results['avg_outbound_wait_min']:.2f} мин")
print(f"  - Макс. ожидание inbound: {enhanced_results['max_inbound_wait_min']:.2f} мин")
print(f"  - Макс. ожидание outbound: {enhanced_results['max_outbound_wait_min']:.2f} мин")

# Тест 3: Симуляция с недостаточным количеством доков (узкое место)
print("\n[Тест 3] Симуляция с УЗКИМ МЕСТОМ (2 дока inbound)")
print("-"*80)
bottleneck_sim = EnhancedWarehouseSimulator(
    staff_count=75,
    efficiency_multiplier=1.0,
    inbound_docks=2,  # Мало!
    outbound_docks=4,
    enable_dock_simulation=True
)
bottleneck_results = bottleneck_sim.run()

print(f"Обработано заказов: {bottleneck_results['achieved_throughput']}")
print(f"\nМетрики доков (с узким местом):")
print(f"  - Среднее время ожидания inbound: {bottleneck_results['avg_inbound_wait_min']:.2f} мин [!]")
print(f"  - Макс. ожидание inbound: {bottleneck_results['max_inbound_wait_min']:.2f} мин [!]")

if bottleneck_results['avg_inbound_wait_min'] > 60:
    print(f"\n[!] ПРЕДУПРЕЖДЕНИЕ: Среднее ожидание > 60 мин! Необходимо больше inbound доков!")

# Тест 4: Сценарий с автоматизацией (efficiency_multiplier = 1.2)
print("\n[Тест 4] Сценарий с базовой автоматизацией (эффективность +20%)")
print("-"*80)
automated_sim = EnhancedWarehouseSimulator(
    staff_count=75,
    efficiency_multiplier=1.2,  # +20% скорость обработки
    inbound_docks=4,
    outbound_docks=4,
    enable_dock_simulation=True
)
automated_results = automated_sim.run()

print(f"Обработано заказов: {automated_results['achieved_throughput']}")
print(f"Среднее время цикла: {automated_results['avg_cycle_time_min']} мин (улучшено благодаря автоматизации)")
print(f"Среднее время ожидания inbound: {automated_results['avg_inbound_wait_min']:.2f} мин")

print("\n" + "="*80)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("="*80)
