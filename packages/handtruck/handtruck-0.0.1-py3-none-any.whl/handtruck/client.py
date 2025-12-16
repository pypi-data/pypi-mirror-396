import hashlib
import io
import logging
import os
import typing as t
from collections import deque
from contextlib import suppress
from dataclasses import dataclass
from functools import partial
from http import HTTPStatus
from itertools import chain
from mimetypes import guess_type
from mmap import PAGESIZE
from pathlib import Path
from tempfile import NamedTemporaryFile

import anyio
import anyio.streams.memory
from anyiomisc import asyncbackoff
from aws_request_signer import UNSIGNED_PAYLOAD
from httpx import URL, HTTPError, AsyncClient, Response, QueryParams

from ._async import generate_in_thread, run_in_thread, parallel_file_writer, ChunkSendStream
from ._xml import (
    AwsObjectMeta, create_complete_upload_request,
    parse_create_multipart_upload_id, parse_list_objects,
)
from .credentials import (
    AbstractCredentials, collect_credentials,
)

log = logging.getLogger(__name__)

CHUNK_SIZE = 2 ** 16

DONE = object()
EMPTY_STR_HASH = hashlib.sha256(b"").hexdigest()
# 5MB

PART_SIZE = 5 * 1024 * 1024
HeadersType = t.Union[t.Dict]

DataType = t.Optional[t.Mapping[str, t.Any]]
RequestContent = t.Optional[t.Union[str, bytes, t.Iterable[bytes], t.AsyncIterable[bytes]]]
PrimitiveData = t.Optional[t.Union[str, int, float, bool]]
QueryParamTypes = t.Union[
    QueryParams,
    t.Mapping[str, t.Union[PrimitiveData, t.Sequence[PrimitiveData]]],
    t.List[t.Tuple[str, PrimitiveData]],
    t.Tuple[t.Tuple[str, PrimitiveData], ...],
    str,
    bytes,
]


@dataclass
class HEADERS:
    CONTENT_LENGTH = 'Content-Length'
    CONTENT_TYPE = 'Content-Type'


class AwsError(HTTPError):
    pass


class AwsUploadError(AwsError):
    pass


class AwsDownloadError(AwsError):
    pass


@run_in_thread
def concat_files(
    target_file: Path, files: t.List[t.IO[bytes]], buffer_size: int,
) -> None:
    with target_file.open("ab") as fp:
        for file in files:
            file.seek(0)
            while True:
                chunk = file.read(buffer_size)
                if not chunk:
                    break
                fp.write(chunk)
            file.close()


@run_in_thread
def write_from_start(
    file: io.BytesIO, chunk: bytes, range_start: int, pos: int,
) -> None:
    file.seek(pos - range_start)
    file.write(chunk)


@generate_in_thread
def gen_without_hash(
    stream: t.Iterable[bytes],
) -> t.Generator[t.Tuple[None, bytes], None, None]:
    for data in stream:
        yield (None, data)


@generate_in_thread
def gen_with_hash(
    stream: t.Iterable[bytes],
) -> t.Generator[t.Tuple[str, bytes], None, None]:
    for data in stream:
        yield hashlib.sha256(data).hexdigest(), data


def file_sender(
    file_name: t.Union[str, Path], chunk_size: int = CHUNK_SIZE,
) -> t.Iterable[bytes]:
    with open(file_name, "rb") as fp:
        while True:
            data = fp.read(chunk_size)
            if not data:
                break
            yield data


async_file_sender = generate_in_thread(file_sender)

MultiPart = tuple

