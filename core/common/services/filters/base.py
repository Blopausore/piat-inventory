from abc import ABC, abstractmethod
from enum import IntEnum

from core.common.services.filters.context import FilterContext


class BaseTransformFilter(ABC):
    class FilterLevel(IntEnum):
        """
        Zero stage :
            Nothing has been done, only init.
            
        First stage :
            The field of attrs have been initialized 
            thanks to the field of the 'Model'
            ctx.attrs = dict(str, None)
        
        Second stage : 
            With the help of a mapping, the field 
            have been completed just has they are 
            in raw
            ctx.attrs : dict(str, str)
            
        Third stage :
            The field have been converted accorded
            to their type define in the 'Model'
            ctx.attrs : dict(str, any)
        
        Fourth stage : 
            The field that needed any type of validation
            has been fulfilled.
            Validate the attribute
        
        """
        ZERO_STAGE      = 0
        FIRST_STAGE     = 10
        SECOND_STAGE    = 20
        THIRD_STAGE     = 30
        FOURTH_STAGE    = 40
        
    def __let__(self, other):
        return self.stage < other.stage
    
    stage = FilterLevel.ZERO_STAGE
    @abstractmethod
    def apply(self, ctx: FilterContext) -> bool:
        pass
