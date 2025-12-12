from .lua_object import *
import math


def builtin_print(*args):
    output = ' '.join(arg.to_str() for arg in args)
    print(output)
    return LuaNil()


def builtin_type(*args):
    if not args:
        return LuaString("nil")

    arg = args[0]
    if isinstance(arg, LuaNil):
        return LuaString("nil")
    elif isinstance(arg, LuaBoolean):
        return LuaString("boolean")
    elif isinstance(arg, LuaNumber):
        return LuaString("number")
    elif isinstance(arg, LuaString):
        return LuaString("string")
    elif isinstance(arg, LuaTable):
        return LuaString("table")
    elif isinstance(arg, LuaFunction):
        return LuaString("function")
    return LuaString("unknown")


def builtin_tonumber(*args):
    if not args:
        return LuaNil()

    arg = args[0]
    try:
        if isinstance(arg, LuaNumber):
            return arg
        elif isinstance(arg, LuaString):
            return LuaNumber(float(arg.value))
    except:
        pass
    return LuaNil()


def builtin_tostring(*args):
    if not args:
        return LuaString("nil")
    return LuaString(args[0].to_str())


def builtin_assert(*args):
    if not args or not args[0].is_truthy():
        msg = args[1].to_str() if len(args) > 1 else "assertion failed!"
        raise RuntimeError(msg)
    return args[0]


def builtin_error(*args):
    msg = args[0].to_str() if args else "error"
    raise RuntimeError(msg)


def builtin_ipairs(*args):
    if not args or not isinstance(args[0], LuaTable):
        return LuaNil()

    table = args[0]
    return LuaTable()


def builtin_pairs(*args):
    if not args or not isinstance(args[0], LuaTable):
        return LuaNil()

    table = args[0]
    return LuaTable()


def builtin_math_abs(*args):
    if args and isinstance(args[0], LuaNumber):
        return LuaNumber(abs(args[0].value))
    return LuaNil()


def builtin_math_floor(*args):
    if args and isinstance(args[0], LuaNumber):
        return LuaNumber(math.floor(args[0].value))
    return LuaNil()


def builtin_math_ceil(*args):
    if args and isinstance(args[0], LuaNumber):
        return LuaNumber(math.ceil(args[0].value))
    return LuaNil()


def builtin_math_sqrt(*args):
    if args and isinstance(args[0], LuaNumber):
        return LuaNumber(math.sqrt(args[0].value))
    return LuaNil()


def builtin_math_sin(*args):
    if args and isinstance(args[0], LuaNumber):
        return LuaNumber(math.sin(args[0].value))
    return LuaNil()


def builtin_math_cos(*args):
    if args and isinstance(args[0], LuaNumber):
        return LuaNumber(math.cos(args[0].value))
    return LuaNil()


def builtin_math_tan(*args):
    if args and isinstance(args[0], LuaNumber):
        return LuaNumber(math.tan(args[0].value))
    return LuaNil()


def builtin_math_max(*args):
    if not args:
        return LuaNil()
    max_val = args[0].to_number()
    for arg in args[1:]:
        max_val = max(max_val, arg.to_number())
    return LuaNumber(max_val)


def builtin_math_min(*args):
    if not args:
        return LuaNil()
    min_val = args[0].to_number()
    for arg in args[1:]:
        min_val = min(min_val, arg.to_number())
    return LuaNumber(min_val)


def builtin_string_len(*args):
    if args and isinstance(args[0], LuaString):
        return LuaNumber(len(args[0].value))
    return LuaNil()


def builtin_string_upper(*args):
    if args and isinstance(args[0], LuaString):
        return LuaString(args[0].value.upper())
    return LuaNil()


def builtin_string_lower(*args):
    if args and isinstance(args[0], LuaString):
        return LuaString(args[0].value.lower())
    return LuaNil()


def builtin_string_sub(*args):
    if not args or not isinstance(args[0], LuaString):
        return LuaNil()

    s = args[0].value
    start = int(args[1].to_number()) if len(args) > 1 else 1
    end = int(args[2].to_number()) if len(args) > 2 else len(s)

    if start < 0:
        start = len(s) + start + 1
    if end < 0:
        end = len(s) + end + 1

    start = max(1, start) - 1
    end = max(0, end)

    return LuaString(s[start:end])


def setup_builtins(env: Environment):
    env.define("print", LuaFunction([], builtin_print, env, is_builtin=True))
    env.define("type", LuaFunction([], builtin_type, env, is_builtin=True))
    env.define("tonumber", LuaFunction([], builtin_tonumber, env, is_builtin=True))
    env.define("tostring", LuaFunction([], builtin_tostring, env, is_builtin=True))
    env.define("assert", LuaFunction([], builtin_assert, env, is_builtin=True))
    env.define("error", LuaFunction([], builtin_error, env, is_builtin=True))
    env.define("ipairs", LuaFunction([], builtin_ipairs, env, is_builtin=True))
    env.define("pairs", LuaFunction([], builtin_pairs, env, is_builtin=True))

    math_table = LuaTable()
    math_table.set(LuaString("abs"), LuaFunction([], builtin_math_abs, env, is_builtin=True))
    math_table.set(LuaString("floor"), LuaFunction([], builtin_math_floor, env, is_builtin=True))
    math_table.set(LuaString("ceil"), LuaFunction([], builtin_math_ceil, env, is_builtin=True))
    math_table.set(LuaString("sqrt"), LuaFunction([], builtin_math_sqrt, env, is_builtin=True))
    math_table.set(LuaString("sin"), LuaFunction([], builtin_math_sin, env, is_builtin=True))
    math_table.set(LuaString("cos"), LuaFunction([], builtin_math_cos, env, is_builtin=True))
    math_table.set(LuaString("tan"), LuaFunction([], builtin_math_tan, env, is_builtin=True))
    math_table.set(LuaString("max"), LuaFunction([], builtin_math_max, env, is_builtin=True))
    math_table.set(LuaString("min"), LuaFunction([], builtin_math_min, env, is_builtin=True))
    math_table.set(LuaString("pi"), LuaNumber(math.pi))
    env.define("math", math_table)

    string_table = LuaTable()
    string_table.set(LuaString("len"), LuaFunction([], builtin_string_len, env, is_builtin=True))
    string_table.set(LuaString("upper"), LuaFunction([], builtin_string_upper, env, is_builtin=True))
    string_table.set(LuaString("lower"), LuaFunction([], builtin_string_lower, env, is_builtin=True))
    string_table.set(LuaString("sub"), LuaFunction([], builtin_string_sub, env, is_builtin=True))
    env.define("string", string_table)
