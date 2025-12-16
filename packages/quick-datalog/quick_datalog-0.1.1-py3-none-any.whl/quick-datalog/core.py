import datetime
import os
import sys
import json
import inspect
import traceback
from functools import wraps  # 保留原函数元信息，关键！

# ===================== 路径与配置初始化 =====================
# 定义路径常量，跨平台兼容
LOG_ROOT = os.path.join(os.getcwd(), "Datalog")
CONFIG_DIR = os.path.join(LOG_ROOT, ".config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "Config.json")

# 自动创建目录（简化写法，exist_ok=True 避免重复创建报错）
os.makedirs(LOG_ROOT, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# 默认配置（把file里的{time}改为{date}，语义更清晰）
DEFAULT_CONF = {
    "pattern": "[{time}][{func}][{type}]:{inform}",
    "file": os.path.join(LOG_ROOT, "log_{date}.txt")
}

# 初始化配置文件（不存在则创建）
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'w', encoding='cp1252') as f:
        json.dump(DEFAULT_CONF, f, indent=4)  # 格式化配置，方便手动修改

# 读取配置
with open(CONFIG_PATH, 'r', encoding='cp1252') as f:
    conf = json.load(f)

# 日志级别控制（-O参数启用生产模式，只显示INFO及以上）
level = 1 if "-O" in sys.argv else 0

# ===================== ANSI颜色配置 =====================
COLORS = {
    "DEBUG": "\033[36m",        # 青色（比灰色醒目）
    "INFO": "\033[32m",         # 绿色
    "WARN": "\033[33m",         # 黄色
    "ERROR": "\033[41;1;37m"    # 红底白字加粗
}
RESET = "\033[0m"  # 重置颜色，避免终端全局变色

# ===================== 日志核心类 =====================
class Datalog(object):
    def __init__(self, pattern=conf["pattern"], file=conf["file"]):
        self.pattern = pattern
        # 按日期命名日志文件（每天一个文件，避免文件过多）
        date_str = datetime.datetime.now().strftime(r"%Y_%m_%d")
        self.file_path = file.format(date=date_str)  # 对应配置里的{date}
        # 追加模式打开，UTF-8编码兼容所有字符（如中文）
        self.file = open(self.file_path, "a", encoding="utf-8")

    def __del__(self):
        """析构函数：程序退出时自动关闭文件，防止句柄泄漏"""
        if hasattr(self, "file") and not self.file.closed:
            self.file.close()

    def _get_real_func_name(self):
        """修复栈帧层级，获取真实的业务函数名（跳过ErrorCatch）"""
        frame = inspect.currentframe()
        # 向上追溯2层：跳过log方法 → 跳过ErrorCatch → 拿到真实函数
        for _ in range(2):
            frame = frame.f_back if frame else None
        func_name = frame.f_code.co_name if frame else "unknown"
        del frame  # 释放栈帧，避免内存泄漏
        return func_name

    def log(self, data, typ=1):
        # 映射日志级别
        type_map = {0: "DEBUG", 1: "INFO", 2: "WARN", 3: "ERROR"}
        log_type = type_map.get(typ, "DEBUG")
        
        # 级别过滤：低于设定级别的日志不输出
        if typ >= level:
            # 格式化日志内容
            log_content = self.pattern.format(
                time=datetime.datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"),
                func=self._get_real_func_name(),  # 用修复后的真实函数名
                type=log_type,
                inform=data
            )
            # 终端带颜色输出
            print(f"{COLORS[log_type]}{log_content}{RESET}")
            # 文件输出（无颜色，立即刷新避免数据丢失）
            print(log_content, file=self.file, flush=True)

# ===================== 装饰器（异常捕获器） =====================
def start_logger(func):
    # 每个装饰器创建独立的logger实例（也可改为单例，按需调整）
    logger = Datalog()

    @wraps(func)  # 保留原函数的__name__、__doc__等元信息
    def ErrorCatch(*args, **kwargs):
        # 注入logger到被装饰函数的局部命名空间
        frame = inspect.currentframe().f_back
        frame.f_locals["logger"] = logger
        
        try:
            # 执行原函数
            return func(*args, **kwargs)
        except Exception as e:
            # 拼接异常信息（含栈追踪）
            error_info = f"函数[{func.__name__}]执行出错: {str(e)}"
            error_info += f"{RESET}\n{traceback.format_exc()}"
            logger.log(error_info, typ=3)
            raise e
        finally:
            del frame  # 释放栈帧，避免内存泄漏

    return ErrorCatch

