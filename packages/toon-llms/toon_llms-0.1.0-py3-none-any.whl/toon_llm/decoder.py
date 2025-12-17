def loads(s: str, schema):
    out = {}
    for part in s.split(";"):
        k, v = part.split("=")
        name = schema.id_to_name[int(k)]
        out[name] = v
    return out
