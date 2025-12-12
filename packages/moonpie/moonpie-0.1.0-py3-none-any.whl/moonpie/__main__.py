#!/usr/bin/env python3
"""
MoonPie Command Line Interface

This module provides command-line execution capabilities for Lua files
and an interactive REPL (Read-Eval-Print Loop).

Usage:
    python -m moonpie <file.lua>    # Execute a Lua file
    python -m moonpie               # Start interactive REPL
    moonpie <file.lua>              # Execute a Lua file (after installation)
    moonpie                         # Start interactive REPL (after installation)
"""

import sys
import argparse
import os
from pathlib import Path
from .lua_interpreter import LuaInterpreter


def start_repl():
    """Start the interactive REPL."""
    interpreter = LuaInterpreter()

    print("MoonPie - Lua Interpreter in Python")
    print(f"Version {__package__.__version__ if hasattr(__package__, '__version__') else '0.1.0'}")
    print("Type 'exit' or press Ctrl+C to quit")
    print()

    while True:
        try:
            line = input("> ")

            if line.strip() in ('exit', 'quit'):
                print("Goodbye!")
                break

            if not line.strip():
                continue

            result = interpreter.run(line)

            if result is not None:
                print(result.to_str())

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(
        prog='moonpie',
        description='MoonPie - A Lua interpreter written in Python',
        epilog='Examples:\n  python -m moonpie script.lua    # Execute file\n  python -m moonpie               # Start REPL',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'file',
        nargs='?',
        help='Lua file to execute (.lua extension recommended). If omitted, starts interactive REPL.'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        return

    if not args.file:
        start_repl()
        return

    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
    except UnicodeDecodeError:
        print(f"Error: Could not read '{args.file}' as UTF-8 text.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Executing Lua file: {args.file}")
        print(f"File size: {len(code)} characters")

    try:
        interpreter = LuaInterpreter()
        result = interpreter.run(code)

    except Exception as e:
        print(f"Error executing Lua: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
