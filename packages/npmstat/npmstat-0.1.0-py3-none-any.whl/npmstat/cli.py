import sys
from typing import Any, Optional

import typer
from rich import print, print_json
from typing_extensions import Annotated

from . import __doc__ as package_doc
from . import api
from ._version import __version__


context_settings = {
    "help_option_names": ["-h", "--help"],
    # "ignore_unknown_options": True,
}

app = typer.Typer(context_settings=context_settings)

state = {"verbose": False}


def vprint(*objects: Any, **kwargs):
    if state.get("verbose"):
        print(*objects, file=sys.stderr, **kwargs)


def version_callback(value: bool):
    if value:
        print(package_doc, file=sys.stderr)
        print(__version__)
        raise typer.Exit()


def clear_cache_callback(value: bool):
    if value:
        api.session.cache.clear()
        print("[bold green]Cache Cleared.")
        raise typer.Exit()


@app.command(no_args_is_help=True, epilog="Docs: https://cssnr.github.io/npmstat/cli/#info")
def info(
    package: Annotated[str, typer.Argument(help="NPM Package Name.")],
    version: Annotated[Optional[str], typer.Argument(help="Package Version")] = None,
    _indent: Annotated[Optional[int], typer.Option("-i", "--indent", help="JSON Indent.")] = 2,
    _purge: Annotated[Optional[bool], typer.Option("-p", "--purge", help="Purge Cache for Request.")] = False,
    _force: Annotated[Optional[bool], typer.Option("-f", "--force-purge", help="Force Purge for Request.")] = False,
):
    """Get Package Information."""
    vprint(f"{package=}", f"{version=}", f"{_indent=}", f"{_purge=}", f"{_force=}", sep="\n")
    r = api.get_package(package, version)
    vprint(f"{r.url=}", f"{r.from_cache=}", sep="\n")
    data = r.json()
    print_json(data=data, indent=_indent or None)


@app.command(no_args_is_help=True, epilog="Docs: https://cssnr.github.io/npmstat/cli/#stats")
def stats(
    package: Annotated[str, typer.Argument(help="NPM Package Name.")],
    period: Annotated[str, typer.Argument(help="Stats Period.")] = "last-day",
    _range: Annotated[bool, typer.Option("--range", "-r", help="Get Range.")] = False,
    _indent: Annotated[Optional[int], typer.Option("-i", "--indent", help="JSON Indent.")] = 2,
    _purge: Annotated[Optional[bool], typer.Option("-p", "--purge", help="Purge Cache for Request.")] = False,
    _force: Annotated[Optional[bool], typer.Option("-f", "--force-purge", help="Force Purge for Request.")] = False,
):
    """Get Package Download Stats."""
    vprint(f"{package=}", f"{period=}", f"{_range=}", f"{_indent=}", f"{_purge=}", f"{_force=}", sep="\n")
    r = api.get_downloads(package, period, get_range=_range)
    vprint(f"{r.url=}", f"{r.from_cache=}", sep="\n")
    data = r.json()
    print_json(data=data, indent=_indent or None)


@app.callback(no_args_is_help=True, epilog="Docs: https://cssnr.github.io/npmstat/cli/")
def main(
    _verbose: Annotated[Optional[bool], typer.Option("-v", "--verbose", help="Verbose Output (jq safe).")] = False,
    _version: Annotated[
        Optional[bool], typer.Option("-V", "--version", help="Show App Version.", callback=version_callback)
    ] = None,
    _cache: Annotated[
        Optional[bool], typer.Option("-C", "--clear-cache", help="Clear Request Cache.", callback=clear_cache_callback)
    ] = None,
):
    """
    NPM Stat CLI

    Example: npmstat -v stats @cssnr/vitepress-swiper
    """
    if _verbose:
        state["verbose"] = _verbose


if __name__ == "__main__":
    app()
