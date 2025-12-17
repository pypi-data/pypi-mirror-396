import os
import shutil
import sys
from pathlib import Path

import click
import tomli
from dotenv import load_dotenv

# Allow running both as package and script
if __package__ is None or __package__ == "":
    # Running as script (e.g. python main.py)
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from logger import logger
    from semgrep_cli import run_semgrep_scan
    from sonarqube_cli import run_sonarqube_scan
    from trivy_cli import run_trivy_scan
else:
    # Running as installed package
    from .logger import logger
    from .semgrep_cli import run_semgrep_scan
    from .sonarqube_cli import run_sonarqube_scan
    from .trivy_cli import run_trivy_scan

# Load environment variables from .env file
load_dotenv()

# Default SonarQube configuration
SONAR_HOST_URL = os.getenv("SONAR_HOST_URL", "https://sonarqube.brainstation-23.xyz")
SONAR_LOGIN = os.getenv("SONAR_LOGIN", "sqa_eb118830887767100489ecfc4b55e42a134bf2cb")


def ensure_reports_dir():
    """Ensure the reports directory exists"""
    reports_dir = Path("code-audit-23/reports")
    reports_dir.mkdir(exist_ok=True, parents=True)
    return reports_dir


def get_sonarqube_credentials():
    """Prompt user for SonarQube credentials if not in environment"""
    click.echo(
        click.style("\n🔑 SonarQube Configuration Required", fg="yellow", bold=True)
    )
    click.echo(click.style("-" * 40, fg="bright_black"))
    sonar_url = click.prompt(
        click.style(
            "Enter SonarQube URL (e.g., http://localhost:9000)", fg="bright_cyan"
        ),
        type=str,
    )
    sonar_token = click.prompt(
        click.style("Enter SonarQube Token (will be hidden)", fg="bright_cyan"),
        hide_input=True,
    )
    click.echo(click.style("✅ Credentials saved for this session\n", fg="green"))
    return sonar_url, sonar_token


def get_version():
    """Get version from package metadata or pyproject.toml"""
    # Try to get version from package metadata first (works in installed package)
    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            ver = version("code-audit-23")
            logger.debug(f"Got version from package metadata: {ver}")
            return ver
        except PackageNotFoundError:
            logger.debug("Package not found in metadata, trying pyproject.toml")
    except ImportError:
        logger.debug("importlib.metadata not available, falling back to pyproject.toml")

    # For development/local execution or when package isn't installed
    try:
        # List of possible locations to find pyproject.toml
        possible_paths = [
            # For development
            Path(__file__).parent.parent / "pyproject.toml",
            # For PyInstaller binary
            (
                Path(sys._MEIPASS) / "pyproject.toml"
                if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
                else None
            ),
            # Current directory as fallback
            Path.cwd() / "pyproject.toml",
        ]

        # Filter out None values and find first existing file
        pyproject_path = next((p for p in possible_paths if p and p.exists()), None)

        if pyproject_path:
            logger.debug(f"Found pyproject.toml at: {pyproject_path}")
            with open(pyproject_path, "rb") as f:
                pyproject = tomli.load(f)
                if "project" in pyproject and "version" in pyproject["project"]:
                    ver = pyproject["project"]["version"]
                    logger.debug(f"Got version from {pyproject_path}: {ver}")
                    return ver
                else:
                    logger.warning(f"Version not found in {pyproject_path}")
        else:
            logger.warning("Could not find pyproject.toml in any expected location")

    except Exception as e:
        logger.warning(f"Error determining version: {e}", exc_info=True)

    logger.warning("Falling back to default version: 0.1.0")
    return "0.1.0"


def show_welcome_banner():
    """Display welcome banner with ASCII art"""
    version = get_version()
    banner = """
     ██████╗ ██████╗ ██████╗ ███████╗    █████╗ ██╗   ██╗██████╗ ██╗████████╗    ██████╗ ██████╗ 
    ██╔════╝██╔═══██╗██╔══██╗██╔════╝   ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝    ╚════██╗╚════██╗
    ██║     ██║   ██║██║  ██║█████╗     ███████║██║   ██║██║  ██║██║   ██║        █████╔╝ █████╔╝
    ██║     ██║   ██║██║  ██║██╔══╝     ██╔══██║██║   ██║██║  ██║██║   ██║       ██╔═══╝  ╚═══██╗
    ╚██████╗╚██████╔╝██████╔╝███████╗   ██║  ██║╚██████╔╝██████╔╝██║   ██║      ███████╗██████╔╝
     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝      ╚══════╝╚═════╝ 
    """
    click.echo(click.style(banner, fg="bright_cyan"))
    click.echo(
        click.style(
            " " * 25 + "🚀  Code Quality & Security Scanner  🚀",
            fg="bright_white",
            bold=True,
        )
    )
    click.echo(click.style(f" " * 35 + f"Version {version}", fg="bright_black"))

    # Ensure reports directory exists
    ensure_reports_dir()


