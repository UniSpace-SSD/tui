import datetime
import sys
from typing import Optional, List
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
    email = get_validated_input(
        "Email",
        r"^[\w\.-]+@[\w\.-]+\.\w{2,}$",
        "Invalid email format."
    )

    while True:
        password = Prompt.ask("Password", password=True)
        if len(password) < 8:
            console.print("[red]Password must be at least 8 characters long.[/red]")
            continue

        password_conf = Prompt.ask("Confirm Password", password=True)

        if password != password_conf:
            console.print("[red]Passwords do not match![/red]")
            continue

        break

    first_name = Prompt.ask("First Name")
    last_name = Prompt.ask("Last Name")

    while True:
        dob_str = get_validated_input(
            "Date of Birth (YYYY-MM-DD)",
            r"^\d{4}-\d{2}-\d{2}$",
            "Invalid format. Use YYYY-MM-DD"
        )
        try:
            dob_date = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            console.print("[red]Invalid date. Please insert a real date.[/red]")
            continue

        if dob_date > datetime.date.today():
            console.print("[red]Date of birth cannot be in the future.[/red]")
            continue

        dob = dob_str
        break

    valid_roles = ["student", "professor"]
    while True:
        role = Prompt.ask("Role", choices=valid_roles, default="student")
        role = role.lower().strip()
        if role in valid_roles:
            break
        console.print(f"[red]Invalid role. Choose one of: {', '.join(valid_roles)}[/red]")

    valid_depts = ["DEMACS", "DIMES", "DIMEG", "DIAM", "DICES"]
    dept = Prompt.ask("Department", choices=valid_depts)

    data = {
        "username": username,
        "email": email,
        "password1": password,
        "password2": password_conf,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": dob,
        "role": role,
        "department": dept,
    }

    res = client.register(data)
    if res['success']:
        console.print("[green]Registration successful! You can now login.[/green]")
    else:
        console.print(f"[red]Registration failed: {res.get('error')}[/red]")
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

        for k, v in user.items():
            if k == "is_superuser":
                if v:
                    table.add_row("is_superuser", str(v))
                else:
                    continue
            elif k == "pk":
                continue

            table.add_row(str(k), str(v))
        console.print(table)
    else:
        console.print("[red]Could not fetch profile.[/red]")
    wait_enter()


def action_list_buildings() -> None:
    buildings: List[Building] = client.get_buildings()
    table = Table(title="Buildings")
    table.add_column("ID", style="dim", max_width=8, overflow="ellipsis")
    table.add_column("Name", style="green")
    table.add_column("Department", style="cyan")
    table.add_column("Address", style="white")

    for b in buildings:
        building_id = b.get('id', '')
        short_id = building_id[:8] + "..." if len(building_id) > 8 else building_id
        table.add_row(short_id, b.get('name', 'N/A'), b.get('department', 'N/A'), b.get('address', 'N/A'))

    console.print(table)
    wait_enter()


