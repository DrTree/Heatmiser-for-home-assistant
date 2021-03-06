import logging
import socket
import json

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


class NeoHub():
    """ Represents a Heatmiser NeoHub. """
    def __init__(self, host, port):
        
        _LOGGER.debug("Creating a Heatmiser NeoHub: %s " % host)
        
        self._host = host
        self._port = port

    def json_request(self, request=None, wait_for_response=False):
        """ Communicate with the json server. """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        try:
            sock.connect((self._host, self._port))
        except OSError:
            sock.close()
            return False

        if not request:
            # no communication needed, simple presence detection returns True
            sock.close()
            return True

        _LOGGER.debug("json_request: %s " % request)

        sock.send(bytearray(json.dumps(request) + "\0\r", "utf-8"))
        try:
            buf = sock.recv(4096)
        except socket.timeout:
            # something is wrong, assume it's offline
            sock.close()
            return False

        # read until a newline or timeout
        buffering = True
        while buffering:
            if "\n" in str(buf, "utf-8"):
                response = str(buf, "utf-8").split("\n")[0]
                buffering = False
            else:
                try:
                    more = sock.recv(4096)
                except socket.timeout:
                    more = None
                if not more:
                    buffering = False
                    response = str(buf, "utf-8")
                else:
                    buf += more

        sock.close()

        response = response.rstrip('\0')

        _LOGGER.debug("json_response: %s " % response)

        return json.loads(response, strict=False)