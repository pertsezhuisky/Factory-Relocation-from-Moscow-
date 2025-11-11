"""
Модуль для взаимодействия с FlexSim: генерация JSON и имитация API.
"""
import json
import os
from typing import Dict, Any, Optional

import config
from core.data_model import LocationSpec, ScenarioResult
from analysis import FleetOptimizer

class FlexSimAPIBridge:
    """
    Управляет созданием конфигурационных файлов для FlexSim и
    имитирует отправку команд через Socket API.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[FlexSimAPIBridge] Инициализирован. Выходная директория: '{self.output_dir}'")

    def send_config(self, json_data: dict) -> bool:
        """Имитирует отправку JSON-конфигурации через сокет."""
        print("  > [API] Отправка конфигурации в FlexSim...")
        response = self._send_command("LOAD_CONFIG", data=json_data)
        return response.get("status") == "OK"

    def start_simulation(self, scenario_id: str) -> bool:
        """Имитирует команду запуска симуляции в FlexSim."""
        print(f"  > [API] Запуск симуляции для сценария '{scenario_id}'...")
        response = self._send_command("START_SIMULATION", data={"scenario": scenario_id})
        return response.get("status") == "OK"

    def receive_kpi(self) -> Dict[str, Any]:
        """Имитирует прием ключевых метрик от FlexSim."""
        print("  > [API] Получение KPI от FlexSim...")
        response = self._send_command("GET_KPI")
        if response.get("status") == "OK":
            # Возвращаем пример словаря, как указано в задаче
            kpi_data = {
                'achieved_throughput': 10500, 
                'resource_utilization': 0.85
            }
            print(f"  > [API] Получены KPI: {kpi_data}")
            return kpi_data
        return {}

    def generate_json_config(self, location_spec: LocationSpec, scenario_data: dict, fleet_optimizer: FleetOptimizer):
        """Создает и сохраняет JSON-конфигурацию для одного сценария."""
        
        # Определяем тип автоматизации на основе инвестиций
        automation_investment = scenario_data.get('automation_investment', 0)
        automation_type = "None"
        if automation_investment == 100_000_000:
            automation_type = "Conveyors+WMS"
        elif automation_investment > 100_000_000:
            automation_type = "AutoStore+AGV"
            
        config_data = {
            "FINANCIALS": {
                "Total_CAPEX": scenario_data['total_capex'],
                "Annual_OPEX": scenario_data['total_opex']
            },
            "LAYOUT": {
                "Total_Area_SQM": config.WAREHOUSE_TOTAL_AREA_SQM,
                "Ceiling_Height": 12,
                "GPP_ZONES": [
                    {"Zone": "Cool_2_8C", "Pallet_Capacity": 3000},
                    {"Zone": "Controlled_15_25C", "Pallet_Capacity": 17000}
                ]
            },
            "RESOURCES": {
                "Staff_Operators": scenario_data['staff_count'],
                "Automation_Type": automation_type,
                "Processing_Time_Coefficient": scenario_data['processing_efficiency']
            },
            "LOGISTICS": {
                "Location_Coords": [location_spec.lat, location_spec.lon],
                "Required_Own_Fleet_Count": fleet_optimizer.calculate_required_fleet(),
                "Delivery_Flows": [
                    {"Dest": "SVO_Aviation", "Volume_Pct": fleet_optimizer.AIR_DELIVERY_SHARE * 100},
                    {"Dest": "CFD_Own_Fleet", "Volume_Pct": fleet_optimizer.CFO_OWN_FLEET_SHARE * 100},
                    {"Dest": "Moscow_LPU", "Volume_Pct": fleet_optimizer.LOCAL_DELIVERY_SHARE * 100}
                ]
            }
        }
        
        # Формируем имя файла на основе имени сценария
        scenario_name = scenario_data.get('name', 'Unknown_Scenario')
        safe_scenario_name = scenario_name.replace('. ', '_').replace(' ', '_')
        filename = f"flexsim_setup_{safe_scenario_name}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        print(f"  > ✅ JSON-конфиг сохранен: {filename}")
        
        # Демонстрация для Сценария 4
        if "4_Move_Advanced_Automation" in safe_scenario_name:
            print("\n--- Демонстрация JSON для Сценария 4 ---")
            print(json.dumps(config_data, ensure_ascii=False, indent=4))
            print("-----------------------------------------\n")

    def _send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Имитирует отправку команды FlexSim (stub-версия из api_bridge.py)."""
        # print(f"[FlexSimAPIBridge STUB] Отправка команды '{command}'...")
        try:
            # Имитируем ошибку подключения, так как сервера нет
            raise ConnectionRefusedError("No FlexSim server is listening (as expected for a stub).")
        except ConnectionRefusedError as e:
            # print(f"[FlexSimAPIBridge STUB] Ошибка (это нормально для заглушки): {e}")
            if command == "LOAD_CONFIG":
                return {"status": "OK", "message": "Configuration loaded."}
            elif command == "START_SIMULATION":
                return {"status": "OK", "message": "Simulation started."}
            elif command == "GET_KPI":
                 return {"status": "OK", "kpi": {"achieved_throughput": 10500, "resource_utilization": 0.85}}
            return {"status": "ERROR", "message": "Unknown command"}