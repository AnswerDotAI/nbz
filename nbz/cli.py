import types
from functools import wraps
import typer
from typing_extensions import Annotated
from fastcore.docments import *
from fastcore.all import *
from rich import print

# commands
from nbdev import cli, release
from nbdev import clean as n_clean

app = typer.Typer()

@app.callback(invoke_without_command=True)
def helper(ctx: typer.Context):
    """
    nbz is a typer-based wrapper around the incredible nbdev project.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())

commands = {
    'clean':n_clean.nbdev_clean,
    'bump_version': release.nbdev_bump_version,    
    'new': cli.nbdev_new,
    'update_license': cli.nbdev_update_license
}

for fname,func in commands.items():
    # Remove call_parse so it doesn't conflict with typer
    func = func.__wrapped__

    # Add to typer.app
    func = app.command()(func)    

    # Prep the annotations
    arguments = docments(func, full=True)
    for arg, meta in arguments.items():
        # print(meta)
        if (meta['anno'] is bool_arg): 
            meta['anno'] = bool
        func.__annotations__[arg] = Annotated[meta['anno'], typer.Argument()]    

    # Fix the name
    func.__name__ = func.__name__.replace('nbdev_','')

    globals()[fname] = func



# Not yet implemented
@app.command()
def export_cli():
    'Not yet implemented'
    print(f'[red][b]ERROR: {export_cli.__doc__}[/b][/red]')


if __name__ == '__main__':
    app()