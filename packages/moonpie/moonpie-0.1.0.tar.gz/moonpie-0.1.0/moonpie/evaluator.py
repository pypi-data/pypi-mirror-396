from .ast_nodes import *
from .lua_object import *
from typing import List


class Evaluator:
    def __init__(self, env: Environment):
        self.env = env

    def eval(self, node: ASTNode, env: Environment = None) -> LuaValue:
        if env is None:
            env = self.env

        if isinstance(node, Program):
            return self.eval_program(node, env)

        elif isinstance(node, NumberLiteral):
            return LuaNumber(node.value)

        elif isinstance(node, StringLiteral):
            return LuaString(node.value)

        elif isinstance(node, BooleanLiteral):
            return LuaBoolean(node.value)

        elif isinstance(node, NilLiteral):
            return LuaNil()

        elif isinstance(node, Identifier):
            return env.get(node.name)

        elif isinstance(node, BinaryOp):
            return self.eval_binary_op(node, env)

        elif isinstance(node, UnaryOp):
            return self.eval_unary_op(node, env)

        elif isinstance(node, Assignment):
            return self.eval_assignment(node, env)

        elif isinstance(node, TableConstructor):
            return self.eval_table(node, env)

        elif isinstance(node, TableAccess):
            return self.eval_table_access(node, env)

        elif isinstance(node, FunctionDef):
            return self.eval_function_def(node, env)

        elif isinstance(node, FunctionCall):
            return self.eval_function_call(node, env)

        elif isinstance(node, IfStatement):
            return self.eval_if(node, env)

        elif isinstance(node, WhileStatement):
            return self.eval_while(node, env)

        elif isinstance(node, RepeatStatement):
            return self.eval_repeat(node, env)

        elif isinstance(node, ForStatement):
            return self.eval_for(node, env)

        elif isinstance(node, ForInStatement):
            return self.eval_for_in(node, env)

        elif isinstance(node, ReturnStatement):
            values = [self.eval(val, env) for val in node.values]
            raise ReturnException(values)

        elif isinstance(node, BreakStatement):
            raise BreakException()

        return LuaNil()

    def eval_program(self, program: Program, env: Environment) -> LuaValue:
        result = LuaNil()
        for stmt in program.statements:
            result = self.eval(stmt, env)
        return result

    def eval_binary_op(self, node: BinaryOp, env: Environment) -> LuaValue:
        left = self.eval(node.left, env)
        right = self.eval(node.right, env)
        op = node.operator

        if op == '+':
            return LuaNumber(left.to_number() + right.to_number())
        elif op == '-':
            return LuaNumber(left.to_number() - right.to_number())
        elif op == '*':
            return LuaNumber(left.to_number() * right.to_number())
        elif op == '/':
            return LuaNumber(left.to_number() / right.to_number())
        elif op == '%':
            return LuaNumber(left.to_number() % right.to_number())
        elif op == '^':
            return LuaNumber(left.to_number() ** right.to_number())
        elif op == '..':
            return LuaString(left.to_str() + right.to_str())
        elif op == '==':
            return LuaBoolean(self.lua_equals(left, right))
        elif op == '~=':
            return LuaBoolean(not self.lua_equals(left, right))
        elif op == '<':
            return LuaBoolean(left.to_number() < right.to_number())
        elif op == '<=':
            return LuaBoolean(left.to_number() <= right.to_number())
        elif op == '>':
            return LuaBoolean(left.to_number() > right.to_number())
        elif op == '>=':
            return LuaBoolean(left.to_number() >= right.to_number())
        elif op == 'and':
            return right if left.is_truthy() else left
        elif op == 'or':
            return left if left.is_truthy() else right

        return LuaNil()

    def eval_unary_op(self, node: UnaryOp, env: Environment) -> LuaValue:
        operand = self.eval(node.operand, env)
        op = node.operator

        if op == '-':
            return LuaNumber(-operand.to_number())
        elif op == 'not':
            return LuaBoolean(not operand.is_truthy())
        elif op == '#':
            if isinstance(operand, LuaTable):
                return LuaNumber(operand.length())
            elif isinstance(operand, LuaString):
                return LuaNumber(len(operand.value))
            return LuaNumber(0)

        return LuaNil()

    def eval_assignment(self, node: Assignment, env: Environment) -> LuaValue:
        values = [self.eval(val, env) for val in node.values]

        while len(values) < len(node.targets):
            values.append(LuaNil())

        for i, target in enumerate(node.targets):
            value = values[i] if i < len(values) else LuaNil()

            if isinstance(target, Identifier):
                if node.is_local:
                    env.define(target.name, value)
                else:
                    env.set(target.name, value)

            elif isinstance(target, TableAccess):
                table = self.eval(target.table, env)
                if isinstance(table, LuaTable):
                    key = self.eval(target.key, env)
                    table.set(key, value)

        return values[0] if values else LuaNil()

    def eval_table(self, node: TableConstructor, env: Environment) -> LuaTable:
        table = LuaTable()
        array_index = 1

        for key, value in node.fields:
            val = self.eval(value, env)
            if key is None:
                table.set(LuaNumber(array_index), val)
                array_index += 1
            else:
                k = self.eval(key, env)
                table.set(k, val)

        return table

    def eval_table_access(self, node: TableAccess, env: Environment) -> LuaValue:
        table = self.eval(node.table, env)
        if isinstance(table, LuaTable):
            key = self.eval(node.key, env)
            return table.get(key)
        return LuaNil()

    def eval_function_def(self, node: FunctionDef, env: Environment) -> LuaValue:
        func = LuaFunction(node.params, node.body, env)

        if node.name:
            if node.is_local:
                env.define(node.name, func)
            else:
                env.set(node.name, func)

        return func

    def eval_function_call(self, node: FunctionCall, env: Environment) -> LuaValue:
        func = self.eval(node.function, env)

        if not isinstance(func, LuaFunction):
            raise TypeError(f"Attempt to call a {type(func).__name__} value")

        args = [self.eval(arg, env) for arg in node.args]

        if func.is_builtin:
            return func.body(*args)

        func_env = Environment(func.closure_env)

        for i, param in enumerate(func.params):
            value = args[i] if i < len(args) else LuaNil()
            func_env.define(param, value)

        try:
            for stmt in func.body:
                self.eval(stmt, func_env)
        except ReturnException as ret:
            return ret.values[0] if ret.values else LuaNil()

        return LuaNil()

    def eval_if(self, node: IfStatement, env: Environment) -> LuaValue:
        condition = self.eval(node.condition, env)

        if condition.is_truthy():
            return self.eval_block(node.then_block, env)

        for elseif_cond, elseif_body in node.elseif_blocks:
            cond = self.eval(elseif_cond, env)
            if cond.is_truthy():
                return self.eval_block(elseif_body, env)

        if node.else_block:
            return self.eval_block(node.else_block, env)

        return LuaNil()

    def eval_while(self, node: WhileStatement, env: Environment) -> LuaValue:
        try:
            while True:
                condition = self.eval(node.condition, env)
                if not condition.is_truthy():
                    break
                try:
                    self.eval_block(node.body, env)
                except BreakException:
                    break
        except ReturnException:
            raise

        return LuaNil()

    def eval_repeat(self, node: RepeatStatement, env: Environment) -> LuaValue:
        try:
            while True:
                try:
                    self.eval_block(node.body, env)
                except BreakException:
                    break
                condition = self.eval(node.condition, env)
                if condition.is_truthy():
                    break
        except ReturnException:
            raise

        return LuaNil()

    def eval_for(self, node: ForStatement, env: Environment) -> LuaValue:
        start = self.eval(node.start, env).to_number()
        end = self.eval(node.end, env).to_number()
        step = self.eval(node.step, env).to_number() if node.step else 1.0

        loop_env = Environment(env)

        try:
            i = start
            if step > 0:
                while i <= end:
                    loop_env.define(node.var, LuaNumber(i))
                    try:
                        self.eval_block(node.body, loop_env)
                    except BreakException:
                        break
                    i += step
            else:
                while i >= end:
                    loop_env.define(node.var, LuaNumber(i))
                    try:
                        self.eval_block(node.body, loop_env)
                    except BreakException:
                        break
                    i += step
        except ReturnException:
            raise

        return LuaNil()

    def eval_for_in(self, node: ForInStatement, env: Environment) -> LuaValue:
        iterator_val = self.eval(node.iterator, env)

        if isinstance(iterator_val, LuaTable):
            loop_env = Environment(env)

            try:
                for i in range(iterator_val.length()):
                    val = iterator_val.get(LuaNumber(i + 1))
                    if len(node.vars) >= 1:
                        loop_env.define(node.vars[0], LuaNumber(i + 1))
                    if len(node.vars) >= 2:
                        loop_env.define(node.vars[1], val)

                    try:
                        self.eval_block(node.body, loop_env)
                    except BreakException:
                        break
            except ReturnException:
                raise

        return LuaNil()

    def eval_block(self, statements: List[ASTNode], env: Environment) -> LuaValue:
        result = LuaNil()
        for stmt in statements:
            result = self.eval(stmt, env)
        return result

    def lua_equals(self, left: LuaValue, right: LuaValue) -> bool:
        if type(left) != type(right):
            return False

        if isinstance(left, LuaNil):
            return True
        elif isinstance(left, LuaBoolean):
            return left.value == right.value
        elif isinstance(left, LuaNumber):
            return left.value == right.value
        elif isinstance(left, LuaString):
            return left.value == right.value
        elif isinstance(left, (LuaTable, LuaFunction)):
            return left is right

        return False
