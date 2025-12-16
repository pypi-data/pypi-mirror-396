import subprocess
import sys
from pathlib import Path

import click

from pytest_tui_runner.logging import logger, setup_logger
from pytest_tui_runner.paths import Paths, find_project_root_by_folder
from pytest_tui_runner.ui.tui.app import TestRunnerApp


@click.group(
    help=(
        "pytest-tui-runner provides a text-based interface (TUI) for selecting and running pytest tests.\n\n"
        "Basic usage:\n\n"
        "  pytest-tui init [PROJECT_PATH]   Create the configuration folder and config.yaml\n\n"
        "  pytest-tui run [PROJECT_PATH]    Launch the TUI to execute tests\n\n"
        "If PROJECT_PATH is omitted, commands operate on the current directory, or\n"
        "in the case of 'run', the tool attempts to automatically locate the project root\n"
        "by searching for a folder named '.pytest_tui_runner' in the current directory\n"
        "and all parent directories.\n\n"
        "Run 'pytest-tui <command> --help' for details."
    ),
)
def cli() -> None:
    """CLI for pytest-tui-runner plugin."""


# ---------------------------------------------------------------------------
# INIT COMMAND
# ---------------------------------------------------------------------------


@cli.command(
    help=(
        "Initialize the project for use with pytest-tui-runner.\n\n"
        "This command creates the folder .pytest_tui_runner and a default config.yaml.\n"
        "It does NOT launch the TUI.\n\n"
        "PROJECT_PATH is optional and defaults to the current directory."
    ),
    epilog=(
        "Examples:\n"
        "  pytest-tui init\n"
        "      Initialize the current directory.\n\n"
        "  pytest-tui init C:/my/project\n"
        "      Initialize a specific project directory."
    ),
)
@click.argument("project_path", required=False, type=click.Path(file_okay=False))
def init(project_path: str | None) -> None:
    """Prepare the configuration folder and files but do not run the application."""
    if project_path:
        root = Path(project_path).resolve()
    else:
        root = Path.cwd().resolve()

    setup_project(root)

    click.echo("\nInitialization complete.")

    click.echo("A default configuration has been created, but it must be adjusted")
    click.echo("so that the test structure matches your project.")
    click.echo()
    click.echo("You can now start the interface using:")
    click.echo(f"  pytest-tui run {root}")
    click.echo()


# ---------------------------------------------------------------------------
# RUN COMMAND
# ---------------------------------------------------------------------------


@cli.command(
    help=(
        "Run the text-based interface (TUI) for selecting and executing pytest tests.\n\n"
        "PROJECT_PATH (optional):\n"
        "  Path to the root of the user's project, or any subdirectory inside it.\n"
        "  The path is used only as a starting point for detecting the actual project root.\n\n"
        "Project root detection:\n"
        "  The tool searches upward from the starting directory and looks for a folder\n"
        "  named '.pytest_tui_runner'. The directory containing this folder is considered\n"
        "  the project root.\n\n"
        "This means that both of the following work:\n\n"
        "  • providing the real project root directly,\n\n"
        "  • providing any path inside the project (the root will be found automatically).\n\n"
        "If PROJECT_PATH is omitted, the search begins in the current working directory.\n"
        "If no project root is found, the command exits with an error and suggests\n"
        "running 'pytest-tui init' to create the configuration folder."
    ),
    epilog=(
        "Examples:\n"
        "  pytest-tui run\n"
        "      Launch the TUI for the nearest configured project.\n\n"
        "  pytest-tui run C:/path/to/project\n"
        "      Search for '.pytest_tui_runner' upward from the provided directory and\n"
        "      launch the TUI using the detected project root."
    ),
)
@click.argument("project_path", required=False, type=click.Path(exists=True, file_okay=False))
def run(project_path: str | None) -> None:
    """Launch the TUI for running tests."""
    try:
        # -----------------------------------------
        # Determine the starting directory
        # -----------------------------------------
        if project_path:
            start_path = Path(project_path).resolve()
        else:
            start_path = Path.cwd().resolve()

        # -----------------------------------------
        # Search for project root from that location
        # -----------------------------------------
        root = find_project_root_by_folder(start_path, [Paths.APP_FOLDER])
        if root is None:
            logger.error(
                f"Could not locate project root starting from '{start_path}'.\n"
                "Hint: run 'pytest-tui init' in your project to create the configuration folder.",
            )
            sys.exit(1)

        # Now we know the correct root → set it
        Paths.set_user_root(root)

        # -----------------------------------------
        # Start application
        # -----------------------------------------
        setup_logger()
        logger.info("=============================== NEW RECORD ===============================")
        logger.debug("---------------------- APPLICATION PREPARATION ----------------------")
        logger.info(f"Path to user's project found: '{root}'")

        logger.info("▶️ Starting the application...")
        app = TestRunnerApp()
        app.run()

    except subprocess.CalledProcessError as e:
        logger.error(f"Error launching the application: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# SHARED INITIALIZATION LOGIC
# ---------------------------------------------------------------------------


def setup_project(user_root: Path) -> None:
    """Create .pytest_tui_runner and config.yaml in the selected directory."""
    Paths.set_user_root(user_root)

    target_dir = Paths.app_dir()
    config_file = Paths.config()

    # Create main folder
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
        click.echo(f"✅ Folder created: {target_dir}")
    else:
        click.echo(f"ℹ️ Folder '{target_dir}' already exists.")

    # Create configuration file
    if not config_file.exists():
        config_file.write_text(
            """categories:
  - label: "Your category label"
    subcategories:
      - label: "Your subcategory label"
        tests:
          - label: "Your test label"
            test_name: "your_test_name"
""",
        )
        click.echo(f"✅ Created config file with example data: {config_file}")
    else:
        click.echo(f"ℹ️ File '{config_file}' already exists.")
