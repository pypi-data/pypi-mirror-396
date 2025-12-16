"""Nodo Planificador - decide qué acciones tomar."""

from typing import Dict, Any, Optional, Callable, List
import json
from datetime import datetime
from langchain.schema import BaseMessage, HumanMessage, AIMessage

# ✅ Imports correctos
from sonika_langchain_bot.bot.nodes.base_node import BaseNode
from sonika_langchain_bot.bot.models import PlannerDecision


class PlannerNode(BaseNode):
    """Nodo que analiza y planifica la siguiente acción."""
    
    def __init__(self, model, tools: List[Any], max_retries: int = 2,
                 on_planner_update: Optional[Callable] = None, logger=None):
        super().__init__(logger)
        self.model = model
        self.tools = tools
        self.max_retries = max_retries
        self.on_planner_update = on_planner_update
        self.tool_descriptions = self._build_tool_descriptions()
    
    def _build_tool_descriptions(self) -> str:
        """Build detailed tool descriptions with parameters."""
        if not self.tools: 
            return "No tools available."
        
        import inspect
        tools_description = ""
        
        for tool in self.tools:
            tools_description += f"\n## {tool.name}\n"
            tools_description += f"**Description:** {tool.description}\n\n"
            
            if hasattr(tool, 'args_schema') and tool.args_schema and hasattr(tool.args_schema, '__fields__'):
                tools_description += "**Parameters:**\n"
                for field_name, field_info in tool.args_schema.__fields__.items():
                    required = "**REQUIRED**" if field_info.is_required() else "*optional*"
                    field_type = field_info.annotation.__name__ if hasattr(field_info.annotation, '__name__') else str(field_info.annotation)
                    field_desc = field_info.description if hasattr(field_info, 'description') else "No description"
                    tools_description += f"- `{field_name}` ({field_type}, {required}): {field_desc}\n"
            
            elif hasattr(tool, 'args_schema') and isinstance(tool.args_schema, dict):
                if 'properties' in tool.args_schema:
                    tools_description += "**Parameters:**\n"
                    for param_name, param_info in tool.args_schema['properties'].items():
                        required = "**REQUIRED**" if param_name in tool.args_schema.get('required', []) else "*optional*"
                        param_desc = param_info.get('description', 'No description')
                        param_type = param_info.get('type', 'any')
                        tools_description += f"- `{param_name}` ({param_type}, {required}): {param_desc}\n"
            
            elif hasattr(tool, '_run'):
                tools_description += "**Parameters:**\n"
                sig = inspect.signature(tool._run)
                for param_name, param in sig.parameters.items():
                    if param_name != 'self':
                        param_type = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'any'
                        required = "**REQUIRED**" if param.default == inspect.Parameter.empty else "*optional*"
                        default_info = f" (default: {param.default})" if param.default != inspect.Parameter.empty else ""
                        tools_description += f"- `{param_name}` ({param_type}, {required}){default_info}\n"
            
            tools_description += "\n"
        
        tools_description += ("## Critical Rules\n"
                            "- Use EXACT parameter names as shown above\n"
                            "- Provide ALL **REQUIRED** parameters\n"
                            "- Match parameter types correctly\n")
        
        return tools_description.strip()
    
    def _convert_messages(self, messages: List[Any]) -> List[BaseMessage]:
        """Convierte Message custom a BaseMessage de LangChain."""
        result = []
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage)):
                result.append(msg)
            elif hasattr(msg, 'is_bot') and hasattr(msg, 'content'):
                if msg.is_bot:
                    result.append(AIMessage(content=msg.content))
                else:
                    result.append(HumanMessage(content=msg.content))
        return result
        
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["planning_attempts"] = state.get("planning_attempts", 0) + 1
        
        for attempt in range(self.max_retries + 1):
            try:
                plan, tokens = self._generate_plan(state, attempt)
                self._accumulate_tokens(state, tokens)
                
                is_valid, error = plan.validate_consistency()
                
                if not is_valid:
                    self.logger.warning(f"Plan inconsistente: {error} (intento {attempt + 1}/{self.max_retries + 1})")
                    if attempt < self.max_retries:
                        continue
                    else:
                        self.logger.error("Máximos reintentos alcanzados, usando fallback")
                        fallback = {
                            "decision": "request_data",
                            "reasoning": [f"Error de planificación: {error}"],
                            "field_needed": "clarification",
                            "context_for_user": "poder ayudarte mejor",
                            "confidence": "low"
                        }
                        return {**state, "planner_output": fallback}
                
                plan_dict = plan.dict()
                
                if self.on_planner_update:
                    try:
                        callback_data = {
                            "decision": plan.decision,
                            "reasoning": plan.reasoning,
                            "confidence": plan.confidence,
                            "timestamp": datetime.now().isoformat()
                        }
                        if plan.actions:
                            callback_data["actions"] = plan.actions
                        if plan.field_needed:
                            callback_data["field_needed"] = plan.field_needed
                        
                        self.on_planner_update(callback_data)
                    except Exception as e:
                        self.logger.warning(f"Callback failed: {e}")
                
                return {**state, "planner_output": plan_dict}
                
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON parsing error: {e} (intento {attempt + 1}/{self.max_retries + 1})")
                if attempt >= self.max_retries:
                    fallback = {
                        "decision": "request_data",
                        "reasoning": ["No pude procesar la respuesta correctamente"],
                        "field_needed": "clarification",
                        "context_for_user": "entender mejor tu solicitud",
                        "confidence": "low"
                    }
                    return {**state, "planner_output": fallback}
            
            except Exception as e:
                self.logger.error(f"Error inesperado: {e} (intento {attempt + 1}/{self.max_retries + 1})")
                if attempt >= self.max_retries:
                    fallback = {
                        "decision": "request_data",
                        "reasoning": [f"Error interno: {str(e)[:100]}"],
                        "field_needed": "clarification",
                        "context_for_user": "procesar tu solicitud",
                        "confidence": "low"
                    }
                    return {**state, "planner_output": fallback}
        
        return {**state, "planner_output": {
            "decision": "request_data",
            "reasoning": ["Error de planificación"],
            "field_needed": "clarification",
            "context_for_user": "ayudarte",
            "confidence": "low"
        }}
    
    def _generate_plan(self, state, attempt):
        system_prompt = self._build_planning_prompt(state)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        raw_messages = state.get("messages", [])
        converted_messages = self._convert_messages(raw_messages)
        
        for msg in converted_messages:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content or ""})
        
        messages.append({"role": "user", "content": state.get("user_input", "")})
        
        response = self.model.invoke(messages)
        tokens = self._extract_token_usage(response)
        
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        plan_dict = json.loads(content)
        plan = PlannerDecision(**plan_dict)
        return plan, tokens
    
    def _build_planning_prompt(self, state):
        return f"""You are a planning engine for a conversational assistant.

# YOUR CAPABILITIES
{state.get('function_purpose', '')}

# CONTEXT
{state.get('dynamic_info', '')}

# AVAILABLE TOOLS
{self.tool_descriptions}

# YOUR TASK
Analyze the user's request and decide what to do next.

## Decision Types:
1. **execute_actions**: When you have all needed information and can execute tools
2. **request_data**: When you need more information from the user

## Output Format (strict JSON)

### For execute_actions:
{{
    "decision": "execute_actions",
    "reasoning": ["analysis step 1", "analysis step 2", "conclusion"],
    "actions": [
        {{
            "action": "<exact_tool_name>",
            "args": {{
                "<param1>": "value1",
                "<param2>": "value2"
            }}
        }}
    ],
    "confidence": "low|medium|high"
}}

### For request_data:
{{
    "decision": "request_data",
    "reasoning": ["why I need this", "what's missing"],
    "field_needed": "<field_name>",
    "context_for_user": "<why you need it>",
    "confidence": "low|medium|high"
}}

## CRITICAL RULES:
1. If decision="execute_actions", you MUST include "actions" array with at least one action
2. Each action MUST have "action" (exact tool name from available tools) and "args" (dict with tool parameters)
3. Match tool parameter names EXACTLY as they appear in tool descriptions
4. Do NOT output execute_actions without providing actions array
5. Output ONLY valid JSON, no additional text

Analyze and decide now:
"""