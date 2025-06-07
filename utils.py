import pathlib
#--- 存储静态数据 ---
country = {
    "1":"德国",
    "2":"英国",
    "3":"日本",
    "4":"苏联",
    "5":"美国",
    "6":"法国",
    "7":"意大利",
    "8":"波兰",
    "9":"芬兰"
    }

def get_file(file_path, pattern="*"):
    """
    函数 获取给定目录下的所有文件的绝对路径
    参数 file_path: 文件目录
    参数 pattern:默认返回所有文件，也可以自定义返回文件类型，例如：pattern="*.py"
    返回值 abspath:文件路径列表
    """
    all_file = []
    files = pathlib.Path(file_path).rglob(pattern)
    for file in files:
        if pathlib.Path.is_file(file):
            all_file.append(file)
    return all_file