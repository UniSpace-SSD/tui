import re
from rich.console import Console
from rich.prompt import Prompt
from typeguard import typechecked

console = Console(force_terminal=True)

@typechecked
def get_validated_input(prompt_text: str, regex_pattern: str, error_message: str) -> str:
    while True:
        value = Prompt.ask(prompt_text)
        if re.match(regex_pattern, value):
            return value
        console.print(f"[red]{error_message}[/red]")
