#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import unittest
from wpy import ID

CONTENT = 'wxnacy'

class TestCase(unittest.TestCase):
    def setUp(self):
        pass
    def teardown(self):
        pass

    def test_random(self):
        for i in range(10000):
            self.assertEqual(6, len(str(ID.random_int(6))))
        for i in range(10000):
            self.assertEqual(6, len(str(ID.random_str(6))))



if __name__ == "__main__":
    unittest.main()
