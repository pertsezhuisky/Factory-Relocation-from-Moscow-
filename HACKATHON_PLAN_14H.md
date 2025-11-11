# 🏁 ХАКАТОН: Перенос HUB-склада за МКАД (14 часов)

## 🎯 Условия

- **Время:** 14 часов (может меньше)
- **Команда:** 4 человека
- **Задача:** Железобетонно переезжаем за МКАД, выбрать оптимальную стратегию
- **Стек:** FlexSim + SimPy
- **Инструменты:** Яндекс.Карты (не Google Maps)

---

## 📊 4 Сценария для анализа

❌ ~~Stay_Moscow~~ - НЕ рассматриваем

✅ **Сценарий 1: Move_No_Mitigation**
- Переезд без компенсаций
- Атрицион: 25% персонала
- Автоматизация: 0
- Инвестиции: Минимальные

✅ **Сценарий 2: Move_With_Compensation**
- Переезд + HR компенсации
- Атрицион: 15% (снижен!)
- Автоматизация: 0
- Инвестиции: 50М руб на удержание

✅ **Сценарий 3: Move_Basic_Automation**
- Переезд + базовая автоматизация
- Атрицион: 25%
- Автоматизация: WMS + конвейеры
- Инвестиции: 100М руб

✅ **Сценарий 4: Move_Advanced_Automation**
- Переезд + высокая автоматизация
- Атрицион: 25%
- Автоматизация: AutoStore + AGV + роботизация
- Инвестиции: 300М руб

---

## 👥 4 Параллельных блока (по человеку)

### 🟦 БЛОК 1: Logistics & Location (Аналитика)
**Ответственный:** Logistics Analyst  
**Время:** 14 часов  
**Инструменты:** Python + Яндекс.Карты API + Excel

**Задачи:**

#### 1.1 Выбор локации за МКАД (4 часа)
```python
# Анализ 3 локаций:
locations = [
    {
        'name': 'Химки',
        'coords': (55.8970, 37.4460),
        'distance_sheremetyevo': 20,  # км
        'rental_cost': 7000,  # руб/м²/год
        'pros': 'Близко к аэропорту',
        'cons': 'Дорого'
    },
    {
        'name': 'Красногорск',
        'coords': (55.8206, 37.3297),
        'distance_sheremetyevo': 30,
        'rental_cost': 5200,
        'pros': 'Оптимальный баланс',
        'cons': 'Средние показатели'
    },
    {
        'name': 'Солнечногорск',
        'coords': (56.1838, 36.9778),
        'distance_sheremetyevo': 35,
        'rental_cost': 3800,
        'pros': 'Дёшево, место для расширения',
        'cons': 'Далеко от Москвы'
    }
]

# Scoring matrix с весами
weights = {
    'distance_sheremetyevo': 0.30,
    'rental_cost': 0.25,
    'transport_access': 0.20,
    'staff_accessibility': 0.15,
    'expansion_potential': 0.10
}

# Выбрать топ-1 локацию
```

#### 1.2 Карты маршрутов с Яндекс.Картами (3 часа)
```python
import requests
import folium

# Яндекс.Карты API
YANDEX_API_KEY = "your_key"

# Маршрут: Шереметьево → Новый склад
route_sheremetyevo = get_route_yandex(
    start=(55.9726, 37.4145),  # Шереметьево
    end=selected_location['coords']
)

# Маршруты доставки по ЦФО
cfo_routes = [
    ('Москва', (55.7558, 37.6173)),
    ('Владимир', (56.1366, 40.3966)),
    ('Тверь', (56.8587, 35.9176)),
    # ... еще 5-7 городов
]

# Визуализация на карте
map = folium.Map(location=[55.75, 37.62], zoom_start=7)
# Добавить маршруты
```

