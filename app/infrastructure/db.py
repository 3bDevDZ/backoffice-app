from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from ..application.common.domain_event_dispatcher import domain_event_dispatcher


class Base(DeclarativeBase):
    pass


engine = None
SessionLocal = None
_domain_events_listener_registered = False


def _dispatch_domain_events(session):
    """Dispatch domain events after transaction commit."""
    # Collect domain events from all tracked aggregates
    domain_events = []
    for obj in session.identity_map.values():
        if hasattr(obj, 'get_domain_events'):
            events = obj.get_domain_events()
            domain_events.extend(events)
            obj.clear_domain_events()
    
    # Dispatch all events (only if we have events to avoid unnecessary processing)
    if domain_events:
        domain_event_dispatcher.dispatch_all(domain_events)


def init_db(db_uri: str) -> None:
    global engine, SessionLocal, _domain_events_listener_registered
    engine = create_engine(db_uri, pool_pre_ping=True, echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    
    # Register event listener to dispatch domain events after commit
    # Only register once globally to avoid duplicate event dispatching
    # The listener is registered at the Session class level, so it applies to all sessions
    if not _domain_events_listener_registered:
        event.listens_for(Session, "after_commit")(_dispatch_domain_events)
        _domain_events_listener_registered = True


@contextmanager
def get_session() -> Iterator[Session]:
    """
    Get a database session with automatic transaction management.
    Domain events are dispatched after commit.
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    session = SessionLocal()
    try:
        yield session
        session.commit()
        # Domain events are dispatched via the after_commit event listener
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
