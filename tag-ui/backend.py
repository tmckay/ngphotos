from abc import ABC, abstractmethod
from collections import deque
from enum import Enum, unique
from multiprocessing import Process, Queue
import os
import sqlite3


@unique
class Table(Enum):
    IMAGE = 'images'
    TAG = 'tags'
    IMAGE_TAGS = 'image_tags'


class Tags:
    @staticmethod
    def parse(raw_tag_input):
        parsed_tags = [] 

        current = deque() 
        quoted = False
        for char in raw_tag_input:
            if char == '"':
                quoted = not quoted
            elif char == ' ' and not quoted:
                tag = ''.join(current)
                current = deque() 
                parsed_tags.append(tag) 
            else:
                current.append(char)

        # case when we only have one tag
        if current:
            tag = ''.join(current)
            parsed_tags.append(tag) 

        return parsed_tags


class CRUDObject(ABC):

    @property
    @abstractmethod
    def insert(self):
        pass

    @property
    @abstractmethod
    def update(self):
        pass

    @property
    @abstractmethod
    def delete(self):
        pass


class Image(CRUDObject):
    
    def insert(self):
        query = f'''INSERT INTO {Table.IMAGE.value} VALUES (null, '{path}', '{md5}')'''

    def update(self):
        query = f''' '''

    def delete(self):
        query = f'''DELETE FROM {Table.IMAGE.value} WHERE image_id = '{image_id}' '''

class Tag(CRUDObject):

    def insert(self):
        pass


class Backend:
    
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def create_table(self):
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {Table.IMAGE.value} (
                                imageid INTEGER PRIMARY KEY,
                                path TEXT UNIQUE,
                                md5 TEXT
                             )''')
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {Table.TAG.value} (
                                tagid INTEGER PRIMARY KEY,
                                tag_value TEXT UNIQUE
                             )''')
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {Table.IMAGE_TAGS.value} (
                                tagid INTEGER,
                                imageid INTEGER,
                                FOREIGN KEY(tagid) REFERENCES {Table.TAG.value}(tagid),
                                FOREIGN KEY(imageid) REFERENCES {Table.IMAGE.value}(imageid)
                             )''')
        self.con.commit()

    def get_images_by_tag(self, tag):
        self.cur.execute(f'''SELECT * FROM {Table.IMAGE.value}
                             INNER JOIN {Table.IMAGE_TAGS.value}
                             ON {Table.IMAGE.value}.imageid = {Table.IMAGE_TAGS.value}.imageid
                             INNER JOIN {Table.TAG.value}
                             ON {Table.IMAGE_TAGS.value}.tagid = {Table.TAG.value}.tagid
                             WHERE tag_value = '{tag}' ''')
        return self.cur.fetchall()

    def add_image(self, path, md5):
        self.cur.execute(f'''SELECT imageid from {Table.IMAGE.value} WHERE path = '{path}' ''')
        rows = self.cur.fetchall()
        assert len(rows) <= 1

        if len(rows) == 1:
            self.image_id = rows[0][0]
        elif len(rows) == 0:
            self.cur.execute(f'''INSERT INTO {Table.IMAGE.value} VALUES (null, '{path}', '{md5}')''')
            self.image_id = self.cur.lastrowid
            self.con.commit()

    def delete_image(self, image_id):
        self.cur.execute(f'''DELETE FROM {Table.IMAGE.value} WHERE image_id = '{image_id}' ''')
        self.con.commit()

    def update_tags(self, tags, image_id=None):
        """If image_id is not provided, we default to adding tags to last added image."""

        def insert_tag(tag):
            nonlocal image_id

            print(f'calling insert tag {tag}')

            self.cur.execute(f'''SELECT * FROM {Table.TAG.value} WHERE tag_value = '{tag}' ''')
            rows = self.cur.fetchall()
            assert len(rows) <= 1

            if len(rows) == 1:
                tag_id = rows[0][0]

            else:
                self.cur.execute(f'''INSERT INTO {Table.TAG.value} VALUES (null, '{tag}')''')
                tag_id = self.cur.lastrowid

                # Use last inserted image if image_id is not passed as argument
                if not image_id:
                    image_id = self.image_id

                self.cur.execute(f'''INSERT INTO {Table.IMAGE_TAGS.value} VALUES ('{tag_id}', '{image_id}')''')
                self.con.commit()

        for tag in Tags.parse(tags):
            insert_tag(tag)

    def reset(self):
        self.cur.execute(f'''DROP TABLE {Table.IMAGE.value}''')
        self.cur.execute(f'''DROP TABLE {Table.TAG.value}''')
        self.cur.execute(f'''DROP TABLE {Table.IMAGE_TAGS.value}''')
        self.con.commit()

        self.create_table()

    def close(self):
        self.con.close()
