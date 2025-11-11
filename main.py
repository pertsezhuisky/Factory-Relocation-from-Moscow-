# main.py

"""
Единственная точка входа в приложение.
Парсит аргументы командной строки и запускает оркестратор симуляций.
"""
import argparse
from core.data_model import LocationSpec
from simulation_runner import SimulationRunner

def main():
    """Главная исполняемая функция."""
    
    parser = argparse.ArgumentParser(
        description="Запуск комплексного анализа релокации склада для FlexSim.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Для красивого вывода помощи
    )
    
    parser.add_argument("--name", type=str, default="Логопарк Север-2", help="Название анализируемой локации.")
    parser.add_argument("--lat", type=float, default=56.095, help="Широта локации.")
    parser.add_argument("--lon", type=float, default=37.388, help="Долгота локации.")
    parser.add_argument("--type", type=str, default="ARENDA", choices=["ARENDA", "POKUPKA"], help="Тип владения: аренда или покупка.")
    
    args = parser.parse_args()

    # 1. Создание объекта (структуры данных) с параметрами локации из аргументов CLI.
    location = LocationSpec(
        name=args.name, 
        lat=args.lat, 
        lon=args.lon, 
        ownership_type=args.type.upper()
    )
    
    # 2. Инициализация и запуск главного исполнителя.
    runner = SimulationRunner(location_spec=location)
    runner.run_all_scenarios()

if __name__ == "__main__":
    main()