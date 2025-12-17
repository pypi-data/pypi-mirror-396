import sys

def add(*args):
    """批量添加参数（自动根据空格拆分）"""
    for arg in args:
        if isinstance(arg, str) and " " in arg:
            # 自动拆分空格分隔的参数（如 "--name 张三" → ["--name", "张三"]）
            sys.argv.extend(arg.split(" "))
        else:
            sys.argv.append(str(arg))

def set(target_arg, new_value):
    """设置参数值（自动保留脚本名）"""
    new_value = str(new_value)
    argv = sys.argv.copy()
    arg_exists = False

    # 遍历修改已有参数
    for i, arg in enumerate(argv):
        if arg == target_arg:
            arg_exists = True
            origin_idx = i - (len(argv) - len(sys.argv))  # 映射到原sys.argv的索引
            if origin_idx + 1 < len(sys.argv):
                sys.argv[origin_idx + 1] = new_value
            else:
                sys.argv.append(new_value)
            break  # 假设参数唯一，找到后直接退出

    # 仅当参数不存在时才追加
    if not arg_exists:
        sys.argv.extend([target_arg, new_value])


def set_batch(param_dict: dict[str, ...]) -> None:
    """批量设置参数"""
    for arg, value in param_dict.items():
        set(arg, value)

def clear():
    """清空参数（自动保留脚本名）"""
    sys.argv = sys.argv[:1]

def reset(args_list):
    """完全替换参数（自动保留脚本名）"""
    sys.argv = [sys.argv[0]] + list(args_list)

def remove(target_arg: str):
    """删除指定参数及其值"""
    to_delete = []
    # 第一步：遍历原sys.argv，记录要删除的索引
    for i, arg in enumerate(sys.argv):
        if arg == target_arg:
            to_delete.append(i)
            # 检查下一个元素是否是参数值
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith(("-", "--")):
                to_delete.append(i + 1)
            break  # 假设参数唯一

    # 第二步：倒序删除（避免正序删除导致索引偏移）
    for idx in sorted(to_delete, reverse=True):
        del sys.argv[idx]

if __name__ == '__main__':
    import argparse

    add("--name 张三", "-a 20")  # 自动拆分空格分隔的参数
    set("--name", "李四")
    set("-a", 67)

    # 解析参数（此时 argparse 会读取修改后的 sys.argv）
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str)
    parser.add_argument("-a", "--age", type=int)
    args = parser.parse_args()

    print(f"姓名：{args.name}，年龄：{args.age}")  # 姓名：张三，年龄：20