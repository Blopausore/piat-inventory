import re
import pandas as pd
from django.db.models import Field
from core.common.services.filters.base import BaseTransformFilter

class CanceledFieldFilter(BaseTransformFilter):
    """ Filter row that contains a 'canceled' key word in it.
    """
    stage = BaseTransformFilter.FilterLevel.SECOND_STAGE
    
    def apply(self, ctx):                
        for key,val in ctx.raw.data.items():
            if val == "":
                continue
            val = val.lower()
            val = re.sub('[^a-z]',"", val)
            if val in {'canceled', 'cancel', 'cancelled'}:
                ctx.error = f"Row canceled in {key} : {val}"
                return False
        return True
    
    