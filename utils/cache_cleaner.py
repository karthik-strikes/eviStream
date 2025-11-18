from pathlib import Path
import shutil

from config import CACHE_DIRS


def clear_cache_directories(cache_root: str = ".") -> None:
    """
    Remove the configured cache directories relative to cache_root.

    Args:
        cache_root: Base directory that contains the cache folders.
    """
    root_path = Path(cache_root).resolve()
    for cache_dir in CACHE_DIRS:
        cache_path = (root_path / cache_dir).resolve()
        if cache_path.exists() and cache_path.is_dir():
            shutil.rmtree(cache_path)
            print(f"Cleared {cache_path}")
        else:
            print(f"{cache_path} doesn't exist")


if __name__ == "__main__":
    clear_cache_directories()
