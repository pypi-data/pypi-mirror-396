class LoginException(Exception):
    """登录异常"""
    ...


class ValidateException(Exception):
    """断言异常"""
    ...


class RenderException(Exception):
    """数据渲染异常"""
    ...


class RequestException(Exception):
    """请求异常"""
    ...


class MysqlDBError(Exception):
    """自定义 Redis 异常"""
    pass


class RedisDBError(Exception):
    """自定义 Redis 异常"""
    pass


class GetAppHttpError(Exception):
    """获取app http对象异常"""


class GetAccountError(GetAppHttpError):
    """获取账号异常"""
    pass