def show_menu():
    """Display main interactive menu"""
    click.echo(click.style("═" * 80, fg="bright_blue"))
    click.echo(
        click.style(
            " " * 22 + "🔍  CODE AUDIT 23 MENU  🔍", fg="bright_cyan", bold=True
        )
    )
    click.echo(click.style("═" * 80, fg="bright_blue"))

    menu_items = [
        (
            "1",
            "Quick Scan (Trivy + Semgrep + SonarQube)",
            "Run all security scans in sequence",
        ),
        (
            "2",
            "Trivy Scan",
            "Scan for vulnerabilities in dependencies and container images",
        ),
        ("3", "Semgrep Scan", "Static code analysis for security issues"),
        ("4", "SonarQube Scan", "Analyze code quality and security issues"),
        ("q", "Quit", "Exit the application"),
    ]

    for num, title, desc in menu_items:
        click.echo(
            click.style(f"  [{num}] ", fg="bright_green", bold=True)
            + click.style(f"{title}", fg="white", bold=True)
        )
        click.echo(click.style(f"      {desc}", fg="bright_black"))
        # click.echo()

    click.echo(click.style("─" * 80, fg="bright_blue"))


def prompt_choice():
    """Prompt user for menu selection with validation"""
    while True:
        choice = (
            click.prompt(
                click.style("\nSelect an option", fg="bright_yellow"),
                type=str,
                default="1",
                show_default=False,
            )
            .strip()
            .lower()
        )

        if choice in ["1", "2", "3", "4", "q", "quit"]:
            return choice
        click.echo(
            click.style(
                "❌ Invalid choice. Please select 1, 2, 3, or q to quit.", fg="red"
            )
        )


def get_project_name():
    """Get project name from config or prompt user"""
    config_dir = Path("code-audit-23")
    config_file = config_dir / "project.txt"

    # Check if config exists
    if config_file.exists():
        try:
            stored_name = config_file.read_text().strip()
            if stored_name:
                logger.debug(f"Found stored project name: {stored_name}")
                return stored_name
        except Exception as e:
            logger.warning(f"Failed to read project name from {config_file}: {e}")

    # Prompt user
    default_name = Path.cwd().name
    click.echo(click.style("\nSet Project Name", fg="yellow", bold=True))
    click.echo(click.style("-" * 40, fg="bright_black"))
    click.echo(
        f"Current detected project name: {click.style(default_name, fg='bright_cyan')}"
    )

    if click.confirm("Do you want to use this name?", default=True):
        project_name = default_name
    else:
        project_name = click.prompt(
            click.style("Enter custom project name", fg="bright_cyan"),
            type=str,
        ).strip()

    # Save choice
    try:
        config_dir.mkdir(exist_ok=True)
        config_file.write_text(project_name)
        click.echo(
            click.style(
                f"✅ Project name '{project_name}' saved to {config_file}", fg="green"
            )
        )
    except Exception as e:
        logger.error(f"Failed to save project name: {e}")
        click.echo(
            click.style(f"⚠️  Failed to save project name preference: {e}", fg="yellow")
        )

    return project_name


