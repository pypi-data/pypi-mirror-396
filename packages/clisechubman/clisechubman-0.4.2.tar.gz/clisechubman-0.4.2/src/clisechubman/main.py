import logging

import typer

from .clisechubman import _apply_rules, _validate_rules

logging.basicConfig(level=logging.INFO)


app = typer.Typer(invoke_without_command=True)


@app.callback()
def callback(ctx: typer.Context) -> None:
    """
    A CLI to help manage findings from AWS Security Hub
    """
    if ctx.invoked_subcommand is None:
        typer.echo("A CLI to help manage findings from AWS Security Hub")


@app.command()
def validate_rules(rules: str = typer.Argument("rules.yaml")) -> None:
    """Validate the rules defined in the given YAML file.

    Parameters
    ----------
    rules : str, optional
        Path to the rules YAML file, by default "rules.yaml".

    Raises
    ------
    typer.Exit
        Exit with code 1 if validation fails.
    """

    if not _validate_rules(rules):
        raise typer.Exit(code=1)


@app.command()
def apply_rules(rules: str = typer.Argument("rules.yaml")) -> None:
    """Apply the rules defined in the given YAML file.

    Parameters
    ----------
    rules : str, optional
        Path to the rules YAML file, by default "rules.yaml".
    """
    _apply_rules(rules)
