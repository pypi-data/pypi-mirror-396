from http_content_parser.api_parser import ApiModelParser
from gentccode.compose_code import ComposeCode, GenerateOptions
from gentccode.url_parse import replace_not_support_char_in_pycode

compose_code = ComposeCode()
api_parser = ApiModelParser()


def generate_req_list_and_code_for_curl(
    curl_file: str,
    assert_list_str: str,
) -> tuple[list, str]:
    req_list = api_parser.get_api_list_for_curl(curl_file=curl_file)
    assert_list = compose_code.append_codes_for_custom_assert(assert_list_str)
    code_str = compose_code.generate_code_for_api_list(
        req_list=req_list,
        assert_list=assert_list,
    )
    return req_list, code_str


def generate_req_list_and_code_for_swagger2(
    swagger2_dict: dict, assert_list_str: str
) -> tuple[list, str]:
    req_list = api_parser.get_api_list_for_swagger(swagger2_dict)
    assert_list = compose_code.append_codes_for_custom_assert(assert_list_str)
    code_str = compose_code.generate_code_for_api_list(
        req_list=req_list, assert_list=assert_list
    )
    return req_list, code_str


def generate_req_list_and_code_for_postman(
    postman_dict: dict,
    assert_list_str: str,
) -> tuple[list, str]:
    req_model_list = api_parser.get_api_list_for_postman(postman_dict)
    assert_list = compose_code.append_codes_for_custom_assert(assert_list_str)
    code_str = compose_code.generate_code_for_api_list(
        req_list=req_model_list,
        assert_list=assert_list,
    )
    return req_model_list, code_str


def generate_req_list_and_code_for_openapi(
    openapi_dict: dict,
    assert_list_str: str,
) -> tuple[list, str]:
    req_model_list = api_parser.get_api_list_for_openapi(openapi_dict)
    assert_list = compose_code.append_codes_for_custom_assert(assert_list_str)
    code_str = compose_code.generate_code_for_api_list(
        req_list=req_model_list,
        assert_list=assert_list,
    )
    return req_model_list, code_str


def generate_req_list_and_code_for_payload(
    payload_list: list,
    payload_type: str,
    req_dict: dict,
    assert_list_str: str,
) -> tuple[list, str]:
    req_list = __compose_req_list_for_payload(
        payload_list=payload_list, payload_type=payload_type, req_dict=req_dict
    )
    assert_list = compose_code.append_codes_for_custom_assert(assert_list_str)
    options = GenerateOptions()
    options.add_method_name_suffix_str = True
    code_str = compose_code.generate_code_for_api_list(
        req_list=req_list,
        assert_list=assert_list,
        options=options,
    )
    return req_list, code_str


def __compose_req_list_for_payload(
    payload_list: list[dict], payload_type: str, req_dict: dict
) -> list[dict]:
    if payload_type not in {"body", "query_param"}:
        return []

    req_list = []
    for payload in payload_list:
        new_path = replace_not_support_char_in_pycode(req_dict.get("path", ""))
        req = {
            "path": req_dict.get("path"),
            "header": {},
            "body": {} if payload_type == "query_param" else payload,
            "query_param": payload if payload_type == "query_param" else {},
            "original_url": req_dict.get("original_url"),
            "method": (req_dict.get("method") or "").lower(),
            "temp_api_label": new_path,
        }
        req_list.append(req)

    return req_list
