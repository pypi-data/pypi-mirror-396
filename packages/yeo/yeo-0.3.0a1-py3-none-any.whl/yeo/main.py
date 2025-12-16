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


def create_default_config():
    with open("yeo.json", "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
        f.write("\n")
    print("yeo.json created.")


def init():
    if not Path("yeo.json").exists():
        create_default_config()
    else:
        with open("yeo.json", "r", encoding="utf-8") as f:
            config = json.load(f)
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


def sync():
    """Check if current directory files are in sync with home directory."""
    if not Path("yeo.json").exists():
        print("yeo.json not found. Run 'yeo init' first.")
        return

    with open("yeo.json", "r") as f:
        config_dict = json.load(f)

    config_files = config_dict["paths"]
    synced_files = []
    out_of_sync_files = []
    missing_files = []

    for file in config_files:
        src_file = Path.home() / file
        dest_file = Path.cwd() / Path(file)

    # file to be synced if missing or hash doesn't match
    # if there is a path but no source file, do nothing.
    # but what if there is a file/dir that exists in the destination,
    # but not in source?
    # in other words they have removed their original dotfile, but the copy
    # remains? what is the intended behaviour? probably to remove it.
    # so this is if dest file *does* exist, and source file *does not*.

        if not src_file.exists():
            print(f"Source file not found: {src_file}.")
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
    for file in files_to_copy:
        src_file = Path.home() / file
        dest_file = Path.cwd() / Path(file)
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_file, dest_file)

    print("\nSummary:")
    print(f"In sync: {len(synced_files)}")
    print(f"Out of sync: {len(out_of_sync_files)}")
    print(f"Missing: {len(missing_files)}")
    if files_to_copy:
        print(f"Copied {len(files_to_copy)} file(s)")


def main():
    parser = argparse.ArgumentParser(prog="yeo")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Create a yeo.json file")
    subparsers.add_parser("sync", help="Sync dotfiles to the current directory")

    args = parser.parse_args()

    if args.command == "init":
        init()
    elif args.command == "sync":
        sync()


if __name__ == "__main__":
    main()
