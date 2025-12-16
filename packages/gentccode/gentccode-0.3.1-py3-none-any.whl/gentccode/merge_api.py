# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod


def merge_api_params(swagger_dict: dict, api_dict: dict) -> tuple[dict, list]:
    result = {}
    swagger_fail_dict = []
    for k, v in swagger_dict.items():
        if v["path_param"] or v["query_param"]:
            if api_dict.get(k):
                temp_v = v
                temp_v["body_type"] = v["body"]
                temp_v["body"] = api_dict[k]["body"]
                temp_v["original_url"] = api_dict[k]["original_url"]
                temp_v["query_param"] = api_dict[k]["query_param"]
                result[k] = temp_v
            else:
                swagger_fail_dict.append(k.replace("_", "/"))
        else:
            if api_dict.get(k):
                result[k] = api_dict[k]
            else:
                swagger_fail_dict.append(k.replace("_", "/"))
                # result[k] = v
    return result, swagger_fail_dict


class SplitKV(ABC):
    def __init__(self) -> None:
        self.CHAR_SPACE_8 = "        "
        self.CHAR_SPACE_4 = "    "

    @abstractmethod
    def splice_param_kv(*args):  # 注意参数的顺序
        pass

    def convert_to_python_type(self, str_type: str):
        str_type = str_type.replace("'", "")
        if not str_type:
            return "None"
        map_types = {
            "string": "str",
            "integer": "(int,float)",
            "object": "dict",
            "number": "(int,float)",
            "boolean": "bool",
            "[array]": "list",
            "array": "list",
            "{}": "dict",
            "[object]": "list",
        }
        return map_types[str_type]

    # put chars to k,v prefix and suffix.
    def splice_kv_str(self, k, v, kv_fix: list[str]) -> tuple[str, str]:
        k_prefix = kv_fix[0]
        k_suffix = kv_fix[1]
        v_prefix = kv_fix[2]
        v_suffix = kv_fix[3]
        new_k = k_prefix + str(k) + k_suffix
        new_v = v_prefix + str(v) + v_suffix
        return new_k, new_v


class SplitAssertResponse(SplitKV):

    # 注意调用方法时参数的顺序
    def splice_param_kv(
        self, param_assign_value_list, kv_fix_list, middle_char, req_data: dict
    ):
        assigin_list = []
        allure_title = req_data["method"] + " :" + req_data["path"]
        case_method_name = "test_case_" + req_data["temp_api_label"].replace(
            "-", "_"
        ).replace("{", "").replace("}", "")
        i = 1
        for param_item in param_assign_value_list:
            result = ""
            for k, v in param_item.items():
                # 保存原有值
                temp_allure_title = allure_title
                temp_case_method_name = case_method_name
                # 生成新值
                temp_allure_title += " assert" + str(i)
                temp_case_method_name += str(i)
                method_str = (
                    f"{self.CHAR_SPACE_4}@allure.title('{temp_allure_title}')\n"
                    + f"{self.CHAR_SPACE_4}def {temp_case_method_name}(self):\n"
                    + f"{self.CHAR_SPACE_8}# assert response\n"
                )
                new_k, _ = self.splice_kv_str(k, v, kv_fix_list)
                result += method_str
                if v:
                    if str(v).replace("'", "") in ["integer", "number"]:
                        result += (
                            self.CHAR_SPACE_8
                            + new_k
                            + " in "
                            + self.convert_to_python_type(str(v))
                            + "\n"
                        )
                    else:
                        result += (
                            self.CHAR_SPACE_8
                            + new_k
                            + middle_char
                            + self.convert_to_python_type(str(v))
                            + "\n"
                        )
                    if k == "['data']":
                        result += self.CHAR_SPACE_8 + new_k + " > 0\n"
                else:
                    if k:
                        result += (
                            self.CHAR_SPACE_8 + new_k + middle_char + "None" + "\n"
                        )
                i += 1
            assigin_list.append(result)
        if not assigin_list:
            assigin_list.append(
                self.CHAR_SPACE_8
                + 'assert response == {}, "api response is not null"\n'
            )

        return assigin_list


class ResponseSplitKV(SplitKV):
    def splice_param_kv(
        self, param_assign_value_list, kv_fix_list, middle_char, method_str
    ):
        assigin_list = []
        for param_item in param_assign_value_list:
            result = ""
            for k, v in param_item.items():
                new_k, _ = self.splice_kv_str(k, v, kv_fix_list)
                result += method_str
                if v:
                    if str(v).replace("'", "") in ["integer", "number"]:
                        result += (
                            self.CHAR_SPACE_8
                            + new_k
                            + " in "
                            + self.convert_to_python_type(str(v))
                            + "\n"
                        )
                    else:
                        result += (
                            self.CHAR_SPACE_8
                            + new_k
                            + middle_char
                            + self.convert_to_python_type(str(v))
                            + "\n"
                        )
                    if k == "['data']":
                        result += self.CHAR_SPACE_8 + new_k + " > 0\n"
                else:
                    if k:
                        result += (
                            self.CHAR_SPACE_8 + new_k + middle_char + "None" + "\n"
                        )
            assigin_list.append(result)
        if not assigin_list:
            assigin_list.append(
                self.CHAR_SPACE_8
                + 'assert response == {}, "api response is not null"\n'
            )
        return assigin_list


if __name__ == "__main__":
    pass
