from .buffer import PysFileBuffer
from .cache import loading_modules, modules, path, undefined, hook
from .checks import is_blacklist_python_builtins, is_private_attribute
from .exceptions import PysSignal
from .handlers import handle_call
from .objects import PysPythonFunction
from .results import PysRunTimeResult
from .symtab import new_symbol_table
from .utils.generic import get_any, is_object_of as isobjectof, import_readline
from .utils.module import get_module_name_from_path, get_module_path, set_python_path
from .utils.path import getcwd, normpath
from .utils.shell import PysCommandLineShell
from .utils.string import normstr

from math import isclose
from importlib import import_module
from os.path import dirname
from types import ModuleType

import builtins

def _supported_method(pyfunc, object, name, *args, **kwargs):
    method = getattr(object, name, undefined)
    if method is undefined:
        return False, None

    if callable(method):
        code = pyfunc.__code__
        handle_call(method, code.context, code.position)
        try:
            result = method(*args, **kwargs)
            if result is not NotImplemented:
                return True, result
        except NotImplementedError:
            pass

    return False, None

class _Printer:

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def __repr__(self):
        return f'Type {self.name}() to see the full information text.'

    def __call__(self):
        print(self.text)

class _Helper(_Printer):

    def __init__(self):
        super().__init__('help', None)

    def __repr__(self):
        return f'Type {self.name}() for interactive help, or {self.name}(object) for help about object.'

    def __call__(self, *args, **kwargs):
        if not (args or kwargs):
            print(
                "Welcome to the PyScript programming language! "
                "This is the help utility directly to the Python help.\n\n"
                "To get help on a specific object, type 'help(object)'.\n"
                "To get the list of built-in functions, types, exceptions, and other objects, "
                "type 'help(\"builtins\")'."
            )
        else:
            return builtins.help(*args, **kwargs)

license = _Printer(
    'license',

    "MIT License - PyScript created by AzzamMuhyala.\n"
    "This language was written as a project and learning how language is works.\n"
    "For more information see on https://github.com/azzammuhyala/pyscript."
)

help = _Helper()

@PysPythonFunction
def require(pyfunc, name):
    name, *other_components = normstr(name).split('>')
    code = pyfunc.__code__
    context = code.context

    for p in path:
        module_path = get_module_path(normpath(p, name, absolute=False))
        if module_path is not None:
            break
    else:
        module_path = get_module_path(normpath(dirname(context.file.name) or getcwd(), name, absolute=False))

    if module_path is None:
        if name == '_pyscript':
            from .. import core as module
        elif name == 'builtins':
            module = pys_builtins
        else:
            module_path = name

    if module_path is not None:

        if module_path in loading_modules:
            raise ImportError(
                f"cannot import module name {name!r} "
                f"from partially initialized module {context.file.name!r}, "
                "mostly during circular import"
            )

        module = modules.get(module_path, None)

        if module is None:

            try:
                loading_modules.add(module_path)

                try:
                    with open(module_path, 'r', encoding='utf-8') as file:
                        file = PysFileBuffer(file, module_path)
                except FileNotFoundError as e:
                    raise ModuleNotFoundError(f"No module named {name!r}") from e
                except BaseException as e:
                    raise ImportError(f"Cannot import module named {name!r}: {e}") from e

                symtab, module = new_symbol_table(
                    file=file.name,
                    name=get_module_name_from_path(name)
                )

                from .runner import pys_runner

                result = pys_runner(
                    file=file,
                    mode='exec',
                    symbol_table=symtab,
                    context_parent=context,
                    context_parent_entry_position=code.position
                )

                if result.error:
                    raise PysSignal(PysRunTimeResult().failure(result.error))

                modules[module_path] = module

            finally:
                if module_path in loading_modules:
                    loading_modules.remove(module_path)

    for component in other_components:
        module = getattr(module, component)

    return module

@PysPythonFunction
def pyimport(pyfunc, name):
    set_python_path(dirname(pyfunc.__code__.context.file.name))
    return import_module(normstr(name))

@PysPythonFunction
def breakpoint(pyfunc):
    if hook.running_breakpoint:
        raise RuntimeError("another breakpoint is still running")

    from .runner import pys_runner

    code = pyfunc.__code__
    symtab = code.context.symbol_table
    shell = PysCommandLineShell('(Pdb) ', '...   ')
    scopes = []

    import_readline()

    try:
        hook.running_breakpoint = True

        while True:

            try:
                text = shell.input()

                split = text.split()
                if split:
                    command, *args = split
                else:
                    command, args = '', []

                if command in (0, 'q', 'quit', 'exit'):
                    code = get_any(args, 0, '0')
                    raise SystemExit(int(code) if code.isdigit() else code)

                elif command in ('c', 'continue'):
                    return

                elif command in ('u', 'up'):
                    count = get_any(args, 0, '')
                    for _ in range(int(count) if count.isdigit() else 1):
                        if scopes:
                            symtab = scopes.pop()
                        else:
                            print('*** Oldest frame')
                            break

                elif command in ('d', 'down'):
                    count = get_any(args, 0, '')
                    parent = symtab.parent
                    for _ in range(int(count) if count.isdigit() else 1):
                        if parent is None:
                            print('*** Newest frame')
                            break
                        else:
                            scopes.append(symtab)
                            symtab = parent

                elif command in ('h', 'help'):
                    print(
                        "\n"
                        "Documented commands:\n"
                        "====================\n"
                        "(c)ontinue          : Exit the debugger and continue the program.\n"
                        "(d)own [count]      : Decrease the scope level (default one) to the older frame.\n"
                        "(h)elp              : Show this help display.\n"
                        "(q)uit / exit [code]: Exit the interpreter by throwing SystemExit.\n"
                        "(u)p [count]        : Increase the scope level (default one) to the older frame.\n"
                    )

                else:
                    pys_runner(
                        file=PysFileBuffer(text, '<breakpoint>'),
                        mode='single',
                        symbol_table=symtab
                    ).process()

            except KeyboardInterrupt:
                shell.reset()
                print('\r--keyboardIterrupt--')

            except EOFError as e:
                raise SystemExit from e

    finally:
        hook.running_breakpoint = False

