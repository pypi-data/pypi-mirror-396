#!/usr/bin/env python
# coding: utf-8
import os
import shutil

def update_software(package_name):
    print("正在检查更新...")
    print(f"Python 解释器路径: {python_executable}")
    try:
        # 使用 os.system 调用 pip，确保通过当前 Python 解释器运行
        os.system(f"{python_executable} -m pip install {package_name} --upgrade")
    except Exception as e:
        print(f"更新失败: {e}")
        print("请检查网络连接或 pip 配置。")
    else:
        print("\n更新操作完成，您可以开展工作。")
        os.system(f"python  {file_path}")
        #os.system(f"python3  {file_path}")
package_name = "easypymanager"
package_names = package_name + ".py"
python_executable = shutil.which('python3') or shutil.which('python')



# 获取当前脚本的绝对路径
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, package_names)
# 更新软件
update_software(package_name)

