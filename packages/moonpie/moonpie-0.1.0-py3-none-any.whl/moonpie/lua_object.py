from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable


class LuaValue(ABC):
    @abstractmethod
    def to_str(self):
        pass

    @abstractmethod
    def is_truthy(self):
        pass

    def to_number(self):
        raise TypeError(f"Cannot convert {type(self).__name__} to number")


class LuaNil(LuaValue):
    def to_str(self):
        return "nil"

    def is_truthy(self):
        return False

    def __repr__(self):
        return "nil"


class LuaBoolean(LuaValue):
    def __init__(self, value: bool):
        self.value = value

    def to_str(self):
        return "true" if self.value else "false"

    def is_truthy(self):
        return self.value

    def __repr__(self):
        return str(self.value).lower()


class LuaNumber(LuaValue):
    def __init__(self, value: float):
        self.value = value

    def to_str(self):
        if self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)

    def is_truthy(self):
        return True

    def to_number(self):
        return self.value

    def __repr__(self):
        return self.to_str()


class LuaString(LuaValue):
    def __init__(self, value: str):
        self.value = value

    def to_str(self):
        return self.value

    def is_truthy(self):
        return True

    def to_number(self):
        try:
            return float(self.value)
        except ValueError:
            raise TypeError(f"Cannot convert string '{self.value}' to number")

    def __repr__(self):
        return f'"{self.value}"'


class LuaTable(LuaValue):
    def __init__(self):
        self.array_part: List[LuaValue] = []
        self.hash_part: Dict[str, LuaValue] = {}

    def set(self, key: LuaValue, value: LuaValue):
        if isinstance(key, LuaNumber):
            idx = int(key.value)
            if idx > 0 and idx == key.value:
                while len(self.array_part) < idx:
                    self.array_part.append(LuaNil())
                self.array_part[idx - 1] = value
                return

        key_str = key.to_str()
        if isinstance(value, LuaNil):
            self.hash_part.pop(key_str, None)
        else:
            self.hash_part[key_str] = value

    def get(self, key: LuaValue):
        if isinstance(key, LuaNumber):
            idx = int(key.value)
            if idx > 0 and idx == key.value and idx <= len(self.array_part):
                return self.array_part[idx - 1]

        key_str = key.to_str()
        return self.hash_part.get(key_str, LuaNil())

    def length(self):
        return len(self.array_part)

    def to_str(self):
        return f"table: {id(self)}"

    def is_truthy(self):
        return True

    def __repr__(self):
        items = []
        for i, val in enumerate(self.array_part, 1):
            items.append(f"[{i}]={repr(val)}")
        for key, val in self.hash_part.items():
            items.append(f"{key}={repr(val)}")
        return "{" + ", ".join(items) + "}"


class LuaFunction(LuaValue):
    def __init__(self, params: List[str], body, env, is_builtin=False):
        self.params = params
        self.body = body
        self.closure_env = env
        self.is_builtin = is_builtin

    def to_str(self):
        return f"function: {id(self)}"

    def is_truthy(self):
        return True

    def __repr__(self):
        return f"<function>"


class BreakException(Exception):
    pass


class ReturnException(Exception):
    def __init__(self, values: List[LuaValue]):
        self.values = values


class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.vars: Dict[str, LuaValue] = {}

    def define(self, name: str, value: LuaValue):
        self.vars[name] = value

    def get(self, name: str):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        return LuaNil()

    def set(self, name: str, value: LuaValue):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent and self.parent.exists(name):
            self.parent.set(name, value)
        else:
            self.vars[name] = value

    def exists(self, name: str):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False
