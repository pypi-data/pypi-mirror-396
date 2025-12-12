from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    EOF = auto()
    ILLEGAL = auto()

    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    NIL = auto()
    TRUE = auto()
    FALSE = auto()

    AND = auto()
    OR = auto()
    NOT = auto()

    IF = auto()
    THEN = auto()
    ELSEIF = auto()
    ELSE = auto()
    END = auto()

    WHILE = auto()
    DO = auto()
    REPEAT = auto()
    UNTIL = auto()
    FOR = auto()
    IN = auto()

    FUNCTION = auto()
    LOCAL = auto()
    RETURN = auto()
    BREAK = auto()

    PLUS = auto()
    MINUS = auto()
    ASTERISK = auto()
    SLASH = auto()
    PERCENT = auto()
    POWER = auto()

    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    ASSIGN = auto()
    CONCAT = auto()
    LENGTH = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()

    COMMA = auto()
    SEMICOLON = auto()
    DOT = auto()
    COLON = auto()
    DOUBLEDOT = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int = 1
    column: int = 1

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"
