import copy
import itertools

"""
为search功能做的用例生成
"""


class CP:
    def __init__(self) -> None:
        self.cartesian_product = []
        self.unique_list = []

    def product_cp_params(self, param) -> list:
        param_copy = copy.deepcopy(param)
        if isinstance(param_copy, list):
            self._product_for_param_list(param_copy)
        elif isinstance(param_copy, dict):
            self._product_for_param_dict(param_copy)
        else:
            print(f"param type ({type(param)}) is not support")
        self._remove_duplicate()
        return self.unique_list

    ###
    # param like: [{'a':1},{'b':2},{'c':3}]
    ###
    def _product_for_param_list(self, param_list: list):
        param_len = len(param_list)
        for i in range(param_len):
            b = []
            for j in range(i, param_len + 1):
                if len(b) > 0:
                    self.cartesian_product.append(list(itertools.product(*b)))
                if j < param_len:
                    b.append([param_list[j]])

    ###
    # param like: {'a':1,'b':2}
    ###
    def _product_for_param_dict(self, param_dict: dict):
        param_list = [k for k, _ in param_dict.items()]
        self._product_for_param_list(param_list)

    def _remove_duplicate(self):
        for cp in self.cartesian_product:
            if cp not in self.unique_list:
                self.unique_list.append(cp)


if __name__ == "__main__":
    pass
