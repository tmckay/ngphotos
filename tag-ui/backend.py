from collections import deque
from multiprocessing import Process, Queue
import os
import sqlite3


IMAGE_TABLE = 'images'
TAG_TABLE = 'tags'
IMAGE_TAGS_TABLE = 'image_tags'


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


class Backend:
    
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def create_table(self):
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {IMAGE_TABLE} (
                                imageid INTEGER PRIMARY KEY,
                                path TEXT UNIQUE,
                                md5 TEXT
                             )''')
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {TAG_TABLE} (
                                tagid INTEGER PRIMARY KEY,
                                tag_value TEXT UNIQUE
                             )''')
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {IMAGE_TAGS_TABLE} (
                                tagid INTEGER,
                                imageid INTEGER,
                                FOREIGN KEY(tagid) REFERENCES {TAG_TABLE}(tagid),
                                FOREIGN KEY(imageid) REFERENCES {IMAGE_TABLE}(imageid)
                             )''')
        self.con.commit()

    def get_images_by_tag(self, tag):
        self.cur.execute(f'''SELECT * FROM {IMAGE_TABLE}
                             INNER JOIN {IMAGE_TAGS_TABLE}
                             ON {IMAGE_TABLE}.imageid = {IMAGE_TAGS_TABLE}.imageid
                             INNER JOIN {TAG_TABLE}
                             ON {IMAGE_TAGS_TABLE}.tagid = {TAG_TABLE}.tagid
                             WHERE tag_value = '{tag}' ''')
        return self.cur.fetchall()

    def add_image(self, path, md5):
        self.cur.execute(f'''SELECT imageid from {IMAGE_TABLE} WHERE path = '{path}' ''')
        rows = self.cur.fetchall()
        assert len(rows) <= 1

        if len(rows) == 1:
            self.image_id = rows[0][0]
        elif len(rows) == 0:
            self.cur.execute(f'''INSERT INTO {IMAGE_TABLE} VALUES (null, '{path}', '{md5}')''')
            self.image_id = self.cur.lastrowid
            self.con.commit()

    def update_tags(self, tags):

        def insert_tag(tag):
            print(f'calling insert tag {tag}')

            self.cur.execute(f'''SELECT * FROM {TAG_TABLE} WHERE tag_value = '{tag}' ''')
            rows = self.cur.fetchall()
            assert len(rows) <= 1

            if len(rows) == 1:
                tag_id = rows[0][0]

            else:
                self.cur.execute(f'''INSERT INTO {TAG_TABLE} VALUES (null, '{tag}')''')
                tag_id = self.cur.lastrowid
                self.cur.execute(f'''INSERT INTO {IMAGE_TAGS_TABLE} VALUES ('{tag_id}', '{self.image_id}')''')
                self.con.commit()

        for tag in Tags.parse(tags):
            insert_tag(tag)

    def reset(self):
        self.cur.execute(f'''DROP TABLE {IMAGE_TABLE}''')
        self.cur.execute(f'''DROP TABLE {TAG_TABLE}''')
        self.cur.execute(f'''DROP TABLE {IMAGE_TAGS_TABLE}''')
        self.con.commit()

        self.create_table()

    def close(self):
        self.con.close()
