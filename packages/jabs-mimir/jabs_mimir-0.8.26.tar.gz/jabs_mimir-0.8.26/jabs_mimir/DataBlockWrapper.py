"""
DataBlockWrapper: A flexible wrapper for structured UI data blocks.
"""

class DataBlockWrapper:
    def __init__(self, meta):
        self._meta = meta

    @property
    def meta(self):
        return self._meta

    def __getattr__(self, key):
        fields = self._meta.get("fields_by_key", {})
        if key in fields:
            return fields[key]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def get(self, key):
        return self._meta.get("fields_by_key", {}).get(key)

    def set(self, key, value):
        try:
            variable = self._meta["fields_by_key"][key]
            if hasattr(variable, "set"):
                variable.set(value)
            else:
                self._meta["fields_by_key"][key] = value
        except KeyError:
            raise KeyError(f"Key '{key}' not found in DataBlockWrapper.")

    def items(self):
        return self._meta.get("fields_by_key", {}).items()

    def values(self):
        return self._meta.get("fields_by_key", {}).values()

    def keys(self):
        return self._meta.get("fields_by_key", {}).keys()
    
    def getValues(self):
        return [value.get() if hasattr(value, "get") else value for value in self._meta.get("fields_by_key", {}).values()]
    
    def has(self, key):
        return key in self.meta.get("fields_by_key", {})

    def __dir__(self):
        return super().__dir__() + list(self._meta.get("fields_by_key", {}).keys())
