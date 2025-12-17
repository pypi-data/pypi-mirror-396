# -*- coding: UTF-8 -*-
import json
import re


def parse_postman(json_file: dict) -> list:
    items = json_file.get("item")
    result = []

    def _collect_vars(obj: dict) -> dict:
        vars_list = obj.get("variable", [])
        m = {}
        for it in vars_list:
            k = it.get("key") or it.get("name")
            v = it.get("value")
            if k:
                m[str(k)] = v if v is not None else ""
        return m

    root_vars = _collect_vars(json_file)
    pattern = re.compile(r"\{\{([^{}]+)\}\}")

    def _resolve(s: str, vars_map: dict) -> str:
        if not isinstance(s, str) or not s:
            return s

        def repl(m):
            key = m.group(1).strip()
            return str(vars_map.get(key, m.group(0)))

        return pattern.sub(repl, s)

    def _walk(item_obj: dict, inherited_vars: dict):
        local_vars = _collect_vars(item_obj)
        vars_map = {**inherited_vars, **local_vars}
        child_items = item_obj.get("item")
        if child_items:
            for child in child_items:
                _walk(child, vars_map)
            return
        if not item_obj.get("request"):
            return
        postman_request = item_obj["request"]
        api_info = {}
        api_info["method"] = postman_request.get("method", "")
        headers = postman_request.get("header", [])
        api_info["header"] = {
            hs.get("key"): _resolve((hs.get("value") or ""), vars_map)
            for hs in headers
            if hs.get("key")
        }
        url_obj = postman_request.get("url", {})
        api_info["url"] = _resolve(url_obj.get("raw", ""), vars_map)
        path_list = url_obj.get("path")
        if not path_list:
            return
        api_info["path"] = "/".join([_resolve(p, vars_map) for p in path_list if p])
        api_info["query_param"] = {
            qs.get("key"): _resolve((qs.get("value") or ""), vars_map)
            for qs in url_obj.get("query", [])
            if qs.get("key")
        }
        body_obj = postman_request.get("body")
        body_val = {}
        if body_obj and body_obj.get("mode") in body_obj:
            temp = body_obj[body_obj["mode"]]
            if isinstance(temp, str):
                temp = _resolve(temp.replace("\\n", "").replace("\n", ""), vars_map)
                if temp:
                    try:
                        temp = json.loads(temp)
                    except Exception:
                        pass
            body_val = temp
        api_info["body"] = body_val
        result.append(api_info)

    if items:
        for it in items:
            _walk(it, root_vars)
    return result

def parse_postman_bak(json_file: dict) -> list:
    # TODO 如果postman中有变量,则无法解析变量的值.
    api_info_list = []
    items = json_file.get("item")
    if items:
        for item in items:
            if item.get("item"):
                api_info_list.extend(parse_postman(item))
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
                            # parse json string
                            try:
                                temp = json.loads(temp)
                            except json.JSONDecodeError:
                                # Not a valid JSON, treat as a plain string
                                pass
                    api_info["body"] = temp
                api_info_list.append(api_info)
    return api_info_list
