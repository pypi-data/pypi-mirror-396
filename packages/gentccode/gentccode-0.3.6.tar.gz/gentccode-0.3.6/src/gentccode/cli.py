import json
import click
from gentccode.check_version import (
    check_package_version,
    get_current_version,
    update_package,
)
from gentccode.convert_to_jmx import convert_payloads_of_curl_to_jmx_file
from gentccode.convert_to_locust import product_locust_code
from gentccode.generate_code import (
    generate_req_list_and_code_for_curl,
    generate_req_list_and_code_for_postman,
    generate_req_list_and_code_for_swagger2,
)
from gentccode.save_code_to_file import (
    write_api_info_to_yaml_file,
    write_code_to_py_file,
)


# 生成的接口信息会保存到这个文件中
YAML_FILE = "api.yaml"
# 生成的接口代码会保存到这个文件中
PY_CASE_FILE = "test_case.py"

PACKAGE_NAME = "gentccode"


@click.group()
def cli1():
    pass


# cli1的回调函数
@cli1.result_callback()
def check_update(url):
    check_package_version(PACKAGE_NAME)


@click.command(help="generate test code based on http's payload")
@click.option("-n", "--node", required=True, help="json node, like: '.','a.'")
@click.option("-p", "--paramtype", required=True, help="query,body")
@click.option(
    "-a", "--assertresponse", required=True, help="like: code=0, res.code='0'"
)
@click.argument("filename", type=click.Path(exists=True))
def cp(node, filename, paramtype, assertresponse):
    pass


@click.command(help="generate test code based on curl file")
@click.argument("filename", type=click.Path(exists=True))
@click.option("-a", "--asserts", required=True, help="like: code=0, res.code='0'")
def curl(filename, asserts):
    req_list, code = generate_req_list_and_code_for_curl(
        curl_file=filename,
        assert_list_str=asserts,
    )
    write_api_info_to_yaml_file(yaml_file=YAML_FILE, req_list=req_list)
    write_code_to_py_file(py_file=PY_CASE_FILE, code_str=code)


@click.command(help="generate test code based on swagger json file")
@click.argument("filename", type=click.Path(exists=True))
def swagger2(filename):
    with open(filename, "r") as f:
        swagger2_dict = json.loads(f.read())
    generate_req_list_and_code_for_swagger2(
        swagger2_dict=swagger2_dict, assert_list_str=""
    )


@click.command(help="generate locust script based on curl file")
@click.argument("filename", type=click.Path(exists=True))
def locust(filename):
    product_locust_code(curl_file_path=filename)


@click.command(help="generate jmeter script based on curl file")
@click.option(
    "-ja",
    "--jsonassert",
    required=True,
    help="json node, like: 'code','data.code','a.b.c'",
)
@click.option(
    "-r",
    "--rate",
    required=True,
    help="qps/s, like: 1, 10",
)
@click.option(
    "-t",
    "--time",
    required=True,
    help="total stress time: 1min, like: 1, 10",
)
@click.argument("filename", type=click.Path(exists=True))
def jmeter(filename, jsonassert, rate, time):  # cli方法中的参数必须为小写
    convert_payloads_of_curl_to_jmx_file(
        curl_file_path=filename, json_path_assert=jsonassert, rate=rate, total_time=time
    )


@click.command()
def version():
    current_version = get_current_version(package_name=PACKAGE_NAME)
    click.echo(f"{PACKAGE_NAME}: v{current_version}")


@click.command(help="upgrade gtc to newest version")
def update():
    update_package(package_name=PACKAGE_NAME)


@click.command(help="generate test code based on postman file")
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "-a", "--assertresponse", required=True, help="like: code=0, res.code='0'"
)
def postman(filename, assertresponse):
    with open(filename, "r") as f:
        postman_dict = json.loads(f.read())
    req_list, code = generate_req_list_and_code_for_postman(
        postman_dict=postman_dict,
        assert_list_str=assertresponse,
    )
    write_api_info_to_yaml_file(yaml_file=YAML_FILE, req_list=req_list)
    write_code_to_py_file(py_file=PY_CASE_FILE, code_str=code)


def main():
    cli1()


# Register commands on import so `from gentccode import cli` yields a ready-to-use group
cli1.add_command(curl)
cli1.add_command(postman)
cli1.add_command(swagger2)
cli1.add_command(locust)
cli1.add_command(cp)
cli1.add_command(jmeter)
cli1.add_command(version)
cli1.add_command(update)
