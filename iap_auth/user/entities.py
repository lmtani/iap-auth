from dataclasses import dataclass
from datetime import datetime


@dataclass
class Token:
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: str
    expires_at: float

    @staticmethod
    def from_dict(data: dict):
        at = data["expires_in"] + datetime.now().timestamp()
        return Token(**data, expires_at=at)

    def is_token_valid(self):
        if self.expires_at > datetime.now().timestamp():
            return True
        return False


@dataclass
class UserCredentials:
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str
    id_token: str

    @staticmethod
    def from_dict(data: dict):
        at = data["expires_in"] + datetime.now().timestamp()
        return Token(**data, expires_at=at)

    def is_token_valid(self):
        if self.expires_at > datetime.now().timestamp():
            return True
        return False
