import logging
import json
from pathlib import Path
from vxutils import loggerConfig
from vxsched import app
from argparse import ArgumentParser

DEFAULT_CONFIG = {
    "log_level": "INFO",
    "log_file": "",
}

DEFAULT_HANDLER_FILE = """
import logging
from vxsched import VXEventHandlers, APP, VXEvent,INIT_EVENT,SHUTDOWN_EVENT

handlers = VXEventHandlers()

@handlers("test")
def test_handler(app:VXSched,event: VXEvent) -> None:
    logging.info(f"test for  {event}")

@handlers(INIT_EVENT)
def init_handler(app:VXSched,event: VXEvent) -> None:
    logging.info(f"init for  {event}")

@handlers(SHUTDOWN_EVENT)
def shutdown_handler(app:VXSched,event: VXEvent) -> None:
    logging.info(f"shutdown for  {event}")

APP.event_handlers.merge(handlers)

"""


def init_command(args: ArgumentParser) -> None:
    """Initialize configuration directory"""
    loggerConfig(level="INFO", filename="", force=True)

    target = Path(args.target)
    if not target.exists():
        target.mkdir(parents=True)
    logging.info(f"Initialize config directory {target}")

    for dir in ["log", "mods", "tmp"]:
        dir_path = target / dir
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
        logging.info(f"Initialize directory {dir_path}")

    # Initialize config file
    config_file = target / "config.json"
    if not config_file.exists():
        with open(config_file, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        logging.info(f"Create config file {config_file}")

    if args.examples:
        handler_file = target / "mods" / "handlers.py"
        with open(handler_file, "w", encoding="utf-8") as f:
            f.write(DEFAULT_HANDLER_FILE)
        logging.info(f"Create example handler file {handler_file}")


def main():
    parser = ArgumentParser(description="vxsched CLI")
    subparsers = parser.add_subparsers(title="command", dest="command")

    # Create init directory and example handler file
    init_parser = subparsers.add_parser("init", help="Initialize config directory")
    init_parser.add_argument(
        "-t", "--target", type=str, default=".", help="Target directory path"
    )
    init_parser.add_argument(
        "--examples", action="store_true", help="Create example handler file"
    )

    init_parser.set_defaults(func=init_command)

    # Create run subcommand
    run_parser = subparsers.add_parser("run", help="Run scheduler")
    run_parser.add_argument(
        "-c", "--config", type=str, default="config.json", help="Config file path"
    )
    run_parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Log level",
    )
    run_parser.add_argument("--log-file", type=str, default="", help="Log file path")
    run_parser.add_argument(
        "-m",
        "--mods",
        type=str,
        default="mods/",
        help="Handlers module path",
    )

    run_parser.set_defaults(func=run_command)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def run_command(args: ArgumentParser) -> None:
    """Run scheduler"""
    if args.log_level:
        loggerConfig(level=args.log_level.upper(), filename=args.log_file, force=True)
    try:
        app.load_modules(args.mods)
        app.start()
        app.wait()
    except KeyboardInterrupt:
        pass
    finally:
        app.stop()


if __name__ == "__main__":
    main()
