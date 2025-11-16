---
description: "Task list for MVP Flask implementation (DDD/CQRS/Events/Outbox)"
---

# Tasks: Gestion Commerciale MVP (Flask)

**Input**: `.specify/gestion-commerciale-spec.md`, `.specify/plan-flask.md`, `architecture-prompt-mvp-commercial.md`
**Prerequisites**: plan-flask.md, spec.md, architecture mapping (DDD/CQRS/Domain Events/Outbox)

**Organization**: Tasks grouped by user story (independent delivery and testing per story)

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3, US4, US5, US6 (MVP scope)
- Include exact file paths in descriptions

## Path Conventions
- Single backend project under `app/`
- Domains in `app/domain/`, application in `app/application/`, API in `app/api/`, infrastructure in `app/infrastructure/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and base structure

- [ ] T001 Create Flask app factory and packages in `app/__init__.py`, `app/config.py`, `app/api/__init__.py`, `app/domain/__init__.py`, `app/application/__init__.py`, `app/infrastructure/__init__.py`
- [ ] T002 Define dependencies in `requirements.txt` (Flask, SQLAlchemy, Marshmallow, Flask-JWT-Extended, Alembic, Celery, kombu, psycopg2-binary, WeasyPrint)
- [ ] T003 [P] Configure formatting/linting (`pyproject.toml` for Black/Ruff) and basic CI workflow file `.github/workflows/ci.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

- [ ] T004 Setup PostgreSQL connection and SQLAlchemy session in `app/infrastructure/db.py`; initialize Alembic config `alembic.ini` and `migrations/`
- [ ] T005 [P] Implement authentication (JWT) in `app/security/auth.py` and RBAC roles in `app/security/rbac.py`; create `User` model in `app/domain/models/user.py`
- [ ] T006 [P] Register API blueprints and error handlers in `app/api/auth.py`, `app/api/products.py`, `app/api/customers.py`, `app/api/stock.py`, `app/api/orders.py`, `app/api/dashboard.py`; common errors in `app/api/errors.py`
- [ ] T007 Create base domain models in `app/domain/models/`: `product.py`, `customer.py`, `stock_item.py`, `order.py`, `order_line.py`
- [ ] T008 Configure structured logging and audit in `app/infrastructure/audit.py`
- [ ] T009 Manage environment configuration in `.env` and `app/config.py`
- [ ] T010 Implement Outbox model and repository in `app/infrastructure/outbox_model.py`, `app/infrastructure/outbox_repository.py`
- [ ] T011 Setup Celery worker and RabbitMQ publisher in `celery_app.py`, `app/infrastructure/event_publisher.py`
- [ ] T012 Implement Domain Event dispatcher and handlers in `app/domain/events.py`, `app/application/event_bus.py`

**Checkpoint**: Foundation ready – user stories can start (in parallel if staffed)

---

## Phase 3: User Story 1 – Auth/RBAC/Audit (Priority: P1) 🎯 MVP

**Goal**: Login, JWT, role-based access control, audit trail

- [ ] T020 [US1] Implement `/auth/login` in `app/api/auth.py` issuing JWT via `auth.py`
- [ ] T021 [US1] Implement `/auth/me` in `app/api/auth.py` returning roles/permissions
- [ ] T022 [US1] Add RBAC decorators for endpoints in `app/security/rbac.py`
- [ ] T023 [US1] Record audit logs for login/logout in `app/infrastructure/audit.py`

**Checkpoint**: Auth flows working, roles enforced, audit populated

---

## Phase 4: User Story 2 – Products (Priority: P1) 🎯 MVP

**Goal**: CRUD products, import/export, business validations

- [ ] T030 [US2] Implement product commands in `app/application/products/commands.py` (create, update, archive)
- [ ] T031 [P] [US2] Define Marshmallow schemas in `app/api/schemas/product_schema.py`
- [ ] T032 [US2] Implement REST endpoints in `app/api/products.py` (list, get, create, update, archive)
- [ ] T033 [US2] Implement import/export CSV in `app/application/products/import_export.py`
- [ ] T034 [US2] Emit `ProductUpdated` domain event in `app/domain/events.py` and update read model if needed

