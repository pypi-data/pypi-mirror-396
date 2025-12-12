import os
import argparse
from scriptrunner.lib import utilities as util
from scriptrunner.lib.interactions import ScriptRunnerInteractions
from scriptrunner import __version__


display_msg = """
===============================================================================

              GUI software for rendering CLI Python scripts and scheduling runs

===============================================================================
                     Type: scriptrunner to run the software
===============================================================================
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description=display_msg,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--version", action="version",
                        version=f"ScriptRunner {__version__}")
    parser.add_argument("-t", "--stype", type=str, default="cli",
                        help="Specify the type of python script: 'cli' or 'all'")
    parser.add_argument("-b", "--base", type=str, default=None,
                        help="Specify the base folder")
    parser.add_argument("path", type=str, nargs='?', default=None,
                        help="Specify the base folder (positional alternative)")
    return parser.parse_args()


def get_base_folder():
    """Get the base folder config."""
    config_data = util.load_config()
    base_folder = "."
    if config_data is not None:
        try:
            base_folder = config_data["last_folder"]
        except KeyError:
            base_folder = "."
    return os.path.abspath(base_folder)


def main():
    args = parse_args()
    script_type = args.stype
    if args.base is not None:
        base_folder = os.path.abspath(args.base)
    elif args.path is not None:
        base_folder = os.path.abspath(args.path)
    else:
        base_folder = get_base_folder()
    app = ScriptRunnerInteractions(base_folder, script_type)
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.on_exit()


if __name__ == "__main__":
    main()
