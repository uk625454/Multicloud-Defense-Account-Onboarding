import socket
import requests
from urllib3.connection import HTTPConnection
from requests.adapters import HTTPAdapter
import logging
import sys

logger = logging.getLogger()


class HTTPAdapterWithSocketOptions(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.socket_options = kwargs.pop("socket_options", None)
        super(HTTPAdapterWithSocketOptions, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.socket_options is not None:
            kwargs["socket_options"] = self.socket_options
        super(HTTPAdapterWithSocketOptions, self).init_poolmanager(*args, **kwargs)


def platform_specific_socket_opts(interval: int) -> list:

    # TCP Keep Alive Probes for different platforms
    platform = sys.platform

    # TCP Keep Alive Probes for Linux
    if (
        platform == "linux"
        and hasattr(socket, "TCP_KEEPIDLE")
        and hasattr(socket, "TCP_KEEPINTVL")
        and hasattr(socket, "TCP_KEEPCNT")
    ):
        logger.info(f"Setting HTTPAdapterWithSocketOptions for platform: {platform}")
        return [
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
            (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, interval),
            (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval),
        ]

    else:
        logger.warning(f"Not setting HTTPAdapterWithSocketOptions for platform: {platform}")
        return []


def keepalive_session():

    # sent TCP keepalives to prevent long running calls
    # from having their socket closed...
    KEEPALIVE_INTERVAL = 10

    adapter = HTTPAdapterWithSocketOptions(
        # pool_connections=1,
        # pool_maxsize=1,
        socket_options=HTTPConnection.default_socket_options
        + platform_specific_socket_opts(KEEPALIVE_INTERVAL),
    )

    if logging.getLevelName(logger.level) == "DEBUG":

        # Enable this (set to == 1) to see HTTP request and response
        HTTPConnection.debuglevel = 0
        requests_log = logging.getLogger("urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    session = requests.Session()
    session.mount("https://", adapter)

    return session