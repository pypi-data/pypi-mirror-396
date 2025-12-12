from .lua_token import Token, TokenType


KEYWORDS = {
    'and': TokenType.AND,
    'break': TokenType.BREAK,
    'do': TokenType.DO,
    'else': TokenType.ELSE,
    'elseif': TokenType.ELSEIF,
    'end': TokenType.END,
    'false': TokenType.FALSE,
    'for': TokenType.FOR,
    'function': TokenType.FUNCTION,
    'if': TokenType.IF,
    'in': TokenType.IN,
    'local': TokenType.LOCAL,
    'nil': TokenType.NIL,
    'not': TokenType.NOT,
    'or': TokenType.OR,
    'repeat': TokenType.REPEAT,
    'return': TokenType.RETURN,
    'then': TokenType.THEN,
    'true': TokenType.TRUE,
    'until': TokenType.UNTIL,
    'while': TokenType.WHILE,
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if source else None

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.pos += 1
        if self.pos >= len(self.source):
            self.current_char = None
        else:
            self.current_char = self.source[self.pos]

    def peek(self, offset=1):
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]

    def skip_whitespace(self):
        while self.current_char and self.current_char in ' \t\n\r':
            self.advance()

    def skip_comment(self):
        if self.current_char == '-' and self.peek() == '-':
            self.advance()
            self.advance()

            if self.current_char == '[' and self.peek() == '[':
                self.advance()
                self.advance()
                while self.current_char:
                    if self.current_char == ']' and self.peek() == ']':
                        self.advance()
                        self.advance()
                        break
                    self.advance()
            else:
                while self.current_char and self.current_char != '\n':
                    self.advance()

    def read_number(self):
        num_str = ''
        has_dot = False

        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if has_dot or (self.peek() and self.peek() == '.'):
                    break
                has_dot = True
            num_str += self.current_char
            self.advance()

        return num_str

    def read_string(self, quote):
        string_val = ''
        self.advance()

        while self.current_char and self.current_char != quote:
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    string_val += '\n'
                elif self.current_char == 't':
                    string_val += '\t'
                elif self.current_char == 'r':
                    string_val += '\r'
                elif self.current_char == '\\':
                    string_val += '\\'
                elif self.current_char == quote:
                    string_val += quote
                else:
                    string_val += self.current_char
                self.advance()
            else:
                string_val += self.current_char
                self.advance()

        if self.current_char == quote:
            self.advance()

        return string_val

    def read_identifier(self):
        id_str = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()
        return id_str

    def get_next_token(self):
        while self.current_char:
            if self.current_char in ' \t\n\r':
                self.skip_whitespace()
                continue

            if self.current_char == '-' and self.peek() == '-':
                self.skip_comment()
                continue

            line, col = self.line, self.column

            if self.current_char.isdigit():
                return Token(TokenType.NUMBER, self.read_number(), line, col)

            if self.current_char in ('"', "'"):
                quote = self.current_char
                string_val = self.read_string(quote)
                return Token(TokenType.STRING, string_val, line, col)

            if self.current_char.isalpha() or self.current_char == '_':
                id_str = self.read_identifier()
                token_type = KEYWORDS.get(id_str, TokenType.IDENTIFIER)
                return Token(token_type, id_str, line, col)

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', line, col)

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', line, col)

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.ASTERISK, '*', line, col)

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.SLASH, '/', line, col)

            if self.current_char == '%':
                self.advance()
                return Token(TokenType.PERCENT, '%', line, col)

            if self.current_char == '^':
                self.advance()
                return Token(TokenType.POWER, '^', line, col)

            if self.current_char == '#':
                self.advance()
                return Token(TokenType.LENGTH, '#', line, col)

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQ, '==', line, col)
                return Token(TokenType.ASSIGN, '=', line, col)

            if self.current_char == '~':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NE, '~=', line, col)
                return Token(TokenType.ILLEGAL, '~', line, col)

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LE, '<=', line, col)
                return Token(TokenType.LT, '<', line, col)

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GE, '>=', line, col)
                return Token(TokenType.GT, '>', line, col)

            if self.current_char == '.':
                self.advance()
                if self.current_char == '.':
                    self.advance()
                    if self.current_char == '.':
                        self.advance()
                        return Token(TokenType.DOUBLEDOT, '...', line, col)
                    return Token(TokenType.CONCAT, '..', line, col)
                return Token(TokenType.DOT, '.', line, col)

            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON, ':', line, col)

            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', line, col)

            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', line, col)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', line, col)

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', line, col)

            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', line, col)

            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', line, col)

            if self.current_char == '[':
                self.advance()
                return Token(TokenType.LBRACKET, '[', line, col)

            if self.current_char == ']':
                self.advance()
                return Token(TokenType.RBRACKET, ']', line, col)

            char = self.current_char
            self.advance()
            return Token(TokenType.ILLEGAL, char, line, col)

        return Token(TokenType.EOF, '', self.line, self.column)

    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens
