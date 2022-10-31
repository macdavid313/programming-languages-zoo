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

from sexpdata import Symbol
from sexpdata import dumps as write_sexp


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
        if var.value() in self.table.keys():
            return self.table[var.value()]
        raise SchemeUnboundVaribleError(var)

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