**Independent Test**: Products feature testable without dependencies on other stories

---

## Phase 5: User Story 3 – Customers (Priority: P1)

**Goal**: CRUD customers, import/export, basic validations

- [ ] T040 [US3] Implement customer commands in `app/application/customers/commands.py` (create, update, archive)
- [ ] T041 [P] [US3] Define Marshmallow schemas in `app/api/schemas/customer_schema.py`
- [ ] T042 [US3] Implement REST endpoints in `app/api/customers.py` (list, get, create, update, archive)
- [ ] T043 [US3] Implement import/export CSV in `app/application/customers/import_export.py`
- [ ] T044 [US3] Emit `CustomerUpdated` domain event in `app/domain/events.py`

**Independent Test**: Customers feature testable independently

---

## Phase 6: User Story 4 – Stock (Priority: P1)

**Goal**: Stock adjustments and reservations with integrity guarantees

- [ ] T050 [US4] Implement stock service in `app/application/stock/service.py` (adjust, reserve, release)
- [ ] T051 [US4] Apply pessimistic locks and atomic transactions in `app/infrastructure/db.py` and stock repository
- [ ] T052 [US4] Implement endpoints in `app/api/stock.py` (adjustments, reservations)
- [ ] T053 [US4] Emit `StockReserved` and `StockReleased` domain events in `app/domain/events.py`

**Independent Test**: Stock operations validate concurrency and integrity

---

## Phase 7: User Story 5 – Sales Orders (Priority: P1)

**Goal**: Create/submit/cancel orders, pricing, stock reservation, proforma PDF

- [ ] T060 [US5] Implement order aggregate behavior in `app/domain/models/order.py` (add line, totals, state)
- [ ] T061 [US5] Implement commands in `app/application/orders/commands.py` (create, submit, cancel)
- [ ] T062 [US5] Implement endpoints in `app/api/orders.py` (list, get, create, submit, cancel)
- [ ] T063 [US5] Generate proforma PDF in `app/application/orders/pdf.py` using WeasyPrint
- [ ] T064 [US5] Publish `OrderSubmittedIntegrationEvent` via Outbox in `app/infrastructure/outbox_repository.py` and Celery publisher

**Independent Test**: Orders flow testable from create to submit/cancel

---

## Phase 8: User Story 6 – Dashboard (Priority: P2)

**Goal**: KPIs and summary metrics for dashboard

- [ ] T070 [US6] Build read-model projections in `app/infrastructure/read_models/dashboard.py`
- [ ] T071 [US6] Implement `app/api/dashboard.py` endpoints (sales totals, top products, stock alerts)

**Independent Test**: Dashboard endpoints return metrics independent of other stories

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements across stories and production readiness

- [ ] T080 [P] Documentation updates in `docs/` and quickstart guide
- [ ] T081 Code cleanup and refactoring across `app/*`
- [ ] T082 Performance optimization (indexes, query tuning) across entities
- [ ] T083 Security hardening (rate limiting, headers, secure cookies)
- [ ] T084 Validate quickstart: run server, create sample data, exercise main flows

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies – can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion – BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if capacity allows)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on desired user stories being complete

### User Story Dependencies

- **US1 (Auth/RBAC/Audit)**: Starts after Foundational – no dependencies
- **US2 (Products)**: Starts after Foundational – independent, may be used by Orders
- **US3 (Customers)**: Starts after Foundational – independent, may be used by Orders
- **US4 (Stock)**: Starts after Foundational – required by Orders reservations
- **US5 (Orders)**: Depends on Products, Customers, Stock services
- **US6 (Dashboard)**: Depends on projections; can read from existing data

### Within Each User Story

- Models before services; services before endpoints
- Core implementation before integration events
- Story complete and independently testable before moving to next

### Parallel Opportunities

- Setup and Foundational tasks marked [P] can run in parallel
- Schema and model tasks in US2/US3 marked [P] can run in parallel
- Different stories can be assigned to different team members post-foundation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] labels map tasks to user stories for traceability
- Each user story should be independently completable and testable
- Keep tasks atomic; commit after each task or logical group
- Use Outbox for integration events only; Domain Events stay in-process