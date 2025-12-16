
class OpenApiParser(object):
    def __init__(self, openapi_json_dict) -> None:
        self.openapi_dict = openapi_json_dict
        self.schema_ref_list = []

    def parse_request_body(self, api_info):
        body_param_dict = {}
        api_content_type = ''
        if api_info.get('requestBody'):
            request_body = api_info['requestBody']
            for content_type, schema in request_body['content'].items():
                api_content_type = content_type
                for k, v in schema['schema']['properties'].items():
                    if v.get('items'):
                        if v['items'].get('$ref'):
                            schema_ref = v['items']['$ref'].split('/')[-1]
                            body_param_dict[k] = self.parse_body_schema(
                                schema_ref)
                            self.schema_ref_list = []
                        else:
                            body_param_dict[k] = [
                                v.get('type', 'unknown_type')]

                    else:
                        body_param_dict[k] = v.get('type', 'unknown_type')
        return body_param_dict, api_content_type

    def parse_parameters(self, params):
        path_param_dict = {}
        body_param_dict = {}
        query_param_dict = {}
        form_data_param_dict = {}
        for param in params:
            if isinstance(param, dict):
                if param.get('in') == 'path':
                    path_param_dict[param['name']] = param['schema']['type']
                elif param.get('in') == 'query':
                    query_param_dict[param['name']] = param['schema']['type']
                elif param.get('in') == 'formData':
                    form_data_param_dict[param['name']
                                         ] = param['schema']['type']
                else:
                    print('error: parameters in type error')

        return body_param_dict, path_param_dict, query_param_dict, form_data_param_dict

    def parse_body_schema(self, param_schema_ref):
        self.schema_ref_list.append(param_schema_ref)
        schema_dict = {}
        schema_info = self.openapi_dict['components']['schemas'].get(
            param_schema_ref)
        if schema_info:
            properties = schema_info.get('properties')
            if isinstance(properties, dict):
                for param, param_type_dict in properties.items():
                    if param_type_dict.get('$ref'):
                        schema_ref_name = param_type_dict['$ref'].split(
                            '/')[-1]
                        if schema_ref_name not in self.schema_ref_list:
                            self.schema_ref_list.append(schema_ref_name)
                            sub_param_value = self.parse_body_schema(
                                schema_ref_name)
                            if param_type_dict.get('type') == 'array':
                                schema_dict[param] = [sub_param_value]
                            else:
                                schema_dict[param] = sub_param_value
                        else:
                            if param_type_dict.get('type') == 'array':
                                schema_dict[param] = [{}]
                            else:
                                schema_dict[param] = {}
                    elif param_type_dict.get('items'):
                        if param_type_dict['items'].get('$ref'):
                            schema_item_ref_name = param_type_dict['items']['$ref'].split(
                                '/')[-1]
                            if schema_item_ref_name not in self.schema_ref_list:
                                self.schema_ref_list.append(
                                    schema_item_ref_name)
                                sub_param_value = self.parse_body_schema(
                                    schema_item_ref_name)
                                schema_dict[param] = [sub_param_value]
                            else:
                                schema_dict[param] = [{}]
                        else:
                            schema_dict[param] = [param_type_dict['type']]
                    else:
                        if param_type_dict.get('type'):
                            schema_dict[param] = param_type_dict['type']
                        else:
                            schema_dict[param] = param_type_dict
        return schema_dict

    def parse_response(self, res_dict):
        res = {}
        # openapi's schema position
        content = res_dict['200']['content']
        schema = {}
        for _, c_v in content.items():
            schema = c_v['schema']
        if schema.get("$ref"):
            schema_ref_name = schema['$ref'].split('/')[-1]
            res = self.parse_body_schema(schema_ref_name)
            self.schema_ref_list = []
            return res
        elif schema.get("items"):
            schema_ref_name = schema['items']['$ref'].split('/')[-1]
            # TODO array schema: [{}] or {} ?
            res = self.parse_body_schema(schema_ref_name)
            self.schema_ref_list = []
            return res
        else:
            for _, v in schema.items():
                if isinstance(v, list):
                    for item_dict in v:
                        if isinstance(item_dict, dict):
                            for item_k, item_v in item_dict.items():
                                if item_k == '$ref':
                                    schema_ref_name = item_v.split('/')[-1]
                                    res.update(
                                        self.parse_body_schema(schema_ref_name))
                                    self.schema_ref_list = []
                                if item_k == 'properties':
                                    for k2, v2 in item_v.items():
                                        if v2.get('$ref'):
                                            schema_ref_name = v2['$ref'].split(
                                                '/')[-1]
                                            res[k2] = self.parse_body_schema(
                                                schema_ref_name)
                                            self.schema_ref_list = []

        return res

    def get_open_api_info(self):
        result = {}
        base_path = self.openapi_dict['servers'][0]['url']
        for path, api_infos in (self.openapi_dict['paths']).items():
            for path_method, api_info in api_infos.items():
                _path_param = {}
                _query_param = {}
                _form_param = {}
                _body_param = {}
                _api_response = {}
                if api_info.get('parameters'):
                    api_param = self.parse_parameters(api_info['parameters'])
                    _path_param = api_param[1]
                    _query_param = api_param[2]
                    _form_param = api_param[3]
                if api_info.get('requestBody'):
                    body_result = self.parse_request_body(api_info)
                    _body_param = body_result[0]
                    # content_type = result[1]
                if api_info.get('responses'):
                    _api_response = self.parse_response(api_info['responses'])

                result[f'{base_path}{path}/{path_method}'] = {'path_param': _path_param,
                                                              'query_param': _query_param, 'form_param': _form_param, 'body_param': _body_param, 'response': _api_response}

        return result