class S3Client:
    def __init__(
        self, client: AsyncClient, url: t.Union[URL, str],
        secret_access_key: t.Optional[str] = None,
        access_key_id: t.Optional[str] = None,
        session_token: t.Optional[str] = None,
        region: str = "",
        credentials: t.Optional[AbstractCredentials] = None,
    ):
        url = URL(url)
        if credentials is None:
            credentials = collect_credentials(
                url=url,
                access_key_id=access_key_id,
                region=region,
                secret_access_key=secret_access_key,
                session_token=session_token,
            )

        if not credentials:
            raise ValueError(
                f"Credentials {credentials!r} is incomplete",
            )

        self._url = url
        self._client = client
        self._credentials = credentials

    @property
    def url(self) -> URL:
        return self._url

    async def request(
        self, method: str, path: str,
        headers: t.Optional[HeadersType] = None,
        params: t.Optional[QueryParams] = None,
        content: t.Optional[RequestContent] = None,
        content_sha256: t.Optional[str] = None,
        **kwargs,
    ) -> Response:
        headers = self._prepare_headers(headers)

        if content is not None and content_sha256 is None:
            content_sha256 = UNSIGNED_PAYLOAD

        url = (self._url.join(path))
        if params:
            url = url.copy_merge_params(params)

        headers = self._make_headers(headers)
        headers.update(
            self._credentials.signer.sign_with_headers(
                method, str(url), headers=headers, content_hash=content_sha256,
            ),
        )
        return await self._client.request(
            method, url, headers=headers, content=content, **kwargs,
        )

    async def get(self, object_name: str, **kwargs) -> Response:
        return await self.request("GET", object_name, **kwargs)

    async def head(
        self, object_name: str,
        content_sha256=EMPTY_STR_HASH,
        **kwargs,
    ) -> Response:
        return await self.request(
            "HEAD", object_name, content_sha256=content_sha256, **kwargs,
        )

    async def delete(
        self, object_name: str,
        content_sha256=EMPTY_STR_HASH,
        **kwargs,
    ) -> Response:
        return await self.request(
            "DELETE", object_name, content_sha256=content_sha256, **kwargs,
        )

    @staticmethod
    def _make_headers(headers: t.Optional[HeadersType]) -> dict:
        headers = dict(headers or {})
        return headers

    def _prepare_headers(
        self, headers: t.Optional[HeadersType],
        file_path: str = "",
    ) -> dict:
        headers = self._make_headers(headers)

        if HEADERS.CONTENT_TYPE not in headers:
            content_type = guess_type(file_path)[0]
            if content_type is None:
                content_type = "application/octet-stream"

            headers[HEADERS.CONTENT_TYPE] = content_type

        return headers

    async def put(
        self, object_name: str,
        content: RequestContent,
        **kwargs,
    ) -> Response:
        return await self.request("PUT", object_name, content=content, **kwargs)

    async def post(
        self, object_name: str,
        content: RequestContent = None,
        **kwargs,
    ) -> Response:
        return await self.request("POST", object_name, content=content, **kwargs)

    async def put_file(
        self, object_name: t.Union[str, Path],
        file_path: t.Union[str, Path],
        *, headers: t.Optional[HeadersType] = None,
        chunk_size: int = CHUNK_SIZE, content_sha256: t.Optional[str] = None,
    ) -> Response:

        headers = self._prepare_headers(headers, str(file_path))
        return await self.put(
            str(object_name),
            headers=headers,
            content=async_file_sender(
                file_path,
                chunk_size=chunk_size,
            ),
            content_sha256=content_sha256,
        )

    @asyncbackoff(
        None, None, 0,
        max_tries=3, exceptions=(HTTPError,),
    )
    async def _create_multipart_upload(
        self,
        object_name: str,
        headers: t.Optional[HeadersType] = None,
    ) -> str:
        resp = await self.post(
            object_name,
            headers=headers,
            params={"uploads": 1},
            content_sha256=EMPTY_STR_HASH,
        )
        payload = resp.read()
        if resp.status_code != HTTPStatus.OK:
            raise AwsUploadError(
                f"Wrong status code {resp.status_code} from s3 with message "
                f"{payload.decode()}.",
            )
        return parse_create_multipart_upload_id(payload)

    @asyncbackoff(
        None, None, 0,
        max_tries=3, exceptions=(AwsUploadError, HTTPError),
    )
    async def _complete_multipart_upload(
        self,
        upload_id: str,
        object_name: str,
        parts: t.List[t.Tuple[int, str]],
    ) -> None:
        complete_upload_request = create_complete_upload_request(parts)
        resp = await self.post(
            object_name,
            headers={"Content-Type": "text/xml"},
            params={"uploadId": upload_id},
            content=complete_upload_request,
            content_sha256=hashlib.sha256(complete_upload_request).hexdigest(),
        )
        if resp.status_code != HTTPStatus.OK:
            payload = resp.content
            raise AwsUploadError(
                f"Wrong status code {resp.status_code} from s3 with message "
                f"{payload!r}.",
            )

    async def _put_part(
        self,
        upload_id: str,
        object_name: str,
        part_no: int,
        content: RequestContent,
        content_sha256: str,
        **kwargs,
    ) -> str:
        resp = await self.put(
            object_name,
            params={"partNumber": part_no, "uploadId": upload_id},
            content=content,
            content_sha256=content_sha256,
            **kwargs,
        )
        payload = resp.content
        if resp.status_code != HTTPStatus.OK:
            raise AwsUploadError(
                f"Wrong status code {resp.status_code} from s3 with message "
                f"{payload!r}.",
            )
        return resp.headers["Etag"].strip('"')

    async def _part_uploader(
        self,
        upload_id: str,
        object_name: str,
        parts_stream: anyio.streams.memory.MemoryObjectReceiveStream[MultiPart],
        results_queue: deque,
        part_upload_tries: int,
        **kwargs,
    ) -> None:
        backoff = asyncbackoff(
            None, None,
            max_tries=part_upload_tries,
            exceptions=(HTTPError,),
        )
        async for part_no, part_hash, part in parts_stream:
            etag = await backoff(self._put_part)(
                upload_id=upload_id,
                object_name=object_name,
                part_no=part_no,
                content=part,
                content_sha256=part_hash,
                **kwargs,
            )
            log.debug(
                "Etag for part %d of %s is %s", part_no, upload_id, etag,
            )
            results_queue.append((part_no, etag))

    async def put_file_multipart(
        self,
        object_name: t.Union[str, Path],
        file_path: t.Union[str, Path],
        *,
        headers: t.Optional[HeadersType] = None,
        part_size: int = PART_SIZE,
        workers_count: int = 1,
        max_size: t.Optional[int] = None,
        part_upload_tries: int = 3,
        calculate_content_sha256: bool = True,
        **kwargs,
    ) -> None:
        """
        Upload data from a file with multipart upload

        object_name: key in s3
        file_path: path to a file for upload
        headers: additional headers, such as Content-Type
        part_size: size of a chunk to send (recommended: >5Mb)
        workers_count: count of coroutines for asyncronous parts uploading
        max_size: maximum size of a queue with data to send (should be
            at least `workers_count`)
        part_upload_tries: how many times trying to put part to s3 before fail
        calculate_content_sha256: whether to calculate sha256 hash of a part
            for integrity purposes
        """
        log.debug(
            "Going to multipart upload %s to %s with part size %d",
            file_path, object_name, part_size,
        )
        await self.put_multipart(
            object_name,
            file_sender(
                file_path,
                chunk_size=part_size,
            ),
            headers=headers,
            workers_count=workers_count,
            max_size=max_size,
            part_upload_tries=part_upload_tries,
            calculate_content_sha256=calculate_content_sha256,
            **kwargs,
        )

    async def _parts_generator(
        self, gen: t.AsyncIterable[tuple], workers_count: int, parts_stream: anyio.streams.memory.MemoryObjectSendStream[MultiPart],
    ) -> int:
        part_no = 1
        async with parts_stream:
            async for part_hash, part in gen:
                log.debug(
                    "Reading part %d (%d bytes)", part_no, len(part),
                )
                await parts_stream.send((part_no, part_hash, part))
                part_no += 1

        return part_no

    async def put_multipart(
        self,
        object_name: t.Union[str, Path],
        content: t.Iterable[bytes],
        *,
        headers: t.Optional[HeadersType] = None,
        workers_count: int = 1,
        max_size: t.Optional[int] = None,
        part_upload_tries: int = 3,
        calculate_content_sha256: bool = True,
        **kwargs,
    ) -> None:
        """
        Send data from iterable with multipart upload

        object_name: key in s3
        data: any iterable that returns chunks of bytes
        headers: additional headers, such as Content-Type
        workers_count: count of coroutines for asyncronous parts uploading
        max_size: maximum size of a queue with data to send (should be
            at least `workers_count`)
        part_upload_tries: how many times trying to put part to s3 before fail
        calculate_content_sha256: whether to calculate sha256 hash of a part
            for integrity purposes
        """
        if workers_count < 1:
            raise ValueError(
                f"Workers count should be > 0. Got {workers_count}",
            )
        max_size = max_size or workers_count

        upload_id = await self._create_multipart_upload(
            str(object_name),
            headers=headers,
        )
        log.debug("Got upload id %s for %s", upload_id, object_name)

        results_queue: deque = deque()
        try:
            async with anyio.create_task_group() as tg:
                send_stream, receive_stream = anyio.create_memory_object_stream()
                for wid in range(workers_count):
                    tg.start_soon(partial(
                        self._part_uploader,
                        upload_id,
                        str(object_name),
                        receive_stream.clone(),
                        results_queue,
                        part_upload_tries,
                        **kwargs,
                    ), name=f"put-worker-{upload_id}@{wid}")
                # Get rid of our copy
                receive_stream.close()
                del receive_stream

                if calculate_content_sha256:
                    gen = gen_with_hash(content)
                else:
                    gen = gen_without_hash(content)

                part_no = await self._parts_generator(gen, workers_count, send_stream)
        except* Exception as excgroup:
            for exc in excgroup.exceptions:
                raise exc from None

        log.debug(
            "All parts (#%d) of %s are uploaded to %s",
            part_no - 1, upload_id, object_name,
        )

        # Parts should be in ascending order
        parts = sorted(results_queue, key=lambda x: x[0])
        await self._complete_multipart_upload(
            upload_id, str(object_name), parts,
        )

    async def _download_range(
        self,
        object_name: str,
        writer: ChunkSendStream,
        *,
        etag: str,
        pos: int,
        range_start: int,
        req_range_start: int,
        req_range_end: int,
        buffer_size: int,
        headers: t.Optional[HeadersType] = None,
        **kwargs,
    ) -> None:
        """
        Downloading range [req_range_start:req_range_end] to `file`
        """
        log.debug(
            "Downloading %s from %d to %d",
            object_name,
            req_range_start,
            req_range_end,
        )
        if not headers:
            headers = {}
        headers = headers.copy()
        headers["Range"] = f"bytes={req_range_start}-{req_range_end}"
        headers["If-Match"] = etag

        resp = await self.get(object_name, headers=headers, **kwargs)
        if resp.status_code not in (HTTPStatus.PARTIAL_CONTENT, HTTPStatus.OK):
            raise AwsDownloadError(
                f"Got wrong status code {resp.status_code} on range download "
                f"of {object_name}",
            )
        assert 'Content-Range' in resp.headers
        assert resp.headers['Content-Range'].startswith(f"bytes {req_range_start}-{req_range_end}/")
        # FIXME: Handle OK
        # FIXME: Handle Content-Range being different from requested
        pos = req_range_start
        async for chunk in resp.aiter_bytes(buffer_size):
            if not chunk:
                break
            await writer.send((pos, chunk))
            pos += len(chunk)

    async def _download_worker(
        self,
        object_name: str,
        writer: ChunkSendStream,
        *,
        etag: str,
        range_step: int,
        range_start: int,
        range_end: int,
        buffer_size: int,
        range_get_tries: int = 3,
        headers: t.Optional[HeadersType] = None,
        **kwargs,
    ) -> None:
        """
        Downloads data in range `[range_start, range_end)`
        with step `range_step` to file `file_path`.
        Uses `etag` to make sure that file wasn't changed in the process.
        """
        log.debug(
            "Starting download worker for range [%d:%d]",
            range_start,
            range_end,
        )
        async with writer:
            backoff = asyncbackoff(
                None, None,
                max_tries=range_get_tries,
                exceptions=(HTTPError,),
            )
            req_range_end = range_start
            for req_range_start in range(range_start, range_end, range_step):
                req_range_end += range_step
                if req_range_end > range_end:
                    req_range_end = range_end
                await backoff(self._download_range)(
                    object_name,
                    writer,
                    etag=etag,
                    pos=(req_range_start - range_start),
                    range_start=range_start,
                    req_range_start=req_range_start,
                    req_range_end=req_range_end - 1,
                    buffer_size=buffer_size,
                    headers=headers,
                    **kwargs,
                )

    async def get_file_parallel(
        self,
        object_name: t.Union[str, Path],
        file_path: t.Union[str, Path],
        *,
        headers: t.Optional[HeadersType] = None,
        range_step: int = PART_SIZE,
        workers_count: int = 1,
        range_get_tries: int = 3,
        buffer_size: int = PAGESIZE * 32,
        **kwargs,
    ) -> None:
        """
        Download object in parallel with requests with Range.
        If file will change while download is in progress -
            error will be raised.

        object_name: s3 key to download
        file_path: target file path
        headers: additional headers
        range_step: how much data will be downloaded in single HTTP request
        workers_count: count of parallel workers
        range_get_tries: count of tries to download each range
        buffer_size: size of a buffer for on the fly data
        """
        file_path = Path(file_path)
        resp = await self.head(str(object_name), headers=headers)
        if resp.status_code != HTTPStatus.OK:
            raise AwsDownloadError(
                f"Got response for HEAD request for {object_name} "
                f"of a wrong status {resp.status_code}",
            )
        etag = resp.headers["Etag"]
        file_size = int(resp.headers["Content-Length"])
        log.debug(
            "Object's %s etag is %s and size is %d",
            object_name,
            etag,
            file_size,
        )

        worker_range_size = file_size // workers_count
        range_end = 0
        try:
            try:
                async with (
                    await anyio.open_file(file_path, "w+b") as fp,
                    parallel_file_writer(fp) as pfw, 
                    anyio.create_task_group() as tg,
                ):
                    for range_start in range(0, file_size, worker_range_size):
                        range_end += worker_range_size
                        if range_end > file_size:
                            range_end = file_size
                        tg.start_soon(partial(
                            self._download_worker,
                            str(object_name),
                            await pfw.get_block(range_start, range_end),
                            buffer_size=buffer_size,
                            etag=etag,
                            headers=headers,
                            range_end=range_end,
                            range_get_tries=range_get_tries,
                            range_start=range_start,
                            range_step=range_step,
                            **kwargs,
                        ), name=f"get-worker@{range_start}")
            except* Exception as excgroup:
                # Unwrap and raise just one
                for exc in excgroup.exceptions:
                    raise exc from None

        except Exception:
            log.exception(
                "Error on file download. Removing possibly incomplete file %s",
                file_path,
            )
            with suppress(FileNotFoundError):
                os.unlink(file_path)
            raise

    async def list_objects_v2(
        self,
        object_name: t.Union[str, Path] = "/",
        *,
        bucket: t.Optional[str] = None,
        prefix: t.Optional[t.Union[str, Path]] = None,
        delimiter: t.Optional[str] = None,
        max_keys: t.Optional[int] = None,
        start_after: t.Optional[str] = None,
    ) -> t.AsyncIterator[t.List[AwsObjectMeta]]:
        """
        List objects in bucket.

        Returns an iterator over lists of metadata objects, each corresponding
        to an individual response result (typically limited to 1000 keys).

        object_name:
            path to listing endpoint, defaults to '/'; a `bucket` value is
            prepended to this value if provided.
        prefix:
            limits the response to keys that begin with the specified
            prefix
        delimiter: a delimiter is a character you use to group keys
        max_keys: maximum number of keys returned in the response
        start_after: keys to start listing after
        """

        params = {
            "list-type": "2",
        }

        if prefix:
            params["prefix"] = str(prefix)

        if delimiter:
            params["delimiter"] = delimiter

        if max_keys:
            params["max-keys"] = str(max_keys)

        if start_after:
            params["start-after"] = start_after

        if bucket is not None:
            object_name = f"/{bucket}"

        while True:
            resp = await self.get(str(object_name), params=params)
            if resp.status_code != HTTPStatus.OK:
                raise AwsDownloadError(
                    f"Got response with wrong status for GET request for "
                    f"{object_name} with prefix '{prefix}'",
                )
            payload = resp.content
            metadata, continuation_token = parse_list_objects(payload)
            if not metadata:
                break
            yield metadata
            if not continuation_token:
                break
            params["continuation-token"] = continuation_token
