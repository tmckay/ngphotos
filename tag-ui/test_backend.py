from backend import Backend, Tags


def test_parse_tags():
    raw_tags = 'fee fi fo fum'
    parsed_tags = Tags.parse(raw_tags)
    assert ['fee', 'fi', 'fo', 'fum'] == sorted(parsed_tags)

    raw_tags = '"hello world" beach'
    parsed_tags = Tags.parse(raw_tags)
    assert ['beach', 'hello world'] == sorted(parsed_tags)


def test_create_tables():
    be = Backend(':memory:')
    be.create_table()
    be.cur.execute('''SELECT count(*) FROM sqlite_master WHERE type = 'table' ''')
    assert be.cur.fetchall()[0][0] == 3

def test_add_image():
    be = Backend(':memory:')
    be.create_table()
    be.add_image('/Users/foo/images/bar.jpg', '123abc')
    be.cur.execute('''SELECT count(*) FROM images''')
    assert be.cur.fetchall()[0][0] == 1

def test_add_image_with_tags():
    tags_to_add = 'fee fi fo fum'
    be = Backend(':memory:')
    be.create_table()
    be.add_image('/Users/foo/images/bar.jpg', '123abc')
    be.update_tags(tags_to_add)

    be.cur.execute('''SELECT count(*) FROM tags''')
    assert be.cur.fetchall()[0][0] == 4

    be.cur.execute('''SELECT count(*) FROM image_tags''')
    assert be.cur.fetchall()[0][0] == 4

    be.cur.execute('''SELECT * FROM tags''')
    tags_added = [row[1] for row in be.cur.fetchall()]
    assert sorted(tags_added) == ['fee', 'fi', 'fo', 'fum'] 
