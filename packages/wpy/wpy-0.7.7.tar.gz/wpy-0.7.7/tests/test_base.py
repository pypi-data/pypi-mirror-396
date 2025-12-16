#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import json
import pytest
from wpy import BaseObject, BaseEnum

class User(BaseObject):
    id = 0
    name = None
    age: int
    location: str


def test_base_object():
    params = dict(
        id=1, name='wxnacy', age = 1, location = 'Beijing'
    )

    user = User( **params)
    assert user.id == 1
    assert user.name == 'wxnacy'
    assert user.age == 1
    assert user.location == 'Beijing'

    assert user.to_dict() == params
    assert user.to_json() == json.dumps(params, sort_keys=True)

    assert user.dict() == params
    assert user.json() == json.dumps(params, sort_keys=True)

class StatusEnum(BaseEnum):
    SUCCESS = 'success'
    FAILED = 'failed'
    INIT = 'init'

def test_base_enum():

    assert StatusEnum.values() == ['success', 'failed', 'init']

    assert StatusEnum.is_valid('success')

    with pytest.raises(ValueError):
        StatusEnum.validate('test')

    assert StatusEnum.get_by_value('init') == StatusEnum.INIT
