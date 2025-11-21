import os


class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    
    # Session configuration
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # Flask-JWT-Extended configuration
    JWT_TOKEN_LOCATION = ["headers", "cookies"]  # Accept tokens from headers and cookies
    # JWT_ACCESS_TOKEN_EXPIRES will be set in init_jwt (don't set to None here)
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"  # Explicit cookie name
    JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_PATH = "/"  # Cookie available for all paths

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///gmflow.db",  # Default to SQLite for local development
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")
    
    # RabbitMQ configuration for Integration Events
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "commercial-management")
    
    # SMTP Email Configuration (Brevo)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp-relay.brevo.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("BREVO_SMTP_EMAIL", "")
    MAIL_PASSWORD = os.getenv("BREVO_SMTP_KEY", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@gmflow.com")
    APP_URL = os.getenv("APP_URL", "http://localhost:5000")
    
    # Stock Management Mode: 'simple' or 'advanced'
    # 'simple': Single site/warehouse, simplified interface (for small businesses)
    # 'advanced': Multi-site support, full features (for larger businesses)
    STOCK_MANAGEMENT_MODE = os.getenv("STOCK_MANAGEMENT_MODE", "simple").lower()  # Default to simple