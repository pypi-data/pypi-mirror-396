import typer
from javajar.java_runner import run_jar
from javajar.java_list import java_list
from javajar.app_version import show_version

app = typer.Typer()

# Add version command
app.command("version")(show_version)

# Add Java JAR execution command
app.command("run")(run_jar)

# Add Java check command
app.command("java-list")(java_list)

if __name__ == "__main__":
    app()