@PysPythonFunction
def globals(pyfunc):
    symbol_table = pyfunc.__code__.context.symbol_table.parent

    if symbol_table:
        result = {}

        while symbol_table:
            result |= symbol_table.symbols
            symbol_table = symbol_table.parent

        return result

    return pyfunc.__code__.context.symbol_table.symbols

@PysPythonFunction
def locals(pyfunc):
    return pyfunc.__code__.context.symbol_table.symbols

pyvars = builtins.vars

@PysPythonFunction
def vars(pyfunc, object=None):
    return (
        pyfunc.__code__.context.symbol_table.symbols
        if object is None else
        pyvars(object)
    )

pydir = builtins.dir

@PysPythonFunction
def dir(pyfunc, *args):
    return (
        pydir(*args)
        if args else
        list(pyfunc.__code__.context.symbol_table.symbols.keys())
    )

@PysPythonFunction
def exec(pyfunc, source, globals=None):
    if not isinstance(globals, (type(None), dict)):
        raise TypeError("exec(): globals must be dict")

    file = PysFileBuffer(source, '<exec>')
    code = pyfunc.__code__

    if globals is None:
        symtab = code.context.symbol_table
    else:
        symtab, _ = new_symbol_table(symbols=globals)

    from .runner import pys_runner

    result = pys_runner(
        file=file,
        mode='exec',
        symbol_table=symtab,
        context_parent=code.context,
        context_parent_entry_position=code.position
    )

    if result.error:
        raise PysSignal(PysRunTimeResult().failure(result.error))

@PysPythonFunction
def eval(pyfunc, source, globals=None):
    if not isinstance(globals, (type(None), dict)):
        raise TypeError("eval(): globals must be dict")

    file = PysFileBuffer(source, '<eval>')
    code = pyfunc.__code__

    if globals is None:
        symtab = code.context.symbol_table
    else:
        symtab, _ = new_symbol_table(symbols=globals)

    from .runner import pys_runner

    result = pys_runner(
        file=file,
        mode='eval',
        symbol_table=symtab,
        context_parent=code.context,
        context_parent_entry_position=code.position
    )

    if result.error:
        raise PysSignal(PysRunTimeResult().failure(result.error))

    return result.value

@PysPythonFunction
def ce(pyfunc, a, b, *, rel_tol=1e-9, abs_tol=0):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    success, result = _supported_method(pyfunc, a, '__ce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
    if not success:
        success, result = _supported_method(pyfunc, b, '__ce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
        if not success:
            raise TypeError(
                f"unsupported operand type(s) for ~= or ce(): {type(a).__name__!r} and {type(b).__name__!r}"
            )

    return result

@PysPythonFunction
def nce(pyfunc, a, b, *, rel_tol=1e-9, abs_tol=0):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return not isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    success, result = _supported_method(pyfunc, a, '__nce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
    if not success:
        success, result = _supported_method(pyfunc, b, '__nce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
        if not success:
            success, result = _supported_method(pyfunc, a, '__ce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
            if not success:
                success, result = _supported_method(pyfunc, b, '__ce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
                if not success:
                    raise TypeError(
                        f"unsupported operand type(s) for ~! or nce(): {type(a).__name__!r} and {type(b).__name__!r}"
                    )
            result = not result

    return result

@PysPythonFunction
def increment(pyfunc, object):
    if isinstance(object, (int, float)):
        return object + 1

    success, result = _supported_method(pyfunc, object, '__increment__')
    if not success:
        raise TypeError(f"bad operand type for unary ++ or increment(): {type(object).__name__!r}")

    return result

@PysPythonFunction
def decrement(pyfunc, object):
    if isinstance(object, (int, float)):
        return object - 1

    success, result = _supported_method(pyfunc, object, '__decrement__')
    if not success:
        raise TypeError(f"bad operand type for unary -- or decrement(): {type(object).__name__!r}")

    return result

def comprehension(init, wrap, condition=None):
    if not callable(wrap):
        raise TypeError("comprehension(): wrap must be callable")
    if not (condition is None or callable(condition)):
        raise TypeError("comprehension(): condition must be callable")

    return map(wrap, init if condition is None else filter(condition, init))

pys_builtins = ModuleType(
    'built-in',
    "Built-in functions, types, exceptions, and other objects.\n\n"
    "This module provides direct access to all 'built-in' identifiers of PyScript and Python."
)

pys_builtins.__dict__.update(
    (name, getattr(builtins, name))
    for name in builtins.dir(builtins)
    if not (is_private_attribute(name) or is_blacklist_python_builtins(name))
)

pys_builtins.__file__ = __file__
pys_builtins.true = True
pys_builtins.false = False
pys_builtins.none = None
pys_builtins.license = license
pys_builtins.help = help
pys_builtins.require = require
pys_builtins.pyimport = pyimport
pys_builtins.breakpoint = breakpoint
pys_builtins.globals = globals
pys_builtins.locals = locals
pys_builtins.vars = vars
pys_builtins.dir = dir
pys_builtins.exec = exec
pys_builtins.eval = eval
pys_builtins.ce = ce
pys_builtins.nce = nce
pys_builtins.increment = increment
pys_builtins.decrement = decrement
pys_builtins.comprehension = comprehension
pys_builtins.isobjectof = isobjectof