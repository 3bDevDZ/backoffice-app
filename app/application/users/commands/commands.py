from app.application.common.cqrs import Command

class LoginCommand(Command):
    username: str
    password: str

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password