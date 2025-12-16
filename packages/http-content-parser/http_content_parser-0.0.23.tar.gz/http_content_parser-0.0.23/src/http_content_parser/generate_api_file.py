# -*- coding: UTF-8 -*-
import copy
import json
import re

from http_content_parser.curl_parser import CurlParser
import yaml
from http_content_parser.req_data import ReqData
from http_content_parser.swagger2_parser import Swagger2Parser
from http_content_parser.openapi_parser import OpenApiParser
from http_content_parser.postman_parser import parse_postman


# TODO 不直接生成yaml文件,只生成dict,方便后续扩展
class GenerateApiFile:
    def __init__(self) -> None:
        pass

    def produce_api_yaml_for_postman(self, json_dict: dict, yaml_file: str):
        api_infos = parse_postman(json_dict)
        for api_info in api_infos:
            req_data = ReqData()
            req_data.path = api_info["path"]
            req_data.header = json.dumps(api_info["header"])
            req_data.body = api_info["body"]
            req_data.query_param = json.dumps(api_info["query_param"])
            req_data.original_url = api_info["url"]
            req_data.method = api_info["method"].lower()
            req_data.temp_api_label = (
                self.convert_swagger2_path(api_info["path"].split("/"), "_")
                .replace("{", "")
                .replace("}", "")
                + "_"
                + api_info["method"].lower()
            )
            self.write_api_content_to_yaml(yaml_file, req_data)
        # remove duplicate key
        self.remove_duplicate_key_for_yaml(yaml_file)

    def produce_api_yaml_for_curl(self, curl_file, yaml_file, curl_filter=None):
        # convert curl
        payload_list = self.convert_curl_data_to_model(
            curl_file_path=curl_file, url_filter=curl_filter
        )
        # handle duplicate key
        new_payload_list = self.handle_duplicate_yaml_key(payload_list)
        # write to yaml
        for payload in new_payload_list:
            self.write_api_content_to_yaml(yaml_file, payload)

    def handle_duplicate_yaml_key(self, payload_list: list[ReqData]) -> list[ReqData]:
        key_filter = {}
        new_payload_list = copy.deepcopy(payload_list)
        for payload, p_copy in zip(payload_list, new_payload_list):
            k = payload.temp_api_label
            if k in key_filter.keys():
                p_copy.temp_api_label = k + "_" + str(key_filter[k])
                key_filter[k] += 1
            else:
                key_filter[k] = 2
        return new_payload_list

    def convert_curl_data_to_model(
        self, curl_file_path, url_filter=None
    ) -> list[ReqData]:
        curl_parser = CurlParser()
        payload_list = []
        with open(curl_file_path, "rt") as f:
            lines = f.readlines()
            line_num_array = curl_parser.get_curl_line_num_scope(lines=lines)
            for r in line_num_array:
                res_dict = curl_parser.split_curl_to_struct(
                    lines, r[0], r[1], url_filter
                )
                req_model = ReqData(dd=res_dict)
                url_content = curl_parser.parse_url(req_model.original_url)
                req_model.temp_api_label = (
                    self.replace_api_label_chars(url_content["path"][1:])
                    + "_"
                    + req_model.method
                )
                req_model.header = json.dumps(req_model.header)
                if url_content["query_params"]:
                    req_model.query_param = json.dumps(url_content["query_params"])
                else:
                    req_model.query_param = {}
                req_model.path = url_content["path"][1:]
                payload_list.append(req_model)
        return payload_list

    def produce_api_yaml_for_swagger2(self, swagger2_dict, yaml_file):
        swagger_parser = Swagger2Parser(swagger2_dict)
        api_dict = swagger_parser.get_swagger_api_info()
        if not api_dict:
            print("check your swagger json")
            return
        for path, path_info in api_dict.items():
            req_data = ReqData()
            req_data.path = self.convert_swagger2_path(path.split("/")[:-1], "/")
            req_data.temp_api_label = (
                self.convert_swagger2_path(path.split("/"), "_")
                .replace("{", "")
                .replace("}", "")
            )
            req_data.method = path.split("/")[-1]
            req_data.query_param = json.dumps(path_info["query_param"])
            req_data.path_param = json.dumps(path_info["path_param"])
            req_data.response = json.dumps(path_info.get("response", {}))
            # swagger中body第一层和第二层key重复,只取第二层后的数据
            for _, v in path_info["body_param"].items():
                req_data.body = json.dumps(v)
            self.write_api_content_to_yaml(yaml_file, req_data)
        # remove duplicate key
        self.remove_duplicate_key_for_yaml(yaml_file)

    def produce_api_yaml_for_openapi3(self, openapi_dict, yaml_file):
        if not openapi_dict:
            print("openapi dict is null")
            return
        parser = OpenApiParser(openapi_dict)
        api_dict = parser.get_open_api_info()
        if not api_dict:
            print("check your swagger json")
            return
        for path, path_info in api_dict.items():
            req_data = ReqData()
            req_data.path = self.convert_swagger2_path(path.split("/")[:-1], "/")
            req_data.temp_api_label = (
                self.convert_swagger2_path(path.split("/"), "_")
                .replace("{", "")
                .replace("}", "")
            )
            req_data.method = path.split("/")[-1]
            req_data.query_param = json.dumps(path_info["query_param"])
            req_data.path_param = json.dumps(path_info["path_param"])
            req_data.response = json.dumps(path_info.get("response", {}))
            req_data.body = json.dumps(path_info["body_param"])
            self.write_api_content_to_yaml(yaml_file, req_data)
        # remove duplicate key
        self.remove_duplicate_key_for_yaml(yaml_file)

    def convert_swagger2_path(self, path_list, split_char):
        if not path_list:
            return ""
        url_path = ""
        for u in path_list:
            if u:
                url_path += u + split_char
        return url_path[:-1]

    def replace_api_label_chars(self, string):
        pattern = r"[+/@?=.]"  # 定义要匹配的特殊字符模式
        replacement = "_"  # 替换为的字符串

        new_string = re.sub(pattern, replacement, string)
        return new_string

    def remove_duplicate_key_for_yaml(self, api_yaml_file_path):
        with open(api_yaml_file_path, "r") as f:
            data = yaml.safe_load(f)
        unique_data = {}
        if data:
            for k, v in data.items():
                if k not in unique_data:
                    unique_data[k] = v

        with open(api_yaml_file_path, "w") as f:
            yaml.dump(unique_data, f)

    def write_api_content_to_yaml(self, file, template: ReqData):
        api_obj = {}
        yaml_obj = {}
        with open(file, "at") as f:
            api_obj["original_url"] = template.original_url
            api_obj["path"] = template.path
            api_obj["query_param"] = template.query_param
            api_obj["path_param"] = template.path_param
            api_obj["header"] = template.header
            api_obj["body"] = template.body
            api_obj["method"] = template.method
            api_obj["response"] = template.response
            yaml_obj[template.temp_api_label] = api_obj
            yaml.dump(yaml_obj, f)
