import logging
import os
from datetime import datetime, timezone, timedelta

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 定义北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_time(*_args):
    """返回北京时间的 time.struct_time，用于日志格式化."""
    return datetime.now(BEIJING_TZ).timetuple()


# 创建格式化器，强制使用北京时间
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
formatter.converter = beijing_time

# 文件日志处理器
file_handler = logging.FileHandler(
    os.path.join(LOG_DIR, "reader.log"),
    encoding="utf-8",
)
file_handler.setFormatter(formatter)

# 控制台日志处理器
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler],
)
