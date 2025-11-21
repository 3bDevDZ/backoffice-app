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
    # Access events while objects are still bound to the session
    domain_events = []
    # Make a copy of identity_map values to avoid iteration issues
    # and to ensure we access objects while they're still bound
    try:
        # Check if session is still active
        if not session.is_active:
            return
        
        # Get all tracked objects before accessing their attributes
        # This ensures we're working with objects that are still bound
        tracked_objects = []
        try:
            tracked_objects = list(session.identity_map.values())
        except (RuntimeError, AttributeError):
            # Session might be closed, skip event dispatch
            return
        
        for obj in tracked_objects:
            # Only process objects that are AggregateRoot (have domain events)
            # Check for _domain_events attribute which is specific to AggregateRoot
            # Location doesn't inherit from AggregateRoot, so it won't have _domain_events
            if not hasattr(obj, '_domain_events'):
                continue
                
            if hasattr(obj, 'get_domain_events'):
                try:
                    events = obj.get_domain_events()
                    if events:
                        domain_events.extend(events)
                        obj.clear_domain_events()
                except (AttributeError, RuntimeError) as e:
                    # If object is detached or error occurs, skip it
                    # This can happen if the object was expunged before commit
                    import logging
                    logging.debug(f"Skipping domain events for {type(obj).__name__}: {e}")
                    pass
    except (RuntimeError, AttributeError):
        # Session might be closed or object detached, skip event dispatch
        pass
    
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
        # The listener runs while the session is still open, so objects are still bound
        # After commit, objects remain in the session until it's closed
    except Exception:
        session.rollback()
        raise
    finally:
        # Close session after events are dispatched
        # Objects will be detached when session closes
        session.close()
