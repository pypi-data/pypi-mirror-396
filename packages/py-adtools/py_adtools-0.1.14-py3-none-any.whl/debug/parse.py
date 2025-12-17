import os
import json
import re


def read_arch_files_in_order(directory_path):
    # 1. 获取目录下所有文件名
    try:
        filenames = os.listdir(directory_path)
    except FileNotFoundError:
        print(f"错误：找不到目录 {directory_path}")
        return

    # 2. 筛选出符合 'archs_数字.json' 格式的文件
    # 正则表达式解释：^archs_(\d+)\.json$ 匹配以archs_开头，中间是数字，以.json结尾的文件
    pattern = re.compile(r"^archs_(\d+)\.json$")

    # 创建一个列表来存储 (数字编号, 完整文件名) 的元组
    valid_files = []

    for filename in filenames:
        match = pattern.match(filename)
        if match:
            # 提取文件名中的数字部分，并转为整数用于排序
            file_num = int(match.group(1))
            valid_files.append((file_num, filename))

    # 3. 关键步骤：按照数字编号进行排序
    valid_files.sort(key=lambda x: x[0])

    # 4. 逐个读取
    data_list = []
    # print(f"--- 开始按顺序读取文件 (共找到 {len(valid_files)} 个) ---")

    for file_num, filename in valid_files:
        full_path = os.path.join(directory_path, filename)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                data_list.append(content)
                # print(f"成功读取: {filename} (编号: {file_num})")

                # 在这里可以对 content 做你需要的处理
                # process_data(content)

        except json.JSONDecodeError:
            print(f"警告: {filename} 不是有效的 JSON 格式")
        except Exception as e:
            print(f"读取 {filename} 时发生错误: {e}")

    return data_list


# 请将此处替换为你图片中文件夹的实际路径
# 如果脚本就在 funsearch_c2... 这个文件夹旁边，路径可能是这样：
folder_path = "./funsearch_c2_1205_1208backup/fs_log"


all_data = read_arch_files_in_order(folder_path)
from adtools import PyProgram

for data in all_data[1:]:
    algo = data["algorithm"]
    code = PyProgram.from_text(algo)

    if code is None:
        print(algo)
        exit()
