import json
from dataclasses import dataclass
from typing import Optional
from gentccode.merge_api import SplitKV
from gentccode.merge_api import ResponseSplitKV
from gentccode.merge_api import SplitAssertResponse
from http_content_parser.param_util import ParamUtil

from gentccode.url_parse import escape_path_params, replace_not_support_char_in_pycode


@dataclass
class GenerateOptions:
    # keep the original misspelled name to match existing keyword usage
    split_respone_assert_to_new_method: bool = False
    add_method_name_suffix_str: bool = False
    add_header_kv: bool = False
    add_payload_assign: bool = True
    add_response_type_assertion: bool = True
    add_query_param_assign: bool = True
    add_reset_header: bool = True


@dataclass
class ComposeMethodOptions:
    split_respone_assert_to_new_method: bool = False
    add_mysql_method_str: Optional[str] = None
    add_before_edit_payload_str: Optional[str] = None
    add_method_name_suffix_str: str = ""
    add_payload_assign: bool = True
    add_response_type_assertion: bool = True
    add_reset_header: bool = True
    append_assert_list: Optional[list[str]] = None
    add_query_param_assign: bool = True
    add_header_kv: bool = False


@dataclass
class GenerateMethodOptions:
    method_name_suffix: str = ""
    edit_header_str: str = ""
    assert_response_str: str = ""
    preset_data_str: str = ""
    add_global_var_str: str = ""
    edit_payload_str: str = ""
    add_query_param_assgin_str: str = ""


