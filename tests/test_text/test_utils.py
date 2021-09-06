from text.utils import textified_kwargs


def test_stringify_kwargs():
    assert textified_kwargs(dict(foo="1", bar="2")) == "foo=1, bar=2"
