from pathlib import Path


def get_project_root() -> Path:
    """
    Robustly determines the project root to ensure file paths work consistently
    across Local Development, Docker, and PyPI installations.

    Returns:
        Path: The absolute path to the project root or the current working directory.
    """
    candidate_root = Path(__file__).resolve().parents[2]

    if (candidate_root / "pyproject.toml").exists():
        return candidate_root

    return Path.cwd().resolve()


PROJECT_DIR = get_project_root()
DATA_DIR = PROJECT_DIR / "data"
PLOTS_DIR = DATA_DIR / "plots"

DATA_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
