# -*- coding: UTF-8 -*-
import json


api_info_list = []


def parse_postman(json_file: dict) -> list:
    # TODO 如果postman中有变量,则无法解析变量的值.
    items = json_file.get("item")
    if items:
        for item in items:
            if item.get("item"):
                parse_postman(item)
            else:
                api_info = {}
                if not item.get("request"):
                    continue
                postman_request = item["request"]
                api_info["method"] = postman_request["method"]
                api_info["header"] = {}
                for hs in postman_request["header"]:
                    api_info["header"][hs["key"]] = hs["value"]
                api_info["url"] = postman_request["url"]["raw"]
                if not postman_request["url"].get("path"):
                    continue
                api_info["path"] = "/".join(postman_request["url"]["path"])
                api_info["query_param"] = {}
                if postman_request["url"].get("query"):
                    for qs in postman_request["url"]["query"]:
                        api_info["query_param"][qs["key"]] = qs["value"]
                api_info["body"] = {}
                if postman_request.get("body"):
                    temp = postman_request["body"][postman_request["body"]["mode"]]
                    if isinstance(temp, str):
                        # \\n 只会出现在value中,一般是用户自己定义的
                        temp = temp.replace("\\n", "").replace("\n", "")
                        if temp:
                            # beautify json string
                            temp = json.dumps(temp) # 转换为 JSON 格式的字符串
                            temp = json.loads(temp)
                    api_info["body"] = temp
                api_info_list.append(api_info)
    return api_info_list
