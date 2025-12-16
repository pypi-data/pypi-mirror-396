import configparser
import contextlib
import datetime
import logging
import math
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, List, Mapping, Optional, Tuple, TypedDict, Union

import anyio
from aws_request_signer import AwsRequestSigner
from httpx import URL, AsyncClient


log = logging.getLogger(__name__)


class AbstractCredentials(ABC):
    @abstractmethod
    def __bool__(self) -> bool:
        ...

    @property
    @abstractmethod
    def signer(self) -> AwsRequestSigner:
        ...


@dataclass(frozen=True)
class StaticCredentials(AbstractCredentials):
    access_key_id: str = ""
    secret_access_key: str = ""
    session_token: Optional[str] = None
    region: str = ""
    service: str = "s3"

    def __bool__(self) -> bool:
        return all((self.access_key_id, self.secret_access_key))

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(access_key_id={self.access_key_id!r}, "
            "secret_access_key="
            f'{"******" if self.secret_access_key else None!r}, '
            f"region={self.region!r}, service={self.service!r})"
        )

    def as_dict(self) -> dict:
        return {
            "region": self.region,
            "access_key_id": self.access_key_id,
            "secret_access_key": self.secret_access_key,
            "session_token": self.session_token,
            "service": self.service,
        }

    @cached_property
    def signer(self) -> AwsRequestSigner:
        return AwsRequestSigner(**self.as_dict())


class URLCredentials(StaticCredentials):
    def __init__(
        self, url: Union[str, URL], *, region: str = "", service: str = "s3",
    ):
        url = URL(url)
        super().__init__(
            access_key_id=url.username or "",
            secret_access_key=url.password or "",
            region=region, service=service,
        )


class EnvironmentCredentials(StaticCredentials):
    def __init__(self, region: str = "", service: str = "s3"):
        super().__init__(
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            session_token=os.getenv("AWS_SESSION_TOKEN"),
            region=os.getenv("AWS_DEFAULT_REGION", region),
            service=service,
        )


class ConfigCredentials(StaticCredentials):
    DEFAULT_CREDENTIALS_PATH = Path.home() / ".aws" / "credentials"
    DEFAULT_CONFIG_PATH = Path.home() / ".aws" / "config"

    @staticmethod
    def _parse_ini_section(path: Path, section: str) -> Mapping[str, str]:
        conf = configparser.ConfigParser()
        if not conf.read(path):
            return {}

        if section not in conf:
            return {}

        return conf[section]

    def __init__(
        self,
        credentials_path: Union[str, Path, None] = None,
        config_path: Union[str, Path, None] = DEFAULT_CONFIG_PATH, *,
        region: str = "", service: str = "s3", profile: str = "auto",
    ):
        if credentials_path is None:
            credentials_path = Path(
                os.getenv(
                    "AWS_SHARED_CREDENTIALS_FILE",
                    self.DEFAULT_CREDENTIALS_PATH,
                ),
            )
        credentials_path = Path(credentials_path)

        if config_path is None:
            config_path = Path(
                os.getenv(
                    "AWS_SHARED_CONFIG_FILE",
                    self.DEFAULT_CONFIG_PATH,
                ),
            )
        config_path = Path(config_path)

        try:
            credentials_paths_exists = (
                credentials_path.exists() and config_path.exists()
            )
        except OSError:
            credentials_paths_exists = False

        if not credentials_paths_exists:
            super().__init__(region=region, service=service)
            return

        if profile == "auto":
            profile = os.getenv("AWS_PROFILE", "default")

        section = self._parse_ini_section(credentials_path, profile)
        access_key_id = section.get("aws_access_key_id", "")
        secret_access_key = section.get("aws_secret_access_key", "")

        section = self._parse_ini_section(config_path, profile)
        region = section.get("region", "")

        super().__init__(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            region=region,
            service=service,
        )


ENVIRONMENT_CREDENTIALS = EnvironmentCredentials()


def merge_credentials(*credentials: StaticCredentials) -> StaticCredentials:
    result = {}
    fields = (
        "access_key_id", "secret_access_key",
        "session_token", "region", "service",
    )

    for candidate in credentials:
        for field in fields:
            if field in result:
                continue
            value = getattr(candidate, field, None)
            if not value:
                continue
            result[field] = value

    return StaticCredentials(**result)


