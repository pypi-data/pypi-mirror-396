import typer

from .circuity import circuity


app = typer.Typer()
app.command()(circuity)


if __name__ == "__main__":
    app()
