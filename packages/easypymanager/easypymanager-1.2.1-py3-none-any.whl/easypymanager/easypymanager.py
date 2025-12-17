import sys
import os
import subprocess
import importlib.util
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import xml.etree.ElementTree as ET
import marshal  # 用于加载 .pyc 文件
from tkinter import Menu

# 获取程序所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 设置文件路径
SETTING_FILE = os.path.join(BASE_DIR, "setting.xml")

def EasyInf():
    """
    软件版本信息。
    """
    inf = {
        '软件名称': '小工具管理器',
        '版本号': '1.2.1',
        '功能介绍': '用于执行Python脚本。',
        'PID': 'MDRDSLFPY06',
        '分组': '系统工具',
        '依赖': 'pyqt5',
        '资源库版本':'202500729'    
    }
    return inf

def create_default_settings():
    """创建默认的 setting.xml 文件"""
    # 默认工作目录为程序所在目录下的 pyfilemanager 文件夹
    default_work_dir = os.path.join(BASE_DIR, "pyfilemanager")
    
    # 如果目录不存在则创建
    if not os.path.exists(default_work_dir):
        os.makedirs(default_work_dir)
    
    # 创建 XML 结构
    root = ET.Element("settings")
    ET.SubElement(root, "python_command").text = "python"
    ET.SubElement(root, "pip_command").text = "python -m pip"
    ET.SubElement(root, "work_dir").text = default_work_dir
    ET.SubElement(root, "check_interval").text = "60000"
    
    # 保存到文件
    tree = ET.ElementTree(root)
    tree.write(SETTING_FILE, encoding="utf-8", xml_declaration=True)
    
    return default_work_dir

class InstallDependenciesThread:
    """安装依赖的线程类"""
    def __init__(self, pip_command, dependencies, callback):
        self.pip_command = pip_command
        self.dependencies = dependencies
        self.callback = callback
    
    def run(self):
        """执行安装依赖"""
        try:
            for dep in self.dependencies:
                if self.pip_command.startswith("python"):
                    # 如果 Pip 命令是 "python -m pip"，拆分为列表
                    command = self.pip_command.split() + ["install", dep.strip()]
                else:
                    command = [self.pip_command, "install", dep.strip()]
                subprocess.run(command, check=True)
            self.callback(True, "")
        except Exception as e:
            self.callback(False, str(e))

