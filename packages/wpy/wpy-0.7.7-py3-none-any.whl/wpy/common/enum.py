#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:


from typing import List, Any, Dict


class EnumMem(object):
    def __init__(self, value, desc):
        self.value = value
        self.desc = desc

    def __str__(self):
        return "<enum.EnumMem object %s:%s>" % (self.value, self.desc)

    def __repr__(self):
        return "<enum.EnumMem object %s:%s>" % (self.value, self.desc)

    def __eq__(self, other):
        """
        等于
        """
        if isinstance(other, EnumMem):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        else:
            raise TypeError("instances can only be of integral or EnumMem.")

    def __ne__(self, other):
        """
        不等于
        """
        if isinstance(other, EnumMem):
            return self.value != other.value
        elif isinstance(other, int):
            return self.value != other
        else:
            raise TypeError("instances can only be of integral or EnumMem.")

    def __lt__(self, other):
        """
        小于
        """
        if isinstance(other, EnumMem):
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
        else:
            raise TypeError("instances can only be of integral or EnumMem.")

    def __gt__(self, other):
        """
        大于
        """
        if isinstance(other, EnumMem):
            return self.value > other.value
        elif isinstance(other, int):
            return self.value > other
        else:
            raise TypeError("instances can only be of integral or EnumMem.")

    def __le__(self, other):
        """
        小于等于
        """
        if isinstance(other, EnumMem):
            return self.value <= other.value
        elif isinstance(other, int):
            return self.value <= other
        else:
            raise TypeError("instances can only be of integral or EnumMem.")

    def __ge__(self, other):
        """
        大于等于
        """
        if isinstance(other, EnumMem):
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other
        else:
            raise TypeError("instances can only be of integral or EnumMem.")


class EnumMetaClass(type):
    def __new__(mcs, name, bases, attr):
        enum_dict = {}
        for i in attr:
            if not isinstance(attr[i], EnumMem):
                continue
            if attr[i].value in enum_dict:
                raise ValueError("enum value can not repeated: %s", attr[i])
            enum_dict[attr[i].value] = attr[i].desc
            attr[i] = attr[i].value
        attr["__enum_dict__"] = enum_dict
        return type.__new__(mcs, name, bases, attr)

    def __setattr__(cls, name, value):
        raise ValueError("cannot set attr on enum class")


class Enum(object, metaclass=EnumMetaClass):
    @classmethod
    def values(cls) -> List[Any]:
        return getattr(cls, "__enum_dict__").keys()

    @classmethod
    def dict(cls) -> Dict[Any, Any]:
        return getattr(cls, "__enum_dict__")

    @classmethod
    def desc(cls, value, default=None):
        enum_dict = cls.dict()
        if default is not None:
            return enum_dict.get(value, default)
        else:
            return enum_dict[value]

    def __setattr__(self, name, value):
        raise ValueError("cannot set attr on enum instance")

    def __new__(cls, **kwargs):
        raise ValueError("cannot instantiate enum object")
