import os
import pickle
import unittest

from tostorchconnector import TosMapDataset, TosIterableDataset, TosCheckpoint
from tostorchconnector.tos_client import CredentialProvider, ReaderType

USE_NATIVE_CLIENT = True
READER_TYPE = ReaderType.SEQUENTIAL


class TestTosDataSet(unittest.TestCase):

    def test_from_urls(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        datasets = TosMapDataset.from_urls(iter([f'tos://{bucket}/key1', f'tos://{bucket}/key2', f'{bucket}/key3']),
                                           region=region, endpoint=endpoint, cred=CredentialProvider(ak, sk),
                                           use_native_client=USE_NATIVE_CLIENT)

        for i in range(len(datasets)):
            print(datasets[i].bucket, datasets[i].key)

    def test_pickle(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        datasets = TosMapDataset.from_prefix(f'tos://{bucket}', region=region,
                                             endpoint=endpoint, cred=CredentialProvider(ak, sk),
                                             use_native_client=USE_NATIVE_CLIENT)
        pickled_datasets = pickle.dumps(datasets)
        assert isinstance(pickled_datasets, bytes)
        unpickled_datasets = pickle.loads(pickled_datasets)
        i = 0
        for dataset in unpickled_datasets:
            print(dataset.bucket, dataset.key)
            i += 1
        print(i)

        pickled = pickle.dumps(unpickled_datasets._data_set)
        assert isinstance(pickled, bytes)

    def test_from_prefix(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        datasets = TosMapDataset.from_prefix(f'tos://{bucket}', region=region,
                                             endpoint=endpoint, cred=CredentialProvider(ak, sk),
                                             use_native_client=USE_NATIVE_CLIENT)

        count = 0
        for i in range(len(datasets)):
            dataset = datasets[i]
            print(dataset.bucket, dataset.key)
            count += 1
            dataset.close()
            # if i == 1:
            #     item = datasets[i]
            #     data = item.read(100)
            #     print(data)
            #     print(len(data))

        print(count)

    def test_from_prefix_iter(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        datasets = TosIterableDataset.from_prefix(f'tos://{bucket}', region=region,
                                                  endpoint=endpoint, cred=CredentialProvider(ak, sk),
                                                  use_native_client=USE_NATIVE_CLIENT, reader_type=ReaderType.RANGED)
        i = 0
        for dataset in datasets:
            print(dataset.bucket, dataset.key)
            # if dataset.key == 'tosutil':
            #     with open('logs/tosutil', 'wb') as f:
            #         while 1:
            #             chunk = dataset.read(8192)
            #             print(len(chunk))
            #             if not chunk:
            #                 break
            #             f.write(chunk)
            dataset.close()
            i += 1
        print(i)

    def test_checkpoint(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        checkpoint = TosCheckpoint(region, endpoint, cred=CredentialProvider(ak, sk),
                                   use_native_client=USE_NATIVE_CLIENT)
        url = f'tos://{bucket}/key1'
        print('test sequential')
        with checkpoint.writer(url) as writer:
            writer.write(b'hello world')
            writer.write(b'hi world')

        with checkpoint.reader(url) as reader:
            print(reader.read())

        with checkpoint.reader(url) as reader:
            data = reader.read(5)
            print(data)
            print(reader.read())
            reader.seek(0)
            data = reader.read(5)
            print(data)

        print('test ranged')
        with checkpoint.reader(url, reader_type=ReaderType.RANGED) as reader:
            data = reader.read(5)
            print(data)
            print(reader.read())
            reader.seek(0)
            data = reader.read(5)
            print(data)
