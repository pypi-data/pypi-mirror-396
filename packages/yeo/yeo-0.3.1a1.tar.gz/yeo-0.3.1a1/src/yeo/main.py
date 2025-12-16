import argparse
import hashlib
import json
import shutil
from pathlib import Path


DEFAULT_CONFIG = {
        "overwrite": False,
        "paths": [
            ".config/nvim/init.lua",
            ".config/alacritty/alacritty.toml",
            ".zshrc",
        ]
}

DEFAULT_TRACKED = {
        "managed_files": []
}


def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        file = json.load(f)
    return file


def create_default_config():
    with open("yeo.json", "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
        f.write("\n")
    print("yeo.json created.")


def init():
    if not Path("yeo.json").exists():
        create_default_config()
    else:
        config = load_file("yeo.json")
        if config["overwrite"] is True:
            create_default_config()
            print("Overwritten config with default configuration file.")
        else:
            print("Overwritten set to false. File not written.")


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


def sync():
    """Check if current directory files are in sync with home directory."""
    if not Path("yeo.json").exists():
        print("yeo.json not found. Run 'yeo init' first.")
        return

    config = load_file("yeo.json")

    config_files = config["paths"]
    synced_files = []
    out_of_sync_files = []
    missing_files = []

    for file in config_files:
        src_file = Path.home() / file
        dest_file = Path.cwd() / file

        if not src_file.exists():
            print(f"Source file not found: {src_file}")
            continue

        if not dest_file.exists():
            missing_files.append(file)
            print(f"Missing (will copy): {file}")
        else:
            src_hash = get_file_hash(src_file)
            dest_hash = get_file_hash(dest_file)

            if src_hash == dest_hash:
                synced_files.append(file)
                print(f"In sync: {file}")
            else:
                out_of_sync_files.append(file)
                print(f"Out of sync (will copy): {file}")

    files_to_copy = missing_files + out_of_sync_files
    copy_files(files_to_copy)

    print("\nSummary:")
    print(f"In sync: {len(synced_files)}")
    print(f"Out of sync: {len(out_of_sync_files)}")
    print(f"Missing: {len(missing_files)}")
    if files_to_copy:
        print(f"Copied {len(files_to_copy)} file(s)")


"""
def clean():
    config = load_file("yeo.json")
    config_files = config["paths"]
    ignore_list = config["ignore"]

    ignore_paths = [Path(".") / Path(p) for p in ignore_list]

    for file in Path(".").rglob("*"):
        if file.is_file():
            if any(file == p or p in file.parents for p in ignore_paths):
                continue  # skip ignored files
        else:
            print(f"Removing: {file}")
            #file.unlink()
"""


def main():
    parser = argparse.ArgumentParser(prog="yeo")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Create a yeo.json file")
    subparsers.add_parser("sync", help="Sync dotfiles to the current directory")
    subparsers.add_parser("clean", help="Removes dotfiles if not in yeo.json")

    args = parser.parse_args()

    if args.command == "init":
        init()
    elif args.command == "sync":
        sync()
    elif args.command == "clean":
        pass
        #clean()


if __name__ == "__main__":
    main()
