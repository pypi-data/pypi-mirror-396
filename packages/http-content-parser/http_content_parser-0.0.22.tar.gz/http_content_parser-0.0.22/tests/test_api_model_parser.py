import json
from http_content_parser.api_parser import ApiModelParser


api_parser = ApiModelParser()


def test_curl_parser():
    curl_file = "./tmp"
    api_info = api_parser.get_api_list_for_curl(curl_file=curl_file)
    print(json.dumps(api_info, indent=4))
