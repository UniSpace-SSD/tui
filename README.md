# UniSpace TUI

Terminal user interface for **UniSpace**, an academic university-space reservation system developed for the **Secure Software Design** course at the University of Calabria (UniCal).

The TUI is a Python client for the UniSpace REST API and provides an alternative interface to the SvelteKit web application.

> **Project status:** completed academic project. This repository is kept as a portfolio/reference snapshot and is not actively maintained.

## Project ecosystem

UniSpace is split across three repositories:

- [`backend`](https://github.com/UniSpace-SSD/backend) — Django REST API
- [`web-frontend`](https://github.com/UniSpace-SSD/web-frontend) — SvelteKit web client
- [`tui`](https://github.com/UniSpace-SSD/tui) — this terminal client

## Features

The terminal client supports:

- user registration
- login and logout
- token-authenticated API requests
- profile display
- listing university buildings
- listing reservable spaces
- creating reservations
- viewing personal reservations
- cancelling pending reservations
- professor-specific reservation management
- confirming or cancelling eligible pending reservations

Registration supports the `student` and `professor` roles and the departments used by the UniSpace backend.

## Tech stack

- **Python 3.13**
- **Rich** for terminal rendering
- **Requests** for REST API communication
- **typeguard** for runtime type checking
- **valid8** for input validation
- **pytest / pytest-cov**
- **requests-mock**
- **Poetry**

The client currently targets:

```text
http://127.0.0.1:8000/api
```

so the UniSpace backend must be running locally.

## Getting started

### Prerequisites

- Python 3.13
- Poetry
- the UniSpace backend running on `127.0.0.1:8000`

### Install dependencies

```bash
poetry install
```

### Run the client

```bash
poetry run python main.py
```

The application starts with an authentication menu and, once logged in, exposes a role-aware UniSpace dashboard.

## Tests

```bash
poetry run pytest
```

Coverage support is available through `pytest-cov` and `.coveragerc`.

## Repository structure

```text
api_client.py   # REST API client and authentication token handling
main.py         # application flows and menus
models.py       # typed data structures used by the client
tui.py          # reusable Rich-based TUI builder
utils.py        # input/validation helpers
tests/          # automated tests
```

## How it communicates with the backend

`UniSpaceClient` keeps a `requests.Session`, stores the authentication token after login and adds it to subsequent requests:

```text
Authorization: Token <token>
```

The client interacts with backend endpoints for authentication, buildings, spaces and reservations.

## Role-aware workflow

After authentication, every user can access profile, reservation, building and space functionality.

Professor accounts additionally receive a reservation-management action that can be used to review eligible pending reservations and confirm or cancel them, according to the permissions enforced by the backend.

## Academic context

UniSpace was built as a two-person project for the **Secure Software Design** course at the **University of Calabria**. This client demonstrates that the backend API is independent from a single graphical interface and can also support a separate Python application.

The TUI additionally provided a compact environment for exercising API workflows, validation, authentication and authorization behaviour.

## Contributors

- [Ronnie2603](https://github.com/Ronnie2603)
- [Shadowz-git](https://github.com/shadowz-git)

See the [UniSpace-SSD organization](https://github.com/UniSpace-SSD) for the complete project.
