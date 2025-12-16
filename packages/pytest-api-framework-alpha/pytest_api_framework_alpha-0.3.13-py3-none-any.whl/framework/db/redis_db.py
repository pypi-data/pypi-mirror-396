import json
import retry
from redis import Redis, ConnectionPool

from framework.utils.log_util import logger
from framework.exceptions import RedisDBError


def safe_redis_call(func):
    """装饰器：捕获 Redis 异常并转成 RedisDBError"""

    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            raise RedisDBError(f"{func.__name__}: {e}")

    return wrapper


class RedisDB:
    def __init__(self, host, port, password, db, max_connections=5):
        self.db = db
        self.max_connections = max_connections
        self.conn = self.__connect(host, port, password, db)

    @retry.retry(tries=5, delay=3)
    def __connect(self, host, port, password, db):
        pool = ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=False,
            max_connections=self.max_connections,
        )
        conn = Redis(connection_pool=pool)
        conn.ping()
        return conn

    # -------------------- string --------------------
    @safe_redis_call
    def set_string(self, name, value, ex=None, log=True):
        res = self.conn.set(name, value, ex=ex)
        if log:
            logger.info(f"set {name}={value}, ex={ex} -> {res}")
        return res

    @safe_redis_call
    def get_string(self, name, log=True):
        if log:
            logger.info(f"get {name}")
        return self.conn.get(name)

    # -------------------- hash --------------------
    @safe_redis_call
    def set_hash(self, name, mapping, log=True):
        res = self.conn.hset(name, mapping=mapping)
        if log:
            logger.info(f"hset {name} {mapping} -> {res}")
        return res

    @safe_redis_call
    def get_hash(self, name, log=True):
        if log:
            logger.info(f"hgetall {name}")
        return self.conn.hgetall(name)

    # -------------------- list --------------------
    @safe_redis_call
    def set_list(self, name, value, log=True):
        """支持: dict / list / str / int / None"""
        if value is None:
            return self.conn.lpush(name, json.dumps(None))

        if isinstance(value, dict):
            value = [json.dumps(value, ensure_ascii=False)]
        elif isinstance(value, list):
            value = [json.dumps(item, ensure_ascii=False) for item in value]
        else:
            value = [str(value)]

        res = self.conn.lpush(name, *value)
        if log:
            logger.info(f"lpush {name} {value} -> {res}")
        return res

    @safe_redis_call
    def get_list(self, name):
        res = self.conn.lrange(name, 0, -1)
        return [json.loads(item) for item in res] if res else []

    @safe_redis_call
    def lpop_all(self, name):
        """弹出并返回队列中所有元素（会清空队列）"""
        items = []
        while True:
            val = self.conn.lpop(name)
            if val is None:
                break
            items.append(val)
        return items

    # -------------------- meta --------------------
    @safe_redis_call
    def set_ttl(self, name, ttl, log=True):
        res = self.conn.expire(name, ttl)
        if log:
            logger.info(f"expire {name} {ttl} -> {res}")
        return res

    @safe_redis_call
    def get_ttl(self, name, log=True):
        ttl = self.conn.ttl(name)
        if log:
            logger.info(f"ttl {name} -> {ttl}")
        return ttl

    @safe_redis_call
    def exists(self, name):
        return self.conn.exists(name)

    @safe_redis_call
    def delete(self, name):
        return self.conn.delete(name)

    # -------------------- queue --------------------
    @safe_redis_call
    def lpush(self, name, *values):
        return self.conn.lpush(name, *values)

    @safe_redis_call
    def rpush(self, name, *values):
        return self.conn.rpush(name, *values)

    @safe_redis_call
    def lpop(self, name):
        return self.conn.lpop(name)

    @safe_redis_call
    def rpop(self, name):
        return self.conn.rpop(name)