# -*- coding: UTF-8 -*-
class Swagger2Parser(object):
    def __init__(self, swagger_json_dict) -> None:
        self.swagger_dict = swagger_json_dict
        self.schema_ref_list = []

    def parse_parameters(self, params):
        path_param_dict = {}
        body_param_dict = {}
        query_param_dict = {}
        form_data_param_dict = {}
        for param in params:
            if isinstance(param, dict):
                if param.get('in') == 'path':
                    path_param_dict[param['name']] = param['type']
                elif param.get('in') == 'body':
                    if param.get('schema'):
                        schema_ref = param['schema']['$ref'].split('/')[-1]
                        body_param_dict[param['name']
                                        ] = self.parse_body_schema(schema_ref)
                        self.schema_ref_list = []
                elif param.get('in') == 'query':
                    query_param_dict[param['name']] = param['type']
                elif param.get('in') == 'formData':
                    form_data_param_dict[param['name']] = param['type']
                else:
                    print('error: parameters in type error')

        return body_param_dict, path_param_dict, query_param_dict, form_data_param_dict

    def parse_body_schema(self, param_schema_ref):
        self.schema_ref_list.append(param_schema_ref)
        schema_dict = {}
        schema_info = self.swagger_dict['definitions'].get(param_schema_ref)
        if schema_info:
            properties = schema_info.get('properties')
            if isinstance(properties, dict):
                for param, param_type_dict in properties.items():
                    if param_type_dict.get('$ref'):
                        schema_ref_name = param_type_dict['$ref'].split(
                            '/')[-1]
                        # prevent infinite loop
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
        if res_dict['200'].get('schema'):
            schema = res_dict['200']['schema']
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

        else:
            print('response dont have schema')
        return res

    def get_swagger_api_info(self):
        result = {}
        base_path = self.swagger_dict['basePath'].replace('/', '')
        for path, api_infos in (self.swagger_dict['paths']).items():
            for path_method, api_info in api_infos.items():
                if api_info.get('parameters'):
                    api_param = self.parse_parameters(api_info['parameters'])
                    api_res = self.parse_response(api_info['responses'])
                    result[f'{base_path}{path}/{path_method}'] = {'path_param': api_param[1],
                                                                  'query_param': api_param[2], 'form_param': api_param[3], 'body_param': api_param[0], 'response': api_res}
                else:
                    result[f'{base_path}{path}/{path_method}'] = {'path_param': {},
                                                                  'query_param': {}, 'form_param': {}, 'body_param': {}}

        return result
