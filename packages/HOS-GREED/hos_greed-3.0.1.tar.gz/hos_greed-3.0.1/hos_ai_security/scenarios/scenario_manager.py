from typing import Dict, Any, List, Optional
from .security_operation import SecurityOperationScenario
from .detection_response import DetectionResponseScenario
from .attack_defense import AttackDefenseScenario
from .knowledge_qa import KnowledgeQAScenario
from .data_security import DataSecurityScenario

class ScenarioManager:
    """场景管理器，负责管理和协调各种AI安全场景"""
    
    def __init__(self):
        self.scenarios = {
            "security_operation": SecurityOperationScenario(),
            "detection_response": DetectionResponseScenario(),
            "attack_defense": AttackDefenseScenario(),
            "knowledge_qa": KnowledgeQAScenario(),
            "data_security": DataSecurityScenario()
        }
    
    def get_scenario(self, scenario_name: str) -> Any:
        """获取指定场景实例"""
        return self.scenarios.get(scenario_name)
    
    def execute_scenario(self, scenario_name: str, data: Any, **kwargs) -> Dict[str, Any]:
        """执行指定场景"""
        if scenario_name not in self.scenarios:
            return {
                "success": False,
                "error": f"场景 {scenario_name} 不存在"
            }
        
        try:
            scenario = self.scenarios[scenario_name]
            result = scenario.execute(data, **kwargs)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_scenarios(self) -> List[str]:
        """列出所有可用场景"""
        return list(self.scenarios.keys())
    
    def get_scenario_description(self, scenario_name: str) -> Optional[str]:
        """获取场景描述"""
        scenario = self.scenarios.get(scenario_name)
        if scenario:
            return scenario.description
        return None
