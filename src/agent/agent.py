import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.tools import TOOL_REGISTRY, execute_tool, get_tool_descriptions

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: Optional[List[Dict[str, Any]]] = None, max_steps: int = 5):
        self.llm = llm
        self.tools = tools if tools is not None else TOOL_REGISTRY
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        TODO: Implement the system prompt that instructs the agent to follow ReAct.
        Should include:
        1.  Available tools and their descriptions.
        2.  Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = get_tool_descriptions()
        return f"""
        You are an intelligent assistant. You have access to the following tools:
        {tool_descriptions}

        Use the following format:
        Thought: your line of reasoning.
        Action: tool_name(arguments)
        Observation: result of the tool call.
        ... (repeat Thought/Action/Observation if needed)
        Final Answer: your final response.

        Important rules:
        - Use only one tool call per Action line.
        - Do not invent tool names.
        - If enough information is gathered, output Final Answer.
        """

    @staticmethod
    def _extract_final_answer(text: str) -> Optional[str]:
        match = re.search(r"Final\s*Answer\s*:\s*(.*)", text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def _extract_action(text: str) -> Optional[Dict[str, str]]:
        match = re.search(
            r"Action\s*:\s*([a-zA-Z_][\w]*)\s*\((.*?)\)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return None
        return {
            "tool_name": match.group(1).strip(),
            "args": match.group(2).strip(),
        }

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = f"User Question: {user_input}"
        steps = 0
        last_response = ""
        system_prompt = self.get_system_prompt()

        while steps < self.max_steps:
            result = self.llm.generate(current_prompt, system_prompt=system_prompt)
            content = result.get("content", "").strip()
            usage = result.get("usage", {})
            latency_ms = result.get("latency_ms")
            last_response = content

            logger.log_event(
                "AGENT_STEP",
                {
                    "step": steps + 1,
                    "response": content,
                    "usage": usage,
                    "latency_ms": latency_ms,
                },
            )

            self.history.append(
                {
                    "step": steps + 1,
                    "prompt": current_prompt,
                    "response": content,
                    "usage": usage,
                    "latency_ms": latency_ms,
                }
            )

            final_answer = self._extract_final_answer(content)
            if final_answer:
                logger.log_event("AGENT_END", {"steps": steps + 1, "status": "completed"})
                return final_answer

            action = self._extract_action(content)
            if action:
                observation = self._execute_tool(action["tool_name"], action["args"])
                logger.log_event(
                    "AGENT_TOOL_CALL",
                    {
                        "step": steps + 1,
                        "tool": action["tool_name"],
                        "args": action["args"],
                        "observation": observation,
                    },
                )
                current_prompt += (
                    f"\n\nAssistant Output:\n{content}"
                    f"\nObservation: {observation}"
                    "\nContinue with Thought/Action or provide Final Answer."
                )
            else:
                current_prompt += (
                    f"\n\nAssistant Output:\n{content}"
                    "\nNo valid Action or Final Answer detected."
                    "\nPlease follow the required format exactly."
                )

            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps, "status": "max_steps_reached"})
        if last_response:
            return (
                "I could not finish within max steps. Last model output:\n"
                f"{last_response}"
            )
        return "I could not produce a final answer within max steps."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        return execute_tool(tool_name, args)
