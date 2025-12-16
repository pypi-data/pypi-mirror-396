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
    result = ParamUtil.split_swagger_param_and_type(s, nontype=True)
    print(result)
