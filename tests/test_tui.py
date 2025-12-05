from tui import RichTUI
from rich.console import Console
import io

def test_builder_pattern():
    def no_op(): pass
    tui = (RichTUI.Builder()
           .set_title("My Menu")
           .set_subtitle("Sub")
           .add_choice("Opt 1", no_op)
           .build())
    assert tui.title == "My Menu"
    assert tui.subtitle == "Sub"
    assert len(tui._choices) == 1
    assert tui._choices[0][0] == "Opt 1"

def test_render_menu(monkeypatch):
    monkeypatch.setattr("tui.system", lambda x: None)
    tui = RichTUI(title="MainMenu", subtitle="SelectOpt")
    tui.add_choice("Login", lambda: None)
    buf = io.StringIO()
    tui.console = Console(file=buf, force_terminal=False, width=120)
    tui.render_menu()
    output = buf.getvalue()
    assert "MainMenu" in output
    assert "SelectOpt" in output
    assert "Login" in output

def test_run_executes_action(monkeypatch):
    monkeypatch.setattr("tui.system", lambda x: None)
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
    tui = RichTUI()
    tui.add_choice("Do It", my_action)
    tui.console = Console(file=io.StringIO(), force_terminal=False)
    tui.run()
    assert was_called is True

def test_invalid_choice(monkeypatch):
    monkeypatch.setattr("tui.system", lambda x: None)
    inputs = [99, 1]
    def fake_ask(prompt, choices=None):
        if not inputs:
            raise KeyboardInterrupt
        return inputs.pop(0)
    monkeypatch.setattr("tui.IntPrompt.ask", fake_ask)
    tui = RichTUI()
    tui.add_choice("Opt", lambda: None)
    buf = io.StringIO()
    tui.console = Console(file=buf, force_terminal=False)
    tui.run()
    output = buf.getvalue()
    assert "Invalid choice" in output