class ConfigDialog:
    """配置对话框"""
    def __init__(self, parent, python_command, pip_command):
        self.parent = parent
        self.python_command = python_command
        self.pip_command = pip_command
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("配置")
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 设置主题颜色，与主界面一致
        primary_color = "#212121"  # 深黑色背景
        secondary_color = "#424242"  # 深灰色
        bg_color = primary_color  # 黑色背景，与主界面一致
        frame_bg = primary_color  # 黑色框架背景
        fg_color = "white"  # 白色文字
        heading_color = "white"
        
        # 设置窗口背景为黑色，与主界面一致
        self.dialog.configure(bg=bg_color)
        
        # 配置对话框内的样式，确保与主界面一致
        style = ttk.Style(self.dialog)
        
        # 配置框架样式
        style.configure("TFrame", 
                       background=frame_bg,
                       borderwidth=0,
                       relief="flat")
        
        # 配置标签样式
        style.configure("TLabel", 
                       background=frame_bg,
                       foreground=fg_color,
                       font=("微软雅黑", 10))
        
        # 配置输入框样式 - 不要边框
        style.configure("TEntry", 
                       background="white",
                       foreground="black",
                       font=("微软雅黑", 10),
                       padding=5,
                       borderwidth=0,  # 不要边框
                       relief="flat")
        
        # 配置按钮样式，所有按钮背景和其他背景一致，没有边框
        style.configure("TButton", 
                       background=primary_color,  # 和其他背景一致的蓝色
                       foreground="white",
                       font=("微软雅黑", 10, "bold"),
                       padding=5,
                       borderwidth=0,
                       relief="flat")
        
        # 创建框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Python 命令输入框
        python_label = ttk.Label(main_frame, text="Python 命令:")
        python_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.python_input = ttk.Entry(main_frame, width=30)
        self.python_input.insert(0, python_command)
        self.python_input.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Pip 命令输入框
        pip_label = ttk.Label(main_frame, text="Pip 命令:")
        pip_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pip_input = ttk.Entry(main_frame, width=30)
        self.pip_input.insert(0, pip_command)
        self.pip_input.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 切换阿里云源按钮
        aliyun_btn = ttk.Button(button_frame, text="切换阿里云源", command=self.switch_to_aliyun_source)
        aliyun_btn.pack(side=tk.LEFT, padx=5)
        
        # 确认按钮
        ok_button = ttk.Button(button_frame, text="确定", command=self.accept)
        ok_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.reject)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # 设置列权重
        main_frame.columnconfigure(1, weight=1)
        
        # 居中显示
        self.center_window()
    
    def center_window(self):
        """居中显示窗口"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def accept(self):
        """接受配置"""
        self.result = (self.python_input.get(), self.pip_input.get())
        self.dialog.destroy()
    
    def reject(self):
        """拒绝配置"""
        self.result = None
        self.dialog.destroy()
    
    def switch_to_aliyun_source(self):
        """切换到阿里云源"""
        try:
            # 阿里云PyPI源地址
            aliyun_source = "https://mirrors.aliyun.com/pypi/simple/"
            
            # 执行pip config命令设置阿里云源
            subprocess.run(["pip", "config", "set", "global.index-url", aliyun_source], check=True, capture_output=True, text=True)
            subprocess.run(["pip", "config", "set", "global.trusted-host", "mirrors.aliyun.com"], check=True, capture_output=True, text=True)
            
            # 显示成功信息
            tk.messagebox.showinfo("成功", "已切换到阿里云PyPI源！", parent=self.dialog)
        except subprocess.CalledProcessError as e:
            # 显示失败信息
            tk.messagebox.showwarning("失败", f"切换阿里云源失败：{e.stderr}", parent=self.dialog)
        except Exception as e:
            tk.messagebox.showwarning("错误", f"发生未知错误：{str(e)}", parent=self.dialog)
    
    def show(self):
        """显示对话框并等待结果"""
        self.parent.wait_window(self.dialog)
        return self.result

class PyFileManager:
    """小工具管理器主窗口"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("小工具管理器 V" + str(EasyInf()['版本号']))
        self.root.geometry("1000x600")
        
        # 默认配置
        self.python_command = "python"  # 启动 Python 的命令
        self.pip_command = "python -m pip"  # 安装依赖的命令
        
        # 检查并创建 setting.xml 文件（如果不存在）
        if not os.path.exists(SETTING_FILE):
            self.work_dir = create_default_settings()
        else:
            # 加载工作目录
            self.work_dir = self.load_work_dir()
            if not self.work_dir:
                # 如果 setting.xml 中没有 work_dir，创建默认设置
                self.work_dir = create_default_settings()
        
        # 确保工作目录存在
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
        
        # 数据持久化文件路径
        self.data_file = os.path.join(self.work_dir, "pytools.xml")  # 将 pytools.xml 保存到工作目录
        
        # 保存原始数据，用于搜索过滤
        self.original_data = []
        
        # 加载配置
        self.load_config()
        
        # 设置样式
        self.setup_style()
        
        # 初始化 UI
        self.init_ui()
        
        # 加载数据
        self.load_data()
        
        # 居中显示窗口
        self.center_window()
    
    def setup_style(self):
        """设置样式"""
        style = ttk.Style()
        
        # 先设置主题，确保样式基于正确的主题
        style.theme_use("clam")
        
        # 定义现代化黑色主题颜色
        primary_color = "#212121"  # 深黑色
        secondary_color = "#424242"  # 中黑色
        bg_color = "#121212"  # 纯黑色
        frame_bg = "#1E1E1E"  # 框架背景色
        card_bg = "#333333"  # 深灰色卡片背景色
        fg_color = "#FFFFFF"  # 白色文字
        heading_color = "#FFFFFF"  # 白色标题
        border_color = "#424242"  # 边框颜色
        
        # 设置全局样式 - 与配置对话框一致，避免点击配置按钮后界面变化
        self.root.configure(bg=primary_color)  # 使用黑色背景
        
        # 配置基本样式
        style.configure(".", font=("微软雅黑", 10))
        
        # 配置工具栏样式
        style.configure("Toolbar.TFrame", 
                       background=primary_color,  # 黑色工具栏
                       borderwidth=0,
                       relief="flat")
        
        # 配置按钮样式 - 确保所有按钮背景和其他背景一致，没有边框
        style.configure("TButton", 
                       background=primary_color,  # 和其他背景一致的黑色
                       foreground="white", 
                       font=("微软雅黑", 10, "bold"), 
                       padding=5,
                       borderwidth=0,
                       relief="flat")
        
        # 配置标签样式 - 与配置对话框一致，白色文字在黑色背景上
        style.configure("TLabel", 
                       foreground="white",  # 白色文字，在黑色背景上可读
                       background=primary_color)
        
        # 配置工具栏标签样式
        style.configure("Toolbar.TLabel", 
                       background=primary_color, 
                       foreground=heading_color)
        
        # 配置输入框样式 - 搜索栏不要边框
        style.configure("TEntry", 
                       background=card_bg,
                       foreground=fg_color,
                       padding=6,
                       borderwidth=0,
                       relief="flat",
                       highlightthickness=0,  # 移除焦点高亮
                       focuscolor="",  # 移除焦点颜色
                       focuswidth=0)  # 移除焦点宽度
        
        # 配置列表框样式 - 确保与整体主题一致
        style.configure("TListbox", 
                       background=card_bg, 
                       foreground=fg_color,
                       borderwidth=1,
                       relief="flat",
                       bordercolor=secondary_color)  # 黑色边框
        
        # 配置树形视图样式 - 确保与整体主题一致
        style.configure("Treeview", 
                       background=card_bg, 
                       foreground=fg_color, 
                       fieldbackground=card_bg,
                       borderwidth=1,
                       relief="flat",
                       bordercolor=secondary_color,  # 黑色边框
                       font=("微软雅黑", 10),  # 设置默认字体
                       rowheight=30)  # 增加行高到30，默认约为20
        
        # 配置树形视图标题样式 - 更突出的标题
        style.configure("Treeview.Heading", 
                       background=primary_color, 
                       foreground=heading_color,
                       font=("微软雅黑", 11, "bold"),  # 标题使用加粗字体
                       borderwidth=0,
                       relief="flat",
                       padding=(5, 5))  # 添加内边距
        
        # 配置树形视图表头悬浮效果 - 鼠标放到表头时显示深灰色
        style.map("Treeview.Heading", 
                  background=[("active", secondary_color), ("disabled", primary_color)],
                  foreground=[("active", heading_color), ("disabled", heading_color)])
        
        # 配置滚动条样式 - 与整体主题一致
        # 直接使用主题颜色变量，确保一致性
        # 配置垂直滚动条
        style.configure("Vertical.TScrollbar", 
                       gripcount=0,
                       relief="flat")
        
        # 针对clam主题，直接配置滚动条的滑块和槽
        style.configure("Vertical.TScrollbar",
                       background=secondary_color,  # 滑块颜色改为主题深灰色
                       troughcolor=frame_bg,  # 槽颜色改为框架背景色
                       arrowcolor="white",  # 箭头颜色改为白色
                       bordercolor=secondary_color,  # 边框颜色改为主题深灰色
                       borderwidth=1)  # 边框宽度设置为1
        
        # 使用map覆盖所有状态
        style.map("Vertical.TScrollbar",
                 background=[("active", secondary_color), ("!active", secondary_color), ("disabled", secondary_color)],
                 troughcolor=[("active", frame_bg), ("!active", frame_bg), ("disabled", frame_bg)])
        
        # 配置水平滚动条
        style.configure("Horizontal.TScrollbar", 
                       gripcount=0,
                       relief="flat")
        
        style.configure("Horizontal.TScrollbar",
                       background=secondary_color,  # 滑块颜色改为主题深灰色
                       troughcolor=frame_bg,  # 槽颜色改为框架背景色
                       arrowcolor="white",  # 箭头颜色改为白色
                       bordercolor=secondary_color,  # 边框颜色改为主题深灰色
                       borderwidth=1)  # 边框宽度设置为1
        
        # 使用map覆盖所有状态
        style.map("Horizontal.TScrollbar",
                 background=[("active", secondary_color), ("!active", secondary_color), ("disabled", secondary_color)],
                 troughcolor=[("active", frame_bg), ("!active", frame_bg), ("disabled", frame_bg)])
        
        # 配置分隔线样式 - 与整体主题一致
        style.configure("TPanedwindow", 
                       background=primary_color,  # 黑色背景，与其他地方一致
                       borderwidth=0,
                       relief="flat")
        
        # 配置标签框样式 - 黑色主题，与整体一致
        style.configure("TLabelframe", 
                       background=primary_color,  # 黑色背景
                       foreground="white",  # 白色文字
                       borderwidth=1,
                       relief="flat",
                       bordercolor=secondary_color)  # 深灰色边框
        
        # 配置按钮悬停效果 - 改为深灰色
        style.map("TButton", 
                  background=[("active", secondary_color), ("disabled", "#BDBDBD")],
                  foreground=[("disabled", "#757575")])
        
        # 配置标签悬停效果
        style.map("TLabel", 
                  background=[("active", secondary_color)])
        
        # 配置输入框悬停效果
        style.map("TEntry", 
                  bordercolor=[("focus", secondary_color)])
        
        # 配置列表框悬停效果
        style.map("TListbox", 
                  background=[("active", secondary_color)])
        
        # 配置树形视图悬停和选中效果
        # active状态会自动应用到当前鼠标下的项目
        style.map("Treeview", 
                  background=[("active", secondary_color),  # 悬停状态使用主题深灰色
                              ("selected", secondary_color)],  # 选中状态使用主题深灰色
                  foreground=[("active", fg_color),  # 悬停状态文字颜色
                              ("selected", fg_color)])  # 选中状态文字颜色
        
        style.configure("TLabelframe.Label", 
                       background=primary_color,  # 黑色背景
                       foreground="white",  # 白色文字
                       font=("微软雅黑", 11, "bold"),
                       padding=5)
        
        # 配置搜索框框架样式
        style.configure("Search.TFrame", 
                       background=primary_color,  # 黑色背景
                       borderwidth=0,
                       relief="flat")
    
    def load_work_dir(self):
        """从 setting.xml 中加载工作目录"""
        try:
            tree = ET.parse(SETTING_FILE)
            root = tree.getroot()
            work_dir = root.find("work_dir").text
            # 检查工作目录是否可访问
            if work_dir and os.path.exists(work_dir) and os.access(work_dir, os.W_OK):
                return work_dir
            else:
                return None
        except Exception as e:
            print(f"加载 setting.xml 失败: {str(e)}")
            return None
    
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def init_ui(self):
        """初始化 UI"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=0)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建工具栏
        self.create_toolbar(main_frame)
        
        # 创建分割框架
        self.paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 左侧分组列表
        self.create_group_list()
        
        # 右侧文件列表
        self.create_file_list()
        
        # 添加到分割窗口
        self.paned_window.add(self.group_frame, weight=1)
        self.paned_window.add(self.file_frame, weight=4)
        
        # 启用拖放功能（tkinter的拖放实现不同，这里暂时注释，后续可以根据需要实现）
    
    def create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent, padding=5)
        toolbar.configure(style="Toolbar.TFrame")
        toolbar.pack(fill=tk.X, side=tk.TOP, pady=0)
        
        # 直接使用默认TButton样式，不指定特殊样式
        # 导入文件按钮
        import_btn = ttk.Button(toolbar, text="导入文件", command=self.import_file)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        # PIP安装按钮
        pip_install_btn = ttk.Button(toolbar, text="PIP安装", command=self.pip_install)
        pip_install_btn.pack(side=tk.LEFT, padx=5)
        
        # WHL安装按钮
        install_whl_btn = ttk.Button(toolbar, text="WHL安装", command=self.install_whl)
        install_whl_btn.pack(side=tk.LEFT, padx=5)
        
        # 配置按钮
        config_btn = ttk.Button(toolbar, text="配置", command=self.configure_commands)
        config_btn.pack(side=tk.LEFT, padx=5)
        
        # 关于按钮
        about_btn = ttk.Button(toolbar, text="关于", command=self.show_about_dialog)
        about_btn.pack(side=tk.LEFT, padx=5)
        
        # 搜索框 - 使用蓝色背景样式
        search_frame = ttk.Frame(toolbar, style="Search.TFrame")
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        search_label = ttk.Label(search_frame, text="搜索:", style="Toolbar.TLabel")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_var.trace("w", self.search_files)
    
    def create_group_list(self):
        """创建左侧分组列表"""
        self.group_frame = ttk.LabelFrame(self.paned_window, text=" ")
        
        # 创建分组列表框架，使用grid布局确保滚动条位置正确
        list_frame = ttk.Frame(self.group_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建分组列表，设置深灰色主题颜色
        self.group_list = tk.Listbox(list_frame, 
                                    font=("微软雅黑", 12), 
                                    selectmode=tk.SINGLE,
                                    bg="#333333",  # 深灰色背景
                                    fg="white",  # 白色文字
                                    selectbackground="#424242",  # 选中时的背景色
                                    selectforeground="white",  # 选中时的文字颜色
                                    highlightbackground="#424242",  # 焦点边框颜色
                                    highlightcolor="#424242")  # 高亮颜色
        self.group_list.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.group_list.insert(tk.END, "全部")
        self.group_list.bind("<<ListboxSelect>>", self.filter_by_group)
        
        # 添加滚动条
        group_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.group_list.yview)
        group_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.group_list.config(yscrollcommand=group_scrollbar.set)
        
        # 设置网格权重，确保列表框可以扩展
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
    
    def create_file_list(self):
        """创建右侧文件列表"""
        self.file_frame = ttk.LabelFrame(self.paned_window, text=" ")
        
        # 创建文件列表框架
        list_frame = ttk.Frame(self.file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文件列表 - 使用extended模式以便实现点击取消选中
        # 调整列顺序，使工具名称更突出
        self.file_list = ttk.Treeview(list_frame, columns=("name", "version", "description", "group"), 
                                    show="headings", selectmode="extended")
        
        # 定义列
        self.file_list.heading("name", text="工具名称", anchor=tk.W)
        self.file_list.heading("version", text="版本", anchor=tk.W)
        self.file_list.heading("description", text="简介", anchor=tk.W)
        self.file_list.heading("group", text="分组", anchor=tk.W)
        
        # 设置列宽，调整顺序和宽度，使工具名称更突出
        self.file_list.column("name", width=250, anchor=tk.W)
        self.file_list.column("version", width=80, anchor=tk.W)
        self.file_list.column("description", width=400, anchor=tk.W)
        self.file_list.column("group", width=120, anchor=tk.W)
        
        # 添加滚动条
        file_scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        file_scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.file_list.xview)
        self.file_list.configure(yscrollcommand=file_scrollbar_y.set, xscrollcommand=file_scrollbar_x.set)
        
        # 布局
        self.file_list.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        file_scrollbar_y.grid(row=0, column=1, sticky=tk.N+tk.S)
        file_scrollbar_x.grid(row=1, column=0, sticky=tk.E+tk.W)
        
        # 设置网格权重
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.file_list.bind("<Double-1>", self.execute_file)
        self.file_list.bind("<Button-3>", self.show_context_menu)
        # 绑定点击事件，实现再次点击取消选中
        self.file_list.bind("<Button-1>", self.on_treeview_click)
        # 绑定鼠标移动事件，实现悬停效果
        self.file_list.bind("<Motion>", self.on_mouse_move)
        # 绑定鼠标离开事件，清除悬停效果
        self.file_list.bind("<Leave>", self.on_mouse_leave)
        
        # 配置悬停样式
        self.file_list.tag_configure("hover", background="#424242", foreground="white")
        # 保存当前悬停的项目ID
        self.hovered_item = None
    
    def create_install_dialog(self, title, default_values=None):
        """创建安装对话框，用于PIP安装和WHL安装"""
        # 创建填写对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置主题颜色，与主界面一致
        primary_color = "#212121"  # 深黑色背景
        secondary_color = "#424242"  # 深灰色
        bg_color = primary_color  # 黑色背景，与主界面一致
        frame_bg = primary_color  # 黑色框架背景
        fg_color = "white"  # 白色文字
        heading_color = "white"
        
        # 设置窗口背景为黑色，与主界面一致
        dialog.configure(bg=bg_color)
        
        # 配置对话框内的样式，确保与主界面一致
        style = ttk.Style(dialog)
        
        # 配置框架样式
        style.configure("TFrame", 
                       background=frame_bg,
                       borderwidth=0,
                       relief="flat")
        
        # 配置标签样式
        style.configure("TLabel", 
                       background=frame_bg,
                       foreground=fg_color,
                       font=("微软雅黑", 10))
        
        # 配置输入框样式 - 不要边框
        style.configure("TEntry", 
                       background="white",
                       foreground="black",
                       font=("微软雅黑", 10),
                       padding=5,
                       borderwidth=1,
                       relief="solid",
                       bordercolor=secondary_color)
        
        # 配置按钮样式，所有按钮背景和其他背景一致，没有边框
        style.configure("TButton", 
                       background=primary_color,  # 和其他背景一致的黑色
                       foreground="white",
                       font=("微软雅黑", 10, "bold"),
                       padding=5,
                       borderwidth=0,
                       relief="flat")
        
        # 创建框架
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 软件名称
        name_label = ttk.Label(main_frame, text="软件名称:")
        name_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        name_input = ttk.Entry(main_frame, width=30)
        name_input.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 版本号
        version_label = ttk.Label(main_frame, text="版本号:")
        version_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        version_input = ttk.Entry(main_frame, width=30)
        version_input.insert(0, "1.0.0")
        version_input.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 功能介绍
        desc_label = ttk.Label(main_frame, text="功能介绍:")
        desc_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        desc_input = ttk.Entry(main_frame, width=30)
        desc_input.insert(0, "无简介")
        desc_input.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        # PID
        pid_label = ttk.Label(main_frame, text="PID:")
        pid_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        pid_input = ttk.Entry(main_frame, width=30)
        pid_input.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 分组
        group_label = ttk.Label(main_frame, text="分组:")
        group_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        group_input = ttk.Entry(main_frame, width=30)
        group_input.insert(0, "未分组")
        group_input.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5)
        
        # PIP包名称（新增）
        pip_label = ttk.Label(main_frame, text="包名称:")
        pip_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        pip_input = ttk.Entry(main_frame, width=30)
        pip_input.grid(row=5, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 启动命令（新增，可选择）
        cmd_label = ttk.Label(main_frame, text="启动命令:")
        cmd_label.grid(row=6, column=0, sticky=tk.W, pady=5)
        cmd_input = ttk.Entry(main_frame, width=30)
        cmd_input.grid(row=6, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 填充默认值
        if default_values:
            if "name" in default_values:
                name_input.insert(0, default_values["name"])
            if "version" in default_values:
                version_input.delete(0, tk.END)
                version_input.insert(0, default_values["version"])
            if "description" in default_values:
                desc_input.delete(0, tk.END)
                desc_input.insert(0, default_values["description"])
            if "pid" in default_values:
                pid_input.insert(0, default_values["pid"])
            if "group" in default_values:
                group_input.delete(0, tk.END)
                group_input.insert(0, default_values["group"])
            if "pip_name" in default_values:
                pip_input.insert(0, default_values["pip_name"])
            if "start_cmd" in default_values:
                cmd_input.insert(0, default_values["start_cmd"])
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=15)
        
        # 保存输入值的变量
        input_values = {}
        
        # 确认按钮 - 先获取输入值，再销毁对话框
        def on_ok():
            # 在对话框关闭前获取输入值
            input_values["name"] = name_input.get()
            input_values["version"] = version_input.get()
            input_values["description"] = desc_input.get()
            input_values["pid"] = pid_input.get()
            input_values["group"] = group_input.get()
            input_values["pip_name"] = pip_input.get()
            input_values["start_cmd"] = cmd_input.get()
            dialog.cancelled = False
            dialog.destroy()
        
        ok_button = ttk.Button(button_frame, text="确定", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        def on_cancel():
            dialog.cancelled = True
            dialog.destroy()
        
        cancel_button = ttk.Button(button_frame, text="取消", command=on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        # 设置列权重
        main_frame.columnconfigure(1, weight=1)
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # 等待对话框关闭
        dialog.cancelled = True  # 默认取消
        self.root.wait_window(dialog)
        
        if dialog.cancelled:
            return None  # 用户取消
        
        # 返回输入值
        return input_values
    
    def create_install_progress_dialog(self):
        """创建安装进度对话框，显示安装过程"""
        dialog = tk.Toplevel(self.root)
        dialog.title("安装进度")
        dialog.geometry("600x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置主题颜色，与主界面一致
        primary_color = "#212121"  # 深黑色背景
        secondary_color = "#424242"  # 深灰色
        bg_color = primary_color  # 黑色背景，与主界面一致
        frame_bg = primary_color  # 黑色框架背景
        fg_color = "white"  # 白色文字
        heading_color = "white"
        
        # 设置窗口背景为黑色，与主界面一致
        dialog.configure(bg=bg_color)
        
        # 配置对话框内的样式，确保与主界面一致
        style = ttk.Style(dialog)
        
        # 配置框架样式
        style.configure("TFrame", 
                       background=frame_bg,
                       borderwidth=0,
                       relief="flat")
        
        # 配置标签样式
        style.configure("TLabel", 
                       background=frame_bg,
                       foreground=fg_color,
                       font=("微软雅黑", 10))
        
        # 配置按钮样式
        style.configure("TButton", 
                       background=primary_color,  # 和其他背景一致的黑色
                       foreground="white",
                       font=("微软雅黑", 10, "bold"),
                       padding=5,
                       borderwidth=0,
                       relief="flat")
        
        # 配置文本框样式
        style.configure("TText", 
                       background="#1E1E1E",
                       foreground="#FFFFFF",
                       font=("Consolas", 10))
        
        # 创建框架
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题标签
        title_label = ttk.Label(main_frame, text="安装过程", font=("微软雅黑", 12, "bold"))
        title_label.pack(anchor=tk.W, pady=5)
        
        # 创建文本框用于显示安装输出
        self.output_text = tk.Text(main_frame, 
                                  bg="#1E1E1E",
                                  fg="#FFFFFF",
                                  font=("Consolas", 10),
                                  wrap=tk.WORD,
                                  state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.output_text, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel_install)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # 保存对话框引用，用于后续更新
        self.progress_dialog = dialog
        self.is_cancelled = False
        
        return dialog
    
    def append_output(self, text):
        """向输出文本框添加内容"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)  # 滚动到底部
        self.output_text.config(state=tk.DISABLED)
        self.progress_dialog.update()  # 更新界面
    
    def cancel_install(self):
        """取消安装"""
        self.is_cancelled = True
        self.append_output("\n用户取消了安装\n")
    
    def close_progress_dialog(self):
        """关闭安装进度对话框"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.destroy()
            self.progress_dialog = None
    
    def install_whl(self):
        """选择并安装 WHL 文件，并添加到工具列表"""
        whl_path = filedialog.askopenfilename(
            parent=self.root,
            title="选择 WHL 文件",
            filetypes=[("WHL Files", "*.whl")]
        )
        if whl_path:
            try:
                # 使用配置的 pip 命令安装 WHL 文件
                if self.pip_command.startswith("python"):
                    # 如果 Pip 命令是 "python -m pip"，拆分为列表
                    command = self.pip_command.split() + ["install", whl_path]
                else:
                    command = [self.pip_command, "install", whl_path]
                
                # 显示安装进度对话框
                self.create_install_progress_dialog()
                
                # 执行安装并实时显示输出
                whl_filename = os.path.basename(whl_path)
                self.append_output(f"开始安装 WHL 文件: {whl_filename}...\n")
                self.append_output(f"命令: {' '.join(command)}\n\n")
                
                # 使用Popen并实时读取输出
                process = subprocess.Popen(command, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         text=True, 
                                         shell=True)
                
                # 实时读取并显示输出
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        self.append_output(line)
                    
                    # 检查是否取消安装
                    if self.is_cancelled:
                        process.terminate()
                        self.close_progress_dialog()
                        return
                
                # 等待进程结束
                return_code = process.wait()
                
                if return_code == 0:
                    self.append_output(f"\nWHL 文件安装成功！\n")
                    self.close_progress_dialog()
                    
                    # 安装成功后，显示对话框让用户填写信息
                    # 从文件名提取默认信息
                    # 移除.whl扩展名
                    package_name = os.path.splitext(whl_filename)[0]
                    # 提取包名（移除版本号）
                    if '-' in package_name:
                        base_name = package_name.split('-')[0]
                    else:
                        base_name = package_name
                    
                    # 显示安装对话框，预填默认值
                    default_values = {
                        "name": base_name,
                        "pid": base_name,
                        "pip_name": base_name,
                        "start_cmd": base_name
                    }
                    
                    input_values = self.create_install_dialog("WHL安装", default_values)
                    if not input_values:
                        messagebox.showinfo("成功", "WHL 文件安装成功，但未添加到工具列表！", parent=self.root)
                        return
                    
                    # 从保存的输入值中获取信息
                    name = input_values["name"]
                    version = input_values["version"]
                    description = input_values["description"]
                    pid = input_values["pid"]
                    group = input_values["group"]
                    pip_name = input_values["pip_name"]
                    start_cmd = input_values["start_cmd"]
                    
                    # 验证必填字段
                    if not name or not pip_name:
                        messagebox.showwarning("错误", "软件名称和包名称不能为空！", parent=self.root)
                        return
                    
                    # 如果启动命令为空，使用PIP包名称
                    if not start_cmd:
                        start_cmd = pip_name
                    
                    # 对于WHL安装的包，我们使用特殊的标记来表示它是通过WHL安装的
                    # 使用格式：pip://package_name:start_cmd
                    file_path = f"pip://{pip_name}:{start_cmd}"
                    
                    # 检查 PID 是否已存在
                    existing_item = self.find_item_by_pid(pid)
                    if existing_item:
                        self.file_list.delete(existing_item)
                        self.remove_data_by_pid(pid)
                    
                    # 添加到文件列表
                    self.file_list.insert("", "end", values=(name, version, description, group, file_path))
                    
                    # 保存到原始数据列表
                    self.original_data.append((name, version, description, group, file_path))
                    
                    # 保存文件信息
                    self.save_data(file_path, name, version, description, pid, group)
                    
                    # 更新分组列表
                    self.update_group_list()
                    
                    messagebox.showinfo("成功", f"WHL 文件 {whl_filename} 安装成功并添加到工具列表！", parent=self.root)
                else:
                    self.append_output(f"\nWHL 文件安装失败，返回码: {return_code}\n")
                    self.progress_dialog.after(2000, self.close_progress_dialog)
                    messagebox.showwarning("失败", f"WHL 文件安装失败", parent=self.root)
                
            except subprocess.CalledProcessError as e:
                self.append_output(f"\n安装失败: {e.stderr}\n")
                self.progress_dialog.after(2000, self.close_progress_dialog)
                messagebox.showwarning("失败", f"WHL 文件安装失败：{e.stderr}", parent=self.root)
            except Exception as e:
                self.append_output(f"\n发生未知错误: {str(e)}\n")
                self.progress_dialog.after(2000, self.close_progress_dialog)
                messagebox.showwarning("失败", f"发生未知错误：{str(e)}", parent=self.root)
    
    def create_install_dialog(self, title, default_values=None):
        """创建安装对话框，用于PIP安装和WHL安装"""
        # 创建填写对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置主题颜色，与主界面一致
        primary_color = "#212121"  # 深黑色背景
        secondary_color = "#424242"  # 深灰色
        bg_color = primary_color  # 黑色背景，与主界面一致
        frame_bg = primary_color  # 黑色框架背景
        fg_color = "white"  # 白色文字
        heading_color = "white"
        
        # 设置窗口背景为黑色，与主界面一致
        dialog.configure(bg=bg_color)
        
        # 配置对话框内的样式，确保与主界面一致
        style = ttk.Style(dialog)
        
        # 配置框架样式
        style.configure("TFrame", 
                       background=frame_bg,
                       borderwidth=0,
                       relief="flat")
        
        # 配置标签样式
        style.configure("TLabel", 
                       background=frame_bg,
                       foreground=fg_color,
                       font=("微软雅黑", 10))
        
        # 配置输入框样式 - 不要边框
        style.configure("TEntry", 
                       background="white",
                       foreground="black",
                       font=("微软雅黑", 10),
                       padding=5,
                       borderwidth=1,
                       relief="solid",
                       bordercolor=secondary_color)
        
        # 配置按钮样式，所有按钮背景和其他背景一致，没有边框
        style.configure("TButton", 
                       background=primary_color,  # 和其他背景一致的黑色
                       foreground="white",
                       font=("微软雅黑", 10, "bold"),
                       padding=5,
                       borderwidth=0,
                       relief="flat")
        
        # 创建框架
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 软件名称
        name_label = ttk.Label(main_frame, text="软件名称:")
        name_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        name_input = ttk.Entry(main_frame, width=30)
        name_input.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 版本号
        version_label = ttk.Label(main_frame, text="版本号:")
        version_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        version_input = ttk.Entry(main_frame, width=30)
        version_input.insert(0, "1.0.0")
        version_input.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 功能介绍
        desc_label = ttk.Label(main_frame, text="功能介绍:")
        desc_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        desc_input = ttk.Entry(main_frame, width=30)
        desc_input.insert(0, "无简介")
        desc_input.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        # PID
        pid_label = ttk.Label(main_frame, text="PID:")
        pid_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        pid_input = ttk.Entry(main_frame, width=30)
        pid_input.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 分组
        group_label = ttk.Label(main_frame, text="分组:")
        group_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        group_input = ttk.Entry(main_frame, width=30)
        group_input.insert(0, "未分组")
        group_input.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5)
        
        # PIP包名称（新增）
        pip_label = ttk.Label(main_frame, text="包名称:")
        pip_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        pip_input = ttk.Entry(main_frame, width=30)
        pip_input.grid(row=5, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 启动命令（新增，可选择）
        cmd_label = ttk.Label(main_frame, text="启动命令:")
        cmd_label.grid(row=6, column=0, sticky=tk.W, pady=5)
        cmd_input = ttk.Entry(main_frame, width=30)
        cmd_input.grid(row=6, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 填充默认值
        if default_values:
            if "name" in default_values:
                name_input.insert(0, default_values["name"])
            if "version" in default_values:
                version_input.delete(0, tk.END)
                version_input.insert(0, default_values["version"])
            if "description" in default_values:
                desc_input.delete(0, tk.END)
                desc_input.insert(0, default_values["description"])
            if "pid" in default_values:
                pid_input.insert(0, default_values["pid"])
            if "group" in default_values:
                group_input.delete(0, tk.END)
                group_input.insert(0, default_values["group"])
            if "pip_name" in default_values:
                pip_input.insert(0, default_values["pip_name"])
            if "start_cmd" in default_values:
                cmd_input.insert(0, default_values["start_cmd"])
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=15)
        
        # 保存输入值的变量
        input_values = {}
        
        # 确认按钮 - 先获取输入值，再销毁对话框
        def on_ok():
            # 在对话框关闭前获取输入值
            input_values["name"] = name_input.get()
            input_values["version"] = version_input.get()
            input_values["description"] = desc_input.get()
            input_values["pid"] = pid_input.get()
            input_values["group"] = group_input.get()
            input_values["pip_name"] = pip_input.get()
            input_values["start_cmd"] = cmd_input.get()
            dialog.cancelled = False
            dialog.destroy()
        
        ok_button = ttk.Button(button_frame, text="确定", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        def on_cancel():
            dialog.cancelled = True
            dialog.destroy()
        
        cancel_button = ttk.Button(button_frame, text="取消", command=on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        # 设置列权重
        main_frame.columnconfigure(1, weight=1)
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # 等待对话框关闭
        dialog.cancelled = True  # 默认取消
        self.root.wait_window(dialog)
        
        if dialog.cancelled:
            return None  # 用户取消
        
        # 返回输入值
        return input_values
    
    def pip_install(self):
        """PIP安装包并添加到工具列表"""
        # 显示安装对话框
        input_values = self.create_install_dialog("PIP安装")
        if not input_values:
            return  # 用户取消，不安装
        
        # 从保存的输入值中获取信息
        name = input_values["name"]
        version = input_values["version"]
        description = input_values["description"]
        pid = input_values["pid"]
        group = input_values["group"]
        pip_name = input_values["pip_name"]
        start_cmd = input_values["start_cmd"]
        
        # 验证必填字段
        if not name or not pip_name:
            messagebox.showwarning("错误", "软件名称和包名称不能为空！", parent=self.root)
            return
        
        # 如果启动命令为空，使用PIP包名称
        if not start_cmd:
            start_cmd = pip_name
        
        # 构建安装命令
        try:
            # 使用配置的 pip 命令安装包
            if self.pip_command.startswith("python"):
                # 如果 Pip 命令是 "python -m pip"，拆分为列表
                command = self.pip_command.split() + ["install", pip_name]
            else:
                command = [self.pip_command, "install", pip_name]
            
            # 显示安装进度对话框
            self.create_install_progress_dialog()
            
            # 执行安装并实时显示输出
            self.append_output(f"开始安装 {pip_name}...\n")
            self.append_output(f"命令: {' '.join(command)}\n\n")
            
            # 使用Popen并实时读取输出
            process = subprocess.Popen(command, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT, 
                                     text=True, 
                                     shell=True)
            
            # 实时读取并显示输出
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.append_output(line)
                
                # 检查是否取消安装
                if self.is_cancelled:
                    process.terminate()
                    self.close_progress_dialog()
                    return
            
            # 等待进程结束
            return_code = process.wait()
            
            if return_code == 0:
                self.append_output(f"\n安装成功！\n")
                
                # 安装成功后，添加到工具列表
                # 对于PIP安装的包，我们使用特殊的标记来表示它是通过PIP安装的
                # 使用格式：pip://package_name:start_cmd
                file_path = f"pip://{pip_name}:{start_cmd}"
                
                # 检查 PID 是否已存在
                existing_item = self.find_item_by_pid(pid)
                if existing_item:
                    self.file_list.delete(existing_item)
                    self.remove_data_by_pid(pid)
                
                # 添加到文件列表
                self.file_list.insert("", "end", values=(name, version, description, group, file_path))
                
                # 保存到原始数据列表
                self.original_data.append((name, version, description, group, file_path))
                
                # 保存文件信息
                self.save_data(file_path, name, version, description, pid, group)
                
                # 更新分组列表
                self.update_group_list()
                
                self.append_output(f"添加到工具列表成功！\n")
                
                # 延迟关闭对话框，让用户看到结果
                self.progress_dialog.after(1000, self.close_progress_dialog)
                
                messagebox.showinfo("成功", f"PIP包 {pip_name} 安装成功并添加到工具列表！", parent=self.root)
            else:
                self.append_output(f"\n安装失败，返回码: {return_code}\n")
                self.progress_dialog.after(2000, self.close_progress_dialog)
                messagebox.showwarning("安装失败", f"PIP包安装失败", parent=self.root)
            
        except subprocess.CalledProcessError as e:
            self.append_output(f"\n安装失败: {e.stderr}\n")
            self.progress_dialog.after(2000, self.close_progress_dialog)
            messagebox.showwarning("安装失败", f"PIP包安装失败：{e.stderr}", parent=self.root)
        except Exception as e:
            self.append_output(f"\n发生未知错误: {str(e)}\n")
            self.progress_dialog.after(2000, self.close_progress_dialog)
            messagebox.showwarning("错误", f"发生未知错误：{str(e)}", parent=self.root)

    
    def show_about_dialog(self):
        """显示关于对话框"""
        messagebox.showinfo("关于", "作者：清粥小菜，邮箱：411703730@qq.com", parent=self.root)
    
    def import_file(self):
        """通过文件对话框导入文件"""
        file_path = filedialog.askopenfilename(
            parent=self.root,
            title="选择文件",
            filetypes=[
                ("Python 文件", "*.py *.pyc"),
                ("扩展模块", "*.pyd *.so"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.add_file_to_list(file_path)
    
    def update_group_list(self):
        """更新分组列表"""
        groups = set()
        for item in self.file_list.get_children():
            group = self.file_list.item(item, "values")[3]
            groups.add(group)
        
        # 清空分组列表并重新添加
        self.group_list.delete(0, tk.END)
        self.group_list.insert(tk.END, "全部")
        for group in sorted(groups):
            self.group_list.insert(tk.END, group)
    
    def filter_by_group(self, event):
        """根据分组过滤文件"""
        selection = self.group_list.curselection()
        if selection:
            group = self.group_list.get(selection[0])
            keyword = self.search_var.get().strip().lower()
            
            # 清空当前显示的列表
            for item in self.file_list.get_children():
                self.file_list.delete(item)
            
            # 根据分组和搜索关键词过滤原始数据并显示
            for data in self.original_data:
                item_group = data[3]
                name = data[0].lower()
                # 同时满足分组和搜索条件
                if (group == "全部" or item_group == group) and \
                   (not keyword or keyword in name):
                    self.file_list.insert("", "end", values=data)
    
    def search_files(self, *args):
        """搜索文件"""
        keyword = self.search_var.get().strip().lower()
        
        # 清空当前显示的列表
        for item in self.file_list.get_children():
            self.file_list.delete(item)
        
        # 根据搜索关键词过滤原始数据并显示
        for data in self.original_data:
            name = data[0].lower()
            if not keyword or keyword in name:
                self.file_list.insert("", "end", values=data)
    
    def on_treeview_click(self, event):
        """处理Treeview点击事件，实现再次点击取消选中"""
        # 先获取点击的项目
        item = self.file_list.identify_row(event.y)
        if not item:
            return  # 点击了空白区域，不处理
        
        # 获取当前选中的项目
        selected_items = self.file_list.selection()
        
        # 如果点击的项目已经被选中，则取消选中
        if item in selected_items:
            # 取消选中所有项目
            self.file_list.selection_remove(item)
        else:
            # 先取消所有选中，然后选中当前项目
            self.file_list.selection_set(item)
    
    def on_mouse_move(self, event):
        """处理鼠标移动事件，实现悬停效果"""
        # 获取当前鼠标位置下的项目
        item = self.file_list.identify_row(event.y)
        
        # 如果鼠标不在任何项目上，清除悬停效果
        if not item:
            if self.hovered_item:
                # 移除之前悬停项目的hover标签
                self.file_list.item(self.hovered_item, tags=())
                self.hovered_item = None
            return
        
        # 如果鼠标移动到了新的项目上
        if item != self.hovered_item:
            # 移除之前悬停项目的hover标签
            if self.hovered_item:
                self.file_list.item(self.hovered_item, tags=())
            
            # 为当前项目添加hover标签
            self.file_list.item(item, tags=("hover",))
            self.hovered_item = item
    
    def on_mouse_leave(self, event):
        """处理鼠标离开事件，清除悬停效果"""
        if self.hovered_item:
            # 移除悬停标签
            self.file_list.item(self.hovered_item, tags=())
            self.hovered_item = None
    

    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 检查是否点击了项目
        item = self.file_list.identify_row(event.y)
        if item:
            self.file_list.selection_set(item)
            
            # 创建右键菜单
            menu = Menu(self.root, tearoff=0)
            menu.add_command(label="运行", command=lambda: self.execute_file(None))
            menu.add_command(label="移除", command=lambda: self.remove_file(item))
            menu.add_command(label="文件位置", command=lambda: self.open_file_location(item))
            
            # 显示菜单
            menu.post(event.x_root, event.y_root)
    
    def open_file_location(self, item):
        """打开文件所在目录并选中文件"""
        if not item:
            item = self.file_list.selection()[0]
        
        file_path = self.file_list.item(item, "values")[4]  # 获取文件路径
        if not file_path:
            messagebox.showwarning("错误", "文件路径无效！", parent=self.root)
            return
        
        # 跳过对PIP安装包的存在性检查，因为它们使用特殊格式
        if file_path.startswith("pip://"):
            messagebox.showinfo("提示", "PIP安装的包无法打开文件位置！", parent=self.root)
            return
        
        if not os.path.exists(file_path):
            messagebox.showwarning("错误", "文件不存在！", parent=self.root)
            return
        
        try:
            # 获取文件的绝对路径
            abs_path = os.path.abspath(file_path)
            file_dir = os.path.dirname(abs_path)
            
            # 根据不同操作系统打开文件位置
            if sys.platform == "win32":
                # Windows: 使用explorer /select命令选中文件
                subprocess.Popen(f'explorer /select,"{abs_path}"', shell=True)
            elif sys.platform == "darwin":
                # macOS: 使用open -R命令在Finder中显示文件
                subprocess.Popen(["open", "-R", abs_path])
            else:
                # Linux或其他系统: 使用xdg-open打开文件所在目录
                subprocess.Popen(["xdg-open", file_dir])
        except Exception as e:
            messagebox.showwarning("错误", f"无法打开文件位置: {str(e)}", parent=self.root)
    
    def remove_file(self, item):
        """移除文件"""
        if not item:
            item = self.file_list.selection()[0]
        
        file_path = self.file_list.item(item, "values")[4]
        if file_path:
            self.file_list.delete(item)
            self.remove_data_by_file_path(file_path)
            self.update_group_list()
    

    
    def configure_commands(self):
        """打开配置对话框"""
        dialog = ConfigDialog(self.root, self.python_command, self.pip_command)
        result = dialog.show()
        if result:
            self.python_command, self.pip_command = result
            self.save_config()  # 保存配置
    
    def save_config(self):
        """保存配置到 XML"""
        if not os.path.exists(self.data_file):
            root = ET.Element("pytools")
        else:
            tree = ET.parse(self.data_file)
            root = tree.getroot()

        # 更新或添加配置
        config = root.find("config")
        if config is None:
            config = ET.SubElement(root, "config")
        python_command = config.find("python_command")
        if python_command is None:
            python_command = ET.SubElement(config, "python_command")
        python_command.text = self.python_command
        pip_command = config.find("pip_command")
        if pip_command is None:
            pip_command = ET.SubElement(config, "pip_command")
        pip_command.text = self.pip_command

        # 保存到文件
        tree = ET.ElementTree(root)
        tree.write(self.data_file, encoding="utf-8", xml_declaration=True)
    
    def load_config(self):
        """从 XML 加载配置"""
        if os.path.exists(self.data_file):
            tree = ET.parse(self.data_file)
            root = tree.getroot()
            config = root.find("config")
            if config is not None:
                python_cmd = config.find("python_command")
                pip_cmd = config.find("pip_command")
                if python_cmd is not None:
                    self.python_command = python_cmd.text
                if pip_cmd is not None:
                    self.pip_command = pip_cmd.text
    
    def save_data(self, file_path, name, version, description, pid, group):
        """保存文件信息到 XML"""
        if not os.path.exists(self.data_file):
            root = ET.Element("pytools")
        else:
            tree = ET.parse(self.data_file)
            root = tree.getroot()

        # 检查是否已存在
        for tool in root.findall("tool"):
            if tool.get("pid") == pid:
                root.remove(tool)

        # 添加新信息
        tool = ET.SubElement(root, "tool", path=file_path, pid=pid, group=group)
        ET.SubElement(tool, "name").text = name
        ET.SubElement(tool, "version").text = version
        ET.SubElement(tool, "description").text = description

        # 保存到文件
        tree = ET.ElementTree(root)
        tree.write(self.data_file, encoding="utf-8", xml_declaration=True)
    
    def load_data(self):
        """从 XML 加载文件信息"""
        if os.path.exists(self.data_file):
            tree = ET.parse(self.data_file)
            root = tree.getroot()
            tools_to_remove = []  # 记录需要移除的工具
            
            # 清空文件列表
            for item in self.file_list.get_children():
                self.file_list.delete(item)
            
            # 清空原始数据
            self.original_data.clear()
            
            for tool in root.findall("tool"):
                file_path = tool.get("path")
                # 跳过对PIP安装包的存在性检查，因为它们使用特殊格式
                if not file_path.startswith("pip://") and not os.path.exists(file_path):
                    print(f"文件无法找到: {file_path}")
                    tools_to_remove.append(tool)  # 记录需要移除的工具
                    continue

                name = tool.find("name").text
                version = tool.find("version").text
                description = tool.find("description").text
                pid = tool.get("pid")
                group = tool.get("group", "未分组")

                # 添加到原始数据列表
                self.original_data.append((name, version, description, group, file_path))
                
                # 添加到文件列表
                self.file_list.insert("", "end", values=(name, version, description, group, file_path))

            # 移除不存在的文件
            for tool in tools_to_remove:
                root.remove(tool)
                tree.write(self.data_file, encoding="utf-8", xml_declaration=True)

            # 更新分组列表
            self.update_group_list()
    
    def remove_data_by_file_path(self, file_path):
        """从 XML 中移除文件信息"""
        if os.path.exists(self.data_file):
            tree = ET.parse(self.data_file)
            root = tree.getroot()
            for tool in root.findall("tool"):
                if tool.get("path") == file_path:
                    root.remove(tool)
                    tree.write(self.data_file, encoding="utf-8", xml_declaration=True)
                    break
    
    def remove_data_by_pid(self, pid):
        """从 XML 中移除指定 PID 的文件信息"""
        if os.path.exists(self.data_file):
            tree = ET.parse(self.data_file)
            root = tree.getroot()
            for tool in root.findall("tool"):
                if tool.get("pid") == pid:
                    root.remove(tool)
                    tree.write(self.data_file, encoding="utf-8", xml_declaration=True)
                    break
    
    def find_item_by_pid(self, pid):
        """根据 PID 查找列表项"""
        if os.path.exists(self.data_file):
            tree = ET.parse(self.data_file)
            root = tree.getroot()
            for tool in root.findall("tool"):
                if tool.get("pid") == pid:
                    file_path = tool.get("path")
                    # 在Treeview中查找
                    for item in self.file_list.get_children():
                        if self.file_list.item(item, "values")[4] == file_path:
                            return item
        return None
    
    def add_file_to_list(self, file_path):
        """将文件添加到列表并保存信息"""
        try:
            name = version = description = pid = group = None
            
            # 尝试获取元信息
            if file_path.endswith((".py", ".pyc")):
                try:
                    if file_path.endswith(".py"):
                        spec = importlib.util.spec_from_file_location("module.name", file_path)
                        if spec is None:
                            raise ImportError(f"无法加载文件: {file_path}")
                        module = importlib.util.module_from_spec(spec)
                        # 安全地执行以获取元信息
                        spec.loader.exec_module(module)
                        
                        # 检查是否有EasyInf函数
                        if hasattr(module, "EasyInf"):
                            easy_inf = module.EasyInf
                            inf = easy_inf()
                            name = inf.get("软件名称", "未知")
                            version = inf.get("版本号", "未知")
                            description = inf.get("功能介绍", "无简介")
                            pid = inf.get("PID", "未知")
                            group = inf.get("分组", "未分组")
                    else:  # .pyc - 暂时跳过复杂的元信息提取
                        print(f"跳过.pyc文件的元信息提取: {file_path}")
                        # 不尝试直接加载.pyc文件，避免"toplevel entry!"错误
                except Exception as e:
                    print(f"获取元信息时出错: {str(e)}")
                    # 详细记录错误，方便调试
                    import traceback
                    traceback.print_exc()
            
            # 如果没有获取到元信息，弹出对话框让用户填写
            if not all([name, version, description, pid, group]):
                # 创建填写对话框
                dialog = tk.Toplevel(self.root)
                dialog.title("填写工具信息")
                dialog.geometry("400x300")
                dialog.resizable(False, False)
                dialog.transient(self.root)
                dialog.grab_set()
                
                # 设置主题颜色，与主界面一致
                primary_color = "#212121"
                secondary_color = "#42A5F5"
                bg_color = primary_color  # 黑色背景，与主界面一致
                frame_bg = primary_color  # 黑色框架背景
                fg_color = "white"  # 白色文字
                heading_color = "white"
                
                # 设置窗口背景为黑色，与主界面一致
                dialog.configure(bg=bg_color)
                
                # 配置对话框内的样式，确保与主界面一致
                style = ttk.Style(dialog)
                
                # 配置框架样式
                style.configure("TFrame", 
                               background=frame_bg,
                               borderwidth=0,
                               relief="flat")
                
                # 配置标签样式
                style.configure("TLabel", 
                               background=frame_bg,
                               foreground=fg_color,
                               font=("微软雅黑", 10))
                
                # 配置输入框样式 - 不要边框
                style.configure("TEntry", 
                               background="white",
                               foreground="black",
                               font=("微软雅黑", 10),
                               padding=5,
                               borderwidth=0,  # 不要边框
                               relief="flat")
                
                # 配置按钮样式，所有按钮背景和其他背景一致，没有边框
                style.configure("TButton", 
                               background=primary_color,  # 和其他背景一致的蓝色
                               foreground="white",
                               font=("微软雅黑", 10, "bold"),
                               padding=5,
                               borderwidth=0,
                               relief="flat")
                
                # 创建框架
                main_frame = ttk.Frame(dialog, padding="10")
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # 软件名称
                default_name = os.path.splitext(os.path.basename(file_path))[0]
                name_label = ttk.Label(main_frame, text="软件名称:")
                name_label.grid(row=0, column=0, sticky=tk.W, pady=5)
                name_input = ttk.Entry(main_frame, width=30)
                name_input.insert(0, default_name)
                name_input.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
                
                # 版本号
                version_label = ttk.Label(main_frame, text="版本号:")
                version_label.grid(row=1, column=0, sticky=tk.W, pady=5)
                version_input = ttk.Entry(main_frame, width=30)
                version_input.insert(0, "1.0.0")
                version_input.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
                
                # 功能介绍
                desc_label = ttk.Label(main_frame, text="功能介绍:")
                desc_label.grid(row=2, column=0, sticky=tk.W, pady=5)
                desc_input = ttk.Entry(main_frame, width=30)
                desc_input.insert(0, "无简介")
                desc_input.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
                
                # PID
                pid_label = ttk.Label(main_frame, text="PID:")
                pid_label.grid(row=3, column=0, sticky=tk.W, pady=5)
                pid_input = ttk.Entry(main_frame, width=30)
                pid_input.insert(0, default_name)
                pid_input.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5)
                
                # 分组
                group_label = ttk.Label(main_frame, text="分组:")
                group_label.grid(row=4, column=0, sticky=tk.W, pady=5)
                group_input = ttk.Entry(main_frame, width=30)
                group_input.insert(0, "未分组")
                group_input.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5)
                
                # 按钮框架
                button_frame = ttk.Frame(main_frame)
                button_frame.grid(row=5, column=0, columnspan=2, pady=10)
                
                # 保存输入值的变量
                input_values = {}
                
                # 确认按钮 - 先获取输入值，再销毁对话框
                def on_ok():
                    # 在对话框关闭前获取输入值
                    input_values["name"] = name_input.get()
                    input_values["version"] = version_input.get()
                    input_values["description"] = desc_input.get()
                    input_values["pid"] = pid_input.get()
                    input_values["group"] = group_input.get()
                    dialog.cancelled = False
                    dialog.destroy()
                
                ok_button = ttk.Button(button_frame, text="确定", command=on_ok)
                ok_button.pack(side=tk.LEFT, padx=5)
                
                # 取消按钮
                def on_cancel():
                    dialog.cancelled = True
                    dialog.destroy()
                
                cancel_button = ttk.Button(button_frame, text="取消", command=on_cancel)
                cancel_button.pack(side=tk.LEFT, padx=5)
                
                # 设置列权重
                main_frame.columnconfigure(1, weight=1)
                
                # 居中显示
                dialog.update_idletasks()
                width = dialog.winfo_width()
                height = dialog.winfo_height()
                x = (dialog.winfo_screenwidth() // 2) - (width // 2)
                y = (dialog.winfo_screenheight() // 2) - (height // 2)
                dialog.geometry(f"{width}x{height}+{x}+{y}")
                
                # 绑定窗口关闭事件
                dialog.protocol("WM_DELETE_WINDOW", on_cancel)
                
                # 等待对话框关闭
                dialog.cancelled = True  # 默认取消
                self.root.wait_window(dialog)
                
                if dialog.cancelled:
                    return  # 用户取消，不导入文件
                
                # 从保存的输入值中获取信息
                name = input_values["name"]
                version = input_values["version"]
                description = input_values["description"]
                pid = input_values["pid"]
                group = input_values["group"]
            
            # 检查 PID 是否已存在
            existing_item = self.find_item_by_pid(pid)
            if existing_item:
                self.file_list.delete(existing_item)
                self.remove_data_by_pid(pid)
            
            # 添加到文件列表
            self.file_list.insert("", "end", values=(name, version, description, group, file_path))
            
            # 保存到原始数据列表
            self.original_data.append((name, version, description, group, file_path))
            
            # 保存文件信息
            self.save_data(file_path, name, version, description, pid, group)
            
            # 更新分组列表
            self.update_group_list()
        except Exception as e:
            messagebox.showwarning("错误", f"无法导入文件: {str(e)}", parent=self.root)
            print(e)
    
    def execute_file(self, event):
        """执行选中的文件"""
        selection = self.file_list.selection()
        if selection:
            item = selection[0]
            file_path = self.file_list.item(item, "values")[4]
            
            # 检查是否是PIP安装的包
            if file_path.startswith("pip://"):
                # 解析PIP包信息，格式：pip://package_name:start_cmd
                pip_info = file_path[6:]  # 移除前缀 "pip://"
                if ":" in pip_info:
                    package_name, start_cmd = pip_info.split(":", 1)
                else:
                    package_name = start_cmd = pip_info
                
                try:
                    # 首先尝试使用配置的 Python 命令 + -m 执行
                    command = [self.python_command, "-m", start_cmd]
                    subprocess.Popen(command, shell=True)
                except Exception as e:
                    # 如果使用 -m 失败，尝试直接使用用户输入的命令，不加任何参数
                    try:
                        print(f"使用 -m 参数执行失败，尝试直接执行: {str(e)}")
                        command = [self.python_command, start_cmd]
                        subprocess.Popen(command, shell=True)
                    except Exception as e2:
                        print(f"直接执行也失败: {str(e2)}")
                        messagebox.showwarning("错误", f"执行PIP包失败: {str(e2)}", parent=self.root)
            else:
                # 常规文件处理
                if not os.path.exists(file_path):
                    print(f"文件无法找到: {file_path}")
                    self.remove_data_by_file_path(file_path)  # 从 XML 中移除文件
                    self.file_list.delete(item)  # 从列表中移除
                    return
                try:
                    if file_path.endswith((".py", ".pyc")):
                        # 使用配置的 Python 命令执行脚本文件
                        subprocess.Popen([self.python_command, file_path], shell=True)
                    elif file_path.endswith((".pyd", ".so")):
                        # 对于扩展模块，使用 import 方法
                        module_name = os.path.splitext(os.path.basename(file_path))[0]
                        # 强制删除模块（如果已存在）
                        if module_name in sys.modules:
                            messagebox.showinfo("提示", "因前期已经加载该模块，为了避免数据丢失，请关闭本工具，重新进入后再执行。", parent=self.root)
                            return
                        
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                    
                except Exception as e:
                    print(f"执行文件失败: {str(e)}")
                    messagebox.showwarning("错误", f"执行文件失败: {str(e)}", parent=self.root)
    

    
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PyFileManager()
    app.run()