class ComposeCode:
    def __init__(self) -> None:
        self.CHAR_SPACE_8 = "        "
        self.CHAR_SPACE_4 = "    "

    def generate_code_for_api_list(
        self,
        req_list: list[dict],
        assert_list: Optional[list[str]] = None,
        # New preferred usage: pass a GenerateOptions instance via `options`
        options: Optional[GenerateOptions] = None,
    ) -> str:
        code_str_list = []
        code_str_list.append(self.generate_code_for_import_and_class_method())
        assert_list = assert_list or []
        # build options object from either provided `options` or legacy booleans
        if options is None:
            options = GenerateOptions()

        for idx, req_info in enumerate(req_list):
            s = f"_{idx}" if options.add_method_name_suffix_str else ""
            method_opts = ComposeMethodOptions(
                split_respone_assert_to_new_method=options.split_respone_assert_to_new_method,
                add_method_name_suffix_str=s,
                add_payload_assign=options.add_payload_assign,
                add_response_type_assertion=options.add_response_type_assertion,
                add_reset_header=options.add_reset_header,
                append_assert_list=assert_list,
                add_query_param_assign=options.add_query_param_assign,
                add_header_kv=options.add_header_kv,
            )
            method_str = self.compose_method_code(req_info, method_opts)
            code_str_list.append(method_str)
        return "".join(code_str_list)

    def compose_method_code(self, req_data: dict, options: ComposeMethodOptions):
        space_8 = self.CHAR_SPACE_8
        payload_str = ""
        before_payload_assgin_str = ""
        payload_assgin_str = ""
        assert_response_str = ""
        add_global_var_str = ""
        edit_header_str = ""
        preset_data_str = ""
        method_name_suffix = ""
        append_assert_str = ""
        query_param_str = ""
        # map options to the various pieces of method code
        if options.add_mysql_method_str:
            preset_data_str += (
                space_8 + f"self.toc_sql.{options.add_mysql_method_str}()\n"
            )
        if options.add_before_edit_payload_str:
            before_payload_assgin_str += (
                f"{space_8}{options.add_before_edit_payload_str}\n"
            )
        if options.add_method_name_suffix_str:
            method_name_suffix += options.add_method_name_suffix_str
        if options.add_payload_assign:
            kv_fix_list = ["req_model.body", "", "", ""]
            payload_assgin_str += self.generate_code_for_payloads_in_method(
                param_dict=req_data.get("body", {}),
                kv_fix_list=kv_fix_list,
                middle_char="=",
            )
        if options.add_response_type_assertion:
            kv_fix_list = ["assert type(response", ")", "", ""]
            if options.split_respone_assert_to_new_method:
                assert_response_str += (
                    self.generate_code_for_respone_type_assertion_in_new_method(
                        param_dict=req_data.get("response", {}),
                        kv_fix_list=kv_fix_list,
                        middle_char=" == ",
                        req_data=req_data,
                    )
                )
                add_global_var_str += f"{space_8}global response\n"
            else:
                assert_response_str += (
                    self.generate_code_for_response_type_assertion_in_method(
                        param_dict=req_data.get("response", {}),
                        kv_fix_list=kv_fix_list,
                        middle_char=" == ",
                    )
                )
        if options.add_reset_header:
            edit_header_str += space_8 + "req_model.header = {}\n"
        if options.append_assert_list:
            for i in options.append_assert_list:
                append_assert_str += f"{space_8}{i}\n"
        if options.add_query_param_assign:
            kv_fix_list = ["req_model.query_param", "", "", ""]
            query_param_str += self.generate_code_for_payloads_in_method(
                param_dict=req_data.get("query_param", {}),
                kv_fix_list=kv_fix_list,
                middle_char="=",
            )
        if options.add_header_kv:
            kv_fix_list = ["req_model.header", "", "", ""]
            edit_header_str += self.generate_code_for_payloads_in_method(
                param_dict=req_data.get("header", {}),
                kv_fix_list=kv_fix_list,
                middle_char="=",
            )

        payload_str = before_payload_assgin_str + payload_assgin_str
        assert_response_str += append_assert_str
        method_opts = GenerateMethodOptions(
            method_name_suffix=method_name_suffix,
            edit_header_str=edit_header_str,
            assert_response_str=assert_response_str,
            preset_data_str=preset_data_str,
            add_global_var_str=add_global_var_str,
            edit_payload_str=payload_str,
            add_query_param_assgin_str=query_param_str,
        )
        return self.generate_code_for_method(req_data=req_data, options=method_opts)

    def generate_code_for_method(
        self, req_data: dict, options: GenerateMethodOptions
    ) -> str:
        space_4 = self.CHAR_SPACE_4
        space_8 = self.CHAR_SPACE_8
        edit_payload = options.edit_payload_str
        assert_response = options.assert_response_str
        global_var = options.add_global_var_str
        edit_header = options.edit_header_str
        preset_data = options.preset_data_str
        method_name_suffix = options.method_name_suffix
        query_param_str = options.add_query_param_assgin_str

        api_label_clean = replace_not_support_char_in_pycode(
            req_data.get("temp_api_label", "")
        )
        method_val = req_data.get("method", "")
        path_val = escape_path_params(req_data.get("path", ""))

        if query_param_str:
            query_param_str = f"{space_8}# edit query_param\n{query_param_str}"
        if edit_header:
            edit_header = f"{space_8}# edit header\n{edit_header}"
        if edit_payload:
            edit_payload = f"{space_8}# edit payload\n{edit_payload}"
        if preset_data:
            preset_data = f"{space_8}# preset data\n{preset_data}"

        method_str = (
            f"{space_4}@allure.title('{method_val}: {path_val}')\n"
            + f"{space_4}def test_{api_label_clean}{method_name_suffix}(self):\n"
            + f"{space_8}# read api info from yaml file, then convert it to dict\n"
            + f"{space_8}api_infos_dict = ParseUtil.parse_api_info_from_yaml(self.api_yaml_path)\n"
            + f"{space_8}# get the specified api information\n"
            + f"{space_8}req_model = api_infos_dict['{req_data['temp_api_label']}']\n"
            + query_param_str
            + edit_header
            + f"{space_8}req_model.header.update(self.header_auth)\n"
            + edit_payload
            + preset_data
            + global_var
            + f"{space_8}# request api\n"
            + f"{space_8}response = HttpUtil.request_with_yaml(req_model, service_name=self.service_name)\n"
            + f"{space_8}# assert response\n"
            + assert_response
            + "\n"
        )
        return method_str

    # return method part str, split assert code to new method.

    def generate_code_for_respone_type_assertion_in_new_method(
        self, param_dict, kv_fix_list, middle_char, req_data: dict
    ) -> str:
        split_kv = SplitAssertResponse()
        return self._get_split_kv_str(
            param_dict, split_kv, kv_fix_list, middle_char, req_data
        )

    # return response assert part code, includes response all body's key and value
    def generate_code_for_response_type_assertion_in_method(
        self, param_dict, kv_fix_list, middle_char, method_str=""
    ):
        split_kv = ResponseSplitKV()
        return self._get_split_kv_str(
            param_dict, split_kv, kv_fix_list, middle_char, method_str
        )

    def _get_split_kv_str(self, param_dict, split_kv: SplitKV, *args):
        response_str = ""
        if not param_dict:
            return response_str

        try:
            if isinstance(param_dict, str):
                normalized = param_dict.replace("\n", "\\n")
                param_dict = json.loads(normalized)
            elif isinstance(param_dict, (dict, list)):
                temp = json.loads(json.dumps(param_dict))
                param_dict = self.replace_line_break_in_dict(temp)
            else:
                print(f"param type is error: {type(param_dict)}\n{param_dict}")
                return response_str
        except Exception:
            print(f"param type is not json str.\n{param_dict}")
            return response_str

        param_assign_value_list = ParamUtil.split_swagger_param_and_type(
            param_dict, nontype=False
        )
        assigin_list = split_kv.splice_param_kv(param_assign_value_list, *args)
        return "".join(assigin_list)

    # return class top part str, includes import and class definition
    def generate_code_for_import_and_class_method(self) -> str:
        space_str_4 = self.CHAR_SPACE_4
        setup_class_str = (
            "# -*- coding: utf-8 -*-\n"
            + "from auth import get_auth\n"
            + "from utils.base.http_util import HttpUtil\n"
            + "from utils.base.parse import ParseUtil\n"
            + "from utils.business.path_util import PathUtil\n"
            + "import allure\n\n\n"
            + "class TestCases:\n"
            + f"{space_str_4}#-----------------------------------------------------------\n"
            + f"{space_str_4}# the value comes from 'conf/env_test.yaml'\n"
            + f"{space_str_4}service_name = 'service_name'\n"
            + f"{space_str_4}# replace with you own auth\n"
            + f"{space_str_4}header_auth = get_auth()\n"
            + f"{space_str_4}# replace with you own path\n"
            + f"{space_str_4}api_yaml_path = PathUtil.get_api_template_yaml_path()\n"
            + f"{space_str_4}#-----------------------------------------------------------\n\n"
        )
        return setup_class_str

    # return payload part str, includes assigin payload's key to value
    def generate_code_for_payloads_in_method(
        self, param_dict, kv_fix_list, middle_char
    ) -> str:
        payload_assigin_str = ""
        if param_dict:
            if isinstance(param_dict, str):
                try:
                    param_dict = json.loads(param_dict)
                except:
                    print(f"api body type is not json str.\n{param_dict}")
                    return payload_assigin_str
            if isinstance(param_dict, (dict, list)):
                temp = json.dumps(param_dict)
                new_param_dict = json.loads(temp)
                new_param_dict = self.replace_line_break_in_dict(new_param_dict)
                param_assign_value_list = ParamUtil.split_swagger_param_and_type(
                    new_param_dict, nontype=False
                )
                for param_item in param_assign_value_list:
                    for k, v in param_item.items():
                        new_k, new_v = self.concatenate_kv_into_str(k, v, kv_fix_list)
                        payload_assigin_str += (
                            self.CHAR_SPACE_8 + new_k + middle_char + new_v + "\n"
                        )
            else:
                print(f"api body type is error: {type(param_dict)}\n{param_dict}")
        return payload_assigin_str

    # put chars to k,v prefix and suffix.
    def concatenate_kv_into_str(self, k, v, kv_fix: list[str]) -> tuple[str, str]:
        k_prefix = kv_fix[0]
        k_suffix = kv_fix[1]
        v_prefix = kv_fix[2]
        v_suffix = kv_fix[3]
        new_k = k_prefix + str(k) + k_suffix
        new_v = v_prefix + str(v) + v_suffix
        return new_k, new_v

    def replace_line_break_in_dict(self, d):
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str) and "\n" in v:
                    d[k] = v.replace("\n", "\\n")
                elif isinstance(v, list):
                    d[k] = [
                        (
                            self.replace_line_break_in_dict(item)
                            if isinstance(item, (dict, list))
                            else (
                                item.replace("\n", "\\n")
                                if isinstance(item, str)
                                else item
                            )
                        )
                        for item in v
                    ]
                elif isinstance(v, dict):
                    d[k] = self.replace_line_break_in_dict(v)
            return d
        elif isinstance(d, list):
            return [
                (
                    self.replace_line_break_in_dict(item)
                    if isinstance(item, (dict, list))
                    else (item.replace("\n", "\\n") if isinstance(item, str) else item)
                )
                for item in d
            ]
        else:
            return d

    def append_codes_for_custom_assert(self, node: str) -> list:
        """
        Generate custom assert statements from a node string.

        Args:
            node: str, format example: "data.id=1,data.name='test'"

        Returns:
            str: Generated assert statements, each on a new line.
        """
        if not node:
            return []

        assert_lines = []

        # 支持多个 node 用逗号分隔
        node_items = node.split(",") if "," in node else [node]

        for item in node_items:
            if "=" not in item:
                continue  # 忽略格式不对的项

            node_key, expect_value = item.split("=", 1)  # 只拆一次
            actual_str = "assert response"

            # 支持多层节点，如 "data.user.id"
            for key in node_key.split("."):
                actual_str += f"['{key}']"

            # 拼接 assert 语句
            assert_lines.append(f"{actual_str} == {expect_value}")

        return assert_lines
