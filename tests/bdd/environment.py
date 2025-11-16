"""Behave environment configuration."""
from behave import fixture, use_fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db import Base, init_db


def before_feature(context, feature):
    """Setup before each feature."""
    # Don't create database here - let before_scenario handle it
    # This ensures a clean database for each scenario
    pass


def before_scenario(context, scenario):
    """Clean up database before each scenario."""
    # Close existing session if it exists
    if hasattr(context, 'db_session'):
        try:
            context.db_session.close()
        except:
            pass
    
    # Recreate database completely for each scenario
    # Use a unique temporary file for each scenario to ensure complete isolation
    import app.infrastructure.db as db_module
    import uuid
    import tempfile
    import os
    
    # Create a unique temporary database file for this scenario
    temp_dir = tempfile.gettempdir()
    db_file = os.path.join(temp_dir, f"test_db_{uuid.uuid4().hex[:8]}.db")
    db_uri = f"sqlite:///{db_file}"
    
    # Remove file if it exists (shouldn't, but just in case)
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except:
            pass
    
    # Initialize database with the unique URI
    # This will create the engine and session factory
    init_db(db_uri)
    
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(db_module.engine)
    
    # Create all tables
    Base.metadata.create_all(db_module.engine)
    
    # Create new session
    context.db_session = db_module.SessionLocal()
    
    # Create Flask app AFTER database is initialized to ensure it uses the test database
    # This registers all handlers with the correct database
    from app import create_app
    # Temporarily override the database URI in config
    import os
    old_db_uri = os.environ.get('DATABASE_URL', None)
    os.environ['DATABASE_URL'] = db_uri
    try:
        context.app = create_app()
        # Override the database URI in app config to use test database
        context.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        # Re-initialize database with test URI (create_app() may have initialized with production DB)
        init_db(db_uri)
    finally:
        # Restore original DATABASE_URL if it existed
        if old_db_uri:
            os.environ['DATABASE_URL'] = old_db_uri
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
    
    # Store db_file for cleanup
    context._temp_db_file = db_file


def after_scenario(context, scenario):
    """Cleanup after each scenario."""
    # Close session
    if hasattr(context, 'db_session'):
        try:
            context.db_session.close()
        except:
            pass
    
    # Remove temporary database file
    if hasattr(context, '_temp_db_file'):
        import os
        try:
            if os.path.exists(context._temp_db_file):
                os.remove(context._temp_db_file)
        except:
            pass


def after_feature(context, feature):
    """Cleanup after each feature."""
    if hasattr(context, 'db_session'):
        try:
        context.db_session.close()
        except:
            pass

