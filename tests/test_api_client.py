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


def test_login_no_key_in_response(client_session):
    client, session = client_session
    session.next_response = DummyResponse(200, {"other": "data"})
    assert client.login("u", "p") is False


def test_login_exception(client_session):
    client, session = client_session
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.login("u", "p") is False


def test_login_failure(client_session):
    client, session = client_session
    session.next_response = DummyResponse(400)
    assert client.login("u", "wrong") is False


def test_get_user_details_success(client_session):
    client, session = client_session
    client.set_token("tok")
    user_data = {
        "pk": 1,
        "username": "u", 
        "email": "e@e.com", 
        "first_name": "f", 
        "last_name": "l",
        "date_of_birth": "2000-01-01", 
        "role": "student",
        "department": "DEMACS",
        "is_superuser": False
    }
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
    session.next_response = DummyResponse(201, {"id": 1, "username": "testuser"})
    result = client.register({"username": "u"})
    assert result == {"success": True, "data": {"id": 1, "username": "testuser"}}
    assert result["success"] is True


def test_register_fail(client_session):
    client, session = client_session
    session.next_response = DummyResponse(400, text="Bad Request")
    result = client.register({"username": "u"})
    assert result == {"success": False, "error": "Bad Request"}
    assert result["success"] is False


def test_register_exception(client_session):
    client, session = client_session
    session.side_effect_exception = requests.exceptions.RequestException("NetErr")
    result = client.register({"username": "u"})
    assert result == {"success": False, "error": "NetErr"}
    assert result["success"] is False


def test_get_buildings_success(client_session):
    client, session = client_session
    b = [{"id": "1", "name": "B", "address": "A", "department": "DEMACS"}]
    session.next_response = DummyResponse(200, b)
    assert client.get_buildings() == b


def test_get_buildings_exception(client_session):
    client, session = client_session
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.get_buildings() == []


def test_get_spaces_success(client_session):
    client, session = client_session
    b = {"id": "1", "name": "B", "address": "A", "department": "DEMACS"}
    s = [{
        "id": "s1", 
        "name": "Space1", 
        "building": b, 
        "floor": 1, 
        "capacity": 10, 
        "type": "lab", 
        "department": "DEMACS",
        "equipments": []
    }]
    session.next_response = DummyResponse(200, s)
    assert client.get_spaces() == s


def test_get_spaces_exception(client_session):
    client, session = client_session
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.get_spaces() == []


def test_get_space_success(client_session):
    client, session = client_session
    b = {"id": "1", "name": "B", "address": "A", "department": "DEMACS"}
    s = {
        "id": "s1", 
        "name": "Space1", 
        "building": b, 
        "floor": 1, 
        "capacity": 10, 
        "type": "lab", 
        "department": "DEMACS",
        "equipments": []
    }
    session.next_response = DummyResponse(200, s)
    assert client.get_space("s1") == s


def test_get_space_exception(client_session):
    client, session = client_session
    session.side_effect_exception = requests.exceptions.RequestException()
    assert client.get_space("s1") is None


def test_get_my_reservations_success(client_session):
    client, session = client_session
    client.set_token("tok")
    b = {"id": "1", "name": "B", "address": "A", "department": "DEMACS"}
    s = {
        "id": "s1", 
        "name": "S", 
        "building": b, 
        "floor": 1, 
        "capacity": 10, 
        "type": "lab", 
        "department": "DEMACS",
        "equipments": []
    }
    r = [{
        "id": "r1", 
        "created_by": 1, 
        "space": s, 
        "start_at": "2023-01-01T10:00:00", 
        "end_at": "2023-01-01T11:00:00",
        "header": "H", 
        "status": "active"
    }]
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


def test_logout_without_token(client_session):
    client, session = client_session
    client.token = None
    client.logout()
    assert client.token is None
    assert "Authorization" not in session.headers


def test_get_user_details_without_token(client_session):
    client, session = client_session
    client.token = None
    assert client.get_user_details() is None


def test_get_buildings_non_200_response(client_session):
    client, session = client_session
    session.next_response = DummyResponse(500)
    result = client.get_buildings()
    assert result == []


def test_get_spaces_non_200_response(client_session):
    client, session = client_session
    session.next_response = DummyResponse(404)
    result = client.get_spaces()
    assert result == []


def test_get_space_non_200_response(client_session):
    client, session = client_session
    session.next_response = DummyResponse(500)
    result = client.get_space("s1")
    assert result is None


def test_get_my_reservations_non_200_response(client_session):
    client, session = client_session
    client.set_token("tok")
    session.next_response = DummyResponse(400)
    result = client.get_my_reservations()
    assert result == []


def test_confirm_reservation_success(client_session):
    client, session = client_session
    client.set_token("tok")
    session.next_response = DummyResponse(200)
    result = client.confirm_reservation("r1")
    assert result is True


def test_confirm_reservation_fail(client_session):
    client, session = client_session
    client.set_token("tok")
    session.next_response = DummyResponse(400)
    result = client.confirm_reservation("r1")
    assert result is False


def test_confirm_reservation_exception(client_session):
    client, session = client_session
    client.set_token("tok")
    session.side_effect_exception = requests.exceptions.RequestException()
    result = client.confirm_reservation("r1")
    assert result is False


def test_get_all_reservations_success(client_session):
    client, session = client_session
    client.set_token("tok")
    reservations = [
        {
            "id": "r1",
            "created_by": 1,
            "space": {"id": "s1", "name": "Space1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "header": "Meeting",
            "status": "PENDING"
        }
    ]
    session.next_response = DummyResponse(200, reservations)
    result = client.get_all_reservations()
    assert result == reservations


def test_get_all_reservations_exception(client_session):
    client, session = client_session
    client.set_token("tok")
    session.side_effect_exception = requests.exceptions.RequestException()
    result = client.get_all_reservations()
    assert result == []


def test_create_reservation_end_time_validation_fail(client_session):
    client, _ = client_session
    res = client.create_reservation("s", "2022-01-01", "10:00", "invalid", "h")
    assert res["success"] is False
    assert "Invalid time" in res["error"]


def test_login_bad_status_code(client_session):
    client, session = client_session
    session.next_response = DummyResponse(500, {"key": "secret"})
    assert client.login("u", "p") is False
    assert client.token is None


def test_register_non_201_success_status(client_session):
    client, session = client_session
    session.next_response = DummyResponse(200, {"id": 1, "username": "testuser"})
    result = client.register({"username": "u"})
    assert result["success"] is False
    assert "error" in result


def test_cancel_reservation_non_200_response(client_session):
    client, session = client_session
    client.set_token("tok")
    session.next_response = DummyResponse(404)
    result = client.cancel_reservation("r1")
    assert result is False


def test_set_token_updates_headers(client_session):
    client, session = client_session
    client.set_token("new_token")
    assert client.token == "new_token"
    assert session.headers.get("Authorization") == "Token new_token"