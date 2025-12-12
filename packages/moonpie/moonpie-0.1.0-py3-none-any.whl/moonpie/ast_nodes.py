from abc import ABC, abstractmethod
from typing import List, Optional, Any


class ASTNode(ABC):
    @abstractmethod
    def __repr__(self):
        pass


class Program(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


class NumberLiteral(ASTNode):
    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"


class StringLiteral(ASTNode):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return f"String({repr(self.value)})"


class BooleanLiteral(ASTNode):
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self):
        return f"Boolean({self.value})"


class NilLiteral(ASTNode):
    def __repr__(self):
        return "Nil"


class Identifier(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"


class BinaryOp(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class UnaryOp(ASTNode):
    def __init__(self, operator: str, operand: ASTNode):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


class Assignment(ASTNode):
    def __init__(self, targets: List[ASTNode], values: List[ASTNode], is_local: bool = False):
        self.targets = targets
        self.values = values
        self.is_local = is_local

    def __repr__(self):
        local_str = "local " if self.is_local else ""
        return f"Assignment({local_str}{self.targets} = {self.values})"


class TableConstructor(ASTNode):
    def __init__(self, fields: List[tuple]):
        self.fields = fields

    def __repr__(self):
        return f"Table({self.fields})"


class TableAccess(ASTNode):
    def __init__(self, table: ASTNode, key: ASTNode):
        self.table = table
        self.key = key

    def __repr__(self):
        return f"TableAccess({self.table}[{self.key}])"


class FunctionDef(ASTNode):
    def __init__(self, name: Optional[str], params: List[str], body: List[ASTNode], is_local: bool = False):
        self.name = name
        self.params = params
        self.body = body
        self.is_local = is_local

    def __repr__(self):
        name_str = self.name if self.name else "<anonymous>"
        return f"FunctionDef({name_str}, {self.params}, {len(self.body)} stmts)"


class FunctionCall(ASTNode):
    def __init__(self, function: ASTNode, args: List[ASTNode]):
        self.function = function
        self.args = args

    def __repr__(self):
        return f"FunctionCall({self.function}, {self.args})"


class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_block: List[ASTNode],
                 elseif_blocks: List[tuple] = None, else_block: List[ASTNode] = None):
        self.condition = condition
        self.then_block = then_block
        self.elseif_blocks = elseif_blocks or []
        self.else_block = else_block or []

    def __repr__(self):
        return f"IfStatement({self.condition}, then={len(self.then_block)}, elseif={len(self.elseif_blocks)}, else={len(self.else_block)})"


class WhileStatement(ASTNode):
    def __init__(self, condition: ASTNode, body: List[ASTNode]):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileStatement({self.condition}, {len(self.body)} stmts)"


class RepeatStatement(ASTNode):
    def __init__(self, body: List[ASTNode], condition: ASTNode):
        self.body = body
        self.condition = condition

    def __repr__(self):
        return f"RepeatStatement({len(self.body)} stmts, until {self.condition})"


class ForStatement(ASTNode):
    def __init__(self, var: str, start: ASTNode, end: ASTNode, step: Optional[ASTNode], body: List[ASTNode]):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body

    def __repr__(self):
        return f"ForStatement({self.var}, {self.start}, {self.end}, {self.step}, {len(self.body)} stmts)"


class ForInStatement(ASTNode):
    def __init__(self, vars: List[str], iterator: ASTNode, body: List[ASTNode]):
        self.vars = vars
        self.iterator = iterator
        self.body = body

    def __repr__(self):
        return f"ForInStatement({self.vars} in {self.iterator}, {len(self.body)} stmts)"


class ReturnStatement(ASTNode):
    def __init__(self, values: List[ASTNode]):
        self.values = values

    def __repr__(self):
        return f"ReturnStatement({self.values})"


class BreakStatement(ASTNode):
    def __repr__(self):
        return "BreakStatement"
