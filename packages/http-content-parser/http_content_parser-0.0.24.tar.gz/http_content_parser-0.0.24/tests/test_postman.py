from http_content_parser.postman_parser import parse_postman


def test_parse_postman_basic_and_vars():
    collection = {
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
    res = parse_postman(collection)
    assert isinstance(res, list)
    assert len(res) == 1
    item = res[0]
    assert item["method"] == "GET"
    assert item["path"] == "v1/users"
    assert item["url"].startswith("https://api.example.com")
    assert item["query_param"]["id"] == "42"
    assert item["header"]["Authorization"] == "Bearer abc123"


def test_parse_postman_no_global_accumulate():
    c = {
        "item": [
            {
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {"raw": "https://x/a", "path": ["a"], "query": []},
                }
            }
        ]
    }
    r1 = parse_postman(c)
    r2 = parse_postman(c)
    assert len(r1) == 1
    assert len(r2) == 1
