import re
import requests
from typing import Optional, List, Dict, Any
from typeguard import typechecked
from models import User, Building, Space, Reservation, ApiResponse

@typechecked
class UniSpaceClient:
    BASE_URL = "http://0.0.0.0:8000/api"

    def __init__(self):
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.user_details: Optional[User] = None

    def set_token(self, token: str):
        self.token = token
        self.session.headers.update({"Authorization": f"Token {token}"})

    def login(self, username: str, password: str) -> bool:
        try:
            headers: Dict[str, str] = {}

            response = self.session.post(
                f"{self.BASE_URL}/auth/login/",
                json={"username": username, "password": password},
                headers=headers,
            )

            if response.status_code in (200, 201):
                data = response.json()
                if "key" in data:
                    self.set_token(data["key"])
                    return True
            return False
        except requests.RequestException:
            return False

    def logout(self):
        if self.token:
            try:
                self.session.post(f"{self.BASE_URL}/auth/logout/")
            except requests.RequestException:
                pass
        self.token = None
        self.session.headers.pop("Authorization", None)
        self.user_details = None

    def get_user_details(self) -> Optional[User]:
        if not self.token:
            return None
        try:
            response = self.session.get(f"{self.BASE_URL}/auth/user/")
            if response.status_code == 200:
                self.user_details = response.json()
                return self.user_details
        except requests.RequestException:
            pass
        return None

    def register(self, data: Dict[str, Any]) -> bool:
        try:
            headers: Dict[str, str] = {}

            response = self.session.post(
                f"{self.BASE_URL}/auth/registration/",
                json=data,
                headers=headers,
            )
            
            return response.status_code == 201
        except requests.RequestException:
            return False

    def get_buildings(self) -> List[Building]:
        try:
            response = self.session.get(f"{self.BASE_URL}/buildings/")
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return []

    def get_spaces(self) -> List[Space]:
        try:
            response = self.session.get(f"{self.BASE_URL}/spaces/")
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return []

    def get_space(self, space_id: str) -> Optional[Space]:
        try:
            response = self.session.get(f"{self.BASE_URL}/spaces/{space_id}/")
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def get_my_reservations(self) -> List[Reservation]:
        try:
            response = self.session.get(f"{self.BASE_URL}/reservations/me/")
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return []

    def create_reservation(
        self,
        space_id: str,
        date: str,
        start_time: str,
        end_time: str,
        header: str
    ) -> ApiResponse:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
        
        if not re.match(r"^\d{2}:\d{2}$", start_time) or not re.match(r"^\d{2}:\d{2}$", end_time):
            return {"success": False, "error": "Invalid time format. Use HH:MM"}

        start_at = f"{date}T{start_time}:00"
        end_at = f"{date}T{end_time}:00"

        payload = {
            "space": space_id,
            "start_at": start_at,
            "end_at": end_at,
            "header": header
        }

        try:
            response = self.session.post(f"{self.BASE_URL}/reservations/", json=payload)
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def cancel_reservation(self, reservation_id: str) -> bool:
        try:
            response = self.session.patch(
                f"{self.BASE_URL}/reservations/{reservation_id}/cancel/",
                json={},
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
