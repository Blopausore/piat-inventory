# core/services/filters/context.py
from django.db.models import Field

class TransformContext:
    def __init__(self, raw, model_class):
        self.raw = raw
        self.order = None
        self.error = None
        self.model_class = model_class
        fields = [
            f.name
            for f in model_class._meta.get_fields()
            if isinstance(f, Field) and f.concrete and not f.auto_created
        ]        
        self.attrs = {f: None for f in fields}

    def instantiate_order(self):
        self.order = self.model_class(raw=self.raw, **self.attrs)
