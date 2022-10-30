from operator import (
    add,
    and_,
    eq,
    floordiv,
    ge,
    gt,
    le,
    lt,
    mod,
    mul,
    ne,
    not_,
    or_,
    sub,
    truediv,
)
from typing import Any, Dict, List

from prompt_toolkit import PromptSession
from sexpdata import Quoted, Symbol
from sexpdata import dumps as write_sexp
from sexpdata import loads as parse_sexp


class SchemeRuntimeError(RuntimeError):
    pass


class SchemeUnboundVaribleError(SchemeRuntimeError):
    def __init__(self, var: Symbol):
        self.var = var

    def __str__(self):
        return "Unbound variable: {0}".format(self.var.value())


class SchemeInvalidExpressionError(SchemeRuntimeError):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "Invalid expression: {0}".format(write_sexp(self.expr))


class SchemeEnvironment:
    def __init__(self):
        self.table: Dict[Symbol, Any] = {}

    def get_var(self, var: Symbol):
        val = self.table.get(var.value())
        if not val:
            raise SchemeUnboundVaribleError(var)
        return val

    def set_var(self, var: Symbol, val: Any):
        self.table[var.value()] = val

    def extend(self, vars: List[Symbol], vals: List[Any]):
        new_env = SchemeEnvironment()
        new_env.table = self.table.copy()
        for var, val in zip(vars, vals):
            new_env.set_var(var, val)
        return new_env

    @staticmethod
    def init_global():
        global_env = SchemeEnvironment()

        # arithmetic
        global_env.set_var(Symbol("+"), add)
        global_env.set_var(Symbol("-"), sub)
        global_env.set_var(Symbol("*"), mul)
        global_env.set_var(Symbol("/"), truediv)
        global_env.set_var(Symbol("floor"), floordiv)
        global_env.set_var(Symbol("mod"), mod)
        # boolean
        global_env.set_var(Symbol("and"), and_)
        global_env.set_var(Symbol("or"), or_)
        global_env.set_var(Symbol("not"), not_)
        # comparison
        global_env.set_var(Symbol("="), eq)
        global_env.set_var(Symbol("!="), ne)
        global_env.set_var(Symbol("<"), lt)
        global_env.set_var(Symbol("<="), le)
        global_env.set_var(Symbol(">"), gt)
        global_env.set_var(Symbol(">="), ge)

        return global_env


def eval_scheme(x, env: SchemeEnvironment):
    match x:
        case int(n) | float(n) | str(n): return n
        case Quoted(): return eval_quoted(x, env)
        case Symbol(): return eval_symbol(x, env)
        case []: return x
        case [first, *_]:
            match first:
                case Symbol():
                    match first.value():
                        case "begin": return eval_begin(x, env)
                        case "set!": return eval_set(x, env)
                        case "if": return eval_if(x, env)
                        case "lambda": return eval_lambda(x, env)
                        case _: return eval_apply_funcall(x, env)
                case _:
                    return eval_apply_funcall(x, env)
        case _: raise SchemeInvalidExpressionError(x)


def eval_quoted(x, env: SchemeEnvironment):
    return x.value()


def eval_symbol(x, env: SchemeEnvironment):
    return env.get_var(x)


def eval_begin(x, env: SchemeEnvironment):
    match x:
        case [_, *forms]:
            val = None
            for form in forms:
                val = eval_scheme(form, env)
            return val
        case _:
            raise SchemeInvalidExpressionError(x)


def eval_set(x, env: SchemeEnvironment):
    match x:
        case [_, var, val]:
            env.set_var(var, eval_scheme(val, env))
            return var.value()
        case _:
            raise SchemeInvalidExpressionError(x)


def eval_if(x, env: SchemeEnvironment):
    match x:
        case [_, test_form, true_form]:
            if eval_scheme(test_form, env):
                return eval_scheme(true_form, env)
            return
        case [_, test_form, true_form, false_form]:
            if eval_scheme(test_form, env):
                return eval_scheme(true_form, env)
            else:
                return eval_scheme(false_form, env)
        case _:
            raise SchemeInvalidExpressionError(x)


def eval_lambda(x, env: SchemeEnvironment):
    match x:
        case [_, params, *body]:
            body = [Symbol("begin")] + body

            def _proc(*args):
                return eval_scheme(body, env.extend(params, args))

            return _proc
        case _:
            raise SchemeInvalidExpressionError(x)


def eval_apply_funcall(x, env: SchemeEnvironment):
    match x:
        case [func, *args]:
            func = eval_scheme(func, env)
            args = [eval_scheme(arg, env) for arg in args]
            return func(*args)
        case _:
            raise SchemeInvalidExpressionError(x)


def scheme():
    global_env = SchemeEnvironment.init_global()
    session = PromptSession(
        message="little scheme > ",
    )

    while True:
        try:
            input = session.prompt().strip()
            if not input:
                continue
            res = eval_scheme(parse_sexp(input), global_env)
        except KeyboardInterrupt:
            continue
        except EOFError:
            print("Bye bye.")
            exit(0)
        except Exception as e:
            print(e)
            continue
        else:
            print(res)


if __name__ == "__main__":
    scheme()
