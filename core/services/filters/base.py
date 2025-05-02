# core/services/transforms/filters/base.py
from abc import ABC, abstractmethod

class BaseTransformFilter(ABC):
    """
    """
    def __let__(self, other):
        return self.stage < other.stage
    
    stage = 0
    @abstractmethod
    def apply(self, ctx: "TransformContext"):
        pass
