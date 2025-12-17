"""CLI entrypoint.

Use ``python -m time_split --help`` to get started.
"""

try:
    import click as _c
    from rics.click import _alias_command_group
    from time_split_app.cli import main as _app_main
except ImportError as e:
    name = "time-split[app]"
    exc = ImportError(f"Install `{name}` to use.", name=name)
    exc.add_note(f"Package `{e.name}` not installed. Run:\n `pip install {name}`\nto use the CLI entrypoint.")
    raise exc from e


@_c.group(
    name="time-split",
    epilog="Visit https://time-split.readthedocs.io/ for help.",
    cls=_alias_command_group.AliasedCommandGroup,
)
def main() -> None:
    """See https://time-split.readthedocs.io/."""


main.add_command(_app_main)

if __name__ == "__main__":
    main()
