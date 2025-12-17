import logging
from typing import Optional

from . import TosObjectReader, TosObjectWriter
from .tos_client import CredentialProvider, TosClientConfig, TosClient, TosLogConfig, ReaderType
from .tos_common import parse_tos_url

log = logging.getLogger(__name__)


class TosCheckpoint(object):
    def __init__(self, region: str,
                 endpoint: Optional[str] = None,
                 cred: Optional[CredentialProvider] = None,
                 client_conf: Optional[TosClientConfig] = None,
                 use_native_client=True,
                 enable_crc=True):
        self._region = region
        self._endpoint = endpoint
        self._cred = cred
        self._client_conf = client_conf
        self._client = TosClient(self._region, self._endpoint, self._cred, self._client_conf, use_native_client,
                                 enable_crc)
        log.info('TosCheckpoint init tos client succeed')

    def reader(self, url: str, reader_type: Optional[ReaderType] = None,
               buffer_size: Optional[int] = None) -> TosObjectReader:
        bucket, key = parse_tos_url(url)
        return self._client.get_object(bucket, key, reader_type=reader_type, buffer_size=buffer_size)

    def writer(self, url: str) -> TosObjectWriter:
        bucket, key = parse_tos_url(url)
        return self._client.put_object(bucket, key)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            try:
                log.info(f'Exception occurred before closing tos client: {exc_type.__name__}: {exc_val}')
            except:
                pass
            finally:
                self.close()
        else:
            self.close()
