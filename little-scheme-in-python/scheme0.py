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

from sexpdata import Quoted, Symbol
from sexpdata import loads as parse_sexp
from prompt_toolkit import PromptSession


class SchemeEnvironment:
    def __init__(self):
        self.table: Dict[Symbol, Any] = {}

    def get_var(self, var: Symbol):
        val = self.table.get(var.value())
        if not val:
            raise RuntimeError("Unbound variable: %s" % var)
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
        global_scheme_environment = SchemeEnvironment()

        # arithmetic
        global_scheme_environment.set_var(Symbol("+"), add)
        global_scheme_environment.set_var(Symbol("-"), sub)
        global_scheme_environment.set_var(Symbol("*"), mul)
        global_scheme_environment.set_var(Symbol("/"), truediv)
        global_scheme_environment.set_var(Symbol("floor"), floordiv)
        global_scheme_environment.set_var(Symbol("mod"), mod)
        # boolean
        global_scheme_environment.set_var(Symbol("and"), and_)
        global_scheme_environment.set_var(Symbol("or"), or_)
        global_scheme_environment.set_var(Symbol("not"), not_)
        # comparison
        global_scheme_environment.set_var(Symbol("="), eq)
        global_scheme_environment.set_var(Symbol("!="), ne)
        global_scheme_environment.set_var(Symbol("<"), lt)
        global_scheme_environment.set_var(Symbol("<="), le)
        global_scheme_environment.set_var(Symbol(">"), gt)
        global_scheme_environment.set_var(Symbol(">="), ge)

        return global_scheme_environment


def eval_scheme(x, env: SchemeEnvironment):

    if isinstance(x, int) or isinstance(x, float):
        return x

    elif isinstance(x, Quoted):
        return eval_quoted(x, env)

    elif isinstance(x, Symbol):
        return eval_symbol(x, env)

    elif isinstance(x, List):
        if len(x) == 0:
            return x
        head = x[0]
        if isinstance(head, Symbol):
            if head.value() == "begin":
                return eval_begin(x, env)
            elif head.value() == "set!":
                return eval_set(x, env)
            elif head.value() == "if":
                return eval_if(x, env)
            elif head.value() == "lambda":
                return eval_lambda(x, env)
            else:
                return eval_apply_funcall(x, env)
        else:
            return eval_apply_funcall(x, env)

    else:
        raise RuntimeError("Don't know how to evaluate %s" % x)


def eval_quoted(x, env: SchemeEnvironment):
    return x.value()


def eval_symbol(x, env: SchemeEnvironment):
    return env.get_var(x)


def eval_begin(x, env: SchemeEnvironment):
    val = None
    for form in x[1:]:
        val = eval_scheme(form, env)
    return val


def eval_set(x, env: SchemeEnvironment):
    assert len(x) == 3
    var = x[1]
    val = x[2]
    env.set_var(var, eval_scheme(val, env))
    return None


def eval_if(x, env: SchemeEnvironment):
    assert len(x) == 3 or len(x) == 4
    test_form, true_form = x[1], x[2]
    false_form = x[3] if len(x) == 4 else []
    if eval_scheme(test_form, env):
        return eval_scheme(true_form, env)
    else:
        return eval_scheme(false_form, env)


def eval_lambda(x, env: SchemeEnvironment):
    assert len(x) >= 2
    params = x[1]
    body = [Symbol("begin")] + x[2:]

    def _proc(*args):
        return eval_scheme(body, env.extend(params, args))

    return _proc


def eval_apply_funcall(x, env: SchemeEnvironment):
    func = eval_scheme(x[0], env)
    args = [eval_scheme(arg, env) for arg in x[1:]]
    return func(*args)


def scheme():
    global_env = SchemeEnvironment.init_global()
    session = PromptSession(
        message="little scheme > ",
    )

    while True:
        try:
            input = session.prompt()
        except KeyboardInterrupt:
            continue
        except EOFError:
            print("Bye bye.")
            exit(0)
        else:
            print(eval_scheme(parse_sexp(input), global_env))


if __name__ == "__main__":
    scheme()
