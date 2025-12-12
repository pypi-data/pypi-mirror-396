# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import gevent
import socket


def get_open_ports(n):
    sockets = [socket.socket() for _ in range(n)]
    try:
        for s in sockets:
            s.bind(("", 0))
        return [s.getsockname()[1] for s in sockets]
    finally:
        for s in sockets:
            s.close()


def wait_tcp_online(host, port, timeout=10):
    """Wait for a TCP port with a timeout.

    Raises a `gevent.Timeout` if the port was not found.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with gevent.Timeout(timeout):
            while True:
                try:
                    sock.connect((host, port))
                    break
                except ConnectionError:
                    pass
                gevent.sleep(0.1)
    finally:
        sock.close()
