"""
高级模式 - Crew 多智能体协作

v0.1.6 - 完整的多智能体协作框架

核心组件：
- Crew: 基础多智能体协作
- CrewRole: 角色定义
- SmartCoordinator: 智能任务分解
- ArtifactStore: 上下文管理
- ParallelExecutor: 并行执行
- ErrorRecovery: 容错机制
- CrewTracer: 可观测性
- CrewPresets: 预设配置
"""

# 基础 Crew
from loom.patterns.crew import (
    Crew,
    sequential_crew,
    parallel_crew,
    coordinated_crew,
)
from loom.patterns.crew_role import CrewRole

# 智能协调
from loom.patterns.coordination import (
    TaskComplexity,
    SubTask,
    TaskDecomposition,
    ComplexityAnalyzer,
    SmartCoordinator,
)

# 上下文管理
from loom.patterns.artifact_store import (
    SubAgentResult,
    ArtifactStore,
)

# 并行执行
from loom.patterns.parallel_executor import (
    ParallelConfig,
    ParallelExecutor,
    DependencyAnalyzer,
)

# 容错和恢复
from loom.patterns.error_recovery import (
    RecoveryAction,
    ErrorContext,
    RecoveryConfig,
    ErrorRecovery,
    CheckpointData,
    CheckpointManager,
)

# 可观测性和评估
from loom.patterns.observability import (
    DecisionLogEntry,
    CrewTracer,
    EvalMetrics,
    CrewEvaluator,
)

# 预设配置
from loom.patterns.presets import (
    CrewConfig,
    CrewPresets,
)

__all__ = [
    # 基础
    "Crew",
    "CrewRole",
    "sequential_crew",
    "parallel_crew",
    "coordinated_crew",
    # 协调
    "TaskComplexity",
    "SubTask",
    "TaskDecomposition",
    "ComplexityAnalyzer",
    "SmartCoordinator",
    # 上下文
    "SubAgentResult",
    "ArtifactStore",
    # 并行
    "ParallelConfig",
    "ParallelExecutor",
    "DependencyAnalyzer",
    # 容错
    "RecoveryAction",
    "ErrorContext",
    "RecoveryConfig",
    "ErrorRecovery",
    "CheckpointData",
    "CheckpointManager",
    # 可观测性
    "DecisionLogEntry",
    "CrewTracer",
    "EvalMetrics",
    "CrewEvaluator",
    # 预设
    "CrewConfig",
    "CrewPresets",
]
