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
    'changelog': release.changelog,
    'conda': release.release_conda,    
    'new': cli.nbdev_new,    
    'release_both': release.release_both,
    'release_gh': release.release_gh,
    'release_git': release.release_git,
    'update_license': cli.nbdev_update_license,
    'watch_export': cli.watch_export
}

for fname,func in commands.items():
    # Remove call_parse so it doesn't conflict with typer
    func = func.__wrapped__

    # Add to typer.app
    func = app.command()(func)

    # Prep the annotations to map accurately to typer
    arguments = docments(func, full=True)
    for arg, meta in arguments.items():
        # This next line might be simplistic and could cause errors
        if meta['anno'] in (bool_arg, store_true): meta['anno'] = bool
        func.__annotations__[arg] = Annotated[meta['anno'], typer.Argument()]

    # Fix the name
    func.__name__ = fname

    # Save to the global namespace
    globals()[fname] = func

# Not yet implemented
# TODO: fix store_true on these commands
nyi_commands = {
    'export_cli': cli.nb_export_cli
}

for fname in nyi_commands.keys():
    @app.command()
    def func():
        'Not yet implemented'
        print(f'[red][b]ERROR: {func.__doc__}[/b][/red]')
    func.__name__ = fname
    globals()[fname] = func

if __name__ == '__main__':
    app()