"""
UtilityModule: Reusable utilities for working with AbstractMimir and DataBlockWrapper.
"""

class UtilityModule:
    @staticmethod
    def buildBlockMeta(fields, **extra):
        """
        Given a list of field definitions, return a structured metadata dictionary
        ready to be passed to DataBlockWrapper.

        Fields should be a list of dicts containing at least 'variable' and optionally 'key'.
        Additional metadata (e.g. label, index) can be passed via kwargs.
        """
        return {
            **extra,
            "fields": fields,
            "fields_by_key": {f["key"]: f["variable"] for f in fields if "key" in f},
        }

    @staticmethod
    def getBlockValues(wrapper, raw=False):
        """
        Extract a dictionary of current values from a DataBlockWrapper.

        If raw=True, return variable objects. Otherwise, return .get() results.
        """
        output = {}
        for key, var in wrapper.items():
            if hasattr(var, "get") and not raw:
                output[key] = var.get()
            else:
                output[key] = var
        return output

    @staticmethod
    def updateBlockFromDict(wrapper, data):
        """
        Given a dict of values, update the DataBlockWrapper by setting matching keys.
        """
        for key, value in data.items():
            try:
                wrapper.set(key, value)
            except KeyError:
                continue

    @staticmethod
    def isBlockValid(wrapper, validatorResolver):
        """
        Check if all fields in a block pass their validator.
        The validatorResolver must take a string name and return a function.
        """
        for f in wrapper.meta.get("fields", []):
            name = f.get("validation")
            var = f.get("variable")
            if name and var and callable(validatorResolver(name)):
                valid = validatorResolver(name)(var.get())
                if not valid:
                    return False
        return True