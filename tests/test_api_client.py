import pytest
import requests
from api_client import UniSpaceClient


class DummyResponse:
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        return self._json_data


class DummySession:
    def __init__(self):
        self.headers = {}
        self.last_method = None
        self.last_url = None
        self.last_json = None
        self.next_response = None
        self.side_effect_exception = None

    def update(self, headers):
        self.headers.update(headers)

    def _request(self, method, url, **kwargs):
        self.last_method = method
        self.last_url = url
        self.last_json = kwargs.get("json")

        if self.side_effect_exception:
            raise self.side_effect_exception

        return self.next_response or DummyResponse(404)

    def post(self, url, **kwargs):
        return self._request("POST", url, **kwargs)

    def get(self, url, **kwargs):
        return self._request("GET", url, **kwargs)

    def patch(self, url, **kwargs):
        return self._request("PATCH", url, **kwargs)


@pytest.fixture
def client_session():
    client = UniSpaceClient()
    session = DummySession()
    client.session = session
    return client, session


def test_login_success(client_session):
    client, session = client_session
    session.next_response = DummyResponse(200, {"key": "secret"})
    assert client.login("u", "p") is True
    assert client.token == "secret"


def test_login_failure(client_session):
    client, session = client_session
    session.next_response = DummyResponse(400)
    assert client.login("u", "wrong") is False


def test_get_user_details_success(client_session):
    client, session = client_session
    client.set_token("tok")
    user_data = {"username": "u", "email": "e@e.com", "first_name": "f", "last_name": "l",
                 "date_of_birth": "2000-01-01", "role": "student"}
    session.next_response = DummyResponse(200, user_data)
    assert client.get_user_details() == user_data


def test_get_user_details_fail(client_session):
    client, session = client_session
    client.set_token("tok")
    session.next_response = DummyResponse(500)
    assert client.get_user_details() is None


def test_get_user_details_exception(client_session):
    client, session = client_session
    client.set_token("tok")
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.get_user_details() is None


def test_register_success(client_session):
    client, session = client_session
    session.next_response = DummyResponse(201)
    assert client.register({"username": "u"}) is True


def test_register_fail(client_session):
    client, session = client_session
    session.next_response = DummyResponse(400)
    assert client.register({"username": "u"}) is False


def test_register_exception(client_session):
    client, session = client_session
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.register({"username": "u"}) is False


def test_get_buildings_success(client_session):
    client, session = client_session
    b = [{"id": 1, "name": "B", "address": "A", "map_image": None}]
    session.next_response = DummyResponse(200, b)
    assert client.get_buildings() == b


def test_get_buildings_exception(client_session):
    client, session = client_session
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.get_buildings() == []


def test_get_spaces_success(client_session):
    client, session = client_session
    b = {"id": 1, "name": "B", "address": "A", "map_image": None}
    s = [{"id": "s1", "name": "Space1", "building": b, "floor": 1, "capacity": 10, "type": "lab", "equipment": [],
          "is_active": True}]
    session.next_response = DummyResponse(200, s)
    assert client.get_spaces() == s


def test_get_spaces_exception(client_session):
    client, session = client_session
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.get_spaces() == []


def test_get_my_reservations_success(client_session):
    client, session = client_session
    client.set_token("tok")
    b = {"id": 1, "name": "B", "address": "A", "map_image": None}
    s = {"id": "s1", "name": "S", "building": b, "floor": 1, "capacity": 10, "type": "lab", "equipment": [],
         "is_active": True}
    r = [{"id": "r1", "user": 1, "space": s, "start_at": "2023-01-01T10:00:00", "end_at": "2023-01-01T11:00:00",
          "header": "H", "status": "active"}]
    session.next_response = DummyResponse(200, r)
    assert client.get_my_reservations() == r


def test_get_my_reservations_exception(client_session):
    client, session = client_session
    client.set_token("tok")
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.get_my_reservations() == []


def test_create_reservation_validation_date_fail(client_session):
    client, _ = client_session
    res = client.create_reservation("s", "bad-date", "10:00", "11:00", "h")
    assert res["success"] is False
    assert "Invalid date" in res["error"]


def test_create_reservation_validation_time_fail(client_session):
    client, _ = client_session
    res = client.create_reservation("s", "2022-01-01", "invalid", "11:00", "h")
    assert res["success"] is False
    assert "Invalid time" in res["error"]


def test_create_reservation_success(client_session):
    client, session = client_session
    session.next_response = DummyResponse(201, {"id": "new"})
    res = client.create_reservation("s", "2022-01-01", "10:00", "11:00", "h")
    assert res["success"] is True


def test_create_reservation_fail(client_session):
    client, session = client_session
    session.next_response = DummyResponse(400, text="Bad Request")
    res = client.create_reservation("s", "2022-01-01", "10:00", "11:00", "h")
    assert res["success"] is False
    assert res["error"] == "Bad Request"


def test_create_reservation_exception(client_session):
    client, session = client_session
    session.side_effect_exception = requests.exceptions.RequestException("NetErr")
    res = client.create_reservation("s", "2022-01-01", "10:00", "11:00", "h")
    assert res["success"] is False
    assert "NetErr" in res["error"]


def test_cancel_reservation_success(client_session):
    client, session = client_session
    client.set_token("tok")
    session.next_response = DummyResponse(200)
    assert client.cancel_reservation("r1") is True


def test_cancel_reservation_fail(client_session):
    client, session = client_session
    client.set_token("tok")
    session.next_response = DummyResponse(400)
    assert client.cancel_reservation("r1") is False


def test_cancel_reservation_exception(client_session):
    client, session = client_session
    client.set_token("tok")
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.cancel_reservation("r1") is False


def test_logout_exception(client_session):
    client, session = client_session
    client.set_token("tok")
    session.side_effect_exception = requests.exceptions.RequestException()
    client.logout()
    assert client.token is None
