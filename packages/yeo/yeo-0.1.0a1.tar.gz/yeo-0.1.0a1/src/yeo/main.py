import argparse
import json
import shutil
from pathlib import Path


def create_config_file():
    if Path("yeo.json").exists():
        response = input("yeo.json already exists. Overwrite? (y/n): ")
        if response.lower() != "y":
            print("File not written.")
            return

    with open("yeo.json", "w") as f:
        json.dump(
            {
                "paths": [
                    ".config/nvim/init.lua",
                    ".config/alacritty/alacritty.toml",
                    ".zshrc",
                ]
            },
            f,
            indent=2,
        )
    print("yeo.json created.")


def copy_files():
    with open("yeo.json", "r") as f:
        config_dict = json.load(f)

    config_files = config_dict["paths"]

    for file in config_files:
        src_file = Path.home() / file
        dest_file = Path.cwd() / Path(file)

        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_file, dest_file)


def sync():
    pass


def main():
    parser = argparse.ArgumentParser(prog="yeo")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Create a yeo.json file")
    subparsers.add_parser("sync", help="Sync your dotfiles to the current directory")
    subparsers.add_parser("hello", help="Sync your dotfiles to the current directory")

    args = parser.parse_args()

    if args.command == "init":
        create_config_file()
    elif args.command == "sync":
        copy_files()
    elif args.command == "hello":
        print("Hello world!")


if __name__ == "__main__":
    main()
