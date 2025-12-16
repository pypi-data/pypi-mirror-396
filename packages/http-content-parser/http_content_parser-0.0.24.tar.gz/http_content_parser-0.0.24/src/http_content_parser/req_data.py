# -*- coding: UTF-8 -*-

"""
__author__ = leo
"""


class ReqData(object):

    def __init__(self, dd=None):
        if dd and isinstance(dd, dict):
            self.__path = dd.get('path', '')
            self.__method = dd.get('method', '')
            self.__body = dd.get('body', {})
            self.__header = dd.get('header', {})
            self.__query_param = dd.get('query_param', {})
            self.__path_param = dd.get('path_param', {})
            self.__original_url = dd.get('original_url', '')
            self.__temp_api_label = dd.get('temp_api_label', '')
            self.__host = ''
            self.__response = dd.get('response', {})
        else:
            self.__host = ''
            self.__path = ''
            self.__method = ''
            self.__body = {}
            self.__header = {}
            self.__query_param = {}
            self.__path_param = {}
            self.__original_url = ''
            self.__temp_api_label = ''
            self.__response = {}

    @property
    def temp_api_label(self):
        return self.__temp_api_label

    @temp_api_label.setter
    def temp_api_label(self, value):
        self.__temp_api_label = value

    @property
    def url(self):
        return self.__host + self.__path

    @property
    def original_url(self):
        return self.__original_url

    @original_url.setter
    def original_url(self, value):
        self.__original_url = value

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self, value):
        self.__method = value

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, value):
        self.__body = value

    @property
    def header(self):
        return self.__header

    @header.setter
    def header(self, value):
        self.__header = value

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, value):
        self.__host = value

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        self.__path = value

    @property
    def query_param(self):
        return self.__query_param

    @query_param.setter
    def query_param(self, value):
        self.__query_param = value

    @property
    def path_param(self):
        return self.__path_param

    @path_param.setter
    def path_param(self, value):
        self.__path_param = value

    @property
    def response(self):
        return self.__response

    @response.setter
    def response(self, value):
        self.__response = value
