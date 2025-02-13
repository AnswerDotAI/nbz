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

# Commands actually implemented
commands = {
    'bump_version': release.nbdev_bump_version,        
    'clean':n_clean.nbdev_clean,
    'new': cli.nbdev_new,
    'update_license': cli.nbdev_update_license,
    'watch_export': cli.watch_export
}

for fname,func in commands.items():
    # Remove call_parse so it doesn't conflict with typer
    func = func.__wrapped__

    # Add to typer.app
    func = app.command()(func)    

    # Prep the annotations
    arguments = docments(func, full=True)
    for arg, meta in arguments.items():
        if (meta['anno'] is bool_arg): meta['anno'] = bool
        func.__annotations__[arg] = Annotated[meta['anno'], typer.Argument()]    

    # Fix the name
    func.__name__ = func.__name__.replace('nbdev_','')

    globals()[fname] = func



# Not yet implemented
# TODO: fix store_true on these commands
nyi_commands = {
    'changelog': release.changelog,
    'export_cli': cli.nb_export_cli
}


for fname in nyi_commands.keys():
    @app.command()
    def func():
        'Not yet implemented'
        print(f'[red][b]ERROR: {export_cli.__doc__}[/b][/red]')
    func.__name__ = fname
    globals()[fname] = func


if __name__ == '__main__':
    app()