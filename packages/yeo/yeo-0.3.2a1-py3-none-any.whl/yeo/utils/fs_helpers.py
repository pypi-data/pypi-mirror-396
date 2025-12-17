import hashlib
import json
import shutil
from pathlib import Path

from .consts import DEFAULT_CONFIG


def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        file = json.load(f)
    return file


def create_default_config():
    with open("yeo.json", "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
        f.write("\n")
    print("yeo.json created.")


def get_file_hash(file_path):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def copy_files(files):
    for file in files:
        src_file = Path.home() / file
        dest_file = Path.cwd() / Path(file)
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_file, dest_file)
