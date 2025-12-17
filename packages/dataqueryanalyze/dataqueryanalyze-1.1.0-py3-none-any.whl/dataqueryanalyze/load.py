#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import platform
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

print(f"Python 版本: {platform.python_version()}")
print(f"完整版本信息: {platform.python_version_tuple()}")
print(f"实现方式: {platform.python_implementation()} {platform.python_version()}")

# 导入DataAnalysisApp类
from .app import DataAnalysisApp

# 定义main函数，复制app.py中的入口点代码
def main():
    app_instance = QApplication(sys.argv)
    app_instance.setStyle('Fusion')  # 使用Fusion风格以获得更好的跨平台一致性
    
    # 设置应用程序字体
    font = QFont()
    font.setFamily('Microsoft YaHei')
    font.setPointSize(9)
    app_instance.setFont(font)
    
    window = DataAnalysisApp()
    window.show()
    sys.exit(app_instance.exec())

if __name__ == '__main__':
    main()
