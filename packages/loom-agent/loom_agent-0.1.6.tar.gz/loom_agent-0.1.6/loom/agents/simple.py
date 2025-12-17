"""
SimpleAgent - 最简单的 Agent 实现

基于递归状态机的基础 Agent
"""

from __future__ import annotations
from typing import List, Optional

from loom.core.message import Message
from loom.core.executor import AgentExecutor
from loom.core.context import ContextManager
from loom.interfaces.llm import BaseLLM
from loom.interfaces.tool import BaseTool
from loom.skills import SkillManager


class SimpleAgent:
    """
    SimpleAgent - 基础递归 Agent

    核心特性：
    - 纯递归调用
    - 自动工具调用
    - Context 自动管理
    - 简单易用

    用途：
    - 单一职责的 Agent
    - 简单的对话
    - 作为 Crew 的成员
    - 快速原型开发

    示例：
    ```python
    from loom.agents import SimpleAgent
    from loom.builtin.llms import OpenAILLM
    from loom.builtin.tools import tool

    # 定义工具
    @tool(name="calculator")
    async def calculator(expression: str) -> float:
        return eval(expression)

    # 创建 Agent
    agent = SimpleAgent(
        name="assistant",
        llm=OpenAILLM(api_key="..."),
        tools=[calculator]
    )

    # 使用
    from loom.core.message import Message

    message = Message(role="user", content="What's 2+2?")
    response = await agent.run(message)
    print(response.content)  # "2+2 equals 4"
    ```
    """

    def __init__(
        self,
        name: str,
        llm: BaseLLM,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
        context_manager: Optional[ContextManager] = None,
        max_recursion_depth: int = 20,
        skills_dir: Optional[str] = None,
        enable_skills: bool = True,
    ):
        """
        初始化 SimpleAgent

        Args:
            name: Agent 名称
            llm: LLM 实例
            tools: 工具列表
            system_prompt: 系统提示词（可选）
            context_manager: Context 管理器（可选）
            max_recursion_depth: 最大递归深度
            skills_dir: 技能目录路径（可选，默认 ./skills）
            enable_skills: 是否启用技能系统
        """
        self.name = name
        self.llm = llm
        self.tools = tools or []

        # Skills 系统
        self.enable_skills = enable_skills
        self.skill_manager = None
        if enable_skills:
            skills_path = skills_dir or "./skills"
            try:
                self.skill_manager = SkillManager(skills_path)
                self.skill_manager.load_all()
                print(f"[{name}] Skills enabled: {self.skill_manager.get_stats()}")
            except Exception as e:
                print(f"[{name}] Failed to load skills: {e}")
                self.enable_skills = False

        # 生成系统提示（包含工具使用启发式 + Skills）
        if system_prompt is None:
            system_prompt = self._generate_default_system_prompt()

        self.system_prompt = system_prompt

        # 创建执行引擎
        self.executor = AgentExecutor(
            agent_name=name,
            llm=llm,
            tools=self.tools,
            context_manager=context_manager or ContextManager(),
            max_recursion_depth=max_recursion_depth,
            system_prompt=self.system_prompt,
        )

    def _generate_default_system_prompt(self) -> str:
        """生成包含工具启发式和技能的默认系统提示"""
        base_prompt = f"You are {self.name}, a helpful assistant."

        # 添加 Skills 索引（如果启用）
        if self.enable_skills and self.skill_manager:
            skills_section = self.skill_manager.get_system_prompt_section()
            if skills_section:
                base_prompt += "\n\n" + skills_section

        if not self.tools:
            return base_prompt

        # 添加工具使用启发式
        tool_guidance = """

# Tool Usage Guidelines

When using tools, follow these best practices:

1. **Understand Available Tools**: Always check which tools are available before deciding how to approach a task.

2. **Match Tools to Intent**: Choose tools that directly match the user's intent and task requirements.

3. **Prefer Specific Tools**: When multiple tools could work, prefer specialized tools over general-purpose ones.

4. **Tool Selection Strategy**:
   - For external/web information: Use web search or external API tools
   - For internal data: Use specialized internal tools (databases, file systems, etc.)
   - For calculations: Use calculator or computation tools
   - For data processing: Use appropriate data transformation tools

5. **Efficient Execution**:
   - Call tools in parallel when they don't depend on each other
   - Chain tool calls logically when one depends on another's output
   - Avoid redundant tool calls - reuse results when possible

6. **Error Handling**:
   - If a tool fails, try an alternative approach
   - Explain tool errors to the user clearly
   - Don't repeatedly call a failing tool

7. **Result Validation**:
   - Verify tool results make sense before using them
   - Cross-check important information when possible
   - Acknowledge uncertainty if tool results are unclear
"""
        return base_prompt + tool_guidance

    async def run(self, message: Message) -> Message:
        """
        核心递归方法

        流程：
        1. 委托给执行引擎
        2. 返回结果

        这个方法实现了递归状态机：
        - LLM 推理 → 工具调用 → 递归调用 run() → 最终结果

        Args:
            message: 输入消息

        Returns:
            响应消息

        Raises:
            AgentError: Agent 执行错误
            RecursionError: 递归深度超限
        """
        return await self.executor.execute(message)

    async def reply(self, message: Message) -> Message:
        """
        便捷方法 - 直接回复（alias for run）

        Args:
            message: 输入消息

        Returns:
            响应消息
        """
        return await self.run(message)

    def reset(self) -> None:
        """重置 Agent 状态"""
        self.executor.reset()

    def get_stats(self) -> dict:
        """获取 Agent 统计信息"""
        stats = {
            "name": self.name,
            "num_tools": len(self.tools),
            "executor_stats": self.executor.get_stats(),
        }

        # 添加 Skills 统计
        if self.enable_skills and self.skill_manager:
            stats["skills"] = self.skill_manager.get_stats()

        return stats

    # ===== Skills Management Methods =====

    def list_skills(self, category: Optional[str] = None) -> List:
        """
        列出可用技能

        Args:
            category: 筛选分类（可选）

        Returns:
            技能列表
        """
        if not self.enable_skills or not self.skill_manager:
            return []

        return self.skill_manager.list_skills(category=category)

    def get_skill(self, name: str):
        """
        获取技能

        Args:
            name: 技能名称

        Returns:
            Skill 实例
        """
        if not self.enable_skills or not self.skill_manager:
            return None

        return self.skill_manager.get_skill(name)

    def reload_skills(self) -> None:
        """重新加载所有技能"""
        if self.enable_skills and self.skill_manager:
            self.skill_manager.reload()
            # 重新生成系统提示
            self.system_prompt = self._generate_default_system_prompt()
            self.executor.system_prompt = self.system_prompt

    def enable_skill(self, name: str) -> bool:
        """启用技能"""
        if not self.enable_skills or not self.skill_manager:
            return False

        result = self.skill_manager.enable_skill(name)
        if result:
            # 更新系统提示
            self.system_prompt = self._generate_default_system_prompt()
            self.executor.system_prompt = self.system_prompt
        return result

    def disable_skill(self, name: str) -> bool:
        """禁用技能"""
        if not self.enable_skills or not self.skill_manager:
            return False

        result = self.skill_manager.disable_skill(name)
        if result:
            # 更新系统提示
            self.system_prompt = self._generate_default_system_prompt()
            self.executor.system_prompt = self.system_prompt
        return result

    def create_skill(
        self,
        name: str,
        description: str,
        category: str = "general",
        **kwargs
    ):
        """
        创建新技能

        Args:
            name: 技能名称
            description: 描述
            category: 分类
            **kwargs: 其他参数

        Returns:
            创建的 Skill 实例
        """
        if not self.enable_skills or not self.skill_manager:
            raise RuntimeError("Skills system is not enabled")

        skill = self.skill_manager.create_skill(
            name=name,
            description=description,
            category=category,
            **kwargs
        )

        # 更新系统提示
        self.system_prompt = self._generate_default_system_prompt()
        self.executor.system_prompt = self.system_prompt

        return skill

    def __repr__(self) -> str:
        return f"SimpleAgent(name='{self.name}', tools={len(self.tools)})"
