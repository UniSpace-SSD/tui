from typing import TypedDict, Optional, List, Union

# Definizione Utente
class User(TypedDict):
    pk: int
    username: str
    email: str
    first_name: str
    last_name: str
    date_of_birth: str  # Formato YYYY-MM-DD
    role: str  # student o professor

# Definizione Edificio
class Building(TypedDict):
    id: int
    name: str
    address: str
    map_image: Optional[str]

# Definizione Spazio / Aula
class Space(TypedDict):
    id: str  # UUID
    name: str
    building: Building
    floor: int
    capacity: int
    type: str  # lab, classroom, ecc.
    equipment: List[str]
    is_active: bool

# Definizione Prenotazione
class Reservation(TypedDict):
    id: str  # UUID
    user: Union[int, User]  # ID utente o oggetto User completo
    space: Union[str, Space]  # ID spazio o oggetto Space completo
    start_at: str  # ISO 8601
    end_at: str  # ISO 8601
    header: str
    status: str  # active, cancelled, ecc.

# Risposta Generica API
class ApiResponse(TypedDict, total=False):
    success: bool
    data: Optional[Union[dict, list, str]]
    error: Optional[str]
