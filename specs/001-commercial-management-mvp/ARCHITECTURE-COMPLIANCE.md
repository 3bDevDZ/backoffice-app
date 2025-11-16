# Architecture Compliance Guide

**Date**: 2025-01-27  
**Feature**: Commercial Management MVP System

## Architecture Principles

This implementation follows the DDD + CQRS + Domain Events architecture as defined in `architecture-prompt-mvp-commercial.md`.

### Key Patterns to Follow

#### 1. CQRS (Command Query Responsibility Segregation)

**Commands (Write Side):**
- Dataclasses extending `Command` from `app.application.common.cqrs`
- Modify system state via Aggregates
- Return success/failure (may return created/updated entity)
- Use `CommandHandler` interface
- Example: `CreateProductCommand`, `UpdateProductCommand`

**Queries (Read Side):**
- Dataclasses extending `Query` from `app.application.common.cqrs`
- Read-only operations
- Return DTOs (dataclasses)
- Use `QueryHandler` interface
- Example: `GetProductByIdQuery`, `ListProductsQuery`

**Mediator Pattern:**
- All commands/queries dispatched via `mediator.dispatch()`
- Handlers registered in `app/__init__.py`
- Single mediator instance: `from app.application.common.mediator import mediator`

#### 2. Domain-Driven Design (DDD)

**Domain Models (Aggregates):**
- Located in `app/domain/models/`
- Extend `Base` from `app.infrastructure.db`
- Contain business logic methods:
  - Static factory methods: `create()`, `from_data()`
  - Instance methods: `update_details()`, `archive()`, `activate()`, etc.
- Validate invariants in methods
- Example: `Product.create()`, `Product.update_details()`, `Product.archive()`

**Domain Events (Future):**
- Will be raised from Aggregates for important state changes
- Named in past tense: `ProductCreatedDomainEvent`, `OrderConfirmedDomainEvent`
- Handled synchronously within same transaction
- Communication INTERNAL only (same bounded context)

**Integration Events (Future):**
- For external communication (e-commerce, other projects)
- Saved to `OutboxEvents` table
- Published asynchronously via Celery worker to RabbitMQ
- Only created when external communication needed

#### 3. Application Layer Structure

```
app/application/
├── common/
│   ├── cqrs.py          # Command, Query, CommandHandler, QueryHandler base classes
│   └── mediator.py      # Mediator pattern implementation
├── {module}/
│   ├── commands/
│   │   ├── commands.py  # Command dataclasses
│   │   └── handlers.py  # CommandHandler implementations
│   └── queries/
│       ├── queries.py   # Query dataclasses
│       ├── handlers.py  # QueryHandler implementations
│       └── {module}_dto.py  # DTO dataclasses
```

**Handler Pattern:**
```python
class CreateProductHandler(CommandHandler):
    def handle(self, command: CreateProductCommand) -> Product:
        with get_session() as session:
            product = Product.create(...)  # Domain factory method
            session.add(product)
            session.commit()
            return product
```

#### 4. Infrastructure Layer

**Database:**
- Use `get_session()` context manager from `app.infrastructure.db`
- Automatic commit on success, rollback on exception
- SQLAlchemy 2.0 with declarative Base

**Transactions:**
- All database operations within `with get_session() as session:`
- Commands handle transactions automatically
- Queries use read-only sessions

#### 5. API Layer

**Structure:**
- Blueprints in `app/api/`
- Endpoints use `@require_roles()` decorator for RBAC
- Dispatch commands/queries via `mediator.dispatch()`
- Return JSON responses

**Pattern:**
```python
@products_bp.post("")
@require_roles("admin", "commercial")
def create():
    data = ProductCreateSchema().load(request.get_json() or {})
    command = CreateProductCommand(**data)
    product = mediator.dispatch(command)
    return jsonify(ProductSchema().dump(product)), 201
```

#### 6. Frontend Routes (Full-Stack Flask)

**Structure:**
- Blueprints in `app/routes/`
- Render Jinja2 templates
- Use Flask-Babel for i18n
- Pass locale and direction to templates

**Pattern:**
```python
@products_routes.route('/products')
@require_roles('admin', 'commercial')
def list():
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    products = mediator.dispatch(ListProductsQuery())
    return render_template('products/list.html',
                         products=products,
                         locale=locale,
                         direction=direction)
```

## Implementation Checklist

### ✅ Completed (Phases 1-2)

- [x] Flask-Babel configuration and initialization
- [x] Base template with RTL support
- [x] Locale detection utilities
- [x] API response wrapper with locale metadata
- [x] User model extended with locale field
- [x] Directory structure created

### 🔄 In Progress (Phase 3+)

- [ ] Domain models with business logic methods
- [ ] Commands and CommandHandlers following CQRS pattern
- [ ] Queries and QueryHandlers following CQRS pattern
- [ ] DTOs for query responses
- [ ] API endpoints using mediator pattern
- [ ] Frontend routes with template rendering
- [ ] Domain Events (when needed for cross-aggregate communication)

## Rules to Follow

### ✅ DO

1. **Domain Models:**
   - Always use factory methods (`create()`) for creation
   - Put business logic in domain methods
   - Validate invariants in domain methods
   - Use static methods for factories

2. **Commands:**
   - Use dataclasses extending `Command`
   - Dispatch via `mediator.dispatch()`
   - Handlers use `get_session()` context manager
   - Return created/updated entity or success

3. **Queries:**
   - Use dataclasses extending `Query`
   - Return DTOs (dataclasses)
   - Use direct database queries (read-only)
   - No business logic in queries

4. **API Endpoints:**
   - Use `@require_roles()` for authorization
   - Validate input with Marshmallow schemas
   - Dispatch commands/queries via mediator
   - Return appropriate HTTP status codes

5. **Templates:**
   - Extend `base.html`
   - Use Flask-Babel `_()` for translations
   - Support RTL with `direction` variable
   - Use locale-aware formatting

### ❌ DON'T

1. **Domain Models:**
   - Don't put data access logic in domain models
   - Don't expose internal state unnecessarily
   - Don't skip validation

2. **Commands/Queries:**
   - Don't put business logic in handlers (use domain methods)
   - Don't bypass mediator
   - Don't return domain entities from queries (use DTOs)

3. **API:**
   - Don't put business logic in controllers
   - Don't access database directly from controllers
   - Don't skip authorization checks

4. **Templates:**
   - Don't hardcode text (use translations)
   - Don't ignore RTL support
   - Don't mix server-side and client-side logic unnecessarily

## Next Steps

Continue with Phase 3 (User Story 1) following these patterns:
1. Create Category domain model with business logic
2. Extend Product domain model following existing pattern
3. Create Commands/Queries following CQRS pattern
4. Create Handlers using mediator pattern
5. Create API endpoints using existing blueprint pattern
6. Create frontend routes with template rendering

