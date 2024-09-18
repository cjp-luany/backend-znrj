import os

import yaml


def merge_dicts(dest, src):
    """
    递归地将 src 字典内容合并到 dest 字典中。
    如果有相同的键且值为字典，则递归合并。
    否则，src 的值会覆盖 dest 的值。
    """
    for key, value in src.items():
        if key in dest:
            if isinstance(dest[key], dict) and isinstance(value, dict):
                merge_dicts(dest[key], value)
            else:
                dest[key] = value
        else:
            dest[key] = value


def read_yaml_files(directory):
    yaml_data = {}

    # 遍历指定目录
    for filename in os.listdir(directory):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                try:
                    # 加载 YAML 文件内容
                    data = yaml.safe_load(file)

                    if data:
                        # 合并当前文件的内容到 yaml_data 中
                        merge_dicts(yaml_data, data)
                except yaml.YAMLError as e:
                    print(f"Error reading {filename}: {e}")

    return yaml_data
