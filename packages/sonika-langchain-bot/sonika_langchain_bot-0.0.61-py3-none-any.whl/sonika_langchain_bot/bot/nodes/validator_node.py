"""Nodo Verificador - valida cumplimiento."""

from typing import Dict, Any
import json
# ✅ Imports correctos
from sonika_langchain_bot.bot.nodes.base_node import BaseNode
from sonika_langchain_bot.bot.models import ValidationResult

class ValidatorNode(BaseNode):
    """Verifica cumplimiento de limitaciones."""
    
    def __init__(self, model, logger=None):
        super().__init__(logger)
        self.model = model
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        executor_output = state.get("executor_output", {})
        planner_output = state.get("planner_output", {})
        
        if not executor_output or planner_output.get("decision") == "request_data":
            return {**state, "validator_output": {
                "approved": True, "violations": [], "feedback_for_planner": None
            }}
        
        try:
            validation, tokens = self._validate(state)
            self._accumulate_tokens(state, tokens)

            print(f"\n🔍 VALIDATOR RESULT:")
            print(f"   Approved: {validation.approved}")
            print(f"   Violations: {validation.violations}")
            print(f"   Feedback: {validation.feedback_for_planner}")

            return {**state, "validator_output": validation.dict()}
        except:
            return {**state, "validator_output": {
                "approved": True, "violations": [], "feedback_for_planner": None
            }}
    
    def _validate(self, state):
        prompt = f"""Validate execution against limitations.

LIMITATIONS: {state.get('limitations', '')}
EXECUTED: {state.get('executor_output', {})}

Output JSON: {{"approved": true/false, "violations": [], "feedback_for_planner": null}}
"""
        response = self.model.invoke([{"role": "system", "content": prompt}])
        tokens = self._extract_token_usage(response)
        
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        validation_dict = json.loads(content)
        validation = ValidationResult(**validation_dict)
        return validation, tokens