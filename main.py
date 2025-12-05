import sys
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from api_client import UniSpaceClient
from tui import RichTUI
from models import User, Building, Space, Reservation
from utils import get_validated_input

client = UniSpaceClient()
console = Console(force_terminal=True)


def wait_enter() -> None:
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


# --- Actions ---
def action_login() -> None:
    console.print("\n[bold]Login[/bold]")
    username = Prompt.ask("Username")
    password = Prompt.ask("Password", password=True)

    if client.login(username, password):
        console.print(f"[green]Welcome back, {username}![/green]")
    else:
        console.print("[red]Login failed. Check your credentials.[/red]")
    wait_enter()


def action_register() -> None:
    console.print("\n[bold]Register User[/bold]")
    username = Prompt.ask("Username")
    email = get_validated_input("Email", r"^[\w\.-]+@[\w\.-]+\.\w+$", "Invalid email format.")
    password = Prompt.ask("Password", password=True)
    password_conf = Prompt.ask("Confirm Password", password=True)
    
    if password != password_conf:
        console.print("[red]Passwords do not match![/red]")
        wait_enter()
        return

    first_name = Prompt.ask("First Name")
    last_name = Prompt.ask("Last Name")
    dob = get_validated_input("Date of Birth (YYYY-MM-DD)", r"^\d{4}-\d{2}-\d{2}$", "Invalid format. Use YYYY-MM-DD")
    role = Prompt.ask("Role", choices=["student", "professor"], default="student")

    data = {
        "username": username, "email": email, "password1": password, "password2": password_conf,
        "first_name": first_name, "last_name": last_name, "date_of_birth": dob, "role": role
    }

    if client.register(data):
        console.print("[green]Registration successful! You can now login.[/green]")
    else:
        console.print("[red]Registration failed.[/red]")
    wait_enter()


def action_logout() -> None:
    client.logout()
    console.print("[yellow]Logged out.[/yellow]")
    wait_enter()


def action_profile() -> None:
    user: Optional[User] = client.get_user_details()
    if user:
        table = Table(title="User Profile", show_header=True)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        # TypedDict doesn't support .items() like a dict at runtime reliably if it's just a structural type,
        # but in Python 3.9+ it behaves like a dict. We cast for safety or access directly.
        # Here we just iterate because we know the structure.
        for k, v in user.items():
            table.add_row(str(k), str(v))
        console.print(table)
    else:
        console.print("[red]Could not fetch profile.[/red]")
    wait_enter()


def action_list_buildings() -> None:
    buildings: List[Building] = client.get_buildings()
    table = Table(title="Buildings")
    table.add_column("Name", style="green")
    table.add_column("Address", style="white")

    for b in buildings:
        table.add_row(b.get('name', 'N/A'), b.get('address', 'N/A'))

    console.print(table)
    wait_enter()


def action_list_spaces() -> None:
    spaces: List[Space] = client.get_spaces()
    table = Table(title="Spaces")
    table.add_column("Building", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Capacity", justify="right")

    for s in spaces:
        # Building might be an ID or an object depending on API depth, but assuming object based on previous code
        # type hint says Space -> building: Building
        b_name = s['building'].get('name', 'N/A') if isinstance(s.get('building'), dict) else str(s.get('building'))
        table.add_row(b_name, s.get('name', 'Unknown'), s.get('type', 'Unknown'), str(s.get('capacity', 0)))

    console.print(table)
    wait_enter()


def action_my_reservations() -> None:
    res: List[Reservation] = client.get_my_reservations()
    if not res:
        console.print("[yellow]No reservations found.[/yellow]")
    else:
        table = Table(title="My Reservations")
        table.add_column("ID", style="dim", max_width=8, overflow="ellipsis")
        table.add_column("Space", style="green")
        table.add_column("Time", style="white")
        table.add_column("Header", style="italic")
        table.add_column("Status", style="bold")

        for r in res:
            start = r.get('start_at', '').replace('T', ' ')[:16]
            end = r.get('end_at', '').replace('T', ' ')[:16]
            
            # handle Space union type (str or dict)
            space_val = r.get('space')
            space_display = space_val
            if isinstance(space_val, dict):
                space_display = space_val.get('name', 'Unknown Space')

            table.add_row(
                r.get('id', ''),
                str(space_display),
                f"{start} -> {end}",
                r.get('header', ''),
                r.get('status', 'unknown')
            )
        console.print(table)

        if Prompt.ask("Cancel a reservation?", choices=["y", "n"], default="n") == "y":
            rid = Prompt.ask("Enter Reservation ID to cancel")
            if client.cancel_reservation(rid):
                console.print("[green]Reservation cancelled.[/green]")
            else:
                console.print("[red]Failed to cancel.[/red]")

    wait_enter()


def action_create_reservation() -> None:
    spaces: List[Space] = client.get_spaces()
    if not spaces:
        console.print("[red]No spaces available.[/red]")
        wait_enter()
        return

    console.print("[bold]Select a Space:[/bold]")
    for i, s in enumerate(spaces):
        print(f"{i + 1}. {s.get('name')} ({s.get('type')})")

    try:
        idx = int(Prompt.ask("Choice", default="1")) - 1
        if not (0 <= idx < len(spaces)):
            raise ValueError

        space_id = spaces[idx]['id']
        space_name = spaces[idx]['name']

        console.print(f"Selected: [green]{space_name}[/green]")

        date = get_validated_input("Date (YYYY-MM-DD)", r"^\d{4}-\d{2}-\d{2}$", "Invalid format. Use YYYY-MM-DD")
        start = get_validated_input("Start Time (HH:MM)", r"^\d{2}:\d{2}$", "Invalid format. Use HH:MM")
        end = get_validated_input("End Time (HH:MM)", r"^\d{2}:\d{2}$", "Invalid format. Use HH:MM")
        header = Prompt.ask("Reason (Header)")

        # Client now validates internally too, but doing it here prevents bad requests
        res = client.create_reservation(space_id, date, start, end, header)
        if res['success']:
            console.print("[green]Reservation Created Successfully![/green]")
        else:
            console.print(f"[red]Error creating reservation: {res.get('error')}[/red]")

    except ValueError:
        console.print("[red]Invalid selection.[/red]")

    wait_enter()


def action_exit() -> None:
    console.print("[bold magenta]Arrivederci![/bold magenta]")
    sys.exit(0)


# --- Menu ---
def get_auth_menu() -> RichTUI:
    return (RichTUI.Builder()
            .set_title("UniSpace API - Login")
            .set_subtitle("Please authenticate")
            .add_choice("Login", action_login)
            .add_choice("Register", action_register)
            .add_choice("Exit", action_exit)
            .build())


def get_main_menu() -> RichTUI:
    user_name = "User"
    if client.user_details:
        user_name = client.user_details.get('username', 'User')
        
    return (RichTUI.Builder()
            .set_title(f"UniSpace Dashboard - {user_name}")
            .set_subtitle("Main Menu")
            .add_choice("My Profile", action_profile)
            .add_choice("My Reservations", action_my_reservations)
            .add_choice("New Reservation", action_create_reservation)
            .add_choice("List Buildings", action_list_buildings)
            .add_choice("List Spaces", action_list_spaces)
            .add_choice("Logout", action_logout)
            .add_choice("Exit", action_exit)
            .build())


def main() -> None:
    while True:
        # Se loggato
        if client.token:
            if not client.user_details:
                client.get_user_details()
            menu = get_main_menu()
            menu.run()
        else:
            menu = get_auth_menu()
            menu.run()


if __name__ == "__main__":
    main()

