from pathlib import Path
import os


DEFAULT_API_URL = "https://app.artefacts.com/api"

SUPPORTED_FRAMEWORKS = [
    "ros2:iron",
    "ros2:humble",
    "ros2:galactic",
    "maniskill:challenge2022",
    "None",
    "none",
    "null",
    None,
]

DEPRECATED_FRAMEWORKS = {
    "ros2:0": "ros2:galactic",
}

HOME = os.path.expanduser("~")
CONFIG_DIR = f"{HOME}/.artefacts"
CACHE_DIR = os.path.join(CONFIG_DIR, "cache")
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

CONFIG_PATH = f"{CONFIG_DIR}/config"
LAST_RUN_MARKER_PATH = os.path.join(CACHE_DIR, "last_run_marker")
LAST_VERSION_MEMO_PATH = os.path.join(CACHE_DIR, "last_version_memo")
