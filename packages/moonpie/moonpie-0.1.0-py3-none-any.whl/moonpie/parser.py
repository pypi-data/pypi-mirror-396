from .lua_token import Token, TokenType
from .ast_nodes import *
from typing import List, Optional


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else Token(TokenType.EOF, '', 0, 0)

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token(TokenType.EOF, '', 0, 0)

    def peek(self, offset=1):
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return Token(TokenType.EOF, '', 0, 0)

    def expect(self, token_type: TokenType):
        if self.current_token.type != token_type:
            raise SyntaxError(f"Expected {token_type.name}, got {self.current_token.type.name} at {self.current_token.line}:{self.current_token.column}")
        token = self.current_token
        self.advance()
        return token

    def match(self, *token_types):
        return self.current_token.type in token_types

    def parse(self):
        statements = []
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.SEMICOLON:
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_statement(self):
        if self.match(TokenType.LOCAL):
            return self.parse_local()
        elif self.match(TokenType.IF):
            return self.parse_if()
        elif self.match(TokenType.WHILE):
            return self.parse_while()
        elif self.match(TokenType.REPEAT):
            return self.parse_repeat()
        elif self.match(TokenType.FOR):
            return self.parse_for()
        elif self.match(TokenType.FUNCTION):
            return self.parse_function()
        elif self.match(TokenType.RETURN):
            return self.parse_return()
        elif self.match(TokenType.BREAK):
            self.advance()
            return BreakStatement()
        else:
            return self.parse_expression_statement()

    def parse_local(self):
        self.advance()

        if self.match(TokenType.FUNCTION):
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.LPAREN)
            params = self.parse_parameter_list()
            self.expect(TokenType.RPAREN)
            body = self.parse_block([TokenType.END])
            self.expect(TokenType.END)
            return FunctionDef(name, params, body, is_local=True)

        targets = [Identifier(self.expect(TokenType.IDENTIFIER).value)]
        while self.match(TokenType.COMMA):
            self.advance()
            targets.append(Identifier(self.expect(TokenType.IDENTIFIER).value))

        values = []
        if self.match(TokenType.ASSIGN):
            self.advance()
            values.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                values.append(self.parse_expression())

        return Assignment(targets, values, is_local=True)

    def parse_if(self):
        self.advance()
        condition = self.parse_expression()
        self.expect(TokenType.THEN)
        then_block = self.parse_block([TokenType.ELSEIF, TokenType.ELSE, TokenType.END])

        elseif_blocks = []
        while self.match(TokenType.ELSEIF):
            self.advance()
            elseif_cond = self.parse_expression()
            self.expect(TokenType.THEN)
            elseif_body = self.parse_block([TokenType.ELSEIF, TokenType.ELSE, TokenType.END])
            elseif_blocks.append((elseif_cond, elseif_body))

        else_block = []
        if self.match(TokenType.ELSE):
            self.advance()
            else_block = self.parse_block([TokenType.END])

        self.expect(TokenType.END)
        return IfStatement(condition, then_block, elseif_blocks, else_block)

    def parse_while(self):
        self.advance()
        condition = self.parse_expression()
        self.expect(TokenType.DO)
        body = self.parse_block([TokenType.END])
        self.expect(TokenType.END)
        return WhileStatement(condition, body)

    def parse_repeat(self):
        self.advance()
        body = self.parse_block([TokenType.UNTIL])
        self.expect(TokenType.UNTIL)
        condition = self.parse_expression()
        return RepeatStatement(body, condition)

    def parse_for(self):
        self.advance()
        var = self.expect(TokenType.IDENTIFIER).value

        if self.match(TokenType.ASSIGN):
            self.advance()
            start = self.parse_expression()
            self.expect(TokenType.COMMA)
            end = self.parse_expression()
            step = None
            if self.match(TokenType.COMMA):
                self.advance()
                step = self.parse_expression()
            self.expect(TokenType.DO)
            body = self.parse_block([TokenType.END])
            self.expect(TokenType.END)
            return ForStatement(var, start, end, step, body)

        elif self.match(TokenType.COMMA, TokenType.IN):
            vars = [var]
            while self.match(TokenType.COMMA):
                self.advance()
                vars.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.IN)
            iterator = self.parse_expression()
            self.expect(TokenType.DO)
            body = self.parse_block([TokenType.END])
            self.expect(TokenType.END)
            return ForInStatement(vars, iterator, body)

        raise SyntaxError(f"Invalid for statement at {self.current_token.line}:{self.current_token.column}")

    def parse_function(self):
        self.advance()
        name = None
        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value
            self.advance()

        self.expect(TokenType.LPAREN)
        params = self.parse_parameter_list()
        self.expect(TokenType.RPAREN)
        body = self.parse_block([TokenType.END])
        self.expect(TokenType.END)
        return FunctionDef(name, params, body)

    def parse_parameter_list(self):
        params = []
        if not self.match(TokenType.RPAREN):
            params.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()
                params.append(self.expect(TokenType.IDENTIFIER).value)
        return params

    def parse_return(self):
        self.advance()
        values = []
        if not self.match(TokenType.END, TokenType.SEMICOLON, TokenType.EOF):
            values.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                values.append(self.parse_expression())
        return ReturnStatement(values)

    def parse_block(self, terminators):
        statements = []
        while not self.match(*terminators) and not self.match(TokenType.EOF):
            if self.match(TokenType.SEMICOLON):
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    def parse_expression_statement(self):
        expr = self.parse_expression()

        if self.match(TokenType.ASSIGN):
            self.advance()
            targets = [expr]
            while isinstance(expr, Identifier) or isinstance(expr, TableAccess):
                if not self.match(TokenType.COMMA):
                    break
                if self.peek().type == TokenType.ASSIGN:
                    break
                self.advance()
                next_expr = self.parse_expression()
                if self.match(TokenType.ASSIGN):
                    break
                targets.append(next_expr)

            values = [self.parse_expression()]
            while self.match(TokenType.COMMA):
                self.advance()
                values.append(self.parse_expression())

            return Assignment(targets, values)

        return expr

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match(TokenType.OR):
            op = self.current_token.value
            self.advance()
            right = self.parse_and()
            left = BinaryOp(left, op, right)
        return left

    def parse_and(self):
        left = self.parse_comparison()
        while self.match(TokenType.AND):
            op = self.current_token.value
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        return left

    def parse_comparison(self):
        left = self.parse_concat()
        while self.match(TokenType.EQ, TokenType.NE, TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self.current_token.value
            self.advance()
            right = self.parse_concat()
            left = BinaryOp(left, op, right)
        return left

    def parse_concat(self):
        left = self.parse_additive()
        while self.match(TokenType.CONCAT):
            op = self.current_token.value
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.match(TokenType.ASTERISK, TokenType.SLASH, TokenType.PERCENT):
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        return left

    def parse_unary(self):
        if self.match(TokenType.NOT, TokenType.MINUS, TokenType.LENGTH):
            op = self.current_token.value
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        return self.parse_power()

    def parse_power(self):
        left = self.parse_postfix()
        if self.match(TokenType.POWER):
            op = self.current_token.value
            self.advance()
            right = self.parse_power()
            return BinaryOp(left, op, right)
        return left

    def parse_postfix(self):
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.LPAREN):
                self.advance()
                args = []
                if not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                expr = FunctionCall(expr, args)

            elif self.match(TokenType.LBRACKET):
                self.advance()
                key = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = TableAccess(expr, key)

            elif self.match(TokenType.DOT):
                self.advance()
                key = self.expect(TokenType.IDENTIFIER).value
                expr = TableAccess(expr, StringLiteral(key))

            else:
                break

        return expr

    def parse_primary(self):
        if self.match(TokenType.NUMBER):
            value = float(self.current_token.value)
            self.advance()
            return NumberLiteral(value)

        if self.match(TokenType.STRING):
            value = self.current_token.value
            self.advance()
            return StringLiteral(value)

        if self.match(TokenType.TRUE):
            self.advance()
            return BooleanLiteral(True)

        if self.match(TokenType.FALSE):
            self.advance()
            return BooleanLiteral(False)

        if self.match(TokenType.NIL):
            self.advance()
            return NilLiteral()

        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value
            self.advance()
            return Identifier(name)

        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        if self.match(TokenType.LBRACE):
            return self.parse_table()

        if self.match(TokenType.FUNCTION):
            self.advance()
            self.expect(TokenType.LPAREN)
            params = self.parse_parameter_list()
            self.expect(TokenType.RPAREN)
            body = self.parse_block([TokenType.END])
            self.expect(TokenType.END)
            return FunctionDef(None, params, body)

        raise SyntaxError(f"Unexpected token {self.current_token.type.name} at {self.current_token.line}:{self.current_token.column}")

    def parse_table(self):
        self.advance()
        fields = []

        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            if self.match(TokenType.LBRACKET):
                self.advance()
                key = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                fields.append((key, value))
            elif self.match(TokenType.IDENTIFIER) and self.peek().type == TokenType.ASSIGN:
                key = StringLiteral(self.current_token.value)
                self.advance()
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                fields.append((key, value))
            else:
                value = self.parse_expression()
                fields.append((None, value))

            if self.match(TokenType.COMMA, TokenType.SEMICOLON):
                self.advance()
            else:
                break

        self.expect(TokenType.RBRACE)
        return TableConstructor(fields)
