import os
from airflow.hooks.base import BaseHook
import json
from distutils import util
import logging
from acceldata_sdk.constants import TORCH_CONNECTION_TIMEOUT_MS, TORCH_READ_TIMEOUT_MS


LOGGER = logging.getLogger("initializer")

class Credentials:
    def __init__(self, conn_id):
        connection = BaseHook.get_connection(conn_id)

        self.url = connection.host
        self.access_key = connection.login
        self.secret_key = connection.password
        if connection.extra is not None and len(connection.extra) > 0:
            version_check = json.loads(connection.extra).get('ENABLE_VERSION_CHECK', False)
            torch_connection_timeout_ms = json.loads(connection.extra).get('TORCH_CONNECTION_TIMEOUT_MS', TORCH_CONNECTION_TIMEOUT_MS)
            torch_read_timeout_ms = json.loads(connection.extra).get('TORCH_READ_TIMEOUT_MS', TORCH_READ_TIMEOUT_MS)
        else:
            version_check = False
            torch_connection_timeout_ms = TORCH_CONNECTION_TIMEOUT_MS
            torch_read_timeout_ms = TORCH_READ_TIMEOUT_MS
        if isinstance(version_check, str):
            self.do_version_check = bool(util.strtobool(version_check))
        else:
            self.do_version_check = version_check

        LOGGER.info('do_version_check: %s ', self.do_version_check)

        if isinstance(torch_connection_timeout_ms, str):
            self.torch_connection_timeout_ms = int(torch_connection_timeout_ms)
        else:
            self.torch_connection_timeout_ms = torch_connection_timeout_ms

        if isinstance(torch_read_timeout_ms, str):
            self.torch_read_timeout_ms = int(torch_read_timeout_ms)
        else:
            self.torch_read_timeout_ms = torch_read_timeout_ms

        LOGGER.debug('torch_connection_timeout_ms: %s ', self.torch_connection_timeout_ms)
        LOGGER.debug('torch_read_timeout_ms: %s ', self.torch_read_timeout_ms)

# setup these 4 env vars in your airflow environment. You can create api keys from torch ui's setting page.
def torch_credentials(conn_id=None):
    if conn_id is None:
        creds = {
            'url': os.getenv('TORCH_CATALOG_URL', 'https://torch.acceldata.local:5443'),
            'access_key': os.getenv('TORCH_ACCESS_KEY', 'OY2VVIN2N6LJ'),
            'secret_key': os.getenv('TORCH_SECRET_KEY', 'da6bDBimQfXSMsyyhlPVJJfk7Zc2gs'),
            'do_version_check': os.getenv('ENABLE_VERSION_CHECK', False),
            'torch_connection_timeout_ms': os.getenv('TORCH_CONNECTION_TIMEOUT_MS', TORCH_CONNECTION_TIMEOUT_MS),
            'torch_read_timeout_ms': os.getenv('TORCH_READ_TIMEOUT_MS', TORCH_CONNECTION_TIMEOUT_MS)
        }
    else:
        creds = Credentials(conn_id).__dict__
    return creds
