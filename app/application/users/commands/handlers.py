from app.application.common.cqrs import CommandHandler
from app.domain.models.user import User
from app.security.auth import issue_token
from .commands import LoginCommand
from ..queries.user_dto import UserDTO
from app.infrastructure.db import get_session

class LoginCommandHandler(CommandHandler):
    def handle(self, command: LoginCommand) -> UserDTO:
        with get_session() as session:
            user = session.query(User).filter_by(username=command.username).one_or_none()
            if user and user.check_password(command.password):
                token = issue_token(user)
                return UserDTO(
                    id=user.id,
                    username=user.username,
                    role=user.role,
                    token=token
                )
            return None