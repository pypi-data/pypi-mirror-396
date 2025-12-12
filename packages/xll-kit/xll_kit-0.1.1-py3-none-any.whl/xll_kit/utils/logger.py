"""
日志配置模块
提供统一的日志配置和格式化
"""
import logging
import sys
from typing import Optional
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # ANSI颜色码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'

    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.RESET}"
            )
        return super().format(record)


def setup_logger(
    name: str = 'xll_kit',
    level: str = 'INFO',
    log_file: Optional[str] = None,
    use_color: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选）
        use_color: 是否使用彩色输出（仅控制台）
        format_string: 自定义日志格式

    Returns:
        配置好的Logger对象

    Example:
        >>> logger = setup_logger('xll_kit', level='DEBUG', log_file='app.log')
        >>> logger.info('Application started')
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 默认日志格式
    if format_string is None:
        format_string = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(message)s'
        )

    # 控制台Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    if use_color:
        console_formatter = ColoredFormatter(format_string)
    else:
        console_formatter = logging.Formatter(format_string)

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件Handler（如果指定了日志文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))

        # 文件日志不使用颜色
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = 'xll_kit') -> logging.Logger:
    """
    获取已配置的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        Logger对象

    Example:
        >>> logger = get_logger('xll_kit.database')
        >>> logger.info('Database connected')
    """
    return logging.getLogger(name)


class LoggerContext:
    """
    日志上下文管理器
    用于临时改变日志级别

    Example:
        >>> logger = get_logger()
        >>> with LoggerContext(logger, 'DEBUG'):
        ...     logger.debug('This will be logged')
    """

    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.old_level = logger.level

    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)


def configure_sqlalchemy_logging(level: str = 'WARNING'):
    """
    配置SQLAlchemy日志级别

    Args:
        level: 日志级别

    Example:
        >>> configure_sqlalchemy_logging('INFO')  # 显示所有SQL
        >>> configure_sqlalchemy_logging('WARNING')  # 只显示警告
    """
    logging.getLogger('sqlalchemy.engine').setLevel(getattr(logging, level.upper()))
    logging.getLogger('sqlalchemy.pool').setLevel(getattr(logging, level.upper()))


def disable_logger(name: str = 'xll_kit'):
    """
    禁用指定的日志记录器

    Args:
        name: 日志记录器名称
    """
    logger = logging.getLogger(name)
    logger.disabled = True


def enable_logger(name: str = 'xll_kit'):
    """
    启用指定的日志记录器

    Args:
        name: 日志记录器名称
    """
    logger = logging.getLogger(name)
    logger.disabled = False


# 默认配置
_default_logger = None


def get_default_logger() -> logging.Logger:
    """
    获取默认的xll_kit日志记录器
    首次调用时自动初始化

    Returns:
        默认Logger对象
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_logger(
            name='xll_kit',
            level='INFO',
            use_color=True
        )
    return _default_logger


# 便捷函数
def debug(msg: str, *args, **kwargs):
    """记录DEBUG级别日志"""
    get_default_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """记录INFO级别日志"""
    get_default_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """记录WARNING级别日志"""
    get_default_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """记录ERROR级别日志"""
    get_default_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """记录CRITICAL级别日志"""
    get_default_logger().critical(msg, *args, **kwargs)


# 使用示例
if __name__ == "__main__":
    # 示例1: 基本使用
    logger = setup_logger('xll_kit', level='DEBUG')
    logger.debug('这是调试信息')
    logger.info('这是普通信息')
    logger.warning('这是警告信息')
    logger.error('这是错误信息')
    logger.critical('这是严重错误信息')

    # 示例2: 使用文件日志
    logger_with_file = setup_logger(
        'xll_kit.db',
        level='INFO',
        log_file='logs/database.log'
    )
    logger_with_file.info('数据库操作日志')

    # 示例3: 临时改变日志级别
    logger = get_logger('xll_kit')
    with LoggerContext(logger, 'DEBUG'):
        logger.debug('临时启用DEBUG级别')
    logger.debug('这条不会显示')

    # 示例4: 配置SQLAlchemy日志
    configure_sqlalchemy_logging('INFO')

    # 示例5: 使用便捷函数
    info('使用便捷函数记录日志')
    error('发生错误')