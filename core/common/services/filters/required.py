import pandas as pd
from django.db.models import Field
from core.common.services.filters.base import BaseTransformFilter

class RequiredFieldFilter(BaseTransformFilter):
    
    def apply(self, ctx):
        missing = []
        if all(pd.isna(value) for value in ctx.attrs.values()):
            ctx.error = f"Row is empty"
            return False
        
        # Check required field
        for f in ctx.model_class._meta.get_fields():
            if not isinstance(f, Field) or not f.concrete or f.auto_created:
                continue
            if f.name == 'raw':
                continue
            if not getattr(f, 'null', False) and not getattr(f, 'blank', False):
                val = ctx.attrs.get(f.name)
                if val in (None, ''):
                    missing.append(f.name)
        if missing:
            ctx.error = f"Required field missing : {', '.join(sorted(missing))}"
            return False
        return True