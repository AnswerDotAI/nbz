"""Commands are used to harness the power of nbdev."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_commands.ipynb.

# %% auto 0
__all__ = ['console', 'error_console', 'nbdev_bump_version', 'Procs', 'nb_export_cli', 'orig_install', 'nbdev_new',
           'nbdev_release_git', 'prompt_help', 'delegates_sorted', 'bump_version', 'check', 'export', 'export_nb',
           'install', 'new', 'release_git']

# %% ../nbs/01_commands.ipynb 2
import types, pathlib, os
from functools import wraps
import typer
from typing_extensions import Annotated
from fastcore.basics import *
from fastcore.docments import *
from fastcore.meta import delegates
from fastcore.script import call_parse
from fastcore.shutil import rmtree,move
from fastcore.utils import *
from rich import print
from rich.console import Console
from shutil import which

# %% ../nbs/01_commands.ipynb 3
from nbdev import cli, release, quarto, doclinks, merge, migrate, sync, release
from nbdev.cli import _update_repo_meta, extract_tgz, _render_nb, nb_export_cli
from nbdev.config import *
from nbdev.doclinks import *
from nbdev.doclinks import _build_modidx
from nbdev.export import optional_procs, nb_export
from nbdev.quarto import nbdev_readme, refresh_quarto_yml, fs_watchdog, install, install_quarto
from nbdev import clean as nbclean
from nbdev import test as nbtest

# %% ../nbs/01_commands.ipynb 4
console = Console(style='bold')
error_console = Console(stderr=True, style="bold red")

# %% ../nbs/01_commands.ipynb 6
from fastcore.imports import *
import inspect

# %% ../nbs/01_commands.ipynb 7
def delegates_sorted(to:FunctionType=None, # Delegatee
              keep=False, # Keep `kwargs` in decorated function?
              but:list=None): # Exclude these parameters from signature
    "Decorator: replace `**kwargs` in signature with params from `to`. Sorts arguments."
    if but is None: but = []
    def _f(f):
        if to is None: to_f,from_f = f.__base__.__init__,f.__init__
        else:          to_f,from_f = to.__init__ if isinstance(to,type) else to,f
        from_f = getattr(from_f,'__func__',from_f)
        to_f = getattr(to_f,'__func__',to_f)
        if hasattr(from_f,'__delwrap__'): return f
        sig = inspect.signature(from_f)
        sigd = dict(sig.parameters)
        k = sigd.pop('kwargs')
        s2 = {k:v.replace(kind=inspect.Parameter.KEYWORD_ONLY) for k,v in inspect.signature(to_f).parameters.items()
              if v.default != inspect.Parameter.empty and k not in sigd and k not in but}
        s2 = dict(sorted(s2.items()))
        anno = {k:v for k,v in getattr(to_f, "__annotations__", {}).items() if k not in sigd and k not in but}
        sigd.update(s2)
        if keep: sigd['kwargs'] = k
        else: from_f.__delwrap__ = to_f
        from_f.__signature__ = sig.replace(parameters=sigd.values())
        if hasattr(from_f, '__annotations__'): from_f.__annotations__.update(anno)
        return f
    return _f

# %% ../nbs/01_commands.ipynb 9
nbdev_bump_version = release.nbdev_bump_version.__wrapped__ # remove callparse

@delegates(release.nbdev_bump_version)
def bump_version(**kwargs):
    """
    Bump the version of a project in `settings.ini` and `__version__` within `__init__.py`.
    
    Examples:    
    
    * `nbz bump-version` will increment a 0.0.1 to 0.0.2
    
    * `nbz bump-version --part 1` will increment a 0.0.1 to 0.1.0    
    
    * `nbz bump-version --part 0` will increment a 0.0.1 to 1.0.0
    
    * `nbz bump-version --unbump` will restore the previous version until it has been saved by git.
    
    ---
    
    Learn more [nbz.answer.ai/commands#version-bump](https://nbz.answer.ai/commands#version-bump)
    """        
    return nbdev_bump_version(**kwargs)
bump_version.rich_help_panel = 'Releasing versions'
bump_version.no_args_is_help=False

# %% ../nbs/01_commands.ipynb 10
def check():
    """
    Check that all the components are configured.
    
    Example:    
    
    * `nbz check`
    
    ---
    
    Learn more [nbz.answer.ai/commands#check](https://nbz.answer.ai/commands#check)
    """
    errors=[]
    
    if which('quarto') is None:
        errors.append('[red]Quarto not yet installed.[/red]\n    Fix: [b]nbz install-quarto[/b]')
        
    if not os.getenv('GITHUB_TOKEN') and not os.getenv('GITHUB_JWT_TOKEN'): 
        errors.append('[red]No github token.[/red]\n    Fix: [b]Set environment variable for GITHUB_TOKEN or GITHUB_JWT_TOKEN[/b]')
        
    try: 
        from twine import settings
        import keyring      
#         cfg = settings.get_repository_config('pypi')
#         console.print(cfg)
#         creds = settings.get_credentials('pypi')
#         if bool(creds.username and creds.password) is False:
#             errors.append('[red]pypi access not setup.[/red]\n    Fix: [b]See https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#create-an-account[/b]')
    except ImportError:
        errors.append('[red]twine not installed.[/red]\n    Fix: [b]pip install twine[/b]')
    
    if errors:
        error_console.print('ERROR: nbdev not fully configured yet.')
        for i, error in enumerate(errors): console.print(f'{i+1}. {error}')
        raise typer.Exit(code=1)
    console.print('[b]Check passed![/b]')
check.rich_help_panel = 'Installation'
check.no_args_is_help=False

# %% ../nbs/01_commands.ipynb 11
Procs = str_enum('Procs',*optional_procs())

# %% ../nbs/01_commands.ipynb 12
@delegates_sorted(nbglob_cli)
def export(
    path:Annotated[pathlib.Path, typer.Argument(help="Export notebooks in `path` to Python modules.")],
    procs: Annotated[List[Procs], typer.Option(help='tokens naming the export processors to use.')] = ['black_format'],
    **kwargs):
    """
    Export notebooks in `path` to Python modules.
    
    Examples: 
    
    * `nbz export .`
    
    * `nbz export path/to/notebook`
    
    ---
    
    Learn more [nbz.answer.ai/commands#export](https://nbz.answer.ai/commands#export)
    """    
    if isinstance(path, str): path=pathlib.Path(path)
    if os.environ.get('IN_TEST',0): return
    if not is_nbdev(): raise Exception('`nbdev_export` must be called from a directory within a nbdev project.')
    if procs:
        import nbdev.export
        procs = [getattr(nbdev.export, p) for p in L(procs)]
    files = nbglob(path=path, as_path=True, **kwargs).sorted('name')
    for f in files: nb_export(f, procs=procs)
    add_init(get_config().lib_path)
    _build_modidx()

export.rich_help_panel = 'Exporting'
export.no_args_is_help=True

# %% ../nbs/01_commands.ipynb 13
nb_export_cli = nb_export_cli.__wrapped__ # remove call_parse

@delegates_sorted(nb_export_cli)
def export_nb(
    target: Annotated[pathlib.Path, typer.Argument(help="Path to notebook to export.")],
    name: Annotated[str, typer.Option(help="Name of python script {name}.py to create. Defaults to {target}")] = None,
    lib_path: Annotated[str, typer.Option(help="Path to destination library.  If not in a nbdev project, defaults to current directory.")] = None,
    **kwargs):
    """
    Export a single nbdev notebook to a python script.
    
    Example: 
    
    * `nbz export-nb path/to/notebook.ipynb`
    
    ---
    
    Learn more [nbz.answer.ai/commands#export-nb](https://nbz.answer.ai/commands#export-nb)
    """
    kwargs['nbname'] = target
    nb_export_cli(**kwargs)
    console.print(f'{target} exported')
    
export_nb.rich_help_panel = 'Exporting'
export_nb.no_args_is_help=True    

# %% ../nbs/01_commands.ipynb 14
orig_install = install.__wrapped__ # remove call_parse


def install():
    """
    Installs Quarto and the current library.

    For Linux and Mac will request your system password. For Windows, will print installation instructions. Example:

    * `nbz install`

    ---

    Learn more [nbz.answer.ai/commands#install](https://nbz.answer.ai/commands#install)

    """
    orig_install()

    
install.rich_help_panel = 'Installation'
install.no_args_is_help=False

# %% ../nbs/01_commands.ipynb 15
nbdev_new = cli.nbdev_new.__wrapped__ # remove call_parse

@delegates_sorted(nbdev_new)
def new(
    target: Annotated[pathlib.Path, typer.Argument(help="Path to create project")],
    **kwargs):
    """
    Create an nbdev project. If the target directory does not exist, creates it.
    
    Examples:
    
    * In your current directory: `nbz new .`
    
    * In a different directory: `nbz new my-project`
    
    ---
    
    Learn more [nbz.answer.ai/commands#new](https://nbz.answer.ai/commands#new)
    """
    # Target directory
    if not target.exists(): 
        console.print(f'Creating and changing to {target} directory')
        target.mkdir()
        os.chdir(target)
    olddir = pathlib.Path('.')
    
    "Create an nbdev project."
    from ghapi.core import GhApi
    nbdev_create_config.__wrapped__(**kwargs)
    with console.status('',spinner="dots"):
        cfg = get_config()
        _update_repo_meta(cfg)
        path = Path()

        _ORG_OR_USR,_REPOSITORY = 'fastai','nbdev-template'
        _TEMPLATE = f'{_ORG_OR_USR}/{_REPOSITORY}'
        template = kwargs.get('template', _TEMPLATE)
        try: org_or_usr, repo = template.split('/')
        except ValueError: org_or_usr, repo = _ORG_OR_USR, _REPOSITORY

        tag = kwargs.get('tag', None)
        if tag is None:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                tag = GhApi(gh_host='https://api.github.com', authenticate=False).repos.get_latest_release(org_or_usr, repo).tag_name

        url = f"https://github.com/{org_or_usr}/{repo}/archive/{tag}.tar.gz"
        extract_tgz(url)
        tmpl_path = path/f'{repo}-{tag}'

        cfg.nbs_path.mkdir(exist_ok=True)
        nbexists = bool(first(cfg.nbs_path.glob('*.ipynb')))
        _nbs_path_sufs = ('.ipynb','.css')
        for o in tmpl_path.ls():
            p = cfg.nbs_path if o.suffix in _nbs_path_sufs else path
            if o.name == '_quarto.yml': continue
            if o.name == 'index.ipynb': _render_nb(o, cfg)
            if o.name == '00_core.ipynb' and not nbexists: move(o, p)
            elif not (path/o.name).exists(): move(o, p)
        rmtree(tmpl_path)

        refresh_quarto_yml()
        nbdev_export.__wrapped__()
        nbdev_readme.__wrapped__()

        # return back to the original directory
        os.chdir(olddir)
new.rich_help_panel = 'Getting started'
new.no_args_is_help=False

# %% ../nbs/01_commands.ipynb 16
nbdev_release_git = release.release_git.__wrapped__ # remove call_parse
prompt_help = "Confirm before deploying new version?"

@delegates_sorted(nbdev_release_git)
def release_git(
    confirm_release: Annotated[
        bool,
        typer.Option(help='Confirm before deploying new version',
                     prompt='Okay to release new version on GitHub?')]=False,
    **kwargs):
    """
    Tag and create a release in GitHub for the current version.
    
    Example:
    
    * `nbz release-git`
    """
    if not confirm_release:
        error_console.print('Confirmation to release not granted.')
        raise typer.Abort()
    nbdev_release_git(**kwargs)
release_git.rich_help_panel = 'Releasing versions'
release_git.no_args_is_help=False    
