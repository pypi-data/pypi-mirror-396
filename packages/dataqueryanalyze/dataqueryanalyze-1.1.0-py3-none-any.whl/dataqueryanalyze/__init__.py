# 数据查析 - DataQueryAnalyze
# 专有软件许可证，保留所有权利
# 未经许可，不得复制、修改、分发或售卖

__version__ = "1.1.0"
__author__ = "Randy"
__email__ = "411703730@qq.com"

# 导入必要的库
import os
import sys
import time
import threading
import requests

# 更新检查配置
UPDATE_SERVER_URL = "https://your-update-server.com/check_update"  # 替换为你的更新服务器URL
UPDATE_TIMEOUT = 10  # 10秒超时
UPDATE_CHECKED = False
UPDATE_AVAILABLE = False



def check_for_updates():
    """检查软件更新"""
    global UPDATE_CHECKED, UPDATE_AVAILABLE
    print("检查软件更新中...")
    
    try:
        # 发送更新检查请求，设置10秒超时
        response = requests.get(
            UPDATE_SERVER_URL,
            params={"version": __version__},
            timeout=UPDATE_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("update_available"):
                latest_version = data.get("latest_version")
                update_url = data.get("update_url")
                print(f"发现新版本: {latest_version}")
                UPDATE_AVAILABLE = True
                
                # 自动更新逻辑
                print("正在自动更新...")
                # 这里可以添加自动更新的具体实现
                # 例如：下载更新包、解压、替换文件等
                
                # 模拟更新过程
                time.sleep(2)
                print("更新完成！")
            else:
                print("当前已是最新版本")
        else:
            print(f"更新检查失败，服务器返回状态码: {response.status_code}")
    except requests.Timeout:
        print("更新检查超时（10秒），跳过更新")
    except requests.RequestException as e:
        print(f"更新检查失败: {str(e)}")
    except Exception as e:
        print(f"更新检查发生未知错误: {str(e)}")
    finally:
        UPDATE_CHECKED = True


# 在导入模块时启动更新检查线程
# 这样可以在不阻塞主程序的情况下检查更新
update_thread = threading.Thread(target=check_for_updates, daemon=True)
update_thread.start()

# 等待更新检查完成或超时
start_time = time.time()
while not UPDATE_CHECKED and (time.time() - start_time) < UPDATE_TIMEOUT + 1:
    time.sleep(0.1)

# 导入主应用类和函数
from .app import DataAnalysisApp
from .load import main

# 导入core模块
from . import core

# 导入extensions模块
from . import extensions

# 导出所有公开API
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "DataAnalysisApp",
    "main",
    "core",
    "extensions"
]
