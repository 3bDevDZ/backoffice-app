from dataclasses import dataclass

@dataclass
class UserDTO:
    id: int
    username: str
    role: str
    token: str