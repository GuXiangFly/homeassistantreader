# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
from src.service.homeassistant_reader_service import HomeAssistantReader
import src.config.log_config
import os


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':

    reader = HomeAssistantReader(
        url=os.getenv("HA_URL", "http://192.168.31.222:8123"),
        token=os.getenv("HA_TOKEN", ""),
    )
    reader.main_process()
