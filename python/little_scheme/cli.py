import argparse
import importlib

from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.lisp import SchemeLexer
from sexpdata import loads as parse_sexp

from little_scheme.common import SchemeEnvironment


def get_argparser():
    parser = argparse.ArgumentParser(
        description="Little toy scheme interpreter"
    )
    parser.add_argument("--variant", default="basic", choices=["basic"])
    return parser

if __name__ == "__main__":
    parser = get_argparser()
    args = parser.parse_args()
    prompt_session = PromptSession(message="little scheme > ", lexer=PygmentsLexer(SchemeLexer))
    module = importlib.import_module(f"little_scheme.{args.variant}")
    global_env = SchemeEnvironment.init_global()

    while True:
        try:
            input = prompt_session.prompt().strip()
            if not input:
                continue
            res = module.eval_scheme(parse_sexp(input), global_env)
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
