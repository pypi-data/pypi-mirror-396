# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
import os
import typing
import contextlib
import subprocess
import atexit
import gevent

from .utils import process_utils
from .utils import tango_utils
from .utils import net_utils

NOSQLTANGODB = "NosqlTangoDB"


class Server:
    def __init__(self, port):
        self._port = port

    @property
    def port(self):
        return self._port


@contextlib.contextmanager
def running_db(
    name,
    db_access: str,
    port: typing.Union[int, str] = "auto",
    debug_protocol=False,
    yaml_root: str | None = None,
    update_tango_host=True,
    timeout=10,
):
    """
    Context manager starting the database from Python.

    It uses subprocess to spawn the database.

    The result is shared when the service is reachable.

    Arguments:
        name: Tango name for the database. Usually "2".
        db_access: Kind of connection. One of "yaml", or "beacon"
        port: Num of port to use for the database. If "auto" the port is
              allocated dynamically
        debug_protocol: If true the database will log debug information to
                        trace the DB protocol
        yaml_root: Location of the initial data if `db_access` is "yaml"
        update_tango_host: If true, TANGO_HOST is updated with the DB port
        timeout: Timeout in second to wait the availability of the service

    Yield:
        A server object sharing the port

    Exception:
        ValueError: If a parameter is wrong
        RuntimeError: If the process fails
    """
    if port == "auto":
        port = net_utils.get_open_ports(1)[0]
    elif not isinstance(port, int):
        raise ValueError(f"'auto' or int is expected for port. Found '{port}'")

    if db_access == "yaml":
        if yaml_root is None:
            raise ValueError("With yaml DB yaml_root have to be specified")
        db_access = f"{db_access}:{yaml_root}"

    args = [NOSQLTANGODB, f"--port={port}"]
    args.append(f"--db_access={db_access}")
    if debug_protocol:
        args.append("--debug_protocol")
    args.append(name)

    if update_tango_host:
        os.environ["TANGO_HOST"] = "localhost:%d" % port

    proc = subprocess.Popen(args)
    with gevent.Timeout(seconds=timeout, exception=RuntimeError):
        tango_utils.wait_tango_db(port=port, db=2)
    try:
        s = Server(port)
        yield s
    finally:
        atexit._run_exitfuncs()
        process_utils.wait_terminate(proc)
