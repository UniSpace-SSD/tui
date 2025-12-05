import pytest
import main
from rich.console import Console
import io


class DummyConsole:
    def __init__(self):
        self.outputs = []

    def print(self, *args, **kwargs):
        buf = io.StringIO()
        temp_console = Console(file=buf, force_terminal=False, width=120)
        temp_console.print(*args, **kwargs)
        self.outputs.append(buf.getvalue())


class DummyClient:
    def __init__(self):
        self.token = None
        self.user_details = None
        self.buildings = []
        self.spaces = []
        self.reservations = []
        self.login_result = True
        self.register_result = True
        self.cancel_result = True
        self.create_res_result = {"success": True, "data": {}}

    def login(self, u, p):
        return self.login_result

    def register(self, data):
        return self.register_result

    def logout(self):
        self.token = None

    def get_user_details(self):
        return self.user_details

    def get_buildings(self):
        return self.buildings

    def get_spaces(self):
        return self.spaces

    def get_my_reservations(self):
        return self.reservations

    def cancel_reservation(self, rid):
        return self.cancel_result

    def create_reservation(self, sid, d, s, e, h):
        return self.create_res_result


@pytest.fixture
def dummy_setup(monkeypatch):
    console = DummyConsole()
    client = DummyClient()
    monkeypatch.setattr(main, "console", console)
    monkeypatch.setattr(main, "client", client)
    return console, client


