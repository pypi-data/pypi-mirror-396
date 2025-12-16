"""
Minimal scheduler placeholder for overlapping compute and copies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ExecutionPlan:
    ops: List[Any] = field(default_factory=list)
    description: str = ""


class Scheduler:
    """
    Placeholder scheduler. Will later manage queues/events for overlap.
    """

    def __init__(self) -> None:
        self.plans: List[ExecutionPlan] = []

    def submit(self, op: Any, plan: Optional[ExecutionPlan] = None) -> None:
        if plan is None:
            plan = ExecutionPlan()
        plan.ops.append(op)
        self.plans.append(plan)

    def run(self) -> None:
        # Placeholder: execute ops sequentially; to be replaced with queue dispatch.
        for plan in self.plans:
            for op in plan.ops:
                if callable(op):
                    op()
