from http_content_parser.param_util import ParamUtil


def test_param_util():
    s = {
        "variable": [
            {"key": "host", "value": "api.example.com"},
            {"name": "token", "value": "abc123"},
        ],
        "item": [
            {
                "name": "Folder",
                "item": [
                    {
                        "name": "GetUser",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "Authorization", "value": "Bearer {{token}}"}
                            ],
                            "url": {
                                "raw": "https://{{host}}/v1/users?id={{uid}}",
                                "path": ["v1", "users"],
                                "query": [{"key": "id", "value": "{{uid}}"}],
                            },
                        },
                        "variable": [{"key": "uid", "value": "42"}],
                    }
                ],
            }
        ],
    }
    result = ParamUtil.split_swagger_param_and_type(s, nontype=False)
    expected_result = [
        {"['variable']": "[]"},
        {"['variable'][0]['key']": "'host'"},
        {"['variable'][0]['value']": "'api.example.com'"},
        {"['variable'][1]['name']": "'token'"},
        {"['variable'][1]['value']": "'abc123'"},
        {"['item']": "[]"},
        {"['item'][0]['name']": "'Folder'"},
        {"['item'][0]['item']": "[]"},
        {"['item'][0]['item'][0]['name']": "'GetUser'"},
        {"['item'][0]['item'][0]['request']": "{}"},
        {"['item'][0]['item'][0]['request']['method']": "'GET'"},
        {"['item'][0]['item'][0]['request']['header']": "[]"},
        {"['item'][0]['item'][0]['request']['header'][0]['key']": "'Authorization'"},
        {
            "['item'][0]['item'][0]['request']['header'][0]['value']": "'Bearer {{token}}'"
        },
        {"['item'][0]['item'][0]['request']['url']": "{}"},
        {
            "['item'][0]['item'][0]['request']['url']['raw']": "'https://{{host}}/v1/users?id={{uid}}'"
        },
        {"['item'][0]['item'][0]['request']['url']['path']": "[]"},
        {"['item'][0]['item'][0]['request']['url']['query']": "[]"},
        {"['item'][0]['item'][0]['request']['url']['query'][0]['key']": "'id'"},
        {"['item'][0]['item'][0]['request']['url']['query'][0]['value']": "'{{uid}}'"},
        {"['item'][0]['item'][0]['variable']": "[]"},
        {"['item'][0]['item'][0]['variable'][0]['key']": "'uid'"},
        {"['item'][0]['item'][0]['variable'][0]['value']": "'42'"},
    ]
    assert result == expected_result


def test_param_util2():
    s = {
        "vmid": ["3690976212158729"],
        "type": ["1"],
        "pn": ["1"],
        "ps": ["24"],
        "playform": ["web"],
        "follow_status": ["0"],
        "web_location": ["333.1387"],
        "w_rid": ["a64a78654a1948dcc86f483f3d86aaef"],
        "wts": ["1765612099"],
    }
    result = ParamUtil.split_swagger_param_and_type(s, nontype=False)
    expected_result = [
        {"vmid": ["3690976212158729"]},
        {"type": ["1"]},
        {"pn": ["1"]},
        {"ps": ["24"]},
        {"playform": ["web"]},
        {"follow_status": ["0"]},
        {"web_location": ["333.1387"]},
        {"w_rid": ["a64a78654a1948dcc86f483f3d86aaef"]},
        {"wts": ["1765612099"]},
    ]
    assert result == expected_result


def test_param_util3():
    s = {
        "vmid": "3690976212158729",
        "type": "1",
        "pn": "1",
        "ps": ["24"],
        "playform": ["web"],
        "follow_status": "0",
        "web_location": "333.1387",
        "w_rid": "a64a78654a1948dcc86f483f3d86aaef",
        "wts": ["1765612099"],
    }
    result = ParamUtil.split_swagger_param_and_type(s, nontype=False)
    expected_result = [
        {"['vmid']": "'3690976212158729'"},
        {"['type']": "'1'"},
        {"['pn']": "'1'"},
        {"ps": ["24"]},
        {"playform": ["web"]},
        {"['follow_status']": "'0'"},
        {"['web_location']": "'333.1387'"},
        {"['w_rid']": "'a64a78654a1948dcc86f483f3d86aaef'"},
        {"wts": ["1765612099"]},
    ]
    assert result == expected_result


def test_param_util4():
    s = {"vmid": "3690976212158729", "type": {}, "name": []}
    result = ParamUtil.split_swagger_param_and_type(s, nontype=False)
    print(result)
    expected_result = [
        {"['vmid']": "'3690976212158729'"},
        {"['type']": "{}"},
        {"['name']": "[]"},
    ]
    assert result == expected_result


def test_param_util_5():
    s = {
        "vmid": ["3690976212158729", "2"],
        "type": ["1", "2", "3"],
        "pn": [],
    }
    result = ParamUtil.split_swagger_param_and_type(s, nontype=False)
    print(result)
    expected_result = [
        {"['vmid']": ["3690976212158729", "2"]},
        {"['type']": ["1", "2", "3"]},
        {"['pn']": '[]'},
    ]
    assert result == expected_result
