import json

from http_content_parser.generate_api_file import GenerateApiFile


def test_curl():
    gaf = GenerateApiFile()
    # with open("./postman.json", "r") as f:
    #     json_dict = json.load(f)
    # gaf.produce_api_yaml_for_postman(json_dict, "./test.yaml")
    curl_file = (
        "./tmp"
    )
    gaf.produce_api_yaml_for_curl(curl_file=curl_file, yaml_file="api.yaml")


def test_for():
    a = "#!/usr/bin/env bash  \t\n \n echo \\n 66 >> /root/pre23"
    b = a.replace("\n", "")
    print(b)
