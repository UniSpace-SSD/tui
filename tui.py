from dataclasses import InitVar, dataclass, field
from typing import Any, Callable, Optional, Tuple, List
from typeguard import typechecked
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.align import Align

from valid8 import validate

from os import system, name

Action = Callable[[], None]
Choice = Tuple[str, Action]
Description = Tuple[str, str]


@typechecked
@dataclass(frozen=True)
class RichTUI:
    create_key: InitVar[Any] = field(default=None)
    __choices: List[Choice] = field(default_factory=list)
    __description: List[Description] = field(default_factory=list)
    console: Console = field(default_factory=lambda: Console(force_terminal=True))

    def __post_init__(self, create_key: Any):
        validate("key", create_key, custom=RichTUI.Builder.is_valid_key)

    def add_choice(self, description: str, function: Action) -> "RichTUI":
        self.__choices.append((description, function))
        return self
    
    def add_description(self, title: str, subtitle: str) -> "RichTUI":
        self.__description.append((title, subtitle))
        return self

    def render_menu(self) -> None:
        system('cls' if name == 'nt' else 'clear')

        title = self.__description[0][0]
        subtitle = self.__description[0][1] 

        self.console.print(Panel(Align.center(f"[bold magenta]{title}[/bold magenta]"), style="blue"))

        table = Table(show_header=False, box=None)
        table.add_column("Index", style="cyan", justify="right")
        table.add_column("Description", style="white")

        for i, (desc, _) in enumerate(self.__choices):
            table.add_row(str(i + 1), desc)

        self.console.print(Panel(table, title=subtitle, border_style="green"))

    def run(self) -> None:
        self.render_menu()

        try:
            choice_idx = IntPrompt.ask(
                "Choice",
                choices=[str(i + 1) for i in range(len(self.__choices))]
            )
            selected_idx = choice_idx - 1

            if 0 <= selected_idx < len(self.__choices):
                _, action = self.__choices[selected_idx]
                action()
            else:
                self.console.print("[red]Invalid choice![/red]")
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Exiting...[/yellow]")
            return

    @dataclass
    class Builder:
        __create_key: object = object()
        __tui: Optional['RichTUI'] = None

        def __init__(self):
            self.__tui = RichTUI(self.__create_key)

        @staticmethod
        def is_valid_key(key: Any):
            return key == RichTUI.Builder.__create_key

        def set_description(self, title: str, subtitle: str) -> "RichTUI.Builder":
            self.__tui.add_description(title, subtitle)
            return self

        def add_choice(self, description: str, function: Action) -> "RichTUI.Builder":
            self.__tui.add_choice(description, function)
            return self

        def build(self) -> 'RichTUI':
            tui = self.__tui
            self.__tui = None
            return tui
