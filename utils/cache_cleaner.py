import os
import shutil

cache_dir = "./"  # or wherever you set it

# Remove cache directories (not files)
cache_dirs = [".semantic_cache", ".evaluation_cache"]

for cache_name in cache_dirs:
    cache_path = os.path.join(cache_dir, cache_name)
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)  # ← Use rmtree for directories
        print(f"Cleared {cache_path}")
    else:
        print(f"{cache_path} doesn't exist") 