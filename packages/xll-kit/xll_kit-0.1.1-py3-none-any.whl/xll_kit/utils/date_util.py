import os
from typing import List, Optional, Union, Iterable
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

from dateutil import parser
from dateutil.relativedelta import relativedelta
import pytz
import random
import re

os.environ["APP_TIMEZONE"] = "Asia/Shanghai"

class DateUtil:
    """企业级日期工具类，支持解析、格式化、时区、加减、周期、判断等"""

    DEFAULT_TZ: str = os.getenv("APP_TIMEZONE", "UTC")
    DEFAULT_FMT: str = "%Y-%m-%d %H:%M:%S%z"

    # 常见时区别名（保持和大型系统兼容）
    COMMON_TZ_ALIASES = {
        "CST": "Asia/Shanghai",       # 中国 CST
        "EST": "America/New_York",
        "PST": "America/Los_Angeles",
        "UTC": "UTC",
        "GMT": "UTC",
    }

    # 黑名单：无法解析的奇怪格式
    INVALID_PATTERNS = [
        r"^\d{2}$",      # 只有 2 位数字
        r"^[A-Za-z]+$",  # 只有字母
    ]

    # ----------------------------------------------------------------------
    # 解析 / 格式化
    # ----------------------------------------------------------------------
    @staticmethod
    def parse(date_str: str, default_tz: Optional[str] = None) -> datetime:
        """
        解析任意日期字符串 → datetime（自动识别时区）。
        """

        if not isinstance(date_str, str):
            raise TypeError("parse() expects a string")

        date_str = date_str.strip()
        default_tz = default_tz or DateUtil.DEFAULT_TZ

        # 黑名单格式检查
        for p in DateUtil.INVALID_PATTERNS:
            if re.match(p, date_str):
                raise ValueError(f"Invalid date string: '{date_str}'")

        # 时区别名处理
        for alias, tz_name in DateUtil.COMMON_TZ_ALIASES.items():
            if re.search(rf"\b{alias}\b", date_str):
                cleaned = date_str.replace(alias, "").strip()
                dt = parser.parse(cleaned)
                return pytz.timezone(tz_name).localize(dt)

        # 常规解析
        dt = parser.parse(date_str)

        # 补全时区
        if dt.tzinfo is None:
            dt = pytz.timezone(default_tz).localize(dt)

        return dt

    @staticmethod
    def format(dt: datetime, fmt: Optional[str] = None) -> str:
        fmt = fmt or DateUtil.DEFAULT_FMT
        return dt.strftime(fmt)

    @staticmethod
    def to_timezone(dt: datetime, tz: Optional[str] = None) -> datetime:
        tz = tz or DateUtil.DEFAULT_TZ
        if dt.tzinfo is None:
            dt = pytz.timezone(DateUtil.DEFAULT_TZ).localize(dt)
        return dt.astimezone(pytz.timezone(tz))

    # ----------------------------------------------------------------------
    # datetime / date / timestamp
    # ----------------------------------------------------------------------
    @staticmethod
    def to_date(dt: datetime) -> date:
        return dt.date()

    @staticmethod
    def to_datetime(d: date, tz: Optional[str] = None) -> datetime:
        if isinstance(d, datetime):
            return d
        if not isinstance(d, date):
            raise TypeError("to_datetime() input must be date or datetime")

        tz = tz or DateUtil.DEFAULT_TZ
        tz_obj = pytz.timezone(tz)
        return tz_obj.localize(datetime.combine(d, time.min))

    @staticmethod
    def to_timestamp(dt: datetime, ms: bool = False) -> int:
        ts = dt.timestamp()
        return int(ts * 1000) if ms else int(ts)

    @staticmethod
    def from_timestamp(ts: Union[int, float], tz: Optional[str] = None) -> datetime:
        tz = tz or DateUtil.DEFAULT_TZ
        return datetime.fromtimestamp(ts, pytz.timezone(tz))

    # ----------------------------------------------------------------------
    # 加减时间
    # ----------------------------------------------------------------------
    @staticmethod
    def add(
        dt: datetime,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0
    ) -> datetime:
        return dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def add_months(dt: datetime, months: int) -> datetime:
        return dt + relativedelta(months=months)

    # ----------------------------------------------------------------------
    # 周期边界（报表常用）
    # ----------------------------------------------------------------------
    @staticmethod
    def day_start(dt: datetime) -> datetime:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def day_end(dt: datetime) -> datetime:
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def week_start(dt: datetime) -> datetime:
        return DateUtil.day_start(dt - timedelta(days=dt.weekday()))

    @staticmethod
    def week_end(dt: datetime) -> datetime:
        return DateUtil.day_end(DateUtil.week_start(dt) + timedelta(days=6))

    @staticmethod
    def month_start(dt: datetime) -> datetime:
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def month_end(dt: datetime) -> datetime:
        start = DateUtil.month_start(dt)
        return DateUtil.month_start(start + relativedelta(months=1)) - timedelta(microseconds=1)

    @staticmethod
    def quarter_start(dt: datetime) -> datetime:
        q_month = ((dt.month - 1) // 3) * 3 + 1
        return dt.replace(month=q_month, day=1, hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def quarter_end(dt: datetime) -> datetime:
        start = DateUtil.quarter_start(dt)
        return DateUtil.month_end(start + relativedelta(months=2))

    # ----------------------------------------------------------------------
    # 时间差
    # ----------------------------------------------------------------------
    @staticmethod
    def diff_seconds(a: datetime, b: datetime) -> int:
        return int((a - b).total_seconds())

    @staticmethod
    def diff_minutes(a: datetime, b: datetime) -> int:
        return DateUtil.diff_seconds(a, b) // 60

    @staticmethod
    def diff_hours(a: datetime, b: datetime) -> int:
        return DateUtil.diff_seconds(a, b) // 3600

    @staticmethod
    def diff_days(a: datetime, b: datetime) -> int:
        return (a.date() - b.date()).days

    # ----------------------------------------------------------------------
    # 判断
    # ----------------------------------------------------------------------
    @staticmethod
    def is_same_day(a: datetime, b: datetime) -> bool:
        return a.date() == b.date()

    @staticmethod
    def is_same_month(a: datetime, b: datetime) -> bool:
        return a.year == b.year and a.month == b.month

    @staticmethod
    def is_same_week(a: datetime, b: datetime) -> bool:
        return a.isocalendar()[:2] == b.isocalendar()[:2]

    @staticmethod
    def in_range(dt: datetime, start: datetime, end: datetime) -> bool:
        return start <= dt <= end

    # ----------------------------------------------------------------------
    # 随机时间（测试/模拟）
    # ----------------------------------------------------------------------
    @staticmethod
    def random_between(start: datetime, end: datetime) -> datetime:
        ts = random.randint(int(start.timestamp()), int(end.timestamp()))
        return datetime.fromtimestamp(ts, start.tzinfo)

    # ----------------------------------------------------------------------
    # 批量解析
    # ----------------------------------------------------------------------
    @staticmethod
    def parse_list(date_list: Iterable[str], default_tz: Optional[str] = None) -> List[datetime]:
        return [DateUtil.parse(x, default_tz) for x in date_list]

    # ----------------------------------------------------------------------
    # 当前时间
    # ----------------------------------------------------------------------
    @staticmethod
    def now(tz: Optional[str] = None) -> datetime:
        tz = tz or DateUtil.DEFAULT_TZ
        return datetime.now(pytz.timezone(tz))

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(pytz.timezone("UTC"))

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """任意时间转 UTC"""
        if dt.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        return dt.astimezone(ZoneInfo("UTC"))

    @staticmethod
    def to_local(dt: datetime, tz: ZoneInfo = ZoneInfo(DEFAULT_TZ)) -> datetime:
        """UTC 转当前配置时区"""
        if dt.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        return dt.astimezone(tz)



def sample_usage():
    print(DateUtil.parse("2024-01-02 10:00:00"))
    print(DateUtil.parse("2024-01-02 10:00:00 CST"))

    print(DateUtil.parse("Tue, 20 Feb 2024 16:00:00 +0800") ) # RFC1123
    print(DateUtil.parse("2024/02/20 10:00"))
    print(DateUtil.parse("2024-02-20"))
    print(DateUtil.parse("20240220"))
    print(DateUtil.parse("2024-02-20T10:20:30Z"))  # ISO8601
    print(DateUtil.parse("Fri Nov 28 17:56:06 CST 2025"))


    local_now = DateUtil.now()
    utc_now = DateUtil.now_utc()
    print(local_now)
    print(DateUtil.to_utc(local_now))

    print(utc_now)
    print(DateUtil.to_local(utc_now))



if __name__ == "__main__":
    sample_usage()
