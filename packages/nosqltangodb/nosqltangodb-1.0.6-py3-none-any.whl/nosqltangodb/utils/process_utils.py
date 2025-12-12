# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
import psutil
import gevent
import sys
import subprocess


def wait_for(stream, target: bytes, timeout=None):
    """Wait for a specific bytes sequence from a stream.

    Arguments:
        stream: The stream to read
        target: The sequence to wait for
    """
    data = b""
    while target not in data:
        char = stream.read(1)
        if not char:
            raise RuntimeError(
                "Target {!r} not found in the following stream:\n{}".format(
                    target, data.decode()
                )
            )
        data += char


def wait_terminate(
    process: int | subprocess.Process | psutil.Process, timeout: int = 10
):
    """
    Try to terminate a process then kill it.

    This ensure the process is terminated.

    Arguments:
        process: A process object from `subprocess` or `psutil`, or an PID int
        timeout: Timeout to way before using a kill signal

    Raises:
        gevent.Timeout: If the kill fails
    """
    if isinstance(process, int):
        try:
            name = str(process)
            process = psutil.Process(process)
        except Exception:
            # PID is already dead
            return
    else:
        name = repr(" ".join(process.args))
        if process.poll() is not None:
            msg = f"Process {name} already terminated with code {process.returncode}"
            print(msg, file=sys.stderr, flush=True)
            return
    process.terminate()
    try:
        with gevent.Timeout(timeout):
            # gevent timeout have to be used here
            # See https://github.com/gevent/gevent/issues/622
            process.wait()
    except gevent.Timeout:
        msg = f"Process {name} doesn't finish: try to kill it..."
        print(msg, file=sys.stderr, flush=True)
        process.kill()
        with gevent.Timeout(10):
            # gevent timeout have to be used here
            # See https://github.com/gevent/gevent/issues/622
            process.wait()
