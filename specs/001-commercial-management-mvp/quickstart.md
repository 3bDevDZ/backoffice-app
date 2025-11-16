# Quick Start Guide: Commercial Management MVP

**Date**: 2025-01-27  
**Feature**: Commercial Management MVP System

## Overview

This guide provides step-by-step instructions to get started with the Commercial Management MVP implementation using Flask.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis (for Celery tasks)
- Git

## Setup Steps

### 1. Clone and Navigate to Project

```bash
cd /path/to/gmflow
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Add Flask-Babel to requirements.txt for i18n support:
```
flask-babel>=4.0.0
```

### 4. Configure Environment

Create `.env` file in project root:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/gmflow_db
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 5. Initialize Database

```bash
# Create database
createdb gmflow_db

# Run migrations
alembic upgrade head
```

### 6. Initialize i18n Translations

```bash
# Extract translatable strings
flask babel extract -F babel.cfg -k _l -o messages.pot .

# Initialize French translations
flask babel init -i messages.pot -d app/translations -l fr

# Initialize Arabic translations
flask babel init -i messages.pot -d app/translations -l ar

# Compile translations
flask babel compile -d app/translations
```

### 7. Seed Initial Data (Optional)

```bash
python app/scripts/seed_admin.py
```

### 8. Run Development Server

```bash
flask run
```

Server will start on `http://localhost:5000`

### 9. Start Celery Worker (for background tasks)

```bash
celery -A app.celery worker --loglevel=info
```

## Project Structure Overview

```
app/
├── api/              # REST API blueprints (JSON endpoints for AJAX)
├── routes/           # Frontend route handlers (template rendering)
├── templates/        # Jinja2 templates (converted from /design HTML files)
├── static/           # Static files (CSS, JS, images)
├── application/      # CQRS layer (commands/queries/handlers)
├── domain/           # Domain models with business logic
├── infrastructure/   # Database, external services
├── security/         # Authentication, RBAC
└── services/         # Domain services

migrations/           # Alembic database migrations
tests/                # Test suites
design/               # Original design HTML files (reference)
```

## Development Workflow

### Adding a New Feature Module

1. **Create Domain Model** (`app/domain/models/`)
   - Define SQLAlchemy model
   - Add business logic methods
   - Add validation rules

2. **Create Application Layer** (`app/application/{module}/`)
   - Commands: `commands/commands.py`, `commands/handlers.py`
   - Queries: `queries/queries.py`, `queries/handlers.py`
   - DTOs: `queries/{module}_dto.py`

3. **Create Frontend Routes** (`app/routes/{module}_routes.py`)
   - Flask blueprint for template rendering
   - Route handlers that render Jinja2 templates
   - Pass data to templates via context
   - Handle form submissions (POST)

4. **Create Templates** (`app/templates/{module}/`)
   - Convert design HTML to Jinja2 template
   - Extend base.html
   - Use Flask-Babel for translations
   - Add RTL support for Arabic

5. **Create API Endpoints** (`app/api/{module}.py`)
   - Flask blueprint for REST API
   - Register routes
   - Add RBAC decorators
   - Use mediator to dispatch commands/queries
   - Return JSON responses

6. **Create Database Migration**
   ```bash
   alembic revision --autogenerate -m "Add {module} tables"
   alembic upgrade head
   ```

7. **Write Tests**
   - Unit tests: domain models, handlers
   - Integration tests: API endpoints, template rendering

### Example: Adding Stock Module

1. **Domain Model** (`app/domain/models/stock.py`):
```python
from app.infrastructure.db import Base
from sqlalchemy import Column, Integer, Numeric, ForeignKey

class StockItem(Base):
    __tablename__ = "stock_items"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    physical_quantity = Column(Numeric(12, 3), nullable=False, default=0)
    reserved_quantity = Column(Numeric(12, 3), nullable=False, default=0)
    
    def reserve(self, quantity):
        # Business logic here
        pass
```

2. **Command** (`app/application/stock/commands/commands.py`):
```python
from app.application.common.cqrs import Command

class CreateStockMovementCommand(Command):
    def __init__(self, product_id, type, quantity, location_from_id=None, location_to_id=None):
        self.product_id = product_id
        self.type = type
        self.quantity = quantity
        self.location_from_id = location_from_id
        self.location_to_id = location_to_id
```

3. **Handler** (`app/application/stock/commands/handlers.py`):
```python
from app.application.common.cqrs import CommandHandler
from app.domain.models.stock import StockMovement
from app.infrastructure.db import get_session

class CreateStockMovementHandler(CommandHandler):
    def handle(self, command):
        with get_session() as session:
            movement = StockMovement.create(...)
            session.add(movement)
            session.commit()
            return movement
```