def collect_credentials(
    *, url: Optional[URL] = None, **kwargs,
) -> StaticCredentials:
    credentials: List[StaticCredentials] = []
    if kwargs:
        credentials.append(StaticCredentials(**kwargs))
    if url:
        credentials.append(URLCredentials(url))
    credentials.append(EnvironmentCredentials())
    credentials.append(ConfigCredentials())
    return merge_credentials(*credentials)


class MetadataDocument(TypedDict, total=False):
    """
    Response example is:

        {
          "accountId" : "123123",
          "architecture" : "x86_64",
          "availabilityZone" : "us-east-1a",
          "billingProducts" : null,
          "devpayProductCodes" : null,
          "marketplaceProductCodes" : null,
          "imageId" : "ami-123123",
          "instanceId" : "i-11232323",
          "instanceType" : "t3a.micro",
          "kernelId" : null,
          "pendingTime" : "2023-06-13T18:18:58Z",
          "privateIp" : "172.33.33.33",
          "ramdiskId" : null,
          "region" : "us-east-1",
          "version" : "2017-09-30"
        }
    """
    region: str


class MetadataSecurityCredentials(TypedDict, total=False):
    Code: str
    Type: str
    AccessKeyId: str
    SecretAccessKey: str
    Token: str
    Expiration: str


class MetadataCredentials(AbstractCredentials):
    METADATA_ADDRESS: str = "169.254.169.254"
    METADATA_PORT: int = 80

    def __init__(self, *, service: str = "s3"):
        self.session = AsyncClient(
            base_url=URL(
                scheme="http",
                host=self.METADATA_ADDRESS.rstrip('/'),
                port=self.METADATA_PORT,
            ),
        )
        self.service = service
        self.refresh_lock: anyio.Lock = anyio.Lock()
        self._signer: Optional[AwsRequestSigner] = None
        self.stack = contextlib.AsyncExitStack()
        self.taskgroup: anyio.abc.TaskGroup

    async def __aenter__(self):
        self.taskgroup = await self.stack.enter_async_context(anyio.create_task_group())
        await self.taskgroup.start(self._refresher, name="MetadataCredentials-refresher")
        return self

    async def __aexit__(self, *_):
        self.taskgroup.cancel_scope.cancel()
        del self.taskgroup
        await self.stack.aclose()

    def __bool__(self) -> bool:
        return hasattr(self, 'taskgroup')

    async def _refresher(self, *, task_status: anyio.abc.TaskStatus[None] = anyio.TASK_STATUS_IGNORED) -> None:
        while True:
            async with self.refresh_lock:
                try:
                    credentials, expires_at = await self._fetch_credentials()
                    self._signer = AwsRequestSigner(**credentials.as_dict())
                    delta = expires_at - datetime.datetime.now(datetime.UTC)
                    sleep_time = math.floor(delta.total_seconds() / 2)
                    task_status.started()
                except Exception as ex:
                    log.exception("Failed to update credentials", exc_info=ex)
                    sleep_time = 60
            await anyio.sleep(sleep_time)

    async def _fetch_credentials(
        self,
    ) -> Tuple[StaticCredentials, datetime.datetime]:
        response = await self.session.get("/latest/dynamic/instance-identity/document")
        document: MetadataDocument = response.json()

        response = await self.session.get("/latest/meta-data/iam/security-credentials/")
        iam_role = response.content.decode()

        response = await self.session.get(f"/latest/meta-data/iam/security-credentials/{iam_role}")
        credentials: MetadataSecurityCredentials = response.json()

        return (
            StaticCredentials(
                region=document["region"],
                access_key_id=credentials["AccessKeyId"],
                secret_access_key=credentials["SecretAccessKey"],
                session_token=credentials["Token"],
            ),
            datetime.datetime.fromisoformat(credentials["Expiration"]),
        )

    @property
    def signer(self) -> AwsRequestSigner:
        if not self._signer:
            raise RuntimeError(
                f"{self.__class__.__name__} must be started before using",
            )
        return self._signer


__all__ = (
    "AbstractCredentials",
    "ConfigCredentials",
    "EnvironmentCredentials",
    "MetadataCredentials",
    "StaticCredentials",
    "URLCredentials",
    "collect_credentials",
    "merge_credentials",
)
