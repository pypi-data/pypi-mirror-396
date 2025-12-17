import copy
import json
from gentccode.cartesian import CP


def compare_node_param_to_cp_param(node_param: dict, cp_param_list: list) -> dict:
    """对比node_param和cp_param中的key,并重新给key赋值

    Args:
        node_param (_type_): 入参中参数
        cp_param_list (list[str]): 根据入参生成的笛卡尔积集合
        result (dict): _description_

    Returns:
        _type_: _description_
    """
    result = {cp: v for k, v in node_param.items() for cp in cp_param_list if cp == k}

    return result


def produce_cp_param_by_node(
    node: str,
    payload_params: list,
) -> list:
    """把请求参数以笛卡尔积的方式生成测试用例代码

    Args:
        payload_params (list): 请求参数 [{'a':{'b':2}}]
        node (str): 参数所在的层级(<=1级), 比如 0级: `.`  --> {'a':{'b':2}}
                                            1级: `a.` --> {'b':2}
    """
    node_cp_param_list = []
    ccp = CP()
    for payload_param in payload_params:
        if isinstance(payload_param, str):
            payload_param = json.loads(payload_param)
        # get filtered param by node
        node_param = {}
        has_nest = False
        if node == ".":
            node_param = payload_param
        else:
            copy_payload_param = copy.deepcopy(payload_param)
            for k in node.split("."):
                if k:
                    node_param = copy_payload_param.get(k)

            has_nest = True

        # produce param according to cp model
        if isinstance(node_param, dict):
            cp_param_list = ccp.product_cp_params(node_param)
        elif isinstance(node_param, list):
            cp_param_list = combine_dicts(node_param)
        else:
            print(f"not support this type for key:{k}")
            continue

        for cp_param in cp_param_list:
            copy_payload_param = copy.deepcopy(payload_param)
            if isinstance(node_param, list):
                # 直接拿cp生成的结果
                new_node_param = cp_param
                if has_nest:
                    replace_nested_key_value(copy_payload_param, node, new_node_param)
                    node_cp_param_list.append(copy_payload_param)
                else:
                    node_cp_param_list.append(new_node_param)
            else:
                for c in cp_param:
                    # copy_payload_param = copy.deepcopy(payload_param)
                    new_node_param = compare_node_param_to_cp_param(node_param, list(c))
                    if has_nest:
                        replace_nested_key_value(copy_payload_param, node, new_node_param)
                        node_cp_param_list.append(copy_payload_param)
                    else:
                        node_cp_param_list.append(new_node_param)
    return node_cp_param_list


# 补全非node节点的key到dict中
def replace_nested_key_value(d: dict, keys: str, new_value):
    key_list = keys.split(".")
    current_key = key_list[0]

    if current_key in d:
        if len(key_list) == 2:
            d[current_key] = new_value
        else:
            replace_nested_key_value(d[current_key], ".".join(key_list[1:]), new_value)


def combine_dicts(dict_list):
    result = list(dict_list)

    # 递归函数，用于生成所有可能的组合
    def recursive_combinations(lst, start, cur_combination):
        if start == len(lst):
            result.append(cur_combination)
            return
        # 不包含当前元素的情况
        recursive_combinations(lst, start + 1, cur_combination)
        # 包含当前元素的情况
        recursive_combinations(lst, start + 1, cur_combination + [lst[start]])

    # 生成所有可能的组合
    recursive_combinations(list(dict_list), 0, [])

    return [k for k in result if type(k) == list and k]
