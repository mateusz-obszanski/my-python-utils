from text.transform import replace_many


def test_replace_many():
    assert replace_many("foo fo", dict(fo="ba", foo="bar")) == "bar ba"
