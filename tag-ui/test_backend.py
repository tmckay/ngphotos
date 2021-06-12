from backend import Backend, Tags, Table


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
    be.cur.execute(f'''SELECT count(*) FROM {Table.IMAGE.value}''')
    assert be.cur.fetchall()[0][0] == 1

def test_add_image_with_tags():
    tags_to_add = 'fee fi fo fum'
    be = Backend(':memory:')
    be.create_table()
    be.add_image('/Users/foo/images/bar.jpg', '123abc')
    be.update_tags(tags_to_add)

    be.cur.execute(f'''SELECT count(*) FROM {Table.TAG.value}''')
    assert be.cur.fetchall()[0][0] == 4

    be.cur.execute(f'''SELECT * FROM {Table.TAG.value}''')
    tags_added = [row[1] for row in be.cur.fetchall()]
    assert sorted(tags_added) == ['fee', 'fi', 'fo', 'fum'] 

    be.cur.execute(f'''SELECT * FROM {Table.IMAGE_TAGS.value}''')
    rows = be.cur.fetchall()
    assert len(rows) == 4
    for row in rows:
        assert row[1] == 1


def test_add_images_with_existing_tags():
    be = Backend(':memory:')
    be.create_table()
    be.add_image('/Users/foo/images/bar.jpg', '123abc')
    be.update_tags('baz')

    be.add_image('/Users/foo/images/buzz.jpg', 'abc123')
    be.update_tags('baz')

    be.cur.execute(f'''SELECT * FROM {Table.TAG.value}''')
    results = be.cur.fetchall()
    assert len(results) == 1
    assert results[0][1] == 'baz'


def test_get_images_by_tag():
    tags_to_add = 'fee fi fo fum'
    be = Backend(':memory:')
    be.create_table()
    be.add_image('/Users/foo/images/bar.jpg', '123abc')
    be.update_tags(tags_to_add)

    be.add_image('/Users/foo/images/baz.jpg', 'abc123')
    be.update_tags('foo bar')
    be.add_image('/Users/foo/images/spam.jpg', 'cda321')
    be.update_tags('foo bar')

    images = be.get_images_by_tag('fee')
    assert images[0][1] == '/Users/foo/images/bar.jpg'


def test_reset():
    be = Backend(':memory:')
    be.create_table()
    be.add_image('/Users/foo/images/bar.jpg', '123abc')
    be.cur.execute(f'''SELECT * FROM {Table.IMAGE.value}''')
    be.reset()
    assert len(be.cur.fetchall()) == 0
