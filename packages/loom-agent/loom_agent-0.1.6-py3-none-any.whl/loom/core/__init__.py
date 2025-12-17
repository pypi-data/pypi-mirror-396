"""
Loom Core - 核心组件

核心模块：
- Message: 统一消息
- BaseAgent: Agent 协议
- AgentExecutor: 执行引擎
- ContextManager: Context 管理
- Events: 事件系统
- Errors: 错误处理
"""

from loom.core.message import Message
from loom.core.base_agent import (
    BaseAgent,
    create_agent,
    is_agent,
    validate_agent,
)
from loom.core.executor import AgentExecutor
from loom.core.context import ContextManager, create_context_manager
from loom.core.events import AgentEvent, AgentEventType
from loom.core.errors import (
    LoomError,
    AgentError,
    ExecutionError,
    ToolError,
    RecursionError,
    ContextError,
    CompressionError,
    MemoryError,
    LLMError,
    ValidationError,
    ConfigurationError,
)

__all__ = [
    # Message
    "Message",
    # Agent
    "BaseAgent",
    "create_agent",
    "is_agent",
    "validate_agent",
    # Executor
    "AgentExecutor",
    # Context
    "ContextManager",
    "create_context_manager",
    # Events
    "AgentEvent",
    "AgentEventType",
    # Errors
    "LoomError",
    "AgentError",
    "ExecutionError",
    "ToolError",
    "RecursionError",
    "ContextError",
    "CompressionError",
    "MemoryError",
    "LLMError",
    "ValidationError",
    "ConfigurationError",
]
