import toon_llm as toon

def test_roundtrip():
    schema = toon.Schema({
        "name": toon.Str(1),
        "age": toon.Int(2),
        "active": toon.Bool(3)
    })

    data = {"name": "Sai", "age": 25, "active": True}
    s = toon.dumps(data, schema=schema)
    out = toon.loads(s, schema=schema)

    assert out["name"] == "Sai"
    assert int(out["age"]) == 25
    assert int(out["active"]) == 1
