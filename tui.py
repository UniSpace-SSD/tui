from dataclasses import dataclass, field
from typing import Callable, Tuple, List
from typeguard import typechecked
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.align import Align

from os import system, name

Action = Callable[[], None]
Choice = Tuple[str, Action]


@typechecked
@dataclass
class RichTUI:
    _choices: List[Choice] = field(default_factory=list)
    console: Console = field(default_factory=lambda: Console(force_terminal=True))
    title: str = "UniSpace TUI"
    subtitle: str = "Select an option"

    def add_choice(self, description: str, function: Action) -> "RichTUI":
        self._choices.append((description, function))
        return self

    def render_menu(self) -> None:
        system('cls' if name == 'nt' else 'clear')

        self.console.print(Panel(Align.center(f"[bold magenta]{self.title}[/bold magenta]"), style="blue"))

        table = Table(show_header=False, box=None)
        table.add_column("Index", style="cyan", justify="right")
        table.add_column("Description", style="white")

        for i, (desc, _) in enumerate(self._choices):
            table.add_row(str(i + 1), desc)

        self.console.print(Panel(table, title=self.subtitle, border_style="green"))

    def run(self) -> None:
        while True:
            self.render_menu()

            try:
                choice_idx = IntPrompt.ask("Choice", choices=[str(i + 1) for i in range(len(self._choices))])
                selected_idx = choice_idx - 1

                if 0 <= selected_idx < len(self._choices):
                    _, action = self._choices[selected_idx]
                    action()
                else:
                    self.console.print("[red]Invalid choice![/red]")
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Exiting...[/yellow]")
                return

    @dataclass
    class Builder:
        _tui: 'RichTUI' = field(default_factory=lambda: RichTUI())

        def set_title(self, title: str) -> "RichTUI.Builder":
            self._tui.title = title
            return self

        def set_subtitle(self, subtitle: str) -> "RichTUI.Builder":
            self._tui.subtitle = subtitle
            return self

        def add_choice(self, description: str, function: Action) -> "RichTUI.Builder":
            self._tui.add_choice(description, function)
            return self

        def build(self) -> 'RichTUI':
            return self._tui
