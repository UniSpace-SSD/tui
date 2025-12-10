from tui import RichTUI
from rich.console import Console
import io

def test_run_just_renders_once(monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(
        "tui.Console",
        lambda *args, **kwargs: Console(file=buf, force_terminal=False)
    )
    monkeypatch.setattr("tui.system", lambda x: None)

    def fake_ask(prompt, choices=None):
        raise KeyboardInterrupt

    monkeypatch.setattr("tui.IntPrompt.ask", fake_ask)

    tui = (
        RichTUI.Builder()
        .set_description("My Menu", "Sub")
        .add_choice("Opt 1", lambda: None)
        .build()
    )

    tui.run()

    output = buf.getvalue()
    assert "My Menu" in output
    assert "Opt 1" in output

def test_render_menu(monkeypatch):
    monkeypatch.setattr("tui.system", lambda x: None)

    buf = io.StringIO()

    monkeypatch.setattr(
        "tui.Console",
        lambda *args, **kwargs: Console(file=buf, force_terminal=False, width=120)
    )

    tui = (
        RichTUI.Builder()
        .set_description("MainMenu", "SelectOpt")
        .add_choice("Login", lambda: None)
        .build()
    )

    tui.render_menu()
    output = buf.getvalue()

    assert "MainMenu" in output
    assert "SelectOpt" in output
    assert "Login" in output


def test_run_executes_action(monkeypatch):
    monkeypatch.setattr("tui.system", lambda x: None)

    buf = io.StringIO()

    monkeypatch.setattr(
        "tui.Console",
        lambda *args, **kwargs: Console(file=buf, force_terminal=False)
    )

    inputs = [1] 

    def fake_ask(prompt, choices=None):
        if not inputs:
            raise KeyboardInterrupt 
        return inputs.pop(0)

    monkeypatch.setattr("tui.IntPrompt.ask", fake_ask)

    was_called = False

    def my_action():
        nonlocal was_called
        was_called = True

    tui = (
        RichTUI.Builder()
        .set_description("Menu", "Sub")
        .add_choice("Do It", my_action)
        .build()
    )

    tui.run()

    assert was_called is True


def test_invalid_choice(monkeypatch):
    monkeypatch.setattr("tui.system", lambda x: None)

    buf = io.StringIO()

    monkeypatch.setattr(
        "tui.Console",
        lambda *args, **kwargs: Console(file=buf, force_terminal=False)
    )

    inputs = [99, 1] 

    def fake_ask(prompt, choices=None):
        if not inputs:
            raise KeyboardInterrupt
        return inputs.pop(0)

    monkeypatch.setattr("tui.IntPrompt.ask", fake_ask)

    tui = (
        RichTUI.Builder()
        .set_description("Menu", "Sub")
        .add_choice("Opt", lambda: None)
        .build()
    )

    tui.run()
    output = buf.getvalue()

    assert "Invalid choice" in output

