# src/aiopythonik/_pythonik_patches/client.pyi

from typing import Any

from requests import Session

from .specs import (
    AssetSpec,
    CollectionSpec,
    FilesSpec,
    JobSpec,
    MetadataSpec,
    SearchSpec,
)


class PythonikClient:
    session: Session
    timeout: int
    base_url: str

    def __init__(
        self,
        app_id: str,
        auth_token: str,
        timeout: int = 3,
        base_url: str = "https://app.iconik.io",
        *,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ) -> None:
        ...

    def acls(self) -> Any:
        ...

    def assets(self) -> AssetSpec:
        ...

    def auth(self) -> Any:
        ...

    def automations(self) -> Any:
        ...

    def collections(self) -> CollectionSpec:
        ...

    def files(self) -> FilesSpec:
        ...

    def jobs(self) -> JobSpec:
        ...

    def metadata(self) -> MetadataSpec:
        ...

    def notifications(self) -> Any:
        ...

    def search(self) -> SearchSpec:
        ...

    def settings(self) -> Any:
        ...

    def stats(self) -> Any:
        ...

    def transcode(self) -> Any:
        ...

    def users(self) -> Any:
        ...

    def users_notifications(self) -> Any:
        ...
