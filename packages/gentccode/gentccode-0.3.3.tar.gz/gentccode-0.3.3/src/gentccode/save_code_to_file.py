import os
from pathlib import Path
from typing import List, Dict, Any
import yaml


def write_api_info_to_yaml_file(yaml_file: str, req_list: List[Dict[str, Any]]) -> None:
    """
    Append API information to a YAML file. If the file does not exist, it will be created.

    Args:
        yaml_file: Path to the YAML file to write.
        req_list: List of API request dictionaries, each containing keys:
                  original_url, path, query_param, path_param, header,
                  body, method, response, temp_api_label.
    """
    yaml_path = Path(yaml_file)
    yaml_path.parent.mkdir(parents=True, exist_ok=True)  # 确保父目录存在

    # 读取已有内容
    if yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as f:
            existing_data = yaml.safe_load(f) or {}
    else:
        existing_data = {}

    # 构造新的 API 数据
    new_data = {
        req_model["temp_api_label"]: {
            key: req_model[key]
            for key in (
                "original_url",
                "path",
                "query_param",
                "path_param",
                "header",
                "body",
                "method",
                "response",
            )
            if key in req_model
        }
        for req_model in req_list
    }

    # 合并已有数据和新数据
    existing_data.update(new_data)

    # 写回 YAML 文件
    with yaml_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(existing_data, f, sort_keys=False, allow_unicode=True)


def write_code_to_py_file(py_file: str, code_str: str):
    with open(py_file, "wt", encoding="utf-8") as f:
        f.write(code_str)
