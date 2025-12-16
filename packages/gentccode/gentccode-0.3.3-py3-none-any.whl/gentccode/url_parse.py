import re


def replace_not_support_char_in_pycode(text: str) -> str:
    pattern = r"[+/@?=.{}]"  # 定义要匹配的特殊字符模式, {}这个虽然是合法的,但是在pycode里会报错
    replacement = "_"  # 替换为的字符串

    new_string = re.sub(pattern, replacement, text)
    return new_string


def escape_path_params(text: str) -> str:
    """
    Python 的 f-string / format 会把 {} 当作占位符，如果你希望它变成纯文本，就需要把 {} 变成 {{}}。
    想保留{}, 可以用此函数进行转义
    """
    return re.sub(r"\{([^{}]+)\}", r"{{\1}}", text)
