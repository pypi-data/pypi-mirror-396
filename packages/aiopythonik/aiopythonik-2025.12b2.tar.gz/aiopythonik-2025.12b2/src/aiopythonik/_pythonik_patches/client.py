from pythonik.client import PythonikClient as _PythonikClient
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


__all__ = ["PythonikClient"]

from .specs import (
    AssetSpec,
    CollectionSpec,
    FilesSpec,
    JobSpec,
    MetadataSpec,
    SearchSpec,
)

# Default connection pool sizes (urllib3/requests defaults are 10)
DEFAULT_POOL_CONNECTIONS = 10
DEFAULT_POOL_MAXSIZE = 10


class PythonikClient(_PythonikClient):
    """
    Extended PythonikClient with configurable connection pool sizes.

    This patch allows configuring the urllib3 connection pool to handle
    higher concurrency workloads without connection churn.
    """

    def __init__(
        self,
        app_id: str,
        auth_token: str,
        timeout: int,
        base_url: str = "https://app.iconik.io",
        *,
        pool_connections: int = DEFAULT_POOL_CONNECTIONS,
        pool_maxsize: int = DEFAULT_POOL_MAXSIZE,
    ):
        """
        Initialize the client with configurable connection pool.

        Args:
            app_id: The app ID for authentication.
            auth_token: The auth token for authentication.
            timeout: The timeout for API requests.
            base_url: The base URL for the API.
            pool_connections: Number of connection pools to cache.
                Controls how many different hosts can have pooled
                connections. Default: 10.
            pool_maxsize: Maximum number of connections per pool.
                Controls concurrent connections to a single host.
                Default: 10. Increase for high-concurrency workloads.
        """
        # Call parent __init__ which sets up session with default pool
        super().__init__(
            app_id=app_id,
            auth_token=auth_token,
            timeout=timeout,
            base_url=base_url,
        )

        # Reconfigure the session's HTTPAdapter with custom pool sizes
        # if they differ from defaults (avoids unnecessary reconfiguration)
        if (
            pool_connections != DEFAULT_POOL_CONNECTIONS
            or pool_maxsize != DEFAULT_POOL_MAXSIZE
        ):
            retry_strategy = Retry(
                total=4,
                backoff_factor=3,
            )
            http_adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=pool_connections,
                pool_maxsize=pool_maxsize,
            )
            self.session.mount("http://", http_adapter)
            self.session.mount("https://", http_adapter)

    def acls(self):
        """
        Access ACLs (Access Control Lists) API endpoints.

        Raises:
            NotImplementedError: ACLs endpoint not yet implemented
        """
        raise NotImplementedError(
            "ACLs endpoint is not yet implemented. "
            "Please check the documentation for updates or contribute "
            "to the pythonik project."
        )

    def assets(self) -> AssetSpec:
        return AssetSpec(self.session, self.timeout, self.base_url)

    def auth(self):
        """
        Access authentication API endpoints.

        Raises:
            NotImplementedError: Auth endpoint not yet implemented
        """
        raise NotImplementedError(
            "Authentication endpoint is not yet implemented. "
            "Please check the documentation for updates or contribute "
            "to the pythonik project."
        )

    def automations(self):
        """
        Access automations API endpoints.

        Raises:
            NotImplementedError: Automations endpoint not yet implemented
        """
        raise NotImplementedError(
            "Automations endpoint is not yet implemented. "
            "Please check the documentation for updates or contribute "
            "to the pythonik project."
        )

    def collections(self) -> CollectionSpec:
        return CollectionSpec(self.session, self.timeout, self.base_url)

    def files(self) -> FilesSpec:
        return FilesSpec(self.session, self.timeout, self.base_url)

    def jobs(self) -> JobSpec:
        return JobSpec(self.session, self.timeout, self.base_url)

    def metadata(self) -> MetadataSpec:
        return MetadataSpec(self.session, self.timeout, self.base_url)

    def notifications(self):
        """
        Access notifications API endpoints.

        Raises:
            NotImplementedError: Notifications endpoint not yet implemented
        """
        raise NotImplementedError(
            "Notifications endpoint is not yet implemented. "
            "Please check the documentation for updates or contribute "
            "to the pythonik project."
        )

    def search(self) -> SearchSpec:
        return SearchSpec(self.session, self.timeout, self.base_url)

    def settings(self):
        """
        Access settings API endpoints.

        Raises:
            NotImplementedError: Settings endpoint not yet implemented
        """
        raise NotImplementedError(
            "Settings endpoint is not yet implemented. "
            "Please check the documentation for updates or contribute "
            "to the pythonik project."
        )

    def stats(self):
        """
        Access statistics API endpoints.

        Raises:
            NotImplementedError: Stats endpoint not yet implemented
        """
        raise NotImplementedError(
            "Statistics endpoint is not yet implemented. "
            "Please check the documentation for updates or contribute "
            "to the pythonik project."
        )

    def transcode(self):
        """
        Access transcoding API endpoints.

        Raises:
            NotImplementedError: Transcode endpoint not yet implemented
        """
        raise NotImplementedError(
            "Transcoding endpoint is not yet implemented. "
            "Please check the documentation for updates or contribute "
            "to the pythonik project."
        )

    def users(self):
        """
        Access users API endpoints.

        Raises:
            NotImplementedError: Users endpoint not yet implemented
        """
        raise NotImplementedError(
            "Users endpoint is not yet implemented. "
            "Please check the documentation for updates or contribute "
            "to the pythonik project."
        )

    def users_notifications(self):
        """
        Access user notifications API endpoints.

        Raises:
            NotImplementedError: User notifications endpoint not yet
                implemented
        """
        raise NotImplementedError(
            "User notifications endpoint is not yet implemented. "
            "Please check the documentation for updates or contribute "
            "to the pythonik project."
        )
