from .lexer import Lexer
from .parser import Parser
from .evaluator import Evaluator
from .lua_object import Environment, ReturnException
from .lua_builtins import setup_builtins


class LuaInterpreter:
    def __init__(self):
        self.global_env = Environment()
        setup_builtins(self.global_env)
        self.evaluator = Evaluator(self.global_env)

    def run(self, source: str):
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            result = self.evaluator.eval(ast, self.global_env)
            return result
        except ReturnException as e:
            return e.values[0] if e.values else None
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            return None
        except Exception as e:
            print(f"Runtime Error: {e}")
            return None

    def run_file(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source = f.read()
            return self.run(source)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