def main():
    """Interactive entrypoint for Audit Scanner"""
    # Clear screen and show welcome banner
    click.clear()
    show_welcome_banner()

    # Initialize SonarQube credentials
    global SONAR_HOST_URL, SONAR_LOGIN
    sonar_credentials_provided = bool(SONAR_HOST_URL and SONAR_LOGIN)

    while True:
        try:
            show_menu()
            choice = prompt_choice()
            # click.clear()

            # Handle quit option
            if choice.lower() in ["q", "quit"]:
                # Ask user if they want to clean up generated files
                if click.confirm(
                    click.style(
                        "\nDo you want to clean up generated files (logs/, reports/) before exiting?",
                        fg="yellow",
                    ),
                    default=False,
                ):
                    base_dir = Path("code-audit-23")
                    if base_dir.exists() and base_dir.is_dir():
                        for directory in ["logs", "reports"]:
                            dir_path = base_dir / directory
                            if dir_path.exists() and dir_path.is_dir():
                                try:
                                    shutil.rmtree(dir_path)
                                    click.echo(f"🧹 Removed {directory}/")
                                except Exception as e:
                                    click.echo(f"⚠️  Failed to remove {directory}/: {e}")

                    # Also try to clean up legacy logs/reports if they exist in root
                    for directory in ["logs", "reports"]:
                        dir_path = Path(directory)
                        if dir_path.exists() and dir_path.is_dir():
                            try:
                                shutil.rmtree(dir_path)
                                click.echo(f"🧹 Removed legacy {directory}/")
                            except Exception as e:
                                pass  # Ignore legacy cleanup errors

                click.echo(
                    click.style(
                        "\n👋 Thank you for using Code Audit 23. Goodbye!\n",
                        fg="bright_blue",
                        bold=True,
                    )
                )
                break

            # Determine project name if SonarQube is involved (Quick Scan or SonarQube only)
            project_name = None
            if choice in ["1", "4"]:
                project_name = get_project_name()

            # Run Trivy scan for Quick Scan or Trivy only
            if choice in ["1", "2"]:
                if choice == "1":
                    click.echo("\n" + "─" * 80)
                report_path = "code-audit-23/reports/trivy.sarif"
                click.echo(
                    click.style(
                        f"🔍 Starting Trivy Vulnerability Scan... (Report will be saved to {report_path})",
                        fg="bright_cyan",
                        bold=True,
                    )
                )
                result = run_trivy_scan(report_path)
                if choice in ["1", "2"] and result:
                    click.echo(
                        click.style(
                            f"\n✅ Trivy Scan completed successfully! Report saved to {report_path}",
                            fg="bright_green",
                            bold=True,
                        )
                    )

            # Run Semgrep scan for Quick Scan or Semgrep only
            if choice in ["1", "3"]:
                if choice == "1":
                    click.echo("\n" + "─" * 80)
                click.echo(
                    click.style(
                        "🔍 Starting Semgrep Scan... (Report will be saved to code-audit-23/reports/semgrep.sarif)",
                        fg="bright_cyan",
                        bold=True,
                    )
                )
                result = run_semgrep_scan()
                if choice in ["1", "3"] and result:
                    click.echo(
                        click.style(
                            "\n✅ Semgrep Scan completed successfully! Report saved to code-audit-23/reports/semgrep.sarif",
                            fg="bright_green",
                            bold=True,
                        )
                    )

            # Run SonarQube scan for Quick Scan or SonarQube only
            if choice in ["1", "4"]:

                if choice == "1":
                    click.echo("\n" + "─" * 80)
                click.echo(
                    click.style(
                        "🚀 Starting SonarQube Scan...", fg="bright_cyan", bold=True
                    )
                )
                try:
                    # Get credentials if not already provided
                    if not sonar_credentials_provided:
                        SONAR_HOST_URL, SONAR_LOGIN = get_sonarqube_credentials()
                        sonar_credentials_provided = True

                    result = run_sonarqube_scan(
                        sonar_url=SONAR_HOST_URL,
                        token=SONAR_LOGIN,
                        project_key=project_name,
                        sources=".",
                    )
                except Exception as e:
                    logger.error(f"SonarQube scan failed: {e}")
                    click.echo(
                        click.style(f"❌ SonarQube scan failed: {str(e)}", fg="red")
                    )
                    if click.confirm(
                        click.style(
                            "Do you want to update SonarQube credentials?", fg="yellow"
                        )
                    ):
                        sonar_url, sonar_token = get_sonarqube_credentials()
                        SONAR_HOST_URL = sonar_url
                        SONAR_LOGIN = sonar_token
                        # Retry the scan with new credentials
                        result = run_sonarqube_scan(
                            sonar_url=SONAR_HOST_URL,
                            token=SONAR_LOGIN,
                            project_key=project_name,
                            sources=".",
                        )
                if choice in ["1", "4"] and result:
                    click.echo(
                        click.style(
                            "\n✅ SonarQube Scan completed successfully!",
                            fg="bright_green",
                            bold=True,
                        )
                    )

            # Show completion message for Quick Scan
            if choice == "1":
                click.echo(click.style("=" * 80 + "\n", fg="bright_green"))
                click.echo(
                    click.style(
                        "✅ Quick Scan completed successfully!",
                        fg="bright_green",
                        bold=True,
                    )
                )
                click.echo(click.style("=" * 80 + "\n", fg="bright_green"))

            # # Ask if user wants to perform another scan
            # click.echo("\n" + "─" * 80)
            # if not click.confirm(click.style("Would you like to perform another scan?", fg='bright_yellow')):
            #     break

            # click.clear()
            # show_welcome_banner()

        except Exception as e:
            logger.error(f"Scan failed: {e}")
            click.echo(click.style("\n❌ An error occurred during the scan.", fg="red"))
            if not click.confirm(
                click.style("Would you like to try again?", fg="yellow")
            ):
                click.echo(
                    click.style(
                        "\n👋 Thank you for using Code Audit 23. Goodbye!\n",
                        fg="bright_blue",
                        bold=True,
                    )
                )
                break
            # click.clear()
            # show_welcome_banner()


if __name__ == "__main__":
    main()
