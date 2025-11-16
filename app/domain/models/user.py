from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash

from ...infrastructure.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(50), nullable=False, default="clerk")
    locale = Column(String(5), nullable=False, default="fr")  # User's preferred language: 'fr' or 'ar'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)