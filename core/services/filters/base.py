# core/services/transforms/filters/base.py
from abc import ABC, abstractmethod

class BaseTransformFilter(ABC):
    """
    Définit l'interface d'un filtre de transformation.
    Chaque filtre prend un contexte et l'enrichit ou le modifie.
    """
    @abstractmethod
    def apply(self, ctx: "TransformContext"):
        pass