#### 1.3 Расчёт транспортных затрат (3 часа)
```python
# Текущие vs Новые затраты
transport_analysis = {
    'current_moscow': {
        'sheremetyevo_distance': 35,  # км
        'avg_cfo_distance': 120,
        'annual_cost': calculate_cost(35, 120)
    },
    'new_location': {
        'sheremetyevo_distance': location['distance_sheremetyevo'],
        'avg_cfo_distance': 145,  # +25 км
        'annual_cost': calculate_cost(location['distance'], 145)
    },
    'delta': new_cost - current_cost,
    'delta_percent': (new_cost / current_cost - 1) * 100
}
```

#### 1.4 Excel-отчёт (4 часа)
- Сравнение 3 локаций
- Транспортные затраты
- Карты маршрутов (screenshots)
- Рекомендация

**Deliverables:**
- ✅ `output/location_comparison.xlsx`
- ✅ `output/maps/yandex_routes_*.png`
- ✅ Python скрипт: `analysis/logistics_yandex.py`

---

### 🟩 БЛОК 2: HR & Attrition (Аналитика + ML)
**Ответственный:** HR Analyst / Data Scientist  
**Время:** 14 часов  
**Инструменты:** Python + scikit-learn + Excel

**Задачи:**

#### 2.1 ML-модель прогноза атрицион (6 часов)
```python
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

# Dataset: 100 сотрудников
employees = pd.DataFrame({
    'id': range(1, 101),
    'position': ['комплектовщик']*60 + ['оператор']*25 + ['менеджер']*15,
    'age': np.random.randint(25, 55, 100),
    'years_in_company': np.random.randint(1, 15, 100),
    'salary': [...],
    'commute_time_current': np.random.randint(30, 90, 100),
    'commute_time_new': np.random.randint(60, 150, 100),  # +30-60 мин
    'has_children': np.random.choice([0, 1], 100),
    'home_location': [...]
})

# Features engineering
employees['commute_increase'] = employees['commute_time_new'] - employees['commute_time_current']
employees['young_with_kids'] = (employees['age'] < 35) & (employees['has_children'] == 1)

# Обучить модель
X = employees[['age', 'commute_increase', 'position_encoded', ...]]
y = employees['will_leave']  # Target: 0 или 1

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# Предсказать кто уйдёт
predictions = model.predict_proba(employees)
employees['leave_probability'] = predictions[:, 1]

# Результат: 25 человек с highest probability уйдут
top_25_leaving = employees.nlargest(25, 'leave_probability')
```

#### 2.2 Компенсационные стратегии (4 часа)
```python
compensation_plans = {
    'plan_1_no_mitigation': {
        'cost': 0,
        'attrition': 0.25,
        'workers_remaining': 75,
        'hiring_cost': 25 * 150_000  # 3.75М
    },
    'plan_2_basic': {
        'cost': 6_000_000,  # Транспорт + проезд
        'attrition': 0.15,  # Снижено!
        'workers_remaining': 85,
        'hiring_cost': 15 * 150_000  # 2.25М
    },
    'plan_3_extended': {
        'cost': 50_000_000,  # Зарплаты + жильё + бонусы
        'attrition': 0.05,  # Минимум!
        'workers_remaining': 95,
        'hiring_cost': 5 * 150_000  # 0.75М
    }
}

# ROI analysis
for plan in compensation_plans:
    plan['total_cost_year1'] = plan['cost'] + plan['hiring_cost']
    plan['roi'] = calculate_roi(plan)
```

#### 2.3 Интеграция в сценарии (2 часа)
```python
# Применить к 4 сценариям
scenarios = {
    'Move_No_Mitigation': {'attrition': 0.25, 'compensation': plan_1},
    'Move_With_Compensation': {'attrition': 0.15, 'compensation': plan_2},
    'Move_Basic_Automation': {'attrition': 0.25, 'compensation': plan_1},
    'Move_Advanced_Automation': {'attrition': 0.25, 'compensation': plan_1}
}
```

#### 2.4 Отчёт (2 часа)
- ML модель и feature importance
- Список 25 человек с риском увольнения
- 3 компенсационных плана
- Рекомендации

**Deliverables:**
- ✅ `models/attrition_model.pkl`
- ✅ `output/hr_attrition_report.xlsx`
- ✅ Python скрипт: `analysis/hr_ml.py`

