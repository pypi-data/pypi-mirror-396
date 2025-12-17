from .types import Bool

def dumps(obj: dict, schema):
    parts = []
    for name, field in schema.fields.items():
        val = obj[name]
        if isinstance(field, Bool):
            val = int(val)
        parts.append(f"{field.id}={val}")
    return ";".join(parts)