def test_login_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    inputs = ["Alice", "secret"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_login()
    output = " ".join(console.outputs)
    assert "Welcome back" in output


def test_login_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.login_result = False
    inputs = ["Bob", "wrong"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_login()
    output = " ".join(console.outputs)
    assert "Login failed" in output


def test_register_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    inputs = ["U", "P", "P", "F", "L", "student"]
    val_inputs = ["test@mail.com", "2000-01-01"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr(main, "get_validated_input", lambda p, r, e: val_inputs.pop(0))
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_register()
    output = " ".join(console.outputs)
    assert "successful" in output


def test_register_pwd_mismatch(dummy_setup, monkeypatch):
    console, client = dummy_setup
    inputs = ["U", "P", "WrongP"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr(main, "get_validated_input", lambda p, r, e: "mail")
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_register()
    output = " ".join(console.outputs)
    assert "match" in output


def test_register_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.register_result = False
    inputs = ["U", "P", "P", "F", "L", "student"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr(main, "get_validated_input", lambda p, r, e: "val")
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_register()
    output = " ".join(console.outputs)
    assert "failed" in output


def test_profile_success(dummy_setup):
    console, client = dummy_setup
    client.user_details = {"username": "test", "email": "test@test.com", "first_name": "T", "last_name": "U",
                           "date_of_birth": "2000-01-01", "role": "student"}
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_profile()
    output = " ".join(console.outputs)
    assert "test" in output


def test_profile_failure(dummy_setup):
    console, client = dummy_setup
    client.user_details = None
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_profile()
    output = " ".join(console.outputs)
    assert "Could not fetch" in output


def test_list_buildings(dummy_setup):
    console, client = dummy_setup
    client.buildings = [{"name": "Build1", "address": "Addr1"}]
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_list_buildings()
    output = " ".join(console.outputs)
    assert "Build1" in output


def test_list_buildings_empty(dummy_setup):
    console, client = dummy_setup
    client.buildings = []
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_list_buildings()
    output = " ".join(console.outputs)
    assert "Buildings" in output


def test_list_spaces(dummy_setup):
    console, client = dummy_setup
    client.spaces = [{"name": "S1", "type": "lab", "capacity": 10, "building": {"name": "B1"}}]
    main.action_list_spaces()
    output = " ".join(console.outputs)
    assert "S1" in output


def test_list_spaces_empty(dummy_setup):
    console, client = dummy_setup
    client.spaces = []
    main.action_list_spaces()
    output = " ".join(console.outputs)
    assert "Spaces" in output


def test_my_reservations_empty(dummy_setup):
    console, client = dummy_setup
    client.reservations = []
    main.action_my_reservations()
    output = " ".join(console.outputs)
    assert "No reservations" in output


def test_my_reservations_no_cancel(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {"id": "r1", "space": {"name": "S"}, "start_at": "2023-01-01T10:00:00", "end_at": "2023-01-01T11:00:00",
         "header": "H", "status": "active"}]
    inputs = ["n"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_my_reservations()
    output = " ".join(console.outputs)
    assert "r1" in output


def test_my_reservations_cancel_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {"id": "r1", "space": {"name": "S"}, "start_at": "2023-01-01T10:00:00", "end_at": "2023-01-01T11:00:00",
         "header": "H", "status": "active"}]
    inputs = ["y", "r1"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_my_reservations()
    output = " ".join(console.outputs)
    assert "cancelled" in output.lower()


def test_my_reservations_cancel_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {"id": "r1", "space": {"name": "S"}, "start_at": "2023-01-01T10:00:00", "end_at": "2023-01-01T11:00:00",
         "header": "H", "status": "active"}]
    client.cancel_result = False
    inputs = ["y", "r1"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_my_reservations()
    output = " ".join(console.outputs)
    assert "Failed" in output


def test_create_reservation_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{"id": "s1", "name": "Space1", "type": "Lab", "capacity": 5}]
    inputs = ["1", "Header"]
    val_inputs = ["2025-01-01", "10:00", "11:00"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr(main, "get_validated_input", lambda p, r, e: val_inputs.pop(0))
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_create_reservation()
    output = " ".join(console.outputs)
    assert "Successfully" in output


def test_create_reservation_no_spaces(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = []
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_create_reservation()
    output = " ".join(console.outputs)
    assert "No spaces" in output


def test_create_reservation_invalid_choice(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{"id": "s1", "name": "Space1", "type": "Lab", "capacity": 5}]
    inputs = ["999"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_create_reservation()
    output = " ".join(console.outputs)
    assert "Invalid" in output


def test_create_reservation_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{"id": "s1", "name": "S1", "type": "T", "capacity": 1}]
    client.create_res_result = {"success": False, "error": "Fail"}
    inputs = ["1", "H"]
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: inputs.pop(0))
    monkeypatch.setattr(main, "get_validated_input", lambda p, r, e: "val")
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_create_reservation()
    output = " ".join(console.outputs)
    assert "Fail" in output


def test_logout(dummy_setup):
    console, client = dummy_setup
    client.token = "TOKEN"
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("builtins.input", lambda: None)
    main.action_logout()
    assert client.token is None
    output = " ".join(console.outputs)
    assert "Logged out" in output


def test_get_auth_menu(dummy_setup):
    console, client = dummy_setup
    menu = main.get_auth_menu()
    assert menu.title == "UniSpace API - Login"
    assert len(menu._choices) == 3


def test_get_main_menu(dummy_setup):
    console, client = dummy_setup
    client.user_details = {"username": "testuser"}
    menu = main.get_main_menu()
    assert "testuser" in menu.title
    assert len(menu._choices) >= 5


def test_get_main_menu_no_user_details(dummy_setup):
    console, client = dummy_setup
    client.user_details = None
    menu = main.get_main_menu()
    assert "User" in menu.title
    assert len(menu._choices) >= 5


def test_action_exit(dummy_setup):
    console, client = dummy_setup
    with pytest.raises(SystemExit) as exc_info:
        main.action_exit()
    assert exc_info.value.code == 0
    output = " ".join(console.outputs)
    assert "Arrivederci" in output


def test_main_loop_unauthenticated(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.token = None
    call_count = [0]

    def fake_run(self):
        call_count[0] += 1
        if call_count[0] >= 2:
            raise KeyboardInterrupt

    monkeypatch.setattr("tui.RichTUI.run", fake_run)
    try:
        main.main()
    except KeyboardInterrupt:
        pass
    assert call_count[0] == 2


def test_main_loop_authenticated(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.token = "test_token"
    client.user_details = None
    call_count = [0]

    def fake_run(self):
        call_count[0] += 1
        if call_count[0] >= 1:
            raise KeyboardInterrupt

    def fake_get_user_details():
        return {"username": "test"}

    monkeypatch.setattr("tui.RichTUI.run", fake_run)
    monkeypatch.setattr(client, "get_user_details", fake_get_user_details)
    try:
        main.main()
    except KeyboardInterrupt:
        pass
    assert call_count[0] == 1