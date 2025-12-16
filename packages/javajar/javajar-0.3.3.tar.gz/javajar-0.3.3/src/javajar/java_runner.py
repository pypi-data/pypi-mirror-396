import subprocess
import sys
import os
from pathlib import Path
from typing import List, Optional
import typer
from typing_extensions import Annotated

from javajar import jdk_manager as jm
from loguru import logger

# ------------------------
# Maven resolution (moved to separate module)
# ------------------------
from javajar.maven_resolver import resolve_from_maven


# ------------------------
# Main commands
# ------------------------

def run_jar(
        jar_file: Annotated[Optional[str], typer.Option("--jar", help="jar的绝对路径")] = None,
        maven: Annotated[Optional[str], typer.Option("--maven", help="jar Maven 坐标 (groupId:artifactId:version")] = None,

        java_version: Annotated[str, typer.Option("--java", help="指定 Java 版本，可选值: 1.8, 11, 17, 21")] = "17",
        java_args: Annotated[str, typer.Option("--java-args", help="传递给 Java 命令的附加参数")] = "",
        jar_args: Annotated[str, typer.Option("--jar-args", help="传递给 JAR 文件的参数")] = "",

        release_repo: Annotated[List[str], typer.Option("--release-repo", help="Release 仓库的基础 URL，可多次指定")] = None,
        snapshot_repo: Annotated[List[str], typer.Option("--snapshot-repo", help="Snapshot 仓库的基础 URL，可多次指定")] = None,
):
    """
    Execute a Java JAR file using 'java -jar' command.
    
    You can either provide a local JAR path (positional argument) or a Maven coordinate via --maven.
    If --maven is used, the tool will look up the artifact in the specified repositories,
    cache it under ~/.ylk_javajar/jar/<artifactId>/<artifactId>-<version>[-classifier].jar, and run it.
    
    Args:
        jar_file: Path to the JAR file to execute (optional when --maven is provided)
        java_args: Additional arguments for the Java command (e.g., -Xmx1g)
        jar_args: Arguments to pass to the JAR file
        verbose: Show verbose output including the full command
        maven: Maven coordinate string
        release_repo: One or more release repository base URLs
        snapshot_repo: One or more snapshot repository base URLs
        :param jar_args:
        :param java_args:
        :param jar_file:
        :param java_version:
        :param snapshot_repo:
        :param release_repo:
        :param maven:
        :param java_distro:
    """

    # Determine jar path either from local file or maven coordinate
    jar_path: Optional[Path] = None

    if maven:
        try:
            release_repo = release_repo or ["https://repo1.maven.org/maven2"]
            snapshot_repo = snapshot_repo or ["https://repo1.maven.org/maven2"]
            jar_path = resolve_from_maven(maven, release_repo, snapshot_repo)
        except Exception as e:
            logger.info(str(e))
            raise typer.Exit(1)
    else:
        if not jar_file:
            logger.info("Error: You must provide either a JAR file path or --maven coordinate.")
            raise typer.Exit(2)
        jar_path = Path(jar_file)

    logger.info(f"JAR file path to execute: {str(jar_path)}")
    # Check if JAR file exists
    if not jar_path.exists():
        logger.info(f"Error: JAR file '{jar_path}' not found!")
        raise typer.Exit(1)

    if not jar_path.is_file():
        logger.info(f"Error: '{jar_path}' is not a file!")
        raise typer.Exit(1)

    if not str(jar_path).lower().endswith('.jar'):
        logger.info(f"Warning: '{jar_path}' does not have a .jar extension")

    # Build the command
    jdk_info = jm.ensure_jdk(java_version)
    if jdk_info is None:
        logger.info(f"Error: Java is not installed or not found in PATH! java_version:{java_version}")
        raise typer.Exit(1)

    logger.info(f"Found matching Java executable path, requested java_version:{java_version}, found java path:{jdk_info.java_exec}")
    cmd = [str(jdk_info.java_exec)]

    # Add Java arguments if provided
    if java_args.strip():
        cmd.extend(java_args.strip().split())

    # Add -jar and the jar file
    cmd.extend(["-jar", str(jar_path.absolute())])

    # Add JAR arguments if provided
    if jar_args.strip():
        cmd.extend(jar_args.strip().split())

    try:
        # Execute the command
        logger.info(f"Executing java command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False)
        # Exit with the same code as the Java process
        if result.returncode != 0:
            raise Exception(f"Java process exited with code {result.returncode}")
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
        raise typer.Exit(130)
    except Exception as e:
        logger.exception(f"Exception executing java command")
        raise typer.Exit(1)
