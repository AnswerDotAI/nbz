import typer
from typing_extensions import Annotated
from fastcore.docments import *
from fastcore.all import *
from nbdev import cli
from rich import print
from functools import wraps

app = typer.Typer()

@app.callback(invoke_without_command=True)
def helper(ctx: typer.Context):
    """
    nbdev-cli is a typer-based wrapper around the incredible nbdev project.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


def func_to_typer(delegated):
    def decorator(func):
        # Set the function's docstring
        func.__doc__ = delegated.__doc__

        # Prep the annotations
        arguments = docments(delegated, full=True)
        for arg, meta in arguments.items():
            if (meta['anno'] is bool_arg): 
                meta['anno'] = bool
            func.__annotations__[arg] = Annotated[meta['anno'], typer.Argument()]
        
        return func
    return decorator

def remove_call_parse(func):
    return func.__wrapped__

@func_to_typer(cli.nbdev_new)
@app.command()
@delegates(cli.nbdev_new)
def new(**kwargs):
    remove_call_parse(cli.nbdev_new)(**kwargs)

@func_to_typer(cli.nbdev_update_license)
@app.command()
@delegates(cli.nbdev_update_license)
def update_license(**kwargs):
    remove_call_parse(cli.nbdev_update_license)(**kwargs)

# @func_to_typer(cli.nb_export_cli)
# @app.command()
# @delegates(cli.nb_export_cli)
# def export_cli(**kwargs):
#     remove_call_parse(cli.nb_export_cli)(**kwargs)


if __name__ == '__main__':
    app()