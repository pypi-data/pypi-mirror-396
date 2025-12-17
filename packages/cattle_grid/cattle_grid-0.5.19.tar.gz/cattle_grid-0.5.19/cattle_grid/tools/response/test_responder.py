from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from cattle_grid.testing.fixtures import *  # noqa

from . import ActivityPubResponder


@pytest.fixture
def test_client(actor_for_test):
    app = FastAPI()

    @app.get("/")
    async def main(responder: ActivityPubResponder):
        return await responder(
            {
                "type": "TestResponseObject",
                "id": "http://localhost/",
                "attributedTo": actor_for_test.actor_id,
            }
        )

    with TestClient(app) as tc:
        yield tc


@pytest.fixture
def test_client_with_html(actor_for_test):
    app = FastAPI()

    @app.get("/")
    async def main(responder: ActivityPubResponder):
        return await responder(
            {
                "type": "TestResponseObject",
                "id": "http://localhost/",
                "attributedTo": actor_for_test.actor_id,
                "url": [{"href": "http://localhost/html", "mediaType": "text/html"}],
            }
        )

    with TestClient(app) as tc:
        yield tc


def test_get_object(test_client, actor_for_test):
    response = test_client.get(
        "/",
        headers={
            "x-ap-location": "http://localhost/",
            "x-cattle-grid-requester": actor_for_test.actor_id,
            "accept": "application/activity+json",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["type"] == "TestResponseObject"


def test_get_object_wrong_location(test_client, actor_for_test):
    response = test_client.get(
        "/",
        headers={
            "x-ap-location": "http://localhost/other",
            "x-cattle-grid-requester": actor_for_test.actor_id,
            "accept": "application/activity+json",
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize("content_type", ["text/html", "text/html; charset=utf-8"])
def test_get_object_request_html(content_type, test_client, actor_for_test):
    response = test_client.get(
        "/",
        headers={
            "x-ap-location": "http://localhost/other",
            "x-cattle-grid-requester": actor_for_test.actor_id,
            "accept": content_type,
        },
    )

    assert response.status_code == 406


@pytest.mark.parametrize("content_type", ["text/html", "text/html; charset=utf-8"])
def test_get_object_request_html_redirected(
    content_type, test_client_with_html, actor_for_test
):
    response = test_client_with_html.get(
        "/",
        headers={
            "x-ap-location": "http://localhost/other",
            "x-cattle-grid-requester": actor_for_test.actor_id,
            "accept": content_type,
        },
        follow_redirects=False,
    )

    assert response.status_code == 307
