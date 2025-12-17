import re
import time
from urllib.parse import urlparse
from http_content_parser.api_parser import ApiModelParser

api_parser = ApiModelParser()

CHAR_SPACE_8 = "        "
CHAR_SPACE_4 = "    "


def get_import_str():
    import_str = (
        "from locust import HttpUser, TaskSet, task\n"
        + "import json\n"
        + "from requests import JSONDecodeError\n\n"
        # + "from gevent.lock import Semaphore\n\n"
        # + "all_users_spawned = Semaphore()\n"
        # + "all_users_spawned.acquire()\n\n"
    )
    return import_str


def get_listener_str():
    listener_str = (
        f"@events.init.add_listener\n"
        + f"def _(environment, **kw):\n"
        + f"{CHAR_SPACE_4}@environment.events.spawning_complete.add_listener\n"
        + f"{CHAR_SPACE_4}def on_spawning_complete(**kw):\n"
        + f"{CHAR_SPACE_8}all_users_spawned.release()\n\n"
    )
    return listener_str


def get_user_class(host: str):
    http_user_class_str = (
        "class MyUser(HttpUser):\n"
        + f"{CHAR_SPACE_4}host = '{host}'\n"
        + f"{CHAR_SPACE_4}#wait_time = between(0, 1)  # 定义用户间隔时间，单位秒\n"
        + f"{CHAR_SPACE_4}tasks = [UserTasks]\n\n"
    )
    return http_user_class_str


def get_user_task_class_str():
    task_set_str = (
        f"class UserTasks(TaskSet):\n"
        # + f"{CHAR_SPACE_4}def on_start(self):\n"
        # + f"{CHAR_SPACE_8}all_users_spawned.wait()\n"
        # + f"{CHAR_SPACE_8}self.wait()\n\n"
    )
    return task_set_str


def get_task_str_of_method(payload: dict):
    method = payload["method"].lower()
    # host = payload.host
    path = payload["path"]
    query_param = payload["query_param"]
    header = payload["header"]
    params_str = ""
    header_str = ""
    if method != "get":
        var_str = (
            f"{CHAR_SPACE_8}body_json={payload['body']}\n"
            + f"{CHAR_SPACE_8}body_json=json.dumps(body_json)\n"
        )
        params_str += f", data=body_json"
    else:
        var_str = ""
        if query_param and query_param != "{}":
            var_str = f"{CHAR_SPACE_8}query_param = {query_param}\n"
            params_str += f", params=query_param"
    if header and header != "{}":
        header_str = f"{CHAR_SPACE_8}header = {header}\n"
        params_str += ", headers=header"

    method_name = replace_api_label_chars(path)
    task_str = (
        f"{CHAR_SPACE_4}@task(1)\n"
        + f"{CHAR_SPACE_4}def {method_name}(self):\n"
        + f"{CHAR_SPACE_8}api_path = '{path}'\n"
        + header_str
        + var_str
        + f"{CHAR_SPACE_8}with self.client.{method}(url=api_path{ params_str }, name=api_path, catch_response=True) as response:\n"
        + f"{CHAR_SPACE_8}{CHAR_SPACE_4}try:\n"
        + f"{CHAR_SPACE_8}{CHAR_SPACE_8}if response.status_code == 200:\n"
        + f"{CHAR_SPACE_8}{CHAR_SPACE_8}{CHAR_SPACE_4}response.success()\n"
        + f"{CHAR_SPACE_8}{CHAR_SPACE_8}else:\n"
        + f"{CHAR_SPACE_8}{CHAR_SPACE_8}{CHAR_SPACE_4}response.fail('response code is not 200')\n"
        + f"{CHAR_SPACE_8}{CHAR_SPACE_4}except JSONDecodeError:\n"
        + f"{CHAR_SPACE_8}{CHAR_SPACE_8}response.failure('Response could not be decoded as JSON')\n\n"
    )
    return task_str


def replace_api_label_chars(string):
    pattern = r"[-+@?={}/.]"  # 定义要匹配的特殊字符模式
    replacement = "_"  # 替换为的字符串

    new_string = re.sub(pattern, replacement, string)
    return new_string


def product_locust_code(curl_file_path):
    now_date = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    http_payloads = api_parser.get_api_list_for_curl(curl_file=curl_file_path)
    py_name = f"locust-{now_date}.py"
    with open(py_name, "at") as f:
        f.write(get_import_str() + get_user_task_class_str())
        host = ""
        for http_payload in http_payloads:
            task_body = get_task_str_of_method(http_payload)
            f.write(task_body)
            temp_url = http_payload["original_url"]
            host = _split_url(temp_url)
        f.write(get_user_class(host))


def _split_url(url):
    if url:
        parsed = urlparse(url)
        l = parsed.scheme + "://" + parsed.netloc + "/"
        return l
    else:
        return ""


if __name__ == "__main__":
    product_locust_code("")
