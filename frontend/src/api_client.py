import requests
from typing import Optional, Dict, Any, Tuple

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.current_user: Optional[Dict[str, Any]] = None

    def set_token(self, token: str):
        self.token = token

    def clear_auth(self):
        self.token = None
        self.current_user = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.set_token(data["access_token"])
                if self.fetch_profile():
                    return True, ""
                return False, "Не удалось загрузить профиль пользователя."
            return False, "Неверное имя пользователя или пароль."
        except requests.ConnectionError:
            return False, "Не удалось подключиться к серверу. Проверьте, запущен ли backend."
        except requests.Timeout:
            return False, "Превышено время ожидания ответа от сервера."
        except requests.RequestException as e:
            return False, f"Ошибка сети: {str(e)}"

    def fetch_profile(self) -> bool:
        if not self.token:
            return False
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=self._get_headers(),
                timeout=5
            )
            if response.status_code == 200:
                self.current_user = response.json()
                return True
            self.clear_auth()
            return False
        except Exception:
            self.clear_auth()
            return False

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return requests.get(
            f"{self.base_url}{endpoint}",
            headers=self._get_headers(),
            params=params,
            timeout=5
        )

    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        return requests.post(
            f"{self.base_url}{endpoint}",
            headers=self._get_headers(),
            json=json_data,
            timeout=5
        )

    def delete(self, endpoint: str) -> requests.Response:
        return requests.delete(
            f"{self.base_url}{endpoint}",
            headers=self._get_headers(),
            timeout=5
        )

api_client = APIClient()