---

### 🟨 БЛОК 3: SimPy Simulation (Программирование)
**Ответственный:** Python Developer  
**Время:** 14 часов  
**Инструменты:** Python + SimPy

**Задачи:**

#### 3.1 Базовая SimPy модель (6 часов)
```python
import simpy
import pandas as pd

class WarehouseSimulation:
    def __init__(self, env, config, workers_count, attrition_rate=0.25):
        self.env = env
        self.config = config
        self.workers = simpy.Resource(env, capacity=int(workers_count * (1 - attrition_rate)))
        
        self.orders_processed = 0
        self.total_cycle_time = 0
        
    def receiving_process(self):
        """Приёмка товара от поставщиков"""
        while True:
            yield self.env.timeout(2)  # Каждые 2 часа поставка
            
            with self.workers.request() as req:
                yield req
                yield self.env.timeout(1)  # 1 час на приёмку
                
    def picking_process(self):
        """Комплектация заказов"""
        while True:
            yield self.env.timeout(0.5)  # Новый заказ каждые 30 мин
            
            with self.workers.request() as req:
                yield req
                # Время зависит от количества работников
                picking_time = 2.5 if self.workers.capacity == 100 else 3.0
                yield self.env.timeout(picking_time)
                
                self.orders_processed += 1
                self.total_cycle_time += picking_time

# Запуск
env = simpy.Environment()
sim = WarehouseSimulation(env, config, workers_count=100, attrition_rate=0.25)
env.run(until=720)  # 30 дней

print(f"Orders processed: {sim.orders_processed}")
print(f"Avg cycle time: {sim.total_cycle_time / sim.orders_processed:.2f} hours")
```

#### 3.2 Модель для 4 сценариев (4 часа)
```python
scenarios = [
    {
        'name': 'Move_No_Mitigation',
        'workers': 75,  # -25%
        'automation_level': 0,
        'throughput_boost': 1.0
    },
    {
        'name': 'Move_With_Compensation',
        'workers': 85,  # -15%
        'automation_level': 0,
        'throughput_boost': 1.0
    },
    {
        'name': 'Move_Basic_Automation',
        'workers': 75,  # -25%
        'automation_level': 1,
        'throughput_boost': 1.2  # +20% за счёт конвейеров
    },
    {
        'name': 'Move_Advanced_Automation',
        'workers': 50,  # Роботы заменяют 25 человек
        'automation_level': 2,
        'throughput_boost': 1.5  # +50% за счёт AutoStore
    }
]

results = []
for scenario in scenarios:
    env = simpy.Environment()
    sim = WarehouseSimulation(env, config, scenario['workers'])
    sim.throughput_boost = scenario['throughput_boost']
    env.run(until=720)
    
    results.append({
        'scenario': scenario['name'],
        'orders_processed': sim.orders_processed * sim.throughput_boost,
        'throughput': sim.orders_processed / 720 * sim.throughput_boost,
        'workers': scenario['workers']
    })

# Экспорт
pd.DataFrame(results).to_csv('output/simulation_results.csv')
```

#### 3.3 Socket API для FlexSim (опционально, 2 часа)
```python
# Только если успеем
import socket
import json

class FlexSimBridge:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 5005))
        
    def send_state(self, state):
        message = json.dumps(state).encode() + b'!'
        self.socket.sendall(message)

# В симуляции
bridge = FlexSimBridge()
bridge.send_state({
    'time': env.now,
    'orders': sim.orders_processed,
    'workers': sim.workers.capacity
})
```

#### 3.4 Финальный скрипт (2 часа)
- Красивый вывод результатов
- Графики (matplotlib)
- Экспорт в JSON/CSV

**Deliverables:**
- ✅ `simpy_models/warehouse.py`
- ✅ `simpy_models/main_simulation.py`
- ✅ `output/simulation_results.csv`
- ✅ `output/simulation_comparison.png`

---

