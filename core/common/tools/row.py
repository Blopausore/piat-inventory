import pandas as pd

def get_value_mapped(row, field_name, mapping):
    possible_columns = mapping.get(field_name, [])
    for col in possible_columns:
        if col in row:
            
            if type(row[col]) in {int, float} and pd.isna(row[col]):
                return None
            return row[col]
    return None


def is_fully_invalid_row(row):
    return all(pd.isna(value) for value in row.values)

def is_duplicate_object(obj, fields=None):
    """
    Check if an object already exists in database based on selected fields.
    
    Args:
        obj: Django model instance (not yet saved)
        fields: list of field names to check uniqueness (default : Meta.unique_together)
        
    Returns:
        bool
    """
    if fields is None:
        # Try to detect fields from Meta.unique_together
        meta = getattr(obj._meta, 'unique_together', None)
        if meta:
            # Django allows multiple unique_together groups, take the first
            fields = meta[0]
        else:
            raise ValueError("No fields provided and no unique_together defined in Meta.")

    filter_kwargs = {field: getattr(obj, field) for field in fields}
    return obj.__class__.objects.filter(**filter_kwargs).exists()