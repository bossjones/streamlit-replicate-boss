#!/usr/bin/env python3
"""
Initialize a new Streamlit project with uv.

Usage:
    ./init_streamlit_project.py my-app
    ./init_streamlit_project.py my-app --with-tests --with-docker
"""

import argparse
import subprocess
import sys
from pathlib import Path

PYPROJECT_TEMPLATE = '''\
[project]
name = "{name}"
version = "0.1.0"
description = "A Streamlit application"
requires-python = ">=3.10"
dependencies = [
    "streamlit>=1.40.0",
    "pandas>=2.0.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "ruff>=0.8.0",
]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
'''

APP_TEMPLATE = '''\
"""Main Streamlit application."""

import streamlit as st

st.set_page_config(
    page_title="{title}",
    page_icon="📊",
    layout="wide",
)


def main():
    st.title("{title}")
    st.write("Welcome to your Streamlit app!")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        option = st.selectbox("Choose an option", ["Option A", "Option B", "Option C"])
        st.write(f"Selected: {{option}}")

    # Main content
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input")
        name = st.text_input("Enter your name")
        if name:
            st.write(f"Hello, {{name}}!")

    with col2:
        st.subheader("Output")
        if st.button("Click me"):
            st.balloons()
            st.success("Button clicked!")


if __name__ == "__main__":
    main()
'''

TEST_TEMPLATE = '''\
"""Tests for the Streamlit app."""

import pytest
from streamlit.testing.v1 import AppTest


def test_app_loads():
    """Test that the app loads without errors."""
    at = AppTest.from_file("app.py")
    at.run()
    assert not at.exception


def test_title_displayed():
    """Test that the title is displayed."""
    at = AppTest.from_file("app.py")
    at.run()
    assert len(at.title) > 0
'''

CONFTEST_TEMPLATE = '''\
"""Pytest configuration and fixtures."""

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app_test():
    """Provide a fresh AppTest instance."""
    at = AppTest.from_file("app.py")
    at.run()
    return at
'''

DOCKERFILE_TEMPLATE = '''\
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy app code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run app
CMD ["uv", "run", "streamlit", "run", "app.py", \\
     "--server.port=8501", "--server.address=0.0.0.0", \\
     "--server.headless=true"]
'''

DOCKERIGNORE_TEMPLATE = '''\
.git
.gitignore
__pycache__
*.pyc
*.pyo
.pytest_cache
.ruff_cache
.mypy_cache
.venv
venv
*.egg-info
dist
build
.streamlit/secrets.toml
'''

GITIGNORE_TEMPLATE = '''\
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# uv
.uv/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Streamlit
.streamlit/secrets.toml

# OS
.DS_Store
Thumbs.db
'''

CONFIG_TEMPLATE = '''\
[server]
headless = true
runOnSave = true
port = 8501

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
'''


def run_command(cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a shell command."""
    try:
        subprocess.run(cmd, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Exit code: {e.returncode}")
        return False


def create_project(
    name: str,
    with_tests: bool = True,
    with_docker: bool = False,
) -> None:
    """Create a new Streamlit project."""
    project_dir = Path(name)

    if project_dir.exists():
        print(f"Error: Directory '{name}' already exists")
        sys.exit(1)

    # Create directory structure
    project_dir.mkdir(parents=True)
    (project_dir / ".streamlit").mkdir()

    if with_tests:
        (project_dir / "tests").mkdir()

    # Create title from name
    title = name.replace("-", " ").replace("_", " ").title()

    # Write files
    (project_dir / "pyproject.toml").write_text(PYPROJECT_TEMPLATE.format(name=name))
    (project_dir / "app.py").write_text(APP_TEMPLATE.format(title=title))
    (project_dir / ".gitignore").write_text(GITIGNORE_TEMPLATE)
    (project_dir / ".streamlit" / "config.toml").write_text(CONFIG_TEMPLATE)

    if with_tests:
        (project_dir / "tests" / "__init__.py").write_text("")
        (project_dir / "tests" / "test_app.py").write_text(TEST_TEMPLATE)
        (project_dir / "tests" / "conftest.py").write_text(CONFTEST_TEMPLATE)

    if with_docker:
        (project_dir / "Dockerfile").write_text(DOCKERFILE_TEMPLATE)
        (project_dir / ".dockerignore").write_text(DOCKERIGNORE_TEMPLATE)

    # Initialize with uv
    print(f"\n📦 Initializing project with uv...")
    if not run_command(["uv", "sync"], cwd=project_dir):
        print("Warning: Failed to run 'uv sync'. You may need to run it manually.")

    # Print success message
    print(f"\n✅ Created Streamlit project: {name}")
    print(f"\n📁 Project structure:")
    print(f"   {name}/")
    print(f"   ├── app.py")
    print(f"   ├── pyproject.toml")
    print(f"   ├── .gitignore")
    print(f"   ├── .streamlit/")
    print(f"   │   └── config.toml")
    if with_tests:
        print(f"   └── tests/")
        print(f"       ├── conftest.py")
        print(f"       └── test_app.py")
    if with_docker:
        print(f"   ├── Dockerfile")
        print(f"   └── .dockerignore")

    print(f"\n🚀 Next steps:")
    print(f"   cd {name}")
    print(f"   uv run streamlit run app.py")
    if with_tests:
        print(f"   uv run pytest  # Run tests")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize a new Streamlit project with uv"
    )
    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "--with-tests",
        action="store_true",
        default=True,
        help="Include test setup (default: True)",
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip test setup",
    )
    parser.add_argument(
        "--with-docker",
        action="store_true",
        help="Include Docker files",
    )

    args = parser.parse_args()

    with_tests = args.with_tests and not args.no_tests

    create_project(
        name=args.name,
        with_tests=with_tests,
        with_docker=args.with_docker,
    )


if __name__ == "__main__":
    main()