4. **API Endpoint** (`app/api/stock.py`):
```python
from flask import Blueprint, jsonify, request
from app.application.common.mediator import mediator
from app.application.stock.commands.commands import CreateStockMovementCommand

stock_bp = Blueprint("stock", __name__)

@stock_bp.post("/movements")
@require_roles("admin", "magasinier")
def create_movement():
    data = request.get_json()
    command = CreateStockMovementCommand(**data)
    movement = mediator.dispatch(command)
    return jsonify(movement.__dict__), 201
```

5. **Frontend Route** (`app/routes/stock_routes.py`):
```python
from flask import Blueprint, render_template
from flask_babel import get_locale
from app.application.common.mediator import mediator
from app.application.stock.queries.queries import GetStockLevelsQuery
from app.security.rbac import require_roles

stock_routes = Blueprint('stock', __name__)

@stock_routes.route('/stock')
@require_roles('admin', 'magasinier')
def index():
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    stock_levels = mediator.dispatch(GetStockLevelsQuery())
    return render_template('stock/index.html',
                         stock_levels=stock_levels,
                         locale=locale,
                         direction=direction)
```

6. **Template** (`app/templates/stock/index.html`):
```jinja2
{% extends "base.html" %}

{% block title %}{{ _('Stock Management') }} - CommerceFlow{% endblock %}

{% block content %}
<div class="p-6">
    <h1 class="text-2xl font-bold text-gray-900">{{ _('Stock Management') }}</h1>
    <!-- Stock content from design/07-stock.html -->
</div>
{% endblock %}
```

7. **Register Blueprints** (`app/__init__.py`):
```python
# API blueprint
from app.api.stock import stock_bp
app.register_blueprint(stock_bp, url_prefix="/api/stock")

# Frontend routes blueprint
from app.routes.stock_routes import stock_routes
app.register_blueprint(stock_routes)
```

## Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/domain/test_product.py
```

### Test Structure

```
tests/
├── unit/
│   ├── domain/          # Domain model tests
│   ├── application/     # Handler tests
│   └── services/        # Service tests
├── integration/
│   ├── api/             # API endpoint tests
│   └── workflows/       # End-to-end workflow tests
└── fixtures/            # Test data factories
```

## Common Tasks

### Creating a Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Description"

# Review generated migration
# Edit if needed

# Apply migration
alembic upgrade head
```

### Running Celery Tasks

```bash
# Start worker
celery -A app.celery worker --loglevel=info

# Start beat scheduler (for periodic tasks)
celery -A app.celery beat --loglevel=info
```

### API Testing with curl

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'

# Get products (use JWT token from login)
curl -X GET http://localhost:5000/api/products \
  -H "Authorization: Bearer <token>"
```

## Internationalization (i18n)

### Setting Up Translations

1. **Extract Strings**:
   ```bash
   flask babel extract -F babel.cfg -k _l -o messages.pot .
   ```

2. **Update Translation Files**:
   - Edit `app/translations/fr/LC_MESSAGES/messages.po` for French
   - Edit `app/translations/ar/LC_MESSAGES/messages.po` for Arabic

3. **Compile Translations**:
   ```bash
   flask babel compile -d app/translations
   ```

### Using Translations in Code

```python
from flask_babel import gettext as _

# In handlers or services
error_message = _('error.validation.required')
status_label = _('status.quote.draft')
```

### Testing with Different Locales

```bash
# French (default)
curl http://localhost:5000/api/products?locale=fr

# Arabic
curl http://localhost:5000/api/products?locale=ar
```

## Key Patterns

### CQRS Pattern

- **Commands**: Write operations (create, update, delete)
- **Queries**: Read operations (list, get by id, search)
- **Mediator**: Dispatches commands/queries to handlers

### Domain Model Pattern

- Business logic in domain models
- Validation in domain methods
- Factory methods for creation
- State transition methods

### Transaction Management

- Use `get_session()` context manager
- Automatic commit on success
- Automatic rollback on exception

### RBAC

- Use `@require_roles()` decorator
- Roles: admin, direction, commercial, magasinier
- Fine-grained permissions per endpoint

## Next Steps

1. Review [data-model.md](./data-model.md) for entity definitions
2. Review [contracts/openapi.yaml](./contracts/openapi.yaml) for API specifications
3. Review [research.md](./research.md) for technical decisions
4. Start implementing modules following the patterns above

## Troubleshooting

### Database Connection Issues

- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in .env
- Check database exists: `psql -l | grep gmflow_db`

### Migration Issues

- Check Alembic version: `alembic current`
- Review migration files in `migrations/versions/`
- Manual rollback: `alembic downgrade -1`

### Import Errors

- Ensure virtual environment is activated
- Check Python path: `python -c "import sys; print(sys.path)"`
- Verify all dependencies installed: `pip list`

## Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- Alembic: https://alembic.sqlalchemy.org/
- Flask-Babel: https://flask-babel.tkte.ch/
- Frontend Design: `/design` folder with Tailwind CSS wireframes
- i18n Requirements: [i18n-requirements.md](./i18n-requirements.md)
- Existing codebase: `app/` directory for reference implementations

