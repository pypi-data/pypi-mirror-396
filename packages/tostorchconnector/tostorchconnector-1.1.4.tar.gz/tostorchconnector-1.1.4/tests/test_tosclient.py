import os
import pickle
import unittest
import uuid

from tosnativeclient import TosClient, TosException


class TestTosClient(unittest.TestCase):
    def test_pickle(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        tos_client = TosClient(region, endpoint, ak, sk)
        pickled_tos_client = pickle.dumps(tos_client)
        assert isinstance(pickled_tos_client, bytes)
        unpickled_tos_client = pickle.loads(pickled_tos_client)

        self._test_list_objects(bucket, unpickled_tos_client)
        self._test_write_read_object(bucket, unpickled_tos_client)

    def test_list_objects(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        tos_client = TosClient(region, endpoint, ak, sk)
        self._test_list_objects(bucket, tos_client)

    def test_write_read_object(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        tos_client = TosClient(region, endpoint, ak, sk)

        self._test_write_read_object(bucket, tos_client)

    def _test_list_objects(self, bucket, tos_client):
        list_stream = tos_client.list_objects(bucket, '', max_keys=1000)
        count = 0
        try:
            for objects in list_stream:
                for content in objects.contents:
                    count += 1
                    print(content.key, content.size)
                    output = tos_client.head_object(bucket, content.key)
                    assert output.etag == content.etag
                    assert output.size == content.size

            print(count)
        except TosException as e:
            print(e.args[0].message)

    def _test_write_read_object(self, bucket, tos_client):
        key = str(uuid.uuid4())
        read_stream = tos_client.get_object(bucket, key, '', 1)

        try:
            offset = 0
            while 1:
                chunk = read_stream.read(offset, 65536)
                if not chunk:
                    break
                offset += len(chunk)
                print(chunk)
        except TosException as e:
            print(e.args[0].status_code)

        write_stream = tos_client.put_object(bucket, key, '')
        write_stream.write(b'hello world')
        write_stream.write(b'hello world')
        write_stream.close()

        output = tos_client.head_object(bucket, key)
        print(output.etag, output.size)

        read_stream = tos_client.get_object(bucket, key, output.etag, output.size)
        try:
            offset = 0
            while 1:
                chunk = read_stream.read(offset, 65536)
                if not chunk:
                    break
                offset += len(chunk)
                print(chunk)
        except TosException as e:
            print(e.args[0].status_code)
