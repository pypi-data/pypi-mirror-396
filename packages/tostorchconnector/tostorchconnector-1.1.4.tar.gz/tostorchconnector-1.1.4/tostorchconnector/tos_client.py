import enum
import logging
import os
import gc

from functools import partial
from typing import Optional, List, Tuple, Any

import tos

import tosnativeclient

from . import SequentialTosObjectReader, TosObjectWriter, TosObjectReader
from .tos_object_meta import TosObjectMeta
from .tos_object_reader import TosObjectStream, RangedTosObjectReader
from .tos_object_writer import PutObjectStream

log = logging.getLogger(__name__)

import threading
import weakref
import traceback

_client_lock = threading.Lock()
_client_map = weakref.WeakSet()


def _before_fork():
    with _client_lock:
        clients = list(_client_map)

    if not clients or len(clients) == 0:
        return

    try:
        for client in clients:
            if client._inner_client is not None:
                if hasattr(client._inner_client, 'close') and callable(client._inner_client.close):
                    client._inner_client.close()
                client._inner_client = None

        _reset_client_map()
        gc.collect()
    except Exception as e:
        log.warning(f'failed to clean up native clients, {str(e)}')
        traceback.print_exc()


def _after_fork_in_child():
    _reset_client_map()


def _reset_client_map():
    global _client_map
    with _client_lock:
        _client_map = weakref.WeakSet()


os.register_at_fork(before=_before_fork, after_in_child=_after_fork_in_child)


class ReaderType(enum.Enum):
    SEQUENTIAL = 'Sequential'
    RANGED = 'Ranged'


class CredentialProvider(object):
    def __init__(self, ak: str, sk: str):
        self._ak = ak
        self._sk = sk

    @property
    def ak(self) -> str:
        return self._ak

    @property
    def sk(self) -> str:
        return self._sk


class TosClientConfig(object):
    def __init__(self, part_size: int = 8 * 1024 * 1024,
                 max_retry_count: int = 3, shared_prefetch_tasks: int = 32, max_upload_part_tasks: int = 32):
        self._part_size = part_size
        self._max_retry_count = max_retry_count
        self._shared_prefetch_tasks = shared_prefetch_tasks
        self._max_upload_part_tasks = max_upload_part_tasks

    @property
    def part_size(self) -> int:
        return self._part_size

    @property
    def max_retry_count(self) -> int:
        return self._max_retry_count

    @property
    def shared_prefetch_tasks(self) -> int:
        return self._shared_prefetch_tasks

    @property
    def max_upload_part_tasks(self) -> int:
        return self._max_upload_part_tasks


class TosLogConfig(object):
    def __init__(self, log_dir: str = '',
                 log_file_name: str = '', log_level: Optional[int] = logging.INFO):
        self._log_dir = log_dir
        self._log_file_name = log_file_name
        self._log_level = log_level

    @property
    def log_level(self) -> Optional[int]:
        return self._log_level

    @property
    def log_dir(self) -> str:
        return self._log_dir

    @property
    def log_file_name(self) -> str:
        return self._log_file_name


