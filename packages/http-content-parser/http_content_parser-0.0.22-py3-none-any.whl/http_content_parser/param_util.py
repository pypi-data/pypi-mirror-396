# -*- coding: UTF-8 -*-

class ParamUtil(object):
    def __init__(self) -> None:
        self._param_list = []

    @staticmethod
    def merge_api_params(swagger_dict: dict, api_dict: dict) -> dict:
        result = {}
        swagger_fail_dict = []
        for k, v in swagger_dict.items():
            if v['path_param'] or v['query_param']:
                if api_dict.get(k):
                    temp_v = v
                    temp_v['body_type'] = v['body']
                    temp_v['body'] = api_dict[k]['body']
                    temp_v['original_url'] = api_dict[k]['original_url']
                    temp_v['query_param'] = api_dict[k]['query_param']
                    result[k] = temp_v
                else:
                    swagger_fail_dict.append(k.replace('_', '/'))
            else:
                if api_dict.get(k):
                    result[k] = api_dict[k]
                else:
                    swagger_fail_dict.append(k.replace('_', '/'))
                    # result[k] = v
        return result, swagger_fail_dict

    @staticmethod
    def split_swagger_param_and_type(param, nontype=False):
        sp = SwaggerParam()
        return sp.split_params(param, '', nontype)

    def split_dict_params(self, params_dict, prefix_str, middle_char, nontype=False):
        for k, v in params_dict.items():
            new_v = self.adjust_type(v, nontype=nontype)
            if isinstance(v, dict):
                if not v:
                    self._param_list.append(
                        prefix_str + f"['{k}']{middle_char}{new_v}")
                else:
                    temp_prefix_str = prefix_str
                    temp_prefix_str += f"['{k}']"
                    self.split_dict_params(
                        v, temp_prefix_str, middle_char, nontype)
            elif isinstance(v, list):
                if not v:
                    self._param_list.append(
                        prefix_str + f"['{k}']{middle_char}{new_v}")
                else:
                    i = 0
                    for item in v:
                        if isinstance(item, dict):
                            temp_prefix_str = prefix_str
                            temp_prefix_str += f"['{k}'][{i}]"
                            self.split_dict_params(
                                item, temp_prefix_str, middle_char, nontype)
                            i += 1
                        else:
                            self._param_list.append(
                                prefix_str + f"['{k}']{middle_char}{new_v}")
                            break

            else:
                self._param_list.append(
                    prefix_str + f"['{k}']{middle_char}{new_v}")

    def split_params(self, param, prefix_str, middle_char, nontype=False):
        if isinstance(param, list):
            for i in range(len(param)):
                temp_prefix_str = prefix_str
                if isinstance(param[i], dict):
                    temp_prefix_str += f"[{i}]"
                    self.split_dict_params(
                        param[i], temp_prefix_str, middle_char, nontype)
        elif isinstance(param, dict):
            self.split_dict_params(param, prefix_str, middle_char, nontype)
        return self._param_list

    # nontype用来控制value值是否输出原值还是参数类型
    def adjust_type(self, value, nontype=False):
        if isinstance(value, (bool, int, dict, list)):
            return value
        else:
            if nontype and len(value) > 10:
                return "'string'"
            else:
                return f"'{value}'"


class SwaggerParam(object):
    def __init__(self) -> None:
        self._param_list = []

    def split_params_for_dict_type(self, params_dict, prefix_str,  nontype=False):
        for k, v in params_dict.items():
            new_v = self.adjust_type(v, nontype=nontype)
            if isinstance(v, dict):
                if not v:
                    self._param_list.append({f"{prefix_str}['{k}']": new_v})
                else:
                    temp_prefix_str = prefix_str
                    temp_prefix_str += f"['{k}']"
                    self.split_params_for_dict_type(
                        v, temp_prefix_str, nontype)
            elif isinstance(v, list):
                if not v:
                    self._param_list.append({prefix_str + f"['{k}']": new_v})
                else:
                    i = 0
                    for item in v:
                        if isinstance(item, dict):
                            temp_prefix_str = prefix_str
                            temp_prefix_str += f"['{k}'][{i}]"
                            self.split_params_for_dict_type(
                                item, temp_prefix_str, nontype)
                            i += 1
                        else:
                            self._param_list.append(
                                {prefix_str + f"['{k}']": new_v})
                            break

            else:
                self._param_list.append({prefix_str + f"['{k}']": new_v})

    def split_params(self, param, prefix_str, nontype=False):
        if isinstance(param, list):
            for i in range(len(param)):
                temp_prefix_str = prefix_str
                if isinstance(param[i], dict):
                    temp_prefix_str += f"[{i}]"
                    self.split_params_for_dict_type(
                        param[i], temp_prefix_str, nontype)
        elif isinstance(param, dict):
            self.split_params_for_dict_type(param, prefix_str, nontype)
        else:
            print('param type is error: ' + type(param))
        return self._param_list

    # nontype用来控制value值是否输出原值还是参数类型
    def adjust_type(self, value, nontype=False):
        if isinstance(value, (bool, int, dict, list)):
            return value
        else:
            if nontype and len(value) > 10:
                return "'string'"
            else:
                return f"'{value}'"