### 🟥 БЛОК 4: FlexSim Visualization (Программирование)
**Ответственный:** FlexSim Specialist  
**Время:** 14 часов  
**Инструменты:** FlexSim

**Задачи:**

#### 4.1 Базовая 3D модель (6 часов)
```
Упрощённая модель склада:
- Зона приёмки (2 дока)
- Складская зона (упрощённые стеллажи)
- Зона комплектации (5 станций)
- Зона отгрузки (2 дока)
- Операторы: показать визуально 100 → 75 человек
```

**Приоритет:**
1. Работоспособность модели
2. Визуализация разницы в персонале
3. Dashboard с метриками

#### 4.2 Визуализация 4 сценариев (4 часа)
```
Для каждого сценария:
- Отдельный слой или состояние модели
- Показать количество работников
- Показать throughput (orders/hour)
- Показать автоматизацию (для сценариев 3-4)
```

**Сценарий 3:** Добавить конвейеры (визуально)  
**Сценарий 4:** Добавить AutoStore (можно схематично)

#### 4.3 Dashboard (2 часа)
```flexscript
// Real-time метрики
- Throughput (orders/hour)
- Workers available
- Utilization (%)
- Avg cycle time

// Comparison bars для 4 сценариев
```

#### 4.4 Экспорт видео (2 часа)
```
Короткое видео (2-3 минуты):
1. Текущая ситуация (0:30)
2. Проблема: -25% персонала (0:15)
3. Сценарий 1 (0:30)
4. Сценарий 2 (0:30)
5. Сценарий 3 (0:30)
6. Сценарий 4 (0:30)
7. Сравнение + рекомендация (0:15)
```

**Deliverables:**
- ✅ `flexsim_models/warehouse_hub.fsm`
- ✅ `output/videos/scenarios_demo.mp4`
- ✅ Screenshots dashboard

---

## ⏱️ Timeline (14 часов)

### Час 0-4: Setup & Parallel Start
```
00:00-01:00  Kickoff, распределение задач
01:00-04:00  Параллельная работа (все 4 блока)

Блок 1: Анализ локаций + API Яндекс.Карт
Блок 2: ML модель атрицион
Блок 3: Базовая SimPy модель
Блок 4: FlexSim базовая модель
```

### Час 4-10: Deep Work
```
04:00-10:00  Основная разработка (6 часов)

Блок 1: Карты маршрутов + транспортные затраты
Блок 2: Компенсационные планы + интеграция
Блок 3: 4 сценария в SimPy
Блок 4: Визуализация сценариев
```

### Час 10-12: Integration & Testing
```
10:00-11:00  Интеграция результатов
11:00-12:00  Тестирование, bug fixes
```

### Час 12-14: Finalization
```
12:00-13:00  Финальные доработки
13:00-13:30  Создание презентации
13:30-14:00  Репетиция презентации
```

---

## 📦 Минимальные Deliverables (MVP)

### Must Have:
1. ✅ **Excel-отчёт** с выбором локации (Блок 1)
2. ✅ **Excel-отчёт** по HR и атрицион (Блок 2)
3. ✅ **CSV/JSON** результаты SimPy для 4 сценариев (Блок 3)
4. ✅ **FlexSim модель** с визуализацией (Блок 4)
5. ✅ **Презентация** (5-7 слайдов) с рекомендацией

### Nice to Have:
- 🔶 Яндекс.Карты с реальными маршрутами
- 🔶 FlexSim видео (2-3 мин)
- 🔶 ML модель (.pkl файл)
- 🔶 Socket интеграция FlexSim ↔ Python

---

## 🎯 Критерии успеха

### Обязательные:
- [ ] Выбрана оптимальная локация за МКАД (с обоснованием)
- [ ] Рассчитана стоимость переезда для каждого сценария
- [ ] Проанализирован атрицион персонала (25% → кто уйдёт)
- [ ] Симуляция 4 сценариев в SimPy работает
- [ ] FlexSim модель демонстрирует разницу
- [ ] Презентация с чёткой рекомендацией