class TosClient(object):
    def __init__(self, region: str, endpoint: Optional[str] = None, cred: Optional[CredentialProvider] = None,
                 client_conf: Optional[TosClientConfig] = None, use_native_client: bool = True,
                 enable_crc: bool = True):
        self._region = region
        self._endpoint = endpoint
        self._cred = CredentialProvider('', '') if cred is None else cred
        self._client_conf = TosClientConfig() if client_conf is None else client_conf
        self._part_size = self._client_conf.part_size
        self._use_native_client = use_native_client
        self._inner_client = None
        self._client_pid = None
        self._enable_crc = enable_crc

    @property
    def _client(self) -> Any:
        if self._client_pid is None or self._client_pid != os.getpid() or self._inner_client is None:
            with _client_lock:
                if self._client_pid is None or self._client_pid != os.getpid() or self._inner_client is None:
                    if self._use_native_client:
                        self._inner_client = tosnativeclient.TosClient(self._region, self._endpoint, self._cred.ak,
                                                                       self._cred.sk,
                                                                       self._client_conf.part_size,
                                                                       self._client_conf.max_retry_count,
                                                                       shared_prefetch_tasks=self._client_conf.shared_prefetch_tasks,
                                                                       enable_crc=self._enable_crc,
                                                                       max_upload_part_tasks=self._client_conf.max_upload_part_tasks)
                    else:
                        self._inner_client = tos.TosClientV2(self._cred.ak, self._cred.sk, endpoint=self._endpoint,
                                                             region=self._region,
                                                             max_retry_count=self._client_conf.max_retry_count,
                                                             enable_crc=self._enable_crc)
                    self._client_pid = os.getpid()
                    _client_map.add(self)

        assert self._inner_client is not None
        return self._inner_client

    @property
    def use_native_client(self) -> bool:
        return self._use_native_client

    def close(self):
        if isinstance(self._client, tosnativeclient.TosClient):
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

    def get_object(self, bucket: str, key: str, etag: Optional[str] = None,
                   size: Optional[int] = None, reader_type: Optional[ReaderType] = None,
                   buffer_size: Optional[int] = None) -> TosObjectReader:
        log.debug(f'get_object tos://{bucket}/{key}')

        if size is None or etag is None:
            get_object_meta = partial(self.head_object, bucket, key)
        else:
            get_object_meta = lambda: TosObjectMeta(bucket, key, size, etag)

        object_stream = TosObjectStream(bucket, key, get_object_meta, self._client)
        if reader_type is not None and reader_type == ReaderType.RANGED:
            return RangedTosObjectReader(bucket, key, object_stream, buffer_size)
        return SequentialTosObjectReader(bucket, key, object_stream)

    def put_object(self, bucket: str, key: str, storage_class: Optional[str] = None) -> TosObjectWriter:
        log.debug(f'put_object tos://{bucket}/{key}')

        if isinstance(self._client, tosnativeclient.TosClient):
            put_object_stream = self._client.put_object(bucket, key, storage_class=storage_class)
        else:
            put_object_stream = PutObjectStream(
                lambda content: self._client.put_object(bucket, key, storage_class=storage_class, content=content))

        return TosObjectWriter(bucket, key, put_object_stream)

    def head_object(self, bucket: str, key: str) -> TosObjectMeta:
        log.debug(f'head_object tos://{bucket}/{key}')

        if isinstance(self._client, tosnativeclient.TosClient):
            resp = self._client.head_object(bucket, key)
            return TosObjectMeta(resp.bucket, resp.key, resp.size, resp.etag)

        resp = self._client.head_object(bucket, key)
        return TosObjectMeta(bucket, key, resp.content_length, resp.etag)

    def gen_list_stream(self, bucket: str, prefix: str, max_keys: int = 1000,
                        delimiter: Optional[str] = None,
                        continuation_token: Optional[str] = None,
                        list_background_buffer_count: int = 1) -> tosnativeclient.ListStream:
        log.debug(f'gen_list_stream tos://{bucket}/{prefix}')

        if isinstance(self._client, tosnativeclient.TosClient):
            delimiter = delimiter if delimiter is not None else ''
            continuation_token = continuation_token if continuation_token is not None else ''
            return self._client.list_objects(bucket, prefix, max_keys=max_keys, delimiter=delimiter,
                                             continuation_token=continuation_token,
                                             list_background_buffer_count=list_background_buffer_count)
        raise NotImplementedError()

    def list_objects(self, bucket: str, prefix: str, max_keys: int = 1000,
                     continuation_token: Optional[str] = None, delimiter: Optional[str] = None) -> Tuple[
        List[TosObjectMeta], bool, Optional[str]]:
        log.debug(f'list_objects tos://{bucket}/{prefix}')

        if isinstance(self._client, tosnativeclient.TosClient):
            raise NotImplementedError()

        resp = self._client.list_objects_type2(bucket, prefix, max_keys=max_keys, continuation_token=continuation_token,
                                               delimiter=delimiter)
        object_metas = []
        for obj in resp.contents:
            object_metas.append(TosObjectMeta(bucket, obj.key, obj.size, obj.etag))
        return object_metas, resp.is_truncated, resp.next_continuation_token
