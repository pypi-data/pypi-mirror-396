import time
from datetime import datetime, timedelta


class DateUtil(object):

    @staticmethod
    def get_long_timestamp(int_type=False):
        """
        获取毫秒级时间戳
        :param int_type: 返回int类型
        :return:
        """
        ts = int(time.time() * 1000)
        return ts if int_type else str(ts)

    @staticmethod
    def get_short_timestamp(int_type=False):
        """
        获取秒级时间戳
        :param int_type: 返回int类型
        :return:
        """
        ts = int(time.time())
        return ts if int_type else str(ts)

    @staticmethod
    def get_current_datetime(fmt="%Y-%m-%d %H:%M:%S"):
        """
        获取当前日期和时间，默认格式 2023-02-19 08:31:51
        :param fmt:
        :return:
        """
        return datetime.now().strftime(fmt)

    @staticmethod
    def get_current_time(fmt="%H:%M:%S"):
        """
        获取当前时间，默认格式 08:30:57
        :param fmt:
        :return:
        """
        return datetime.now().strftime(fmt)

    @staticmethod
    def get_current_date(fmt="%Y-%m-%d"):
        """
        获取当前日期，默认格式 2023-02-19
        :param fmt:
        :return:
        """
        return datetime.now().strftime(fmt)

    @staticmethod
    def timestamp2datetime(timestamp, fmt="%Y-%m-%d %H:%M:%S"):
        """
        时间戳转日期时间
        :param timestamp:
        :param fmt:
        :return:
        """
        if isinstance(timestamp, str):
            timestamp = int(timestamp[:10])
        return datetime.fromtimestamp(timestamp).strftime(fmt)

    @staticmethod
    def timestamp2date(timestamp, fmt="%Y-%m-%d"):
        """
        时间戳转日期
        :param timestamp:
        :param fmt:
        :return:
        """
        if isinstance(timestamp, str):
            timestamp = int(timestamp[:10])
        return datetime.fromtimestamp(timestamp).strftime(fmt)

    @staticmethod
    def datetime2timestamp(date_str, fmt="%Y-%m-%d %H:%M:%S", millisecond=False, int_type=False):
        """
        日期时间转时间戳
        :param date_str:
        :param fmt:
        :param millisecond: 返回毫秒级
        :param int_type: 返回int类型
        :return:
        """
        ts = int(time.mktime(time.strptime(date_str, fmt)))
        if millisecond:
            return ts if int_type else str(ts * 1000)
        return ts if int_type else str(ts * 1000)

    @staticmethod
    def date2timestamp(date_str, fmt="%Y-%m-%d", millisecond=False, int_type=False):
        """
        日期转时间戳
        :param date_str:
        :param fmt:
        :param millisecond: 毫秒级
        :param int_type: 返回int类型
        :return:
        """
        ts = int(time.mktime(time.strptime(date_str, fmt)))
        if millisecond:
            return ts if int_type else str(ts * 1000)
        return ts if int_type else str(ts * 1000)

    @staticmethod
    def GMT2date(GMT, fmt='%a %b %d %Y'):
        """
        GMT 格式转日期
        :param GMT:
        :param fmt:
        :return:
        """
        return datetime.strptime(GMT, fmt).strftime("%Y-%m-%d")

    @staticmethod
    def GMT2datetime(GMT, fmt='%a %b %d %H:%M:%S %Y'):
        """
        GMT 格式转日期时间
        :param GMT:
        :param fmt:
        :return:
        """
        return datetime.strptime(GMT, fmt).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def add_days(days, base_date=None, fmt="%Y-%m-%d"):
        """
        日期加天数
        :param days: 天数
        :param base_date: 时间起点
        :param fmt:
        :return:
        """
        if base_date:
            dt = datetime.strptime(base_date, fmt)
        else:
            dt = datetime.now()
        return (dt + timedelta(days=days)).strftime(fmt)

    @staticmethod
    def sub_days(days, base_date=None, fmt="%Y-%m-%d"):
        """
        日期减去指定天数
        :param days: 天数
        :param base_date: 时间起点
        :param fmt:
        :return:
        """
        return DateUtil.add_days(-days, base_date, fmt)

    @staticmethod
    def add_seconds(seconds, base_datetime=None, fmt="%Y-%m-%d %H:%M:%S"):
        """
        日期时间加减秒
        :param seconds: 秒数
        :param base_datetime: 时间起点
        :param fmt:
        :return:
        """
        if base_datetime:
            dt = datetime.strptime(base_datetime, fmt)
        else:
            dt = datetime.now()
        return (dt + timedelta(seconds=seconds)).strftime(fmt)

    @staticmethod
    def diff_days(date1, date2, fmt="%Y-%m-%d"):
        """
        计算两个日期相差天数
        :param date1:
        :param date2:
        :param fmt:
        :return:
        """
        d1 = datetime.strptime(date1, fmt)
        d2 = datetime.strptime(date2, fmt)
        return abs((d1 - d2).days)

    @staticmethod
    def diff_seconds(dt1, dt2, fmt="%Y-%m-%d %H:%M:%S"):
        """
        计算两个时间相差秒数
        :param dt1:
        :param dt2:
        :param fmt:
        :return:
        """
        d1 = datetime.strptime(dt1, fmt)
        d2 = datetime.strptime(dt2, fmt)
        return abs(int((d1 - d2).total_seconds()))

    @staticmethod
    def format_datetime(date_str, from_fmt, to_fmt):
        """
        格式转换，如 20230922 → 2023-09-22
        :param date_str:
        :param from_fmt:
        :param to_fmt:
        :return:
        """
        return datetime.strptime(date_str, from_fmt).strftime(to_fmt)
