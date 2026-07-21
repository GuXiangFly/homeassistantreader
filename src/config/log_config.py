import glob
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from logging.handlers import TimedRotatingFileHandler

# @author guxiang
# @date 2026-07-21

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 定义北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# 日志保留时长（小时）
LOG_RETENTION_HOURS = 72


def beijing_time(*_args):
    """返回北京时间的 time.struct_time，用于日志格式化."""
    return datetime.now(BEIJING_TZ).timetuple()


def cleanup_old_logs():
    """清理超过 LOG_RETENTION_HOURS 小时的旧日志文件."""
    pattern = os.path.join(LOG_DIR, "reader.log.*")
    cutoff_time = time.time() - LOG_RETENTION_HOURS * 3600

    for log_file in glob.glob(pattern):
        try:
            if os.path.getmtime(log_file) < cutoff_time:
                os.remove(log_file)
        except OSError:
            pass


# 创建格式化器，强制使用北京时间
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
formatter.converter = beijing_time

# 按小时轮转的文件日志处理器
# - 当前日志写入 reader.log
# - 每小时轮转一次，旧文件重命名为 reader.log.yyyyMMddHH
# - backupCount=72 保留最近 72 个轮转文件（即 72 小时）
file_handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "reader.log"),
    when="H",
    interval=1,
    backupCount=72,
    encoding="utf-8",
)
# Python 3.12 不支持构造参数 suffix，构造后覆盖即可
file_handler.suffix = "%Y%m%d%H"
file_handler.setFormatter(formatter)

# 控制台日志处理器
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# 启动时清理过期日志
cleanup_old_logs()

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler],
)
