from .db import Base, engine


def create_all() -> None:
    if engine is None:
        raise RuntimeError("Engine not initialized. Ensure app created DB before invoking.")
    Base.metadata.create_all(bind=engine)


def drop_all() -> None:
    if engine is None:
        raise RuntimeError("Engine not initialized. Ensure app created DB before invoking.")
    Base.metadata.drop_all(bind=engine)