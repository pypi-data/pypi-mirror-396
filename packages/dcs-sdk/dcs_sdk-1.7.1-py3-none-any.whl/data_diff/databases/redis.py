#  Copyright 2022-present, the Waterdip Labs Pvt. Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import threading
import time

from loguru import logger
from redis import ConnectionPool, Redis, RedisError


class RedisBackend:
    _INSTANCE = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, force_recreate: bool = False):
        with cls._lock:
            if cls._INSTANCE is None or force_recreate:
                logger.info("Creating a new RedisBackend instance (force_recreate=%s)", force_recreate)
                cls._INSTANCE = cls._create_instance()
            return cls._INSTANCE

    @classmethod
    def _create_instance(cls):
        redis_url = (
            os.getenv("DCS_REDIS_URL", None)
            or os.getenv("DCS_RABBIT_URL", None)
            or os.getenv("REDIS_URL", None)
            or os.getenv("RABBIT_URL", None)
        )
        if not redis_url:
            logger.warning("environment variable is not configured for redis")
            return None
        try:
            pool = ConnectionPool.from_url(
                redis_url,
                max_connections=int(os.getenv("DCS_REDIS_MAX_CONNECTIONS", "100")),
                health_check_interval=int(os.getenv("DCS_REDIS_HEALTH_CHECK_INTERVAL", "30")),
                socket_connect_timeout=float(os.getenv("DCS_REDIS_SOCKET_CONNECT_TIMEOUT", "5")),
                socket_timeout=float(os.getenv("DCS_REDIS_SOCKET_TIMEOUT", "5")),
                socket_keepalive=True,
            )
            client = Redis(connection_pool=pool, decode_responses=False, retry_on_timeout=True)
            # ping to ensure connection and raise early if config wrong
            client.ping()
            return cls(client)
        except RedisError as exc:
            logger.exception("Failed to create Redis client: %s", exc)
            raise

    def __init__(self, client: Redis):
        self._client = client

    @property
    def client(self) -> Redis:
        return self._client

    def ensure_connected(self) -> bool:
        try:
            self._client.ping()
            return True
        except RedisError:
            logger.warning("Redis ping failed; trying to recreate connection/pool")
            try:
                time.sleep(0.2)
                new_instance = self.__class__._create_instance()
                self.__class__._INSTANCE = new_instance
                self._client = new_instance.client
                self._client.ping()
                logger.info("Recreated Redis client/pool successfully")
                return True
            except Exception as exc:
                logger.exception("Failed to recreate Redis client: %s", exc)
                return False

    def close(self):
        try:
            self._client.connection_pool.disconnect()
            logger.info("Closed Redis connection pool")
        except Exception as e:
            logger.exception("Error closing Redis connection pool: %s", e)
