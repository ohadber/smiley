"""
Implement all-over tests for the server.
"""
import json

import pytest
from flask_api.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from server import create_app


@pytest.fixture
def client():
    """
    Create a test client for the flask server.
    :return:
    """
    app = create_app()
    client = app.test_client()
    return client


def test_single_pic(client, image_dir):
    """
    Ensure the server works for the general case. Send one picture and assert
    a dict is returned.

    :type client: flask.testing.FlaskClient
    :type image_dir: pathlib.Path
    """
    pic_path = image_dir / 'gadot.png'
    data = dict(files=(str(pic_path),))
    response = client.post('/', data=data)
    assert response.status_code == HTTP_200_OK

    data = json.loads(response.data)
    assert isinstance(data, dict)


def test_no_data(client):
    """
    Make sure that when no data sent a regular string response is returned
    represented as bytes with an error message.

    :type client: flask.testing.FlaskClient
    """
    response = client.post('/', data=())
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "Error" in str(response.data)
