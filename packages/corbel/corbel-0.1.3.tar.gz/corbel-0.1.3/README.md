# Corbel

Corbel is a Python dataclass extension library providing **mixins and utilities** for:

- Validation
- Comparison and hashing
- Copying and updating
- Serialization to/from dicts and JSON
- Property-level metadata (`@corbel_property`)
- Protocol-based hooks for validation, serialization, and deserialization

---

## Installation

```base
pip install corbel
```

---

## Core Mixins

### 1. Corbel

The base mixin that provides:

- Cached `asdict` results
- Field and property introspection
- Hook methods for updates and validation

```python
from corbel import dataclass
from corbel import Corbel, field

@dataclass
class Base(Corbel):
    x: int = field()
    y: str = field()

inst = Base(1, "hello")
print(inst.asdict())  # {'x': 1, 'y': 'hello'}
```

---

### 2. Serializable

Provides `to_dict`, `from_dict`, `to_json`, `from_json` for dataclasses.

- Supports nested dataclasses
- Optional wrapper key for JSON (`__json_wrapper__`)
- Configurable inclusion rules (`__inclusion__`)

```python
from corbel import dataclass
from corbel import Serializable, field, Include

@dataclass
class User(Serializable):
    id: int = field()
    name: str = field()
    email: str | None = field(default=None)

user = User(1, "Alice")
print(user.to_dict())  # {'id': 1, 'name': 'Alice', 'email': None}
alice = User.from_dict({"id": 1, "name": "Alice", "email": None})

# JSON with wrapper
print(user.to_json(wrapper="user"))  # {"user": {"id":1,"name":"Alice","email":null}}
alice = User.from_json('{"user": {"id":1,"name":"Alice","email":null}', wrapper="user")

# Custom class-level JSON wrapper
@dataclass
class WrappedUser(Serializable):
    __json_wrapper__ = "account"
    id: int = field()
    name: str = field()

u = WrappedUser(5, "Bob")
print(u.to_json())  # {"account": {"id":5,"name":"Bob"}}

# Using inclusion rules
@dataclass
class PartialUser(Serializable):
    __inclusion__ = Include.NON_NONE
    id: int = field()
    name: str = field()
    email: str | None = field(default=None)

pu = PartialUser(1, "Alice")
print(pu.to_dict())  # {'id': 1, 'name': 'Alice'}  # email omitted
```

---

### 3. Updatable

Provides immutable-style updates:

- `copy()`: shallow copy
- `update(**kwargs)`: returns a new instance with updated fields
- `batch_update()`: context manager to temporarily disable validation

```python
from corbel import dataclass
from corbel import Updatable, field

@dataclass
class Point(Updatable):
    x: int = field()
    y: int = field()

p1 = Point(1, 2)
p2 = p1.update(x=10)  # new instance
print(p1.asdict())    # {'x': 1, 'y': 2}
print(p2.asdict())    # {'x': 10, 'y': 2}

# batch update
with p2.batch_update() as temp:
    temp.x = 20
    temp.y = 30
print(p2.asdict())  # {'x': 10, 'y': 2}, p2 unchanged
```

---

### 4. Validated

Automatically validates fields on initialization and update:

- Define a `validator` in `field()` metadata
- Supports `allow_none=True`
- Raises `ValidationError` on failure

```python
from corbel import dataclass
from corbel import Validated, field, ValidationError

def positive(value: int) -> bool:
    return value > 0

@dataclass
class BankAccount(Validated):
    balance: int = field(validator=positive)

try:
    acct = BankAccount(-10)  # raises ValidationError
except ValidationError as e:
    print(e)

acct = BankAccount(100)
acct.balance = -50  # raises ValidationError
```

---

### 5. Hashable

Caches a hash based on dataclass fields:

- Automatically invalidates on field update
- Suitable for dict keys and set members

```python
from corbel import dataclass
from corbel import Hashable, field

@dataclass
class Coord(Hashable):
    x: int = field()
    y: int = field()

c1 = Coord(1, 2)
c2 = Coord(1, 2)

print(hash(c1) == hash(c2))  # True
c1.x = 3
print(hash(c1) == hash(c2))  # False
```

---

### 6. Comparable

Provides `<`, `<=`, `>`, `>=`, `==` based on field values:

- Lexicographic comparison of fields
- Supports total ordering

```python
from corbel import dataclass
from corbel import Comparable, field

@dataclass
class Version(Comparable):
    major: int = field()
    minor: int = field()

v1 = Version(1, 0)
v2 = Version(1, 1)
print(v1 < v2)  # True
print(v1 == v2) # False
```

---

### 7. @corbel_property

Custom property decorator supporting:

- `validator`
- `serializer` / `deserializer`
- `allow_none` / `ignore`

```python
from corbel import dataclass
from corbel import Corbel, corbel_property, field

def positive(x: int) -> bool:
    return x > 0

@dataclass
class Example(Corbel):
    _value: int = field()

    @corbel_property(validator=lambda v: positive(v))
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, val: int) -> None:
        self._value = val

ex = Example(5)
print(ex.value)  # 5
ex.value = 10    # OK
# ex.value = -1  # Raises ValueError
```

---

### 8. Protocol Examples

#### ValidatorProtocol

```python
from typing import Any

def positive_validator(value: int) -> bool:
    return value > 0

print(positive_validator(5))   # True
print(positive_validator(-1))  # False
```

#### SerializerProtocol

```python
from typing import Any

def uppercase_serializer(value: Any) -> Any:
    if isinstance(value, str):
        return value.upper()
    return value

print(uppercase_serializer("hello"))  # "HELLO"
```

#### DeserializerProtocol

```python
from typing import Any

def deserialize_int(value: Any, type_hint: int) -> int:
    if type_hint == int and isinstance(value, str):
        return int(value)
    return value

print(deserialize_int("42", int))  # 42
```

---

### 9. Combining Mixins

Mixins can be combined for full-featured dataclasses:

```python
from corbel import dataclass
from corbel import Serializable, Updatable, Validated, Hashable, Comparable, field, corbel_property

@dataclass
class Product(Serializable, Updatable, Validated, Hashable, Comparable):
    name: str = field()
    price: float = field()

    @corbel_property()
    def discounted_price(self) -> float:
        return self.price * 0.9

prod = Product("Widget", 100)
prod2 = prod.update(price=120)
print(prod.to_dict())  # {'name': 'Widget', 'price': 100}
print(prod2.discounted_price)  # 108.0
```

---

## Utilities

- `asdict(obj, include_private=False)`: convert instance to dict
- `field(**kwargs)`: wrapper for dataclass fields with Corbel metadata
- `fields(obj)`: returns dataclass fields
- `Include` enum: `ALWAYS`, `NON_NONE`, `NON_EMPTY`, `NON_DEFAULT`
- Exceptions: `ValidationError`, `DeserializeError`, `InclusionError`, `CorbelError`
- Class-level options for Serializable:  
  - `__json_wrapper__` – wrap the JSON output under a key  
  - `__inclusion__` – control which fields are included

---

## License

MIT License. See [LICENSE](https://github.com/bnlucas/corbel/blob/main/LICENSE).
