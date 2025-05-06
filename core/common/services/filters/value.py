import re
import pandas as pd
from django.db.models import Field
from core.common.services.filters.base import BaseTransformFilter

class ValueFieldFilter(BaseTransformFilter):
    """ Filter row a certain value.
    
    :args::
     field_name (str) : The field
    """
    ...