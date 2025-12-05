import pytest
from utils import get_validated_input

def test_get_validated_input_success(monkeypatch):
    monkeypatch.setattr("utils.Prompt.ask", lambda text: "valid@email.com")
    monkeypatch.setattr("utils.console.print", lambda *args, **kwargs: None)
    result = get_validated_input("Email", r".+@.+", "Invalid email")
    assert result == "valid@email.com"

def test_get_validated_input_retry(monkeypatch):
    inputs = ["bad", "good@email.com"]
    monkeypatch.setattr("utils.Prompt.ask", lambda text: inputs.pop(0))
    monkeypatch.setattr("utils.console.print", lambda *args, **kwargs: None)
    result = get_validated_input("Email", r".+@.+", "Invalid email")
    assert result == "good@email.com"