### Желательные:
- [ ] Яндекс.Карты интеграция
- [ ] ML модель с feature importance
- [ ] FlexSim видео
- [ ] ROI analysis на 3-5 лет

---

## 📊 Финальная презентация (5-7 слайдов)

### Слайд 1: Проблема
- Необходимость переезда за МКАД
- Потеря 25% персонала
- Нужно выбрать оптимальную стратегию

### Слайд 2: Анализ локаций
- 3 кандидата (Химки / Красногорск / Солнечногорск)
- Scoring matrix
- **Рекомендация:** [Локация X]
- Карта Яндекс с маршрутами

### Слайд 3: HR и атрицион
- ML-прогноз: кто уйдёт (25 человек)
- 3 компенсационных плана
- Cost-benefit анализ

### Слайд 4: 4 Сценария - Результаты
```
Таблица:
| Сценарий | Throughput | Workers | Year 1 Cost | ROI |
|----------|------------|---------|-------------|-----|
| 1. No Mitigation | 1,200/day | 75 | 150М | 3 года |
| 2. With Compensation | 1,400/day | 85 | 200М | 2.5 года |
| 3. Basic Automation | 1,440/day | 75 | 250М | 3 года |
| 4. Advanced Automation | 1,800/day | 50 | 450М | 4 года |
```

### Слайд 5: FlexSim Визуализация
- Screenshot или GIF 3D модели
- Dashboard с метриками
- Сравнение сценариев

### Слайд 6: Рекомендация
**РЕКОМЕНДУЕМ: Сценарий [X]**

Обоснование:
- Оптимальный баланс cost/benefit
- Быстрый ROI
- Минимальные риски
- Соответствует бюджету

### Слайд 7: Next Steps
- План внедрения (timeline)
- Ключевые риски и митигация
- Бюджет детально

---

## 💾 Структура для быстрого старта

```
hackathon-warehouse/
├── data/
│   ├── employees.csv              # 100 человек (генерируем)
│   ├── locations.json             # 3 локации
│   └── transport_config.json      # Параметры транспорта
│
├── block1_logistics/              # Блок 1
│   ├── yandex_maps.py             # API Яндекс.Карт
│   ├── location_selection.py      # Выбор локации
│   └── transport_costs.py         # Расчёты
│
├── block2_hr/                     # Блок 2
│   ├── ml_attrition.py            # ML модель
│   └── compensation_plans.py      # HR планы
│
├── block3_simpy/                  # Блок 3
│   ├── warehouse_model.py         # SimPy модель
│   └── run_scenarios.py           # 4 сценария
│
├── block4_flexsim/                # Блок 4
│   └── warehouse.fsm              # FlexSim модель
│
└── output/
    ├── location_comparison.xlsx
    ├── hr_report.xlsx
    ├── simulation_results.csv
    ├── maps/                      # Яндекс.Карты
    ├── videos/                    # FlexSim видео
    └── presentation.pptx          # Финальная презентация
```

---

## ⚡ Quick Commands

### Setup (5 минут)
```bash
pip install simpy pandas numpy scikit-learn matplotlib openpyxl requests folium
```

### Генерация данных
```bash
python generate_synthetic_data.py
```

### Запуск блоков
```bash
# Блок 1
python block1_logistics/location_selection.py

# Блок 2
python block2_hr/ml_attrition.py

# Блок 3
python block3_simpy/run_scenarios.py

# Блок 4
# Открыть FlexSim вручную
```

---

## 🎯 Ключевые цифры для запоминания

- **100 операторов** → **75 после переезда** (-25%)
- **Шереметьево:** 35 км (сейчас) → 20-35 км (новая локация)
- **Стоимость аренды:** 3,800 - 7,000 руб/м²/год
- **Площадь склада:** ~12,000 - 15,000 м²
- **Throughput:** 1,500 заказов/день (сейчас)
- **4 сценария переезда** (без варианта остаться)

---

**ГЛАВНОЕ:** За 14 часов сделать работающий MVP с чёткой рекомендацией!

**Удачи! 🚀**
