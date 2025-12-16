from typing import Optional

from redis import Redis
from redis.asyncio import Redis as AsyncRedis


class ExtendedRedis(Redis):
    def __init__(self, *args, **kwargs):
        self._namespace: Optional[str] = None
        super().__init__(*args, **kwargs)

    @classmethod
    def extend(cls, redis: Redis, *, namespace: str | None = None):
        return ExtendedRedis._create_with_namespace(redis=redis, namespace=namespace)

    def clone_with_namespace(self, namespace: str) -> "ExtendedRedis":
        """
        Creates a new Redis instance with the same connection parameters.
        """
        return self._create_with_namespace(namespace=namespace, redis=self)

    def delete_namespace_keys(self):
        if self._namespace is None:
            raise ValueError("[Db] Namespace not set")
        # Pattern for keys to be deleted
        pattern = f"{self._namespace}:*"

        # Get keys matching the pattern
        keys = self.keys(pattern)
        # Delete the keys
        if keys:
            self.delete(*keys)  # type: ignore

    @classmethod
    def _create_with_namespace(
        cls, redis: Redis, *, namespace: str | None
    ) -> "ExtendedRedis":
        """
        Creates a new Redis instance with the same connection parameters.
        """
        # Retrieve the connection parameters from the current Redis instance
        connection_params = {
            "host": redis.connection_pool.connection_kwargs.get("host", "localhost"),
            "port": redis.connection_pool.connection_kwargs.get("port", 6379),
            "db": redis.connection_pool.connection_kwargs.get("db", 0),
            "password": redis.connection_pool.connection_kwargs.get("password", None),
            "socket_timeout": redis.connection_pool.connection_kwargs.get(
                "socket_timeout", None
            ),
            # Always ensure responses are decoded to strings
            "decode_responses": True,
        }

        # Create and return a new instance with the same connection params
        clone = ExtendedRedis(**connection_params)
        clone.set_namespace(namespace)
        return clone

    def set_namespace(self, namespace: str | None):
        self._namespace = namespace  # set namespace

    def get_namespace_key(self, key: str) -> str:
        if self._namespace is None:
            raise ValueError("[Db] Namespace not set")
        return f"{self._namespace}:{key}"


class ExtendedAsyncRedis(AsyncRedis):
    def __init__(self, *args, **kwargs):
        self._namespace: Optional[str] = None
        super().__init__(*args, **kwargs)

    @classmethod
    def extend(cls, aredis: AsyncRedis, *, namespace: str | None = None):
        return ExtendedAsyncRedis._create_with_namespace(
            aredis=aredis, namespace=namespace
        )

    def clone_with_namespace(self, namespace: str) -> "ExtendedAsyncRedis":
        """
        Creates a new Redis instance with the same connection parameters.
        """
        return self._create_with_namespace(namespace=namespace, aredis=self)

    def delete_namespace_keys(self):
        if self._namespace is None:
            raise ValueError("[Db] Namespace not set")
        # Pattern for keys to be deleted
        pattern = f"{self._namespace}:*"

        # Get keys matching the pattern
        keys = self.keys(pattern)
        # Delete the keys
        if keys:
            self.delete(*keys)  # type: ignore

    @classmethod
    def _create_with_namespace(
        cls, aredis: AsyncRedis, *, namespace: str | None
    ) -> "ExtendedAsyncRedis":
        """
        Creates a new Redis instance with the same connection parameters.
        """
        # Retrieve the connection parameters from the current Redis instance
        connection_params = {
            "host": aredis.connection_pool.connection_kwargs.get("host", "localhost"),
            "port": aredis.connection_pool.connection_kwargs.get("port", 6379),
            "db": aredis.connection_pool.connection_kwargs.get("db", 0),
            "password": aredis.connection_pool.connection_kwargs.get("password", None),
            "socket_timeout": aredis.connection_pool.connection_kwargs.get(
                "socket_timeout", None
            ),
            # Always ensure responses are decoded to strings
            "decode_responses": True,
        }

        # Create and return a new instance with the same connection params
        clone = ExtendedAsyncRedis(**connection_params)
        clone.set_namespace(namespace)
        return clone

    def set_namespace(self, namespace: str | None):
        self._namespace = namespace  # set namespace

    def get_namespace_key(self, key: str) -> str:
        if self._namespace is None:
            raise ValueError("[Db] Namespace not set")
        return f"{self._namespace}:{key}"
