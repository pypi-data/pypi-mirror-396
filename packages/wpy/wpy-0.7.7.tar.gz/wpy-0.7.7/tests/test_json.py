#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import unittest
from wpy import JSON


class TestCase(unittest.TestCase):
    def setUp(self):
        pass
    def teardown(self):
        pass

    def test_filter(self):
        book = dict(id = 2, name = 'size', price = 5)
        user = dict(id = 1, name = "wxnacy", book= book)

        res = JSON.filter(source = dict(user), source_include=['id', 'book'])
        data = dict(id = 1, book= book)
        self.assertEqual(res, data)

        res = JSON.filter(dict(user), 'id', 'book')
        data = dict(id = 1, book= book)
        self.assertEqual(res, data)

        res = JSON.filter(dict(user), 'id', 'book.id')
        data = dict(id = 1, book= dict(id = 2))
        self.assertEqual(res, data)

        res = JSON.filter(dict(user), 'id', 'book.id', 'book.name')
        data = dict(id = 1, book= dict(id = 2, name = "size"))
        self.assertEqual(res, data)

        res = JSON.filter(dict(user), 'id', 'book[id,name]')
        data = dict(id = 1, book= dict(id = 2, name = "size"))
        self.assertEqual(res, data)

        res = JSON.filter(dict(user), source_exclude=['name', 'book'])
        data = dict(id = 1)
        self.assertEqual(res, data)

        res = JSON.filter(dict(user), source_exclude=['name', 'book.price'])
        data = dict(id = 1, book= dict(id = 2, name = "size"))
        self.assertEqual(res, data)

        print(user)
        res = JSON.filter(dict(user), source_exclude=['name', 'book.price', 'book.id'])
        data = dict(id = 1, book= dict(name = "size"))
        self.assertEqual(res, data)

        res = JSON.filter(dict(user), source_exclude=['name', 'book[id,price]'])
        data = dict(id = 1, book= dict(name = "size"))
        self.assertEqual(res, data)

    def test_getattr(self):

        book = dict(id = 2, name = 'size', price = 5)
        user = dict(id = 1, name = "wxnacy", book= book)
        user = JSON.BaseDict(user)
        self.assertEqual(1, user.id)
        self.assertEqual(book, user.book)

    def test_filter_list(self):
        book = dict(id = 2, name = 'size', price = 5)
        book1 = dict(id = 3, name = 'bo', price = 6)
        user = dict(id = 1, name = "wxnacy", books= [book, book1])

        res = JSON.filter(user, 'id', 'books.id')
        data = dict(id = 1, books = [dict(id = 2), dict(id = 3)])
        self.assertEqual(res, data)

        res = JSON.filter(user, 'id', 'books.id', 'books.price')
        data = dict(id = 1, books = [dict(id = 2, price = 5),
            dict(id = 3, price=6)])
        self.assertEqual(res, data)

        res = JSON.filter(user, 'id', 'books[id,price]')
        data = dict(id = 1, books = [dict(id = 2, price = 5),
            dict(id = 3, price=6)])
        self.assertEqual(res, data)

        res = JSON.filter(user, source_exclude=['name', 'books.name'])
        data = dict(id = 1, books = [dict(id = 2, price = 5),
            dict(id = 3, price=6)])
        self.assertEqual(res, data)

        res = JSON.filter(user, source_exclude=['name', 'books.name',
            'books.price'])
        data = dict(id = 1, books = [dict(id = 2), dict(id = 3)])
        self.assertEqual(res, data)

        res = JSON.filter(user, source_exclude = ['name', 'books[name,price]'])
        data = dict(id = 1, books = [dict(id = 2), dict(id = 3)])
        self.assertEqual(res, data)

if __name__ == "__main__":
    unittest.main()
