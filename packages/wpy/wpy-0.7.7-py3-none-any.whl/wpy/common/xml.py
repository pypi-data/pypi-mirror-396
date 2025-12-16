#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import xmltodict
import json

class XML():
    @staticmethod
    def xml2dict(xmlstr: str):
        '''
        convert xml string to dict
        '''
        return json.loads(json.dumps(xmltodict.parse(xmlstr)))

    @staticmethod
    def dict2xml(j: dict):
        '''
        convert dict to xml string
        '''
        return xmltodict.unparse(j)

