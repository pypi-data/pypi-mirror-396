"""
Loom Agents - Agent 实现

可用的 Agent：
- SimpleAgent: 基础递归 Agent
- ReActAgent: ReAct 模式 Agent（待实现）
- CrewAgent: Crew 编排 Agent（待实现）
"""

from loom.agents.simple import SimpleAgent

# Import future agents when implemented
try:
    from loom.agents.react_agent import ReActAgent
except ImportError:
    ReActAgent = None

__all__ = [
    "SimpleAgent",
]

# Add ReActAgent to __all__ when implemented
if ReActAgent:
    __all__.append("ReActAgent")
