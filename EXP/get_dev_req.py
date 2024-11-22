import pkg_resources  # type: ignore
import subprocess
import sys
from typing import Any, Set


def get_needed_packages() -> Set[str]:
    """Return a set of needed packages"""
    return {
        "fastapi",
        "requests",
        "pydantic",
        "boto3",
        "mangum",
        "openai",
        "uvicorn",
        "python-dotenv",
    }


def generate_requirements() -> Any:
    """
    Generate requirements.txt by:
    1. Getting all installed packages
    2. Filtering for only the ones used in the project
    3. Writing them to requirements.txt with versions in sorted order
    """
    needed_packages = get_needed_packages()

    # Get all installed packages with versions
    installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

    # Create sorted requirements list
    requirements = []
    for package in needed_packages:
        if package in installed:
            requirements.append(f"{package}=={installed[package]}")
        else:
            print(f"Warning: {package} is not installed")

    # Sort requirements alphabetically
    requirements.sort()

    # Write sorted requirements to file
    with open("requirements.txt", "w") as f:
        for req in requirements:
            f.write(f"{req}\n")

    print("Sorted requirements.txt has been generated!")


def install_missing_packages() -> Any:
    """Install any missing packages from the needed list"""
    needed_packages = sorted(list(get_needed_packages()))  # Sort installation list too

    for package in needed_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == "__main__":
    print("Checking for missing packages...")
    install_missing_packages()
    print("\nGenerating requirements.txt...")
    generate_requirements()