def action_list_spaces() -> None:
    spaces: List[Space] = client.get_spaces()
    table = Table(title="Spaces")
    table.add_column("ID", style="dim", max_width=8, overflow="ellipsis")
    table.add_column("Building", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Department", style="magenta")
    table.add_column("Capacity", justify="right")

    for s in spaces:
        space_id = s.get('id', '')
        short_id = space_id[:8] + "..." if len(space_id) > 8 else space_id
        
        if isinstance(s.get('building'), dict):
            b_name = s['building'].get('name', 'N/A')
        else:
            b_name = str(s.get('building', 'Unknown'))
        
        table.add_row(
            short_id,
            b_name, 
            s.get('name', 'Unknown'), 
            s.get('type', 'Unknown'), 
            s.get('department', 'N/A'),  
            str(s.get('capacity', 0))
        )

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
            reservation_id = r.get('id', '')
            short_id = reservation_id[:8] + "..." if len(reservation_id) > 8 else reservation_id
            
            start = r.get('start_at', '').replace('T', ' ')[:16]
            end = r.get('end_at', '').replace('T', ' ')[:16]

            space_val = r.get('space')
            space_display = space_val
            if isinstance(space_val, dict):
                space_display = space_val.get('name', 'Unknown Space')

            table.add_row(
                short_id,
                str(space_display),
                f"{start} -> {end}",
                r.get('header', ''),
                r.get('status', 'unknown')
            )
        console.print(table)

        if Prompt.ask("Cancel a reservation?", choices=["y", "n"], default="n") == "y":
            # Filtra solo le prenotazioni PENDING dell'utente corrente
            pending_reservations = [r for r in res if r.get('status', '').upper() == 'PENDING']
            
            if not pending_reservations:
                console.print("[yellow]There are no reservations to cancel at the moment (no PENDING reservations).[/yellow]")
                wait_enter()
                return
            
            # Mostra solo gli ID delle prenotazioni PENDING
            console.print(f"\n[bold]Available PENDING reservation IDs for cancellation:[/bold]")
            for r in pending_reservations:
                reservation_id = r.get('id', '')
                start = r.get('start_at', '').replace('T', ' ')[:16]
                space_name = "Unknown"
                if isinstance(r.get('space'), dict):
                    space_name = r.get('space', {}).get('name', 'Unknown')
                
                console.print(f"  [cyan]{reservation_id}[/cyan] - Space: {space_name}, Time: {start}, Reason: {r.get('header', 'N/A')}")
            
            rid = Prompt.ask("\nEnter full Reservation ID to cancel")
            
            # Verifica che l'ID inserito sia tra quelli PENDING
            pending_ids = [r.get('id') for r in pending_reservations]
            if rid not in pending_ids:
                console.print("[red]Invalid ID or reservation is not in PENDING status.[/red]")
                wait_enter()
                return
            
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
        space_id = s.get('id', '')
        short_id = space_id[:8] + "..." if len(space_id) > 8 else space_id
        print(f"{i + 1}. [{short_id}] {s.get('name')} ({s.get('type')})")

    try:
        idx = int(Prompt.ask("Choice", default="1")) - 1
        if not (0 <= idx < len(spaces)):
            raise ValueError

        space_id = spaces[idx]['id']
        space_name = spaces[idx]['name']

        console.print(f"Selected: [green]{space_name}[/green] (ID: {space_id})")

        date = get_validated_input("Date (YYYY-MM-DD)", r"^\d{4}-\d{2}-\d{2}$", "Invalid format. Use YYYY-MM-DD")
        start = get_validated_input("Start Time (HH:MM)", r"^\d{2}:\d{2}$", "Invalid format. Use HH:MM")
        end = get_validated_input("End Time (HH:MM)", r"^\d{2}:\d{2}$", "Invalid format. Use HH:MM")
        header = Prompt.ask("Reason (Header)")

        res = client.create_reservation(space_id, date, start, end, header)
        if res['success']:
            console.print("[green]Reservation Created Successfully![/green]")
        else:
            console.print(f"[red]Error creating reservation: {res.get('error')}[/red]")

    except ValueError:
        console.print("[red]Invalid selection.[/red]")

    wait_enter()


def action_manage_reservations() -> None:
    res: List[Reservation] = client.get_all_reservations()
    if not res:
        console.print("[yellow]No reservations found.[/yellow]")
    else:
        table = Table(title="All Reservations")
        table.add_column("ID", style="dim", max_width=8, overflow="ellipsis")
        table.add_column("User", style="yellow")
        table.add_column("Space", style="green")
        table.add_column("Time", style="white")
        table.add_column("Status", style="bold")

        for r in res:
            reservation_id = r.get('id', '')
            short_id = reservation_id[:8] + "..." if len(reservation_id) > 8 else reservation_id
            
            start = r.get('start_at', '').replace('T', ' ')[:16]
            end = r.get('end_at', '').replace('T', ' ')[:16]

            space_val = r.get('space')
            space_display = space_val
            if isinstance(space_val, dict):
                space_display = space_val.get('name', 'Unknown Space')

            user_val = r.get('created_by')
            user_display = user_val
            if isinstance(user_val, dict):
                user_display = user_val.get('username', 'Unknown User')

            table.add_row(
                short_id,
                str(user_display),
                str(space_display),
                f"{start} -> {end}",
                r.get('status', 'unknown')
            )
        console.print(table)

        action = Prompt.ask("Action", choices=["confirm", "cancel", "back"], default="back")
        if action in ["confirm", "cancel"]:
            # Filtra solo le prenotazioni con status PENDING
            pending_reservations = [r for r in res if r.get('status', '').upper() == 'PENDING']
            
            if not pending_reservations:
                console.print(f"[yellow]There are no reservations to {action} at the moment (no PENDING reservations).[/yellow]")
                wait_enter()
                return
            
            # Mostra solo gli ID delle prenotazioni PENDING
            console.print(f"\n[bold]Available PENDING reservation IDs for {action}:[/bold]")
            for r in pending_reservations:
                reservation_id = r.get('id', '')
                start = r.get('start_at', '').replace('T', ' ')[:16]
                
                console.print(f"  [cyan]{reservation_id}[/cyan] - Time: {start}")
            
            rid = Prompt.ask(f"\nEnter full Reservation ID to {action}")
            
            # Verifica che l'ID inserito sia tra quelli PENDING
            pending_ids = [r.get('id') for r in pending_reservations]
            if rid not in pending_ids:
                console.print("[red]Invalid ID or reservation is not in PENDING status.[/red]")
                wait_enter()
                return
            
            if action == "confirm":
                if client.confirm_reservation(rid):
                    console.print("[green]Reservation confirmed.[/green]")
                else:
                    console.print("[red]Failed to confirm.[/red]")
            elif action == "cancel":
                if client.cancel_reservation(rid):
                    console.print("[green]Reservation cancelled.[/green]")
                else:
                    console.print("[red]Failed to cancel.[/red]")

    wait_enter()


def action_exit() -> None:
    console.print("[bold magenta]Arrivederci![/bold magenta]")
    sys.exit(0)


# --- Menu ---
def get_auth_menu() -> RichTUI:
    return (RichTUI.Builder()
            .set_description("UniSpace API - Login", "Please authenticate")
            .add_choice("Login", action_login)
            .add_choice("Register", action_register)
            .add_choice("Exit", action_exit)
            .build())


def get_main_menu() -> RichTUI:
    user_name = "User"
    if client.user_details:
        user_name = client.user_details.get('username', 'User')

    builder = (RichTUI.Builder()
               .set_description(f"UniSpace Dashboard - {user_name}", "Main Menu")
               .add_choice("My Profile", action_profile)
               .add_choice("My Reservations", action_my_reservations))

    role = client.user_details.get("role", "") if client.user_details else ""
    if role == "professor":
        builder.add_choice("Manage Reservations", action_manage_reservations)

    return (builder
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