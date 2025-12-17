import copy
import itertools


def dict_cartesian_product(
    template_dict,
    sample_dict,
    required_fields=None,
    target_sections=None,
    filters=None,
) -> list:
    """
    template_dict: 原始模板
    sample_dict: 样本值
    required_fields: 必填字段字典
    target_sections: 需要做笛卡尔积的一级 key 列表（其余保持不变）
    filters: 过滤规则 dict: {section: {field: [允许的值]}}
    """

    results = []
    required_fields = required_fields or {}
    target_sections = target_sections or list(sample_dict.keys())
    filters = filters or {}

    fixed_sections = {
        k: v for k, v in template_dict.items() if k not in target_sections
    }

    sub_combinations = {}
    for section in target_sections:
        fields = sample_dict[section]
        keys = list(fields.keys())
        values_product = itertools.product(*[fields[k] for k in keys])
        sub_combinations[section] = []
        for combo in values_product:
            combo_dict = {}
            skip = False
            for k, v in zip(keys, combo):
                # 检查必填字段
                if k in required_fields.get(section, []) and v is None:
                    skip = True
                    break
                # None 表示该字段可以省略
                if v is not None:
                    # 检查过滤规则
                    if section in filters and k in filters[section]:
                        if v not in filters[section][k]:
                            skip = True
                            break
                    combo_dict[k] = v
            if not skip:
                sub_combinations[section].append(combo_dict)

    all_sections = list(sub_combinations.keys())
    for combo in itertools.product(*[sub_combinations[s] for s in all_sections]):
        new_json = copy.deepcopy(fixed_sections)
        for sec_name, sec_value in zip(all_sections, combo):
            new_json[sec_name] = sec_value
        results.append(new_json)

    return results
