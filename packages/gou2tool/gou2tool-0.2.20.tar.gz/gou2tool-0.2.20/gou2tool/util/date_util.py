import time
from datetime import datetime, timedelta


class DateUtil:
    """日期工具类"""

    @staticmethod
    def date(format_str='%Y-%m-%d %H:%M:%S', timestamp=None):
        """
        获取当前时间或指定时间戳的格式化日期

        Args:
            format_str: 日期格式，默认为 '%Y-%m-%d %H:%M:%S'
            timestamp: 时间戳，None表示当前时间

        Returns:
            str: 格式化后的日期字符串
        """
        if timestamp is None:
            return datetime.now().strftime(format_str)
        else:
            return datetime.fromtimestamp(timestamp).strftime(format_str)

    @staticmethod
    def now(format_str='%Y-%m-%d %H:%M:%S', timestamp=None):
        """
        获取当前时间或指定时间戳的格式化日期（别名方法）

        Args:
            format_str: 日期格式，默认为 '%Y-%m-%d %H:%M:%S'
            timestamp: 时间戳，None表示当前时间

        Returns:
            str: 格式化后的日期字符串
        """
        return DateUtil.date(format_str, timestamp)

    @staticmethod
    def current_microseconds():
        """
        获取当前时间的微秒部分

        Returns:
            int: 微秒数
        """
        return int((time.time() - int(time.time())) * 1000000)

    @staticmethod
    def date_with_microseconds(format_str='%Y-%m-%d %H:%M:%S.%f', microtime=None):
        """
        格式化包含微秒的时间

        Args:
            format_str: 日期格式，默认为 '%Y-%m-%d %H:%M:%S.%f'
            microtime: 微秒时间戳，None表示当前时间

        Returns:
            str: 格式化后的时间（包含微秒）
        """
        if microtime is None:
            microtime = time.time()

        dt = datetime.fromtimestamp(microtime)
        return dt.strftime(format_str)

    @staticmethod
    def date_cn():
        """
        获取中文格式的当前日期时间

        Returns:
            str: 中文格式的日期时间
        """
        return datetime.now().strftime('%Y年%m月%d日 %H时%M分%S秒')

    @staticmethod
    def current():
        """
        获取当前时间的时间戳（毫秒）

        Returns:
            int: 当前时间毫秒数
        """
        return int(round(time.time() * 1000))

    @staticmethod
    def current_seconds():
        """
        获取当前时间的时间戳（秒）

        Returns:
            int: 当前时间秒数
        """
        return int(time.time())

    @staticmethod
    def first_day_of_month(year=None, month=None, format_str='%Y-%m-%d'):
        """
        获取指定月份的第一天

        Args:
            year: 年份，默认为当前年份
            month: 月份，默认为当前月份
            format_str: 日期格式，默认为 '%Y-%m-%d'

        Returns:
            str: 指定月份第一天日期
        """
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month

        dt = datetime(year, month, 1)
        return dt.strftime(format_str)

    @staticmethod
    def last_day_of_month(year=None, month=None, format_str='%Y-%m-%d'):
        """
        获取指定月份的最后一天

        Args:
            year: 年份，默认为当前年份
            month: 月份，默认为当前月份
            format_str: 日期格式，默认为 '%Y-%m-%d'

        Returns:
            str: 指定月份最后一天日期
        """
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month

        # 下个月第一天减一天就是本月最后一天
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        last_day = next_month.replace(day=1) - timedelta(days=1)
        return last_day.strftime(format_str)

    @staticmethod
    def first_day_of_year(year=None, format_str='%Y-%m-%d'):
        """
        获取指定年份的第一天

        Args:
            year: 年份，默认为当前年份
            format_str: 日期格式，默认为 '%Y-%m-%d'

        Returns:
            str: 指定年份第一天日期
        """
        if year is None:
            year = datetime.now().year

        dt = datetime(year, 1, 1)
        return dt.strftime(format_str)

    @staticmethod
    def last_day_of_year(year=None, format_str='%Y-%m-%d'):
        """
        获取指定年份的最后一天

        Args:
            year: 年份，默认为当前年份
            format_str: 日期格式，默认为 '%Y-%m-%d'

        Returns:
            str: 指定年份最后一天日期
        """
        if year is None:
            year = datetime.now().year

        dt = datetime(year, 12, 31)
        return dt.strftime(format_str)

    @staticmethod
    def first_day_of_week(year=None, week=None, format_str='%Y-%m-%d'):
        """
        获取指定周的第一天（周一）

        Args:
            year: 年份，默认为当前年份
            week: 周数，默认为当前周
            format_str: 日期格式，默认为 '%Y-%m-%d'

        Returns:
            str: 指定周第一天日期
        """
        if year is None:
            year = datetime.now().year
        if week is None:
            week = datetime.now().isocalendar()[1]

        # 计算该年第1周的周一
        jan_4 = datetime(year, 1, 4)  # 该年第一个周四
        first_monday = jan_4 - timedelta(days=jan_4.weekday())
        target_monday = first_monday + timedelta(weeks=week - 1)

        return target_monday.strftime(format_str)

    @staticmethod
    def last_day_of_week(year=None, week=None, format_str='%Y-%m-%d'):
        """
        获取指定周的最后一天（周日）

        Args:
            year: 年份，默认为当前年份
            week: 周数，默认为当前周
            format_str: 日期格式，默认为 '%Y-%m-%d'

        Returns:
            str: 指定周最后一天日期
        """
        if year is None:
            year = datetime.now().year
        if week is None:
            week = datetime.now().isocalendar()[1]

        # 计算该年第1周的周一
        jan_4 = datetime(year, 1, 4)  # 该年第一个周四
        first_monday = jan_4 - timedelta(days=jan_4.weekday())
        target_sunday = first_monday + timedelta(weeks=week - 1, days=6)

        return target_sunday.strftime(format_str)

    @staticmethod
    def today_number(with_leading_zero=True):
        """
        获取今天是几号

        Args:
            with_leading_zero: 是否补零，默认True

        Returns:
            str: 今天的日期号码
        """
        if with_leading_zero:
            return datetime.now().strftime('%d')
        else:
            return datetime.now().strftime('%-d')

    @staticmethod
    def day_number(timestamp=None, with_leading_zero=True):
        """
        获取指定时间戳是几号

        Args:
            timestamp: 时间戳，默认为当前时间
            with_leading_zero: 是否补零，默认True

        Returns:
            str: 指定时间的日期号码
        """
        if timestamp is None:
            timestamp = time.time()

        dt = datetime.fromtimestamp(timestamp)
        if with_leading_zero:
            return dt.strftime('%d')
        else:
            return dt.strftime('%-d')

    @staticmethod
    def is_today(date_param=None, format_str='%Y-%m-%d'):
        """
        判断指定日期是否为今天

        Args:
            date_param: 日期参数，可以是日期字符串、时间戳或None（默认为当前时间）
            format_str: 日期格式，默认为 '%Y-%m-%d'

        Returns:
            bool: 如果指定日期是今天则返回True，否则返回False
        """
        today = datetime.now().strftime(format_str)

        if date_param is None:
            check_date = today
        elif isinstance(date_param, (int, float)):
            check_date = datetime.fromtimestamp(date_param).strftime(format_str)
        else:
            check_date = datetime.strptime(str(date_param), format_str).strftime(format_str)

        return today == check_date

    @staticmethod
    def is_yesterday(date_param=None, format_str='%Y-%m-%d'):
        """
        判断指定日期是否为昨天

        Args:
            date_param: 日期参数，可以是日期字符串、时间戳或None（默认为当前时间）
            format_str: 日期格式，默认为 '%Y-%m-%d'

        Returns:
            bool: 如果指定日期是昨天则返回True，否则返回False
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime(format_str)

        if date_param is None:
            check_date = datetime.now().strftime(format_str)
        elif isinstance(date_param, (int, float)):
            check_date = datetime.fromtimestamp(date_param).strftime(format_str)
        else:
            check_date = datetime.strptime(str(date_param), format_str).strftime(format_str)

        return yesterday == check_date
