from typing import TypedDict, Optional, List, Union, NotRequired
from typing_extensions import NotRequired  # Per compatibilità con Python < 3.11

# Definizione Utente
class User(TypedDict):
    pk: int
    username: str
    email: str
    first_name: str
    last_name: str
    date_of_birth: NotRequired[str]  # Formato YYYY-MM-DD, può essere null
    role: str 
    department: str  
    is_superuser: bool

# Definizione Edificio
class Building(TypedDict):
    id: str  # UUID nel backend
    name: str
    address: str
    department: str

# Definizione Spazio / Aula
class Space(TypedDict, total=False):
    id: str  # UUID
    name: str
    building: Building
    floor: int
    capacity: int
    type: str  # room, lab, auditorium, meeting_room, library
    department: str
    equipments: NotRequired[List[str]]  

# Definizione Prenotazione
class Reservation(TypedDict):
    id: str  # UUID
    created_by: Union[int, User]  
    space: Union[str, Space]  # ID spazio o oggetto Space completo
    start_at: str  # ISO 8601
    end_at: str  # ISO 8601
    header: str
    status: str  # PENDING, CONFIRMED, CANCELLED
    # Campi aggiuntivi dal backend
    created_at: NotRequired[str]
    updated_at: NotRequired[str]
    cancelled_at: NotRequired[Optional[str]]

# Definizione Equipment
class Equipment(TypedDict):
    id: int
    name: str
    description: NotRequired[str]

# Risposta Generica API
class ApiResponse(TypedDict, total=False):
    success: bool
    data: NotRequired[Union[dict, list, str]]
    error: NotRequired[str]