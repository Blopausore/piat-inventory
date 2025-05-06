from django.db.models import Field


class FilterContext:
    def __init__(self, raw, model_class):
        self.raw = raw
        self.order = None
        self.error = None
        self._model_class = model_class
        fields = [
            f.name
            for f in model_class._meta.get_fields()
            if isinstance(f, Field) and f.concrete and not f.auto_created
        ]        
        self._attrs = {f: None for f in fields}

    @property
    def attrs(self):
        return self._attrs
    
    @property
    def model_class(self):
        return self._model_class
    
    
    def instantiate_order(self):
        self._attrs['raw'] = self.raw
        self.order = self.model_class(**self.attrs)


