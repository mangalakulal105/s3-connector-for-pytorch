from functools import partial
from itertools import chain
from typing import Iterator, List

from s3dataset_s3_client._s3dataset import (
    ObjectInfo,
    ListObjectResult,
    ListObjectStream,
)

from s3dataset._s3client import S3Client, S3Reader


class S3BucketIterable:
    def __init__(self, client: S3Client, bucket: str, prefix: str):
        self._client = client
        self._bucket = bucket
        self._prefix = prefix

    def __iter__(self):
        # This allows us to iterate multiple times by re-creating the `_list_stream`
        return iter(S3BucketIterator(self._client, self._bucket, self._prefix))


class S3BucketIterator:
    def __init__(self, client: S3Client, bucket: str, prefix: str):
        self._client = client
        self._bucket = bucket
        self._list_stream = _PickleableListObjectStream(client, bucket, prefix)

    def __iter__(self) -> Iterator[S3Reader]:
        return map(
            self._create_s3reader,
            chain.from_iterable(map(_extract_object_info, self._list_stream)),
        )

    def _create_s3reader(self, object_info: ObjectInfo):
        return S3Reader(
            self._bucket,
            object_info.key,
            object_info,
            get_stream=partial(self._client.get_object, self._bucket, object_info.key),
        )


class _PickleableListObjectStream:
    def __init__(self, client: S3Client, bucket: str, prefix: str):
        self._client = client
        self._list_stream = iter(client.list_objects(bucket, prefix))

    def __iter__(self):
        return self

    def __next__(self) -> ListObjectResult:
        return next(self._list_stream)

    def __getstate__(self):
        return {
            "client": self._client,
            "bucket": self._list_stream.bucket,
            "prefix": self._list_stream.prefix,
            "delimiter": self._list_stream.delimiter,
            "max_keys": self._list_stream.max_keys,
            "continuation_token": self._list_stream.continuation_token,
            "complete": self._list_stream.complete,
        }

    def __setstate__(self, state):
        self._client = state["client"]
        self._list_stream = ListObjectStream._from_state(**state)


def _extract_object_info(list_result: ListObjectResult) -> List[ObjectInfo]:
    return list_result.object_info
