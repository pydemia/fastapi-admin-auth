import boto3
import os

from typing import Callable, Iterator, Optional, List, ContextManager, Tuple
from urllib.parse import urlparse
import tempfile
import yaml

from sqlalchemy.orm import Session
from sqlalchemy import (
    Column,
    String,
)
from ..database import Base, Database
from ..types.exceptions import HandledException, ResponseCode


__all__ = [
    "StorageList",
    "Storage",
]


_GCS_PREFIX = "gs://"
_S3_PREFIX = "s3://"
_BLOB_RE = "https://(.+?).blob.core.windows.net/(.+)"
_LOCAL_PREFIX = "file://"
_RUNTIME_PREFIX = "runtime_datas/"
_URI_RE = "https?://(.+)/(.+)"
_HTTP_PREFIX = "http(s)://"
_HEADERS_SUFFIX = "-headers"


class StorageList(Base):
    __tablename__ = "STORAGE_LIST"
    __table_args__ = {'extend_existing': True}

    storage_nm = Column(String(60), primary_key=True, nullable=False)
    type = Column(String(8), nullable=False)
    nfs_mount_path = Column(String(100), nullable=False)
    accesskey = Column(String(100), nullable=False)
    secretkey = Column(String(100), nullable=False)
    endpoint = Column(String(100), nullable=False)


# 참조 코드: https://github.com/kserve/kserve/blob/master/python/kserve/kserve/storage.py
class Storage:
    @staticmethod
    def download(uri: str, out_dir: str = None, session: Session = None) -> list:
        if uri.startswith(_RUNTIME_PREFIX):
            return Storage._download_runtime_data(uri, session)
        else:
            is_local = False
            if uri.startswith(_LOCAL_PREFIX):
                is_local = True
            if out_dir is None:
                if is_local:
                    # noop if out_dir is not set and the path is local
                    return Storage._download_local(uri, session)
                out_dir = tempfile.mkdtemp()
            elif not os.path.exists(out_dir):
                os.mkdir(out_dir)

            if uri.startswith(_S3_PREFIX):
                return Storage._download_s3(uri, out_dir, session)
            else:
                raise Exception(f"Cannot recognize storage type for {uri}"
                                f"\n'{_GCS_PREFIX}', '{_S3_PREFIX}', '{_LOCAL_PREFIX}', and '_HTTP_PREFIX' are the current available storage type.")

    @staticmethod
    def _download_runtime_data(uri, session: Session = None):
        storage_nm = uri.split("/")[1]
        sess: Session = session

        if sess is None:
            with open("config.yaml") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                db = Database(config)
                with db.session() as sess:
                    storage: StorageList = sess.query(StorageList).filter(StorageList.storage_nm == storage_nm).first()
        else:
            storage: StorageList = sess.query(StorageList).filter(StorageList.storage_nm == storage_nm).first()
        if not storage:
            raise HandledException(ResponseCode.MODEL_NOT_FOUND, e=None)
        nfs_mount_path = storage.nfs_mount_path
        return [os.path.join(nfs_mount_path, uri)]

    @staticmethod
    def _download_local(uri, session: Session = None):
        pass

    @staticmethod
    def _download_s3(uri, temp_dir: str, session: Session = None):
        parsed = urlparse(uri, scheme='s3')
        bucket_name = parsed.netloc
        bucket_path = parsed.path.lstrip('/')
        sess: Session = session

        if sess is None:
            with open("config.yaml") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                db = Database(config)
                with db.session() as sess:
                    storage: StorageList = sess.query(StorageList).filter(StorageList.storage_nm == bucket_name).first()
        else:
            storage: StorageList = sess.query(StorageList).filter(StorageList.storage_nm == bucket_name).first()

        if not storage:
            print("S3 접속 정보 없음")
            raise HandledException(ResponseCode.MODEL_NOT_FOUND, e=None)

        aws_access_key_id = storage.accesskey
        aws_secret_access_key = storage.secretkey
        endpoint_url = storage.endpoint

        s3 = boto3.resource(service_name="s3",
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            endpoint_url=endpoint_url)

        bucket = s3.Bucket(bucket_name)
        _downloads = []
        for obj in bucket.objects.filter(Prefix=bucket_path):
            # Skip where boto3 lists the directory as an object
            if obj.key.endswith("/"):
                continue
            # In the case where bucket_path points to a single object, set the target key to bucket_path
            # Otherwise, remove the bucket_path prefix, strip any extra slashes, then prepend the target_dir
            target_key = (obj.key
                          if bucket_path == obj.key
                          else obj.key.replace(bucket_path, "", 1).lstrip("/"))
            target = f"{temp_dir}/{target_key}"
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target), exist_ok=True)
            bucket.download_file(obj.key, target)
            _downloads.append(target)

        return _downloads


###############################################################
# 단위 테스트 영역
# How to test
#    1. go to below of airuntime-py directory
#    2. type below
#        pytest common/utils/storage.py
###############################################################
def test_download():
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        # print(config)
        db = Database(config)
        with db.session() as sess:
            print(sess)
            downloads = Storage.download('s3://runtime-929-7bdc6675-7739-41f4-a27f-ccfc2f4943dc/mdl-feb53009-a9f3-4332-a151-4c81b3fcddfc/data/data.csv', session=sess)
            print(downloads)


if __name__ == "__main__":
    # test_download()
    downloads = Storage.download('runtime_datas/runtime-1701-2da91881-80b9-499a-a1a5-72ada534f9d2/mdl-cdd9ffd3-d1fb-4b91-b97e-9c26ba6ad5a1/82980/data/data.csv', session=None)
    print(downloads)
    downloads = Storage.download('s3://runtime-1120-b173c67d-ffdc-4969-83f7-199ecacad4c9/mdl-4e50bdaf-9eec-4a93-8053-7e5bfc133c5f/d1db3/data/data.csv', session=None)
    print(downloads)
