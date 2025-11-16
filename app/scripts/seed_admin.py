import os

from app import create_app
from app.infrastructure.db import get_session
from app.domain.models.user import User


def seed_admin() -> None:
    # Initialize app to set up database
    app = create_app()
    
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")

    with app.app_context():
        with get_session() as session:
            existing = session.query(User).filter(User.username == admin_username).first()
            if existing:
                print(f"Admin user '{admin_username}' already exists. Skipping seed.")
                return

            admin = User(username=admin_username, role="admin")
            admin.set_password(admin_password)
            session.add(admin)
            session.commit()
            print(f"[OK] Admin user '{admin_username}' created successfully with role 'admin'.")
            print(f"  Username: {admin_username}")
            print(f"  Password: {admin_password}")


if __name__ == "__main__":
    seed_admin()