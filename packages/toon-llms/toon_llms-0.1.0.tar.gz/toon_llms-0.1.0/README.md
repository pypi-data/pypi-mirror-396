# TOON (Token-Oriented Object Notation) Spec v0.1.0

TOON is a compact, human-readable serialization format designed for large language models (LLMs), reducing token usage compared to JSON.

## Data Types

- **String**: `"hello world"`
- **Number**: `42` or `3.14`
- **Boolean**: `true` / `false`
- **Null**: `null`
- **Array**: `[1, 2, 3]`
- **Object**: `{key1: value1, key2: value2}`

> Unlike JSON, TOON:
> - Omits quotes around simple keys when possible
> - Uses compact separators to reduce token count
> - Supports optional type hints for LLM embeddings

## Examples

```python
import toon_llm as toon

data = {
    "name": "Alice",
    "age": 30,
    "is_member": True,
    "preferences": ["chess", "badminton"]
}

# Serialize
toon_str = toon.dumps(data)

# Deserialize
obj = toon.loads(toon_str)
