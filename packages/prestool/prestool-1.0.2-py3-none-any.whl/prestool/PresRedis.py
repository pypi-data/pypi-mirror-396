from redis import StrictRedis
from contextlib import contextmanager


class PresRedis:
    def __init__(self):
        super().__init__()
        self.redis_host = ''
        self.redis_port = 6379

    @contextmanager
    def conn_redis(self):
        r = StrictRedis(host=self.redis_host, port=self.redis_port)
        try:
            yield r
        finally:
            r.close()