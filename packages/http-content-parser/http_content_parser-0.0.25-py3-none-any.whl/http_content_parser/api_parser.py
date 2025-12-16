# -*- coding: UTF-8 -*-
import copy
import json
import re
from http_content_parser.curl_parser import CurlParser
from http_content_parser.openapi_parser import OpenApiParser
from http_content_parser.postman_parser import parse_postman
from http_content_parser.req_data import ReqData
from http_content_parser.swagger2_parser import Swagger2Parser


class ApiModelParser:
    def get_api_model_for_curl(self, curl_file, curl_filter=None) -> list[ReqData]:
        # convert curl
        payload_list = self.convert_curl_data_to_model(
            curl_file_path=curl_file, url_filter=curl_filter
        )
        # handle duplicate key
        new_payload_list = self.__handle_duplicate_api_label(payload_list)
        return new_payload_list

    def get_api_list_for_curl(self, curl_file, curl_filter=None) -> list[dict]:
        # convert curl
        payload_list = self.convert_curl_data_to_list(
            curl_file_path=curl_file, url_filter=curl_filter
        )
        # handle duplicate key
        new_payload_list = self.__handle_duplicate_api_label_for_dict(payload_list)
        return new_payload_list

    def get_api_model_for_postman(self, json_dict: dict) -> list[ReqData]:
        payload_list = self.convert_postman_to_model(postman_dict=json_dict)
        # handle duplicate key
        new_payload_list = self.__handle_duplicate_api_label(payload_list)
        return new_payload_list

    def get_api_list_for_postman(self, json_dict: dict) -> list[dict]:
        payload_list = self.convert_postman_to_list(postman_dict=json_dict)
        # handle duplicate key
        new_payload_list = self.__handle_duplicate_api_label_for_dict(payload_list)
        return new_payload_list

    def get_api_model_for_swagger(self, json_dict: dict) -> list[ReqData]:
        payload_list = self.convert_swagger_to_model(swagger2_dict=json_dict)
        # handle duplicate key
        new_payload_list = self.__handle_duplicate_api_label(payload_list)
        return new_payload_list

    def get_api_list_for_swagger(self, json_dict: dict) -> list[dict]:
        payload_list = self.convert_swagger_to_list(swagger2_dict=json_dict)
        # handle duplicate key
        new_payload_list = self.__handle_duplicate_api_label_for_dict(payload_list)
        return new_payload_list

    def get_api_model_for_openapi(self, json_dict: dict) -> list[ReqData]:
        payload_list = self.convert_openapi_to_model(openapi_dict=json_dict)
        # handle duplicate key
        new_payload_list = self.__handle_duplicate_api_label(payload_list)
        return new_payload_list

    def get_api_list_for_openapi(self, json_dict: dict) -> list[dict]:
        payload_list = self.convert_openapi_to_list(openapi_dict=json_dict)
        # handle duplicate key
        new_payload_list = self.__handle_duplicate_api_label_for_dict(payload_list)
        return new_payload_list

    def convert_curl_data_to_list(
        self, curl_file_path: str, url_filter=None
    ) -> list[dict]:
        curl_parser = CurlParser()
        payload_list = []
        with open(curl_file_path, "rt") as f:
            lines = f.readlines()
            line_num_array = curl_parser.get_curl_line_num_scope(lines=lines)
            for s, e in line_num_array:
                res = curl_parser.split_curl_to_struct(lines, s, e, url_filter)
                url_content = curl_parser.parse_url(res.get("original_url", ""))
                path_str = url_content.get("path", "")[1:]
                method = (res.get("method", "") or "").lower()
                label = self.__replace_api_label_chars(path_str) + "_" + method
                req_data = {
                    "path": path_str,
                    "header": json.dumps(res.get("header", {})),
                    "body": res.get("body", {}),
                    "query_param": (
                        json.dumps(url_content.get("query_params", {}))
                        if url_content.get("query_params")
                        else {}
                    ),
                    "original_url": res.get("original_url", ""),
                    "method": method,
                    "temp_api_label": label,
                }
                payload_list.append(req_data)
        return payload_list

    def convert_curl_data_to_model(
        self, curl_file_path: str, url_filter=None
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
                    self.__replace_api_label_chars(url_content["path"][1:])
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

    def convert_postman_to_list(self, postman_dict: dict) -> list[dict]:
        api_infos = parse_postman(postman_dict) or []
        payload_list = []
        for api_info in api_infos:
            path = api_info.get("path", "")
            method = (api_info.get("method", "") or "").lower()
            label = (
                self.__handle_http_path(path.split("/"), "_")
                .replace("{", "")
                .replace("}", "")
                + "_"
                + method
            )
            req_data = {
                "path": path,
                "header": json.dumps(api_info.get("header", {})),
                "body": api_info.get("body", {}),
                "query_param": json.dumps(api_info.get("query_param", {})),
                "original_url": api_info.get("url", ""),
                "method": method,
                "temp_api_label": label,
            }
            payload_list.append(req_data)
        return payload_list

    def convert_postman_to_model(self, postman_dict: dict) -> list[ReqData]:
        api_infos = parse_postman(postman_dict)
        payload_list = []
        for api_info in api_infos:
            req_data = ReqData()
            req_data.path = api_info["path"]
            req_data.header = json.dumps(api_info["header"])
            req_data.body = api_info["body"]
            req_data.query_param = json.dumps(api_info["query_param"])
            req_data.original_url = api_info["url"]
            req_data.method = api_info["method"].lower()
            req_data.temp_api_label = (
                self.__handle_http_path(api_info["path"].split("/"), "_")
                .replace("{", "")
                .replace("}", "")
                + "_"
                + api_info["method"].lower()
            )
            payload_list.append(req_data)
        return payload_list

    def convert_swagger_to_model(self, swagger2_dict: dict) -> list[ReqData]:
        swagger_parser = Swagger2Parser(swagger2_dict)
        api_dict = swagger_parser.get_swagger_api_info()
        if not api_dict:
            print("check your swagger json")
            return []
        payload_list = []
        for path, path_info in api_dict.items():
            req_data = ReqData()
            req_data.path = self.__handle_http_path(path.split("/")[:-1], "/")
            req_data.temp_api_label = (
                self.__handle_http_path(path.split("/"), "_")
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
            payload_list.append(req_data)
        return payload_list

    def convert_swagger_to_list(self, swagger2_dict: dict) -> list[dict]:
        swagger_parser = Swagger2Parser(swagger2_dict)
        api_dict = swagger_parser.get_swagger_api_info()
        if not api_dict:
            return []
        payload_list = []
        for path, path_info in api_dict.items():
            parts = path.split("/")
            path_val = self.__handle_http_path(parts[:-1], "/")
            label_val = (
                self.__handle_http_path(parts, "_").replace("{", "").replace("}", "")
            )
            body_param = path_info.get("body_param", {})
            body_val = next(iter(body_param.values()), {})
            req_data = {
                "path": path_val,
                "temp_api_label": label_val,
                "method": parts[-1],
                "query_param": json.dumps(path_info.get("query_param", {})),
                "path_param": json.dumps(path_info.get("path_param", {})),
                "response": json.dumps(path_info.get("response", {})),
                "body": json.dumps(body_val),
            }
            payload_list.append(req_data)
        return payload_list

    def convert_openapi_to_model(self, openapi_dict: dict) -> list[ReqData]:
        if not openapi_dict:
            return []
        payload_list = []
        parser = OpenApiParser(openapi_dict)
        api_dict = parser.get_open_api_info()
        if not api_dict:
            return []
        for path, path_info in api_dict.items():
            parts = path.split("/")
            req = ReqData()
            req.path = self.__handle_http_path(parts[:-1], "/")
            req.temp_api_label = (
                self.__handle_http_path(parts, "_").replace("{", "").replace("}", "")
            )
            req.method = parts[-1]
            req.query_param = json.dumps(path_info.get("query_param", {}))
            req.path_param = json.dumps(path_info.get("path_param", {}))
            req.response = json.dumps(path_info.get("response", {}))
            req.body = json.dumps(path_info.get("body_param", {}))
            payload_list.append(req)
        return payload_list

    def convert_openapi_to_list(self, openapi_dict: dict) -> list[dict]:
        if not openapi_dict:
            return []
        payload_list = []
        parser = OpenApiParser(openapi_dict)
        api_dict = parser.get_open_api_info()
        if not api_dict:
            return []
        for path, path_info in api_dict.items():
            parts = path.split("/")
            path_val = self.__handle_http_path(parts[:-1], "/")
            label_val = (
                self.__handle_http_path(parts, "_").replace("{", "").replace("}", "")
            )
            req_data = {
                "path": path_val,
                "temp_api_label": label_val,
                "method": parts[-1],
                "query_param": json.dumps(path_info.get("query_param", {})),
                "path_param": json.dumps(path_info.get("path_param", {})),
                "response": json.dumps(path_info.get("response", {})),
                "body": json.dumps(path_info.get("body_param", {})),
            }
            payload_list.append(req_data)
        return payload_list

    def __handle_http_path(self, path_list: list, split_char: str) -> str:
        if not path_list:
            return ""
        url_path = ""
        for u in path_list:
            if u:
                url_path += u + split_char
        return url_path[:-1]

    def __replace_api_label_chars(self, string: str) -> str:
        pattern = r"[+/@?=.]"  # 定义要匹配的特殊字符模式
        replacement = "_"  # 替换为的字符串

        new_string = re.sub(pattern, replacement, string)
        return new_string

    def __handle_duplicate_api_label(
        self, payload_list: list[ReqData]
    ) -> list[ReqData]:
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

    def __handle_duplicate_api_label_for_dict(
        self, payload_list: list[dict]
    ) -> list[dict]:
        key_filter = {}
        new_payload_list = copy.deepcopy(payload_list)
        for payload, p_copy in zip(payload_list, new_payload_list):
            k = payload["temp_api_label"]
            if k in key_filter.keys():
                p_copy["temp_api_label"] = k + "_" + str(key_filter[k])
                key_filter[k] += 1
            else:
                key_filter[k] = 2
        return new_payload_list
