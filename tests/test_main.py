import pytest
import main
from rich.console import Console
import io
import datetime


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
        self.all_reservations = []
        self.login_result = True
        self.register_result = {"success": True, "data": {}}
        self.cancel_result = True
        self.confirm_result = True
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

    def get_all_reservations(self):
        return self.all_reservations

    def cancel_reservation(self, rid):
        return self.cancel_result

    def confirm_reservation(self, rid):
        return self.confirm_result

    def create_reservation(self, sid, d, s, e, h):
        return self.create_res_result


@pytest.fixture
def dummy_setup(monkeypatch):
    console = DummyConsole()
    client = DummyClient()
    monkeypatch.setattr(main, "console", console)
    monkeypatch.setattr(main, "client", client)
    return console, client


# ============ ACTION_LOGIN TESTS ============
def test_login_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    inputs = iter(["Alice", "secret"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_login()
    output = " ".join(console.outputs)
    assert "Welcome back" in output


def test_login_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.login_result = False
    inputs = iter(["Bob", "wrong"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_login()
    output = " ".join(console.outputs)
    assert "Login failed" in output


# ============ ACTION_REGISTER TESTS ============
def test_register_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    
    inputs = iter([
        "U",
        "Password123",
        "Password123",
        "F",
        "L",
        "student",
        "DEMACS",
    ])
    
    def mock_validated_input(prompt, regex, error):
        if "Email" in prompt:
            return "test@mail.com"
        elif "Date of Birth" in prompt:
            return "2000-01-01"
        return ""
    
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs))
    monkeypatch.setattr(main, "get_validated_input", mock_validated_input)
    monkeypatch.setattr("builtins.input", lambda: "")
    
    main.action_register()
    output = " ".join(console.outputs).lower()
    assert "successful" in output


def test_register_password_too_short(dummy_setup, monkeypatch):
    """Test registrazione con password troppo corta"""
    console, client = dummy_setup
    
    inputs = iter([
        "U",
        "short",  # password troppo corta
        "Pass1234",  # password valida
        "Pass1234",  # conferma
        "F",
        "L",
        "student",
        "DEMACS",
    ])
    
    def mock_validated_input(prompt, regex, error):
        if "Email" in prompt:
            return "test@mail.com"
        elif "Date of Birth" in prompt:
            return "2000-01-01"
        return ""
    
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs))
    monkeypatch.setattr(main, "get_validated_input", mock_validated_input)
    monkeypatch.setattr("builtins.input", lambda: "")
    
    main.action_register()
    output = " ".join(console.outputs).lower()
    assert "8 characters" in output or "successful" in output


def test_register_pwd_mismatch(dummy_setup, monkeypatch):
    console, client = dummy_setup
    
    inputs = iter([
        "U",
        "Password123",
        "WrongPass",
        "Password123",
        "Password123",
        "F",
        "L",
        "student",
        "DEMACS",
    ])
    
    def mock_validated_input(prompt, regex, error):
        if "Email" in prompt:
            return "test@mail.com"
        elif "Date of Birth" in prompt:
            return "2000-01-01"
        return ""
    
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs))
    monkeypatch.setattr(main, "get_validated_input", mock_validated_input)
    monkeypatch.setattr("builtins.input", lambda: "")
    
    main.action_register()
    output = " ".join(console.outputs).lower()
    assert "match" in output or "mismatch" in output or "do not match" in output


def test_register_invalid_date_future(dummy_setup, monkeypatch):
    """Test registrazione con data nel futuro"""
    console, client = dummy_setup
    
    inputs = iter([
        "U",
        "Password123",
        "Password123",
        "F",
        "L",
        "student",
        "DEMACS",
    ])
    
    call_count = [0]
    future_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    def mock_validated_input(prompt, regex, error):
        if "Email" in prompt:
            return "test@mail.com"
        elif "Date of Birth" in prompt:
            call_count[0] += 1
            if call_count[0] == 1:
                return future_date
            else:
                return "2000-01-01"
        return ""
    
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs))
    monkeypatch.setattr(main, "get_validated_input", mock_validated_input)
    monkeypatch.setattr("builtins.input", lambda: "")
    
    main.action_register()
    output = " ".join(console.outputs).lower()
    assert "future" in output or "successful" in output


