import json
import os
from http_content_parser.api_parser import ApiModelParser


api_parser = ApiModelParser()

curl_file = os.path.dirname(os.path.abspath(__file__)) + "/tmp"


def test_curl_parser():
    api_info = api_parser.get_api_list_for_curl(curl_file=curl_file)
    print(json.dumps(api_info, indent=4))

