"""
Модуль для взаимодействия с FlexSim: генерация JSON и имитация API.
"""
import json
import os
from typing import Dict, Any, Optional

import config
from core.data_model import LocationSpec, ScenarioResult

class FlexsimBridge:
    """
    Управляет созданием конфигурационных файлов для FlexSim и
    имитирует отправку команд через Socket API.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[FlexsimBridge] Инициализирован. Выходная директория: '{self.output_dir}'")

    def generate_json_config(self, location_spec: LocationSpec, scenario_result: ScenarioResult, scenario_params: dict):
        """Создает и сохраняет JSON-конфигурацию для одного сценария."""
        
        # Определяем, какие системы автоматизации включены в сценарии
        automation_systems = []
        automation_investment = scenario_params.get('automation_investment_rub', 0)
        if automation_investment == 100_000_000:
            automation_systems.append("Conveyors")
        elif automation_investment > 100_000_000:
            automation_systems.extend(["Conveyors", "AGV", "RoboticArms"])
            
        config_data = {
            "Global_Settings": {
                "Scenario_Name": scenario_result.scenario_name,
                "location_name": location_spec.name,
                "coordinates": {"lat": location_spec.lat, "lon": location_spec.lon}
            },
            "Resource_Pool": {
                "Operators": scenario_result.staff_count,
                "Automated_Systems": automation_systems
            },
            "Process_Times": {
                "Base_Efficiency_Multiplier": scenario_params.get('efficiency_multiplier', 1.0)
            },
            "Throughput_Targets": {
                "Monthly_Orders_Target": config.TARGET_ORDERS_MONTH,
                "Monthly_Orders_Achieved": scenario_result.throughput_orders
            }
        }
        
        # Формируем имя файла на основе имени сценария
        safe_scenario_name = scenario_result.scenario_name.replace('. ', '_').replace(' ', '_')
        filename = f"flexsim_setup_{safe_scenario_name}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        print(f"  > ✅ JSON-конфиг сохранен: {filename}")

    def send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Имитирует отправку команды FlexSim (stub-версия из api_bridge.py)."""
        print(f"[FlexsimBridge STUB] Отправка команды '{command}'...")
        try:
            # Имитируем ошибку подключения, так как сервера нет
            raise ConnectionRefusedError("No FlexSim server is listening (as expected for a stub).")
        except ConnectionRefusedError as e:
            print(f"[FlexsimBridge STUB] Ошибка (это нормально для заглушки): {e}")
            if command == "LOAD_CONFIG":
                return {"status": "OK", "message": "Configuration loaded."}
            elif command == "START_SIMULATION":
                return {"status": "OK", "message": "Simulation started."}
            elif command == "GET_KPI":
                 return {"status": "OK", "kpi": {"throughput": 999, "utilization": 0.9}}
            return {"status": "ERROR", "message": "Unknown command"}