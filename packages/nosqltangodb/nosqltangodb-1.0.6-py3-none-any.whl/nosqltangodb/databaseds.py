"""Run the tango.databaseds.database server with bliss db_access."""

from __future__ import annotations
import sys
import argparse
import logging

from .database import main as base_main


OPTIONS = None


def db_access_str(string: str) -> list[str]:
    """
    Parse db_access with extra params.

    Can be:
        -`beacon`
        -`yaml:/path/to/directory`
    """
    if ":" not in string:
        return [string]
    return string.split(":", 1)


def setup_db_access_path():
    from tango.databaseds import db_access
    from . import db_access as local_db_access

    db_access.__path__ = local_db_access.__path__ + db_access.__path__


HELP_DB_ACCESS = """
Database type.
Can be one of: 'beacon' / 'yaml:path-to-directory'
"""


def main(args: list[str] | None = None):
    global OPTIONS
    if args is None:
        args = sys.argv[1:]

    setup_db_access_path()

    # Display message (used for synchronization with parent process)
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=None, help="Database port")
    p.add_argument(
        "--db_access", required=True, type=db_access_str, help=HELP_DB_ACCESS
    )
    p.add_argument("db_name", help="Database name")
    p.add_argument(
        "argv", nargs=argparse.REMAINDER, help="Extra params passed to the database"
    )
    p.add_argument(
        "--debug_protocol",
        action="store_true",
        help="If defined, log the database protocol calls",
    )
    p.add_argument(
        "-l",
        "--logging_level",
        dest="logging_level",
        type=int,
        default=0,
        help="logging_level 0:WARNING,1:INFO,2:DEBUG",
    )

    options, args = p.parse_known_args(args)

    print("Dict Tango database")
    print(f"Connector: {' '.join(options.db_access)}")
    print(f"Starting on port {options.port}...", flush=True)

    OPTIONS = options

    if options.debug_protocol:
        for module_name in ["_abstract", "yaml", "beacon"]:
            logger = logging.getLogger(f"nosqltangodb.db_access.{module_name}")
            logger.setLevel(logging.DEBUG)

    # Run
    if options.port:
        args.insert(0, "--port=%s" % options.port)
    args.insert(0, "--db_access=%s" % options.db_access[0])
    args += [options.db_name]
    args += [f"-{'v' * options.logging_level}"]
    args += options.argv
    base_main(args)


if __name__ == "__main__":
    main()
