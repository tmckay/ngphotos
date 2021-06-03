from backend import Backend


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
    be = Backend(':memory:')
    be.create_table()
    be.add_image('/Users/foo/images/bar.jpg', '123abc')
    be.update_tags('fee fi fo fum')

    be.cur.execute('''SELECT count(*) FROM tags''')
    assert be.cur.fetchall()[0][0] == 4

    be.cur.execute('''SELECT count(*) FROM image_tags''')
    assert be.cur.fetchall()[0][0] == 4

