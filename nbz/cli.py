import types
from functools import wraps
import typer
from typing_extensions import Annotated
from fastcore.docments import *
from fastcore.all import *
from rich import print

# commands
from nbdev import cli, release, config, quarto, doclinks, merge, migrate, sync
from nbdev import clean as nbclean
from nbdev import test as nbtest

app = typer.Typer(rich_markup_mode="markdown")

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
    'clean':nbclean.nbdev_clean,        
    'changelog': release.changelog,
    'conda': release.release_conda, 
    'create_config': config.nbdev_create_config,  
    'docs': quarto.nbdev_docs,
    'filter': cli.nbdev_filter,
    'fix': merge.nbdev_fix,
    'install': quarto.install,
    'install_hooks': nbclean.nbdev_install_hooks,
    'install_quarto': quarto.install_quarto,
    'merge': merge.nbdev_merge,
    'migrate': migrate.nbdev_migrate,    
    'new': cli.nbdev_new,    
	'prepare': quarto.prepare,
	'preview': quarto.nbdev_preview,
    'proc_nbs': quarto.nbdev_proc_nbs,
    'pypi': release.release_pypi, 
	'readme': quarto.nbdev_readme,
    'release_both': release.release_both,
    'release_gh': release.release_gh,
    'release_git': release.release_git,       
    'requirements': release.write_requirements,
    'sidebar': quarto.nbdev_sidebar,
    'test': nbtest.nbdev_test,
    'trust': nbclean.nbdev_trust,
    'update': sync.nbdev_update,
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
    'export': doclinks.nbdev_export,
    'export_cli': cli.nb_export_cli,
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