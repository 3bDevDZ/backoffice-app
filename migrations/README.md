Alembic Migrations
===================

This directory contains database migration scripts managed by Alembic.

Quickstart
----------

1. Ensure `DATABASE_URL` is set (or uses project default):
   `postgresql+psycopg2://tms_user:tms_password@db:5432/gsflowdb`

2. Create a new revision (autogenerate):
   `alembic revision -m "message" --autogenerate`

3. Apply migrations:
   `alembic upgrade head`

Notes
-----

- The migration env uses the app's SQLAlchemy `Base.metadata` for autogenerate.
- Keep migrations deterministic; prefer explicit changes over autogenerate deltas when needed.