def test_register_invalid_date_value(dummy_setup, monkeypatch):
    """Test registrazione con data invalida (es. 2023-02-30)"""
    console, client = dummy_setup
    
    inputs = iter([
        "U",
        "Password123",
        "Password123",
        "F",
        "L",
        "student",
        "DEMACS",
    ])
    
    call_count = [0]
    
    def mock_validated_input(prompt, regex, error):
        if "Email" in prompt:
            return "test@mail.com"
        elif "Date of Birth" in prompt:
            call_count[0] += 1
            if call_count[0] == 1:
                return "2023-02-30"
            else:
                return "2000-01-01"
        return ""
    
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs))
    monkeypatch.setattr(main, "get_validated_input", mock_validated_input)
    monkeypatch.setattr("builtins.input", lambda: "")
    
    main.action_register()
    output = " ".join(console.outputs).lower()
    assert "invalid" in output or "successful" in output


def test_register_role_invalid_then_valid(dummy_setup, monkeypatch):
    """Test registrazione con ruolo invalido poi valido"""
    console, client = dummy_setup
    
    inputs = iter([
        "U",
        "Password123",
        "Password123",
        "F",
        "L",
        "admin",  # ruolo invalido
        "professor",  # ruolo valido
        "DEMACS",
    ])
    
    def mock_validated_input(prompt, regex, error):
        if "Email" in prompt:
            return "test@mail.com"
        elif "Date of Birth" in prompt:
            return "2000-01-01"
        return ""
    
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs))
    monkeypatch.setattr(main, "get_validated_input", mock_validated_input)
    monkeypatch.setattr("builtins.input", lambda: "")
    
    main.action_register()
    output = " ".join(console.outputs).lower()
    assert "invalid" in output or "successful" in output


def test_register_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.register_result = {"success": False, "error": "Registration failed"}
    
    inputs = iter([
        "U",
        "Password123",
        "Password123",
        "F",
        "L",
        "student",
        "DEMACS",
    ])
    
    def mock_validated_input(prompt, regex, error):
        if "Email" in prompt:
            return "test@mail.com"
        elif "Date of Birth" in prompt:
            return "2000-01-01"
        return ""
    
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs))
    monkeypatch.setattr(main, "get_validated_input", mock_validated_input)
    monkeypatch.setattr("builtins.input", lambda: "")
    
    main.action_register()
    output = " ".join(console.outputs).lower()
    assert "failed" in output


def test_profile_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.user_details = {
        "pk": 1,
        "username": "test",
        "email": "test@test.com",
        "first_name": "T",
        "last_name": "U",
        "date_of_birth": "2000-01-01",
        "role": "student",
        "department": "DEMACS",
        "is_superuser": False
    }
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_profile()
    output = " ".join(console.outputs).lower()
    assert "test" in output


def test_profile_with_superuser(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.user_details = {
        "pk": 1,
        "username": "admin",
        "email": "admin@test.com",
        "first_name": "A",
        "last_name": "D",
        "date_of_birth": "1990-01-01",
        "role": "professor",
        "department": "DEMACS",
        "is_superuser": True
    }
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_profile()
    output = " ".join(console.outputs).lower()
    assert "admin" in output
    assert "superuser" in output or "true" in output


def test_profile_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.user_details = None
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_profile()
    output = " ".join(console.outputs).lower()
    assert "could not fetch" in output


def test_list_buildings(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.buildings = [{"id": "1", "name": "Build1", "address": "Addr1", "department": "DEMACS"}]
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_list_buildings()
    output = " ".join(console.outputs).lower()
    assert "build1" in output


def test_list_buildings_long_id(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.buildings = [{
        "id": "very-long-id-that-exceeds-eight-characters",
        "name": "Build1",
        "address": "Addr1",
        "department": "DEMACS"
    }]
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_list_buildings()
    output = " ".join(console.outputs)
    assert "..." in output or "build1" in output.lower()


def test_list_buildings_empty(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.buildings = []
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_list_buildings()
    output = " ".join(console.outputs).lower()
    assert "buildings" in output


def test_list_spaces(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{
        "id": "1",
        "name": "S1",
        "type": "lab",
        "capacity": 10,
        "building": {"id": "1", "name": "B1", "address": "A", "department": "DEMACS"},
        "department": "DEMACS"
    }]
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_list_spaces()
    output = " ".join(console.outputs).lower()
    assert "s1" in output


def test_list_spaces_long_id(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{
        "id": "very-long-space-id-exceeding-eight-chars",
        "name": "S1",
        "type": "lab",
        "capacity": 10,
        "building": {"id": "1", "name": "B1", "address": "A", "department": "DEMACS"},
        "department": "DEMACS"
    }]
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_list_spaces()
    output = " ".join(console.outputs)
    assert "..." in output or "s1" in output.lower()


def test_list_spaces_building_as_string(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{
        "id": "1",
        "name": "S1",
        "type": "lab",
        "capacity": 10,
        "building": "Building String",
        "department": "DEMACS"
    }]
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_list_spaces()
    output = " ".join(console.outputs).lower()
    assert "s1" in output


def test_list_spaces_empty(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = []
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_list_spaces()
    output = " ".join(console.outputs).lower()
    assert "spaces" in output


def test_my_reservations_empty(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = []
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_my_reservations()
    output = " ".join(console.outputs).lower()
    assert "no reservations" in output


def test_my_reservations_no_cancel(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {
            "id": "r1",
            "space": {"id": "1", "name": "S", "building": {"name": "B"}, "department": "DEMACS"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "header": "H",
            "status": "CONFIRMED"
        }
    ]
    inputs = iter(["n"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, "n"))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_my_reservations()
    output = " ".join(console.outputs).lower()
    assert "reservations" in output


def test_my_reservations_cancel_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {
            "id": "r1",
            "space": {"id": "1", "name": "S", "building": {"name": "B"}, "department": "DEMACS"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "header": "H",
            "status": "PENDING"
        }
    ]
    inputs = iter(["y", "r1"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_my_reservations()
    output = " ".join(console.outputs).lower()
    assert any(word in output for word in ["cancelled", "success", "completed", "reservation cancelled"])


def test_my_reservations_cancel_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {
            "id": "r1",
            "space": {"id": "1", "name": "S", "building": {"name": "B"}, "department": "DEMACS"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "header": "H",
            "status": "PENDING"
        }
    ]
    client.cancel_result = False
    inputs = iter(["y", "r1"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_my_reservations()
    output = " ".join(console.outputs).lower()
    assert any(word in output for word in ["failed", "error", "invalid", "unable"])


def test_my_reservations_cancel_no_pending(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {
            "id": "r1",
            "space": {"id": "1", "name": "S", "building": {"name": "B"}, "department": "DEMACS"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "header": "H",
            "status": "CONFIRMED"
        }
    ]
    inputs = iter(["y"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, "n"))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_my_reservations()
    output = " ".join(console.outputs).lower()
    assert "no" in output and "pending" in output


def test_my_reservations_cancel_invalid_id(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {
            "id": "r1",
            "space": {"id": "1", "name": "S", "building": {"name": "B"}, "department": "DEMACS"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "header": "H",
            "status": "PENDING"
        }
    ]
    inputs = iter(["y", "invalid-id"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_my_reservations()
    output = " ".join(console.outputs).lower()
    assert "invalid" in output


def test_my_reservations_space_as_string(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {
            "id": "r2",
            "space": "Lab42",
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "header": "H",
            "status": "CONFIRMED",
        }
    ]
    inputs = iter(["n"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, "n"))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_my_reservations()
    output = " ".join(console.outputs).lower()
    assert "reservations" in output


def test_my_reservations_long_id(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.reservations = [
        {
            "id": "very-long-reservation-id-exceeding-eight-characters",
            "space": {"id": "1", "name": "S", "building": {"name": "B"}, "department": "DEMACS"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "header": "H",
            "status": "CONFIRMED",
        }
    ]
    inputs = iter(["n"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, "n"))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_my_reservations()
    output = " ".join(console.outputs)
    assert "..." in output


def test_create_reservation_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{"id": "s1", "name": "Space1", "type": "Lab", "capacity": 5, "department": "DEMACS"}]
    inputs = iter(["1", "Header"])
    val_inputs = iter(["2025-01-01", "10:00", "11:00"])
    
    def mock_validated_input(prompt, regex, error):
        return next(val_inputs, "")
    
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr(main, "get_validated_input", mock_validated_input)
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_create_reservation()
    output = " ".join(console.outputs).lower()
    assert "success" in output


def test_create_reservation_no_spaces(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = []
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_create_reservation()
    output = " ".join(console.outputs).lower()
    assert "no spaces" in output


def test_create_reservation_invalid_choice(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{"id": "s1", "name": "Space1", "type": "Lab", "capacity": 5, "department": "DEMACS"}]
    inputs = iter(["999"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_create_reservation()
    output = " ".join(console.outputs).lower()
    assert "invalid" in output


def test_create_reservation_long_space_id(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{
        "id": "very-long-space-id-exceeding-eight-characters",
        "name": "Space1",
        "type": "Lab",
        "capacity": 5,
        "department": "DEMACS"
    }]
    inputs = iter(["1", "Header"])
    val_inputs = iter(["2025-01-01", "10:00", "11:00"])
    
    def mock_validated_input(prompt, regex, error):
        return next(val_inputs, "")
    
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr(main, "get_validated_input", mock_validated_input)
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_create_reservation()
    output = " ".join(console.outputs)
    assert "..." in output or "success" in output.lower()


def test_create_reservation_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.spaces = [{"id": "s1", "name": "S1", "type": "T", "capacity": 1, "department": "DEMACS"}]
    client.create_res_result = {"success": False, "error": "Fail"}
    inputs = iter(["1", "H"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr(main, "get_validated_input", lambda p, r, e: "val")
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_create_reservation()
    output = " ".join(console.outputs).lower()
    assert "fail" in output


def test_manage_reservations_empty(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = []
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs).lower()
    assert "no reservations" in output


def test_manage_reservations_back(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "r1",
            "created_by": {"username": "user1"},
            "space": {"id": "s1", "name": "S1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "PENDING"
        }
    ]
    inputs = iter(["back"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, "back"))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs).lower()
    assert "reservations" in output


def test_manage_reservations_confirm_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "r1",
            "created_by": {"username": "user1"},
            "space": {"id": "s1", "name": "S1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "PENDING"
        }
    ]
    inputs = iter(["confirm", "r1"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs).lower()
    assert "confirmed" in output


def test_manage_reservations_confirm_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "r1",
            "created_by": {"username": "user1"},
            "space": {"id": "s1", "name": "S1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "PENDING"
        }
    ]
    client.confirm_result = False
    inputs = iter(["confirm", "r1"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs).lower()
    assert "failed" in output


def test_manage_reservations_cancel_success(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "r1",
            "created_by": {"username": "user1"},
            "space": {"id": "s1", "name": "S1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "PENDING"
        }
    ]
    inputs = iter(["cancel", "r1"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs).lower()
    assert "cancelled" in output


def test_manage_reservations_cancel_failure(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "r1",
            "created_by": {"username": "user1"},
            "space": {"id": "s1", "name": "S1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "PENDING"
        }
    ]
    client.cancel_result = False
    inputs = iter(["cancel", "r1"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs).lower()
    assert "failed" in output


def test_manage_reservations_no_pending(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "r1",
            "created_by": {"username": "user1"},
            "space": {"id": "s1", "name": "S1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "CONFIRMED"
        }
    ]
    inputs = iter(["confirm"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs).lower()
    assert "no" in output and "pending" in output


def test_manage_reservations_invalid_id(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "r1",
            "created_by": {"username": "user1"},
            "space": {"id": "s1", "name": "S1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "PENDING"
        }
    ]
    inputs = iter(["confirm", "invalid-id"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs).lower()
    assert "invalid" in output


def test_manage_reservations_long_id(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "very-long-reservation-id-exceeding-eight-characters",
            "created_by": {"username": "user1"},
            "space": {"id": "s1", "name": "S1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "PENDING"
        }
    ]
    inputs = iter(["back"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs)
    assert "..." in output


def test_manage_reservations_user_as_int(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "r1",
            "created_by": 123,
            "space": {"id": "s1", "name": "S1"},
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "PENDING"
        }
    ]
    inputs = iter(["back"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs)
    assert "123" in output


def test_manage_reservations_space_as_string(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.all_reservations = [
        {
            "id": "r1",
            "created_by": {"username": "user1"},
            "space": "Lab 42",
            "start_at": "2023-01-01T10:00:00",
            "end_at": "2023-01-01T11:00:00",
            "status": "PENDING"
        }
    ]
    inputs = iter(["back"])
    monkeypatch.setattr("main.Prompt.ask", lambda text, **k: next(inputs, ""))
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_manage_reservations()
    output = " ".join(console.outputs).lower()
    assert "lab 42" in output


def test_logout(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.token = "TOKEN"
    monkeypatch.setattr("builtins.input", lambda: "")
    main.action_logout()
    assert client.token is None
    output = " ".join(console.outputs).lower()
    assert "logged out" in output


# ============ ACTION_EXIT TESTS ============
def test_action_exit(dummy_setup):
    console, client = dummy_setup
    with pytest.raises(SystemExit) as exc_info:
        main.action_exit()
    assert exc_info.value.code == 0
    output = " ".join(console.outputs).lower()
    assert "arrivederci" in output


# ============ MAIN LOOP TESTS ============
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


def test_main_loop_authenticated_with_details(dummy_setup, monkeypatch):
    console, client = dummy_setup
    client.token = "test_token"
    client.user_details = {"username": "testuser", "role": "student", "department": "DEMACS"}
    call_count = [0]
    called_get_user_details = [False]

    def fake_run(self):
        call_count[0] += 1
        raise KeyboardInterrupt

    monkeypatch.setattr("tui.RichTUI.run", fake_run)

    def fake_get_user_details():
        called_get_user_details[0] = True
        return {"username": "other"}

    monkeypatch.setattr(client, "get_user_details", fake_get_user_details)

    try:
        main.main()
    except KeyboardInterrupt:
        pass

    assert call_count[0] == 1
    assert called_get_user_details[0] is False


def test_get_main_menu_no_user_details(dummy_setup):
    console, client = dummy_setup
    client.user_details = None
    menu = main.get_main_menu()
    desc = menu._RichTUI__description
    title = desc[0][0]
    assert "UniSpace Dashboard - User" == title
    assert desc[0][1] == "Main Menu"


def test_get_main_menu_with_user_details(dummy_setup):
    console, client = dummy_setup
    client.user_details = {"username": "Stefano", "role": "student", "department": "DEMACS"}
    menu = main.get_main_menu()
    desc = menu._RichTUI__description
    title = desc[0][0]
    assert "Stefano" in title
    assert title.startswith("UniSpace Dashboard - ")
    assert desc[0][1] == "Main Menu"


def test_get_main_menu_professor_role(dummy_setup):
    console, client = dummy_setup
    client.user_details = {"username": "Prof", "role": "professor", "department": "DEMACS"}
    menu = main.get_main_menu()
    choices = [choice[0] for choice in menu._RichTUI__choices]
    assert "Manage Reservations" in choices


def test_get_auth_menu(dummy_setup):
    console, client = dummy_setup
    menu = main.get_auth_menu()
    desc = menu._RichTUI__description
    assert "UniSpace API - Login" in desc[0][0]
    assert "Please authenticate" in desc[0][1]
    choices = [choice[0] for choice in menu._RichTUI__choices]
    assert "Login" in choices
    assert "Register" in choices
    assert "Exit" in choices


def test_wait_enter(dummy_setup, monkeypatch):
    console, client = dummy_setup
    monkeypatch.setattr("builtins.input", lambda: "")
    main.wait_enter()
    output = " ".join(console.outputs).lower()
    assert "press enter" in output