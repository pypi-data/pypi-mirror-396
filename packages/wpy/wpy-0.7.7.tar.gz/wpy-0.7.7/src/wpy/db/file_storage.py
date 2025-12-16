#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
文件存储
"""


import os
import shutil
import uuid
from datetime import datetime
from wpy.files import FileUtils

class FileStorageError(Exception):
    pass

class FileStorage(object):
    def __init__(self, root):
        self.root = root

    def list_db_names(self):
        if not os.path.exists(self.root):
            return []
        return os.listdir(self.root)

    def get_db(self, db):
        return FileDB(self.root, db)

class FileDB(FileStorage):
    def __init__(self, root, db):
        super().__init__(root)
        self.db = db

        self.db_root = os.path.join(os.path.expanduser(root), db)

    def _create_db_root(self):
        self._create_root(self.db_root)

    def _create_root(self, root):
        if not os.path.exists(root):
            os.makedirs(root)

    def list_table_names(self):
        if not os.path.exists(self.db_root):
            return []
        return os.listdir(self.db_root)

    def get_table(self, table):
        return FileTable(self.root, self.db, table)

class FileTable(FileDB):
    def __init__(self, root, db, table):
        super().__init__(root, db)
        self.table = table
        self.table_root = os.path.join(os.path.expanduser(root), db, table)

    def _create_table_root(self):
        self._create_root(self.table_root)

    def _generage_id(self):
        """生成 id"""
        return str(uuid.uuid4())

    def insert(self, doc):
        data = dict(doc)
        self._create_table_root()
        _id = doc.get("_id") or self._generage_id()
        if self._exists_id(_id):
            raise FileStorageError('{}._id {} is exists'.format(self.table, _id))
        data['_id'] = _id
        data['_create_time'] = self._now()
        data['_update_time'] = self._now()
        table_path = os.path.join(self.table_root, _id)
        FileUtils.write_dict(table_path, data)
        return _id

    def find_one_by_id(self, _id):
        """通过 _id 查找"""
        if self._exists_id(_id):
            return self._read_by_id(_id)
        return None

    def find(self, query, **kwargs):
        if '_id' in query:
            item = self.find_one_by_id(query['_id'])
            return [item] if item else []
        ids = self._list_ids()
        res = []
        for _id in ids:
            doc = self._read_by_id(_id)
            if not self._exists_doc(query, doc):
                continue
            res.append(doc)

        res.sort(lambda x: x.get("_create_time"))
        return res

    def find_one(self, query, **kwargs):
        docs = self.find(query, **kwargs)
        return docs[0] if docs else None

    def update(self, query, update_data):
        if '_id' in update_data:
            raise FileStorageError('_id can not update')
        docs = self.find(query)
        count = 0
        for doc in docs:
            doc.update(update_data)
            if self._update(doc):
                count += 1
        return count

    def delete(self, query):
        """删除数据"""
        docs = self.find(query)
        count = 0
        for doc in docs:
            _id = doc.get("_id")
            if self._delete_by_id(_id):
                count += 1
        return count

    def drop(self):
        """删除表"""
        if os.path.exists(self.table_root):
            #  os.removedirs(self.table_root)
            shutil.rmtree(self.table_root)

    def _delete_by_id(self, _id):
        if self._exists_id(_id):
            os.remove(self._generage_path(_id))
            return True
        return False

    def _update(self, doc):
        _id = doc.get("_id")
        doc['_update_time'] = self._now()
        FileUtils.write_dict(self._generage_path(_id), doc)
        return True

    def _now(self):
        return str(datetime.now())

    def _exists_doc(self, query, doc):
        for k, v in query.items():
            if doc.get(k) != v:
                return False
        return True

    def _list_ids(self):
        if not os.path.exists(self.table_root):
            return []
        return os.listdir(self.table_root)

    def _read_by_id(self, _id):
        return FileUtils.read_dict(self._generage_path(_id))

    def _generage_path(self, _id):
        return os.path.join(self.table_root, _id)

    def _exists_id(self, _id):
        return os.path.exists(self._generage_path(_id))
