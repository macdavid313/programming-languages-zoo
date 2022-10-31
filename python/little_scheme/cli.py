import argparse
import importlib

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.lexers.lisp import SchemeLexer
from pygments.styles.emacs import EmacsStyle
from sexpdata import loads as parse_sexp

from little_scheme.common import SchemeEnvironment


def get_argparser():
    parser = argparse.ArgumentParser(
        prog="little-scheme", description="Little toy scheme interpreter"
    )
    parser.add_argument("--variant", default="basic", choices=["basic"])
    return parser


def get_prompt_session():
    return PromptSession(
        message="little scheme λ ",
        lexer=PygmentsLexer(SchemeLexer),
        auto_suggest=AutoSuggestFromHistory(),
        style=style_from_pygments_cls(EmacsStyle),
        color_depth=ColorDepth.TRUE_COLOR,
    )


def main():
    args = get_argparser().parse_args()
    module = importlib.import_module(f"little_scheme.{args.variant}")

    global_env = SchemeEnvironment.init_global()

    prompt_session = get_prompt_session()

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


if __name__ == "__main__":
    main()
