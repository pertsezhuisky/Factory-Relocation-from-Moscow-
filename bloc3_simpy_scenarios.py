# block3_simpy_scenarios.py

import simpy
import math

# =============================================================================
# ШАГ 1: Определение входных данных и структуры (Data Setup)
# =============================================================================

# --- ОБЩИЕ ПАРАМЕТРЫ СКЛАДА ---
BASE_PARAMETERS = {
    "warehouse": {
        "area_sqm": 15500,
        "office_area_sqm": 1500,
    },
    "staff": {
        "initial_operator_count": 100,
        "operator_salary_rub": 105000,
    },
    "operations": {
        "monthly_throughput_orders": 10000,
    }
}

# --- ДАННЫЕ ПО СЦЕНАРИЯМ ПЕРЕЕЗДА ---
SCENARIOS_DATA = {
    1: {
        "name": "Move No Mitigation",
        "description": "Переезд без каких-либо мер по удержанию персонала или автоматизации.",
        "staff_attrition_percentage": 0.25,
        "capital_investment_mln_rub": 0,
    },
    2: {
        "name": "Move With Compensation",
        "description": "Переезд с внедрением компенсационного пакета для удержания персонала.",
        "staff_attrition_percentage": 0.15,
        "capital_investment_mln_rub": 50,
    },
    3: {
        "name": "Move Basic Automation",
        "description": "Переезд с внедрением базовой автоматизации для компенсации потерь персонала.",
        "staff_attrition_percentage": 0.25,
        "capital_investment_mln_rub": 100,
    },
    4: {
        "name": "Move Advanced Automation",
        "description": "Переезд с внедрением продвинутой автоматизации для повышения эффективности.",
        "staff_attrition_percentage": 0.25,
        "capital_investment_mln_rub": 300,
    }
}

# =============================================================================
# ШАГ 2: Создание базовой SimPy модели склада (SimPy Environment)
# =============================================================================

# --- КОНСТАНТЫ СИМУЛЯЦИИ ---
SIMULATION_DAYS = 20  # Длительность симуляции в рабочих днях (1 месяц)
MINUTES_PER_WORKING_DAY = 8 * 60  # Количество минут в 8-часовом рабочем дне
ORDERS_PER_MONTH = BASE_PARAMETERS["operations"]["monthly_throughput_orders"]
ORDERS_PER_DAY = ORDERS_PER_MONTH / SIMULATION_DAYS
# Время между поступлением заказов в минутах
INTER_ARRIVAL_TIME_MIN = MINUTES_PER_WORKING_DAY / ORDERS_PER_DAY
ORDER_PROCESSING_TIME_MIN = 15  # Время обработки одного заказа одним оператором

class WarehouseSim:
    """
    Класс для симуляции работы склада по одному из сценариев.
    """
    def __init__(self, scenario_params, base_params):
        self.env = simpy.Environment()
        self.scenario_params = scenario_params
        self.base_params = base_params

        # Расчет доступного персонала с учетом потерь
        initial_staff = self.base_params["staff"]["initial_operator_count"]
        attrition = self.scenario_params["staff_attrition_percentage"]
        self.available_operators = math.floor(initial_staff * (1 - attrition))

        # Создание ресурса "операторы"
        self.operators = simpy.Resource(self.env, capacity=self.available_operators)
        
        # Для сбора статистики
        self.processed_orders_count = 0

    def order_processing(self, order_id):
        """Процесс обработки одного заказа."""
        print(f"Время {self.env.now:.2f}: Заказ #{order_id} поступил на склад.")
        
        # Запрос одного оператора из пула ресурсов
        with self.operators.request() as request:
            yield request  # Ожидание, пока оператор не освободится
            
            print(f"Время {self.env.now:.2f}: Оператор начал обработку заказа #{order_id}.")
            
            # Процесс обработки заказа
            yield self.env.timeout(ORDER_PROCESSING_TIME_MIN)
            
            print(f"Время {self.env.now:.2f}: Заказ #{order_id} обработан и завершен.")
            self.processed_orders_count += 1

    def order_generator(self):
        """Генерирует заказы с заданной периодичностью."""
        order_id = 0
        while True:
            order_id += 1
            # Запускаем процесс обработки для нового заказа
            self.env.process(self.order_processing(order_id))
            # Ожидаем поступления следующего заказа
            yield self.env.timeout(INTER_ARRIVAL_TIME_MIN)

    def run(self, until_time):
        """Запускает симуляцию."""
        print(f"--- ЗАПУСК СИМУЛЯЦИИ ДЛЯ СЦЕНАРИЯ: '{self.scenario_params['name']}' ---")
        print(f"Доступное количество операторов: {self.available_operators}")
        print("-" * 40)

        # Запускаем генератор заказов
        self.env.process(self.order_generator())
        # Запускаем симуляцию на заданное время
        self.env.run(until=until_time)

        print("\n" + "-" * 40)
        print("СИМУЛЯЦИЯ ЗАВЕРШЕНА")
        print(f"Обработано заказов: {self.processed_orders_count}")
        print("-" * 40 + "\n")


# --- Запуск симуляции ---
if __name__ == "__main__":
    # Длительность симуляции в минутах
    SIMULATION_DURATION_MINUTES = SIMULATION_DAYS * MINUTES_PER_WORKING_DAY
    
    # Выбираем сценарий для запуска (для примера, Сценарий 1)
    scenario_id_to_run = 1
    selected_scenario = SCENARIOS_DATA[scenario_id_to_run]

    # Создаем и запускаем симуляцию
    simulation = WarehouseSim(selected_scenario, BASE_PARAMETERS)
    simulation.run(until_time=SIMULATION_DURATION_MINUTES)