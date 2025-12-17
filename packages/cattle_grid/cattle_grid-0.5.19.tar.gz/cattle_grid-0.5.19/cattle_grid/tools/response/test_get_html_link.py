import pytest
from . import get_html_link


@pytest.mark.parametrize(
    "obj",
    [
        {},
        {"url": []},
        {"url": None},
        {"url": {"mediaType": "other"}},
        {"url": [{"mediaType": "other"}]},
    ],
)
def test_get_html_link_none(obj):
    assert get_html_link(obj) is None


@pytest.mark.parametrize(
    "obj",
    [
        {"url": "url"},
        {"url": ["url"]},
        {"url": {"mediaType": "text/html", "href": "url"}},
        {"url": [{"mediaType": "text/html", "href": "url"}]},
    ],
)
def test_get_html_link_success(obj):
    assert get_html_link(obj) == "url"
