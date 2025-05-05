# core/services/transforms/filters/base.py
from abc import ABC, abstractmethod
from core.common.services.filters.context import TransformContext


class BaseTransformFilter(ABC):
    """
    """
    def __let__(self, other):
        return self.stage < other.stage
    
    stage = 0
    @abstractmethod
    def apply(self, ctx: TransformContext) -> bool:
        pass
