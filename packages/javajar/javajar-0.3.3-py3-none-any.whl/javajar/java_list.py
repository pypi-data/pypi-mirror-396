import typer

from javajar import jdk_manager as jm


def java_list():
    """
    列出所有可用的java版本
    """
    javas = jm.java_list()

    if 0 == len(javas):
        typer.echo("没有找到可用的java版本")
        return

    typer.echo("检查到以下可用的java版本")
    for java in javas:
        typer.echo(java)
