from flask_jwt_extended import JWTManager, create_access_token, get_jwt
from datetime import timedelta
from typing import Optional

from ..infrastructure.db import get_session
from ..domain.models.user import User


jwt: Optional[JWTManager] = None


def init_jwt(app) -> JWTManager:
    global jwt
    jwt = JWTManager(app)
    
    # Set JWT configuration - override defaults if needed
    if "JWT_ACCESS_TOKEN_EXPIRES" not in app.config or app.config.get("JWT_ACCESS_TOKEN_EXPIRES") is None:
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)
    
    # Ensure other required JWT configs are set
    app.config.setdefault("JWT_TOKEN_LOCATION", ["headers", "cookies"])
    app.config.setdefault("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
    app.config.setdefault("JWT_COOKIE_SECURE", False)
    app.config.setdefault("JWT_COOKIE_HTTPONLY", True)
    app.config.setdefault("JWT_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("JWT_COOKIE_PATH", "/")
    
    return jwt


def authenticate(username: str, password: str) -> Optional[User]:
    with get_session() as db:
        user = db.query(User).filter_by(username=username).one_or_none()
        if user and user.check_password(password):
            return user
        return None


def issue_token(user: User) -> str:
    claims = {"roles": [user.role], "username": user.username}
    return create_access_token(identity=str(user.id), additional_claims=claims)