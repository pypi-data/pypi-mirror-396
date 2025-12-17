import json
from decimal import Decimal
from datetime import datetime

import retry
import pymysql
from pymysql import MySQLError
from dbutils.pooled_db import PooledDB

import config.settings as settings
from framework.utils.log_util import logger
from framework.exceptions import MysqlDBError


def safe_mysql_call(func):
    """装饰器：捕获 Mysql 异常并转成 MysqlDBError"""

    def wrapper(self, *args, **kwargs):
        sql = None
        # 从参数中尝试提取 SQL
        if len(args) > 0 and isinstance(args[0], str):
            sql = args[0]
        elif 'sql' in kwargs:
            sql = kwargs['sql']
        try:
            return func(self, *args, **kwargs)
        except MySQLError as e:
            logger.error(f"{func.__name__}执行SQL出错: {sql}: {e}")
            raise MysqlDBError(e)
        except Exception as e:
            logger.error(f"{func.__name__} 未知错误: {e}")
            raise MysqlDBError(e)

    return wrapper


class MysqlDB:
    def __init__(self, host, username, password, port, db, max_connections=5):
        self.__create_pool(host, username, password, port, db, max_connections)

    @retry.retry(tries=getattr(settings, "MYSQL_RETRIES", 5), delay=getattr(settings, "MYSQL_DELAY", 3))
    def __create_pool(self, host, username, password, port, db, max_connections):
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections= getattr(settings, "MYSQL_MAX_CONNECTIONS", 5),
            mincached=1,
            maxcached=max_connections,
            blocking=True,
            maxusage=None,
            setsession=[],
            ping=0,
            host=host,
            user=username,
            password=password,
            db=db,
            port=port,
            charset='utf8'
        )

    @safe_mysql_call
    def query(self, sql, log=True):
        """查询，返回结果"""
        connection = self.pool.connection()  # 获取一个连接
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql)
            if log:
                logger.info(f"执行SQL: {sql}")
            result = cursor.fetchall()
            if len(result) == 1:
                result = result[0]
            elif len(result) == 0:
                result = None
            if isinstance(result, dict) or isinstance(result, list):
                if log:
                    logger.info(f"SQL执行结果: {json.dumps(result, default=MysqlDB.custom_serializer)}")
            else:
                if log:
                    logger.info(f"SQL执行结果: {result}")
            return result

        finally:
            cursor.close()  # 关闭游标
            connection.close()  # 将连接返回到连接池

    @safe_mysql_call
    def insert(self, sql, log=True):
        """修改，新增，删除"""
        connection = self.pool.connection()  # 获取一个连接
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql)
            if log:
                logger.info(f"执行SQL: {sql}")
            connection.commit()
            inserted_id = cursor.lastrowid
            if log:
                logger.info(f"插入的记录的主键ID: {inserted_id}")
            return inserted_id

        finally:
            cursor.close()  # 关闭游标
            connection.close()  # 将连接返回到连接池

    @safe_mysql_call
    def execute(self, sql, log=True):
        """修改，新增，删除"""
        connection = self.pool.connection()  # 获取一个连接
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            result = cursor.execute(sql)
            if log:
                logger.info(f"执行SQL: {sql}")
            connection.commit()
            if log:
                logger.info(f"SQL执行结果: {result}")
            return result

        finally:
            cursor.close()  # 关闭游标
            connection.close()  # 将连接返回到连接池

    @safe_mysql_call
    def executemany(self, sql, data, log=True):
        """修改，新增，删除"""
        connection = self.pool.connection()  # 获取一个连接
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.executemany(sql, data)
            if log:
                logger.info(f"执行SQL: {sql}")
            connection.commit()
            if log:
                logger.info(f"{cursor.rowcount} records inserted.")

        finally:
            cursor.close()  # 关闭游标
            connection.close()  # 将连接返回到连接池

    @staticmethod
    def custom_serializer(obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, bytes):
                return obj.decode(errors='ignore', encoding='utf-8')
            # 不处理的类型：直接返回原对象
            return obj
        except Exception:
            return obj