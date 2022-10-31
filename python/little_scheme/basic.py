from sexpdata import Quoted, Symbol

from little_scheme.common import SchemeEnvironment, SchemeInvalidExpressionError


def eval_scheme(x, env: SchemeEnvironment):
    match x:
        case int(n) | float(n):
            return n
        case Quoted():
            return eval_quoted(x, env)
        case Symbol():
            return eval_symbol(x, env)
        case []:
            return x
        case [first, *_]:
            match first:
                case Symbol():
                    match first.value():
                        case "begin":
                            return eval_begin(x, env)
                        case "set!":
                            return eval_set(x, env)
                        case "define":
                            return eval_define(x, env)
                        case "if":
                            return eval_if(x, env)
                        case "lambda":
                            return eval_lambda(x, env)
                        case _:
                            return eval_apply_funcall(x, env)
                case _:
                    return eval_apply_funcall(x, env)
        case _:
            raise SchemeInvalidExpressionError(x)


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
            return
        case _:
            raise SchemeInvalidExpressionError(x)


def eval_define(x, env: SchemeEnvironment):
    match x:
        case [_, Symbol(), form]:
            sym: Symbol = x[1]
            return eval_scheme(
                [Symbol("begin"), [Symbol("set!"), sym, form], Quoted(sym.value())],
                env,
            )
        case [_, [Symbol(), *params], *body]:
            sym: Symbol = x[1][0]
            return eval_scheme(
                [Symbol("define"), sym, [Symbol("lambda"), params, *body]], env
            )
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
