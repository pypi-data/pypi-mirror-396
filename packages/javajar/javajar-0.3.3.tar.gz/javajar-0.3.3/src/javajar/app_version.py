import importlib
import typer
import importlib.metadata


def show_version():
    """显示版本信息"""
    version = importlib.metadata.version("javajar")
    typer.echo(f"{version}")
