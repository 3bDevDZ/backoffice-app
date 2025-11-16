# Implementation Plan — Flask Backend (MVP Phase 1)
Version 0.1 — 15/11/2025 — Status: Draft

---

## 1. Overview

- Scope: Implement MVP modules (Products, Clients, Stock, Sales, Dashboard) per `gestion-commerciale-spec.md` using Flask.
- Goals: Reliable REST API, RBAC security, audit logging, PDF generation for quotes/orders, import/export, and strong data integrity for stock/reservations.
- Database: PostgreSQL (recommended). SQLAlchemy ORM + Alembic migrations.

---

## 2. Tech Stack

- Core: `Flask`, `Flask SQLAlchemy`, `Alembic`, `Flask-JWT-Extended` (Auth), `Marshmallow` (validation), `Flask-Smorest` or `Flask-RESTX` (API docs/options), `WeasyPrint` (PDF), `Celery + Redis` (async tasks), `python-dotenv`.
- Testing: `pytest`, `pytest-cov`, `factory_boy`.
- Observability: `structlog` (JSON logs), `Flask-Logging` config, request/response logging middleware.
- File storage: Local `uploads/` for product images; later S3-compatible option.

---

## 3. Project Structure

```
app/
  __init__.py            # App factory, extensions init
  config.py              # Config classes (Dev/Prod/Test)
  extensions.py          # db, ma, jwt, celery, etc.
  blueprints/
    auth/                # login/logout/me
    products/            # products, categories, price lists
    clients/             # clients, addresses, contacts, conditions
    stock/               # stock view, movements, inventories
    sales/               # quotes, orders, PDFs, workflows
    dashboard/           # KPI endpoints
  models/                # SQLAlchemy models
  schemas/               # Marshmallow schemas
  services/              # domain logic (pricing, inventory, reservations)
  pdf_templates/         # Jinja templates (quotes/orders PDF)
  tasks/                 # Celery tasks (emails, reminders)
  utils/                 # common helpers (errors, pagination)
migrations/              # Alembic
tests/                   # pytest suites per module
instance/                # instance config, .env loading
uploads/                 # product images
```

---

## 4. Data Model (MVP)

- Products: Product, Category (tree), Variant, PriceList, PriceRule.
- Clients: Client (B2B/B2C), Address, Contact, CommercialConditions.
- Stock: StockItem (by product/variant + location), Movement, Inventory, InventoryCount.
- Sales: Quote, QuoteLine, Order, OrderLine, WorkflowHistory.
- Security/Audit: User, Role, Permission, AuditLog.

Key constraints:
- Unique codes (product, variant; client code auto); barcode unique if present.
- Stock counts: physical ≥ 0; reserved ≤ physical.
- Referential integrity: prevent delete if referenced in documents.

---

## 5. API Surface (Endpoints)

- Auth: `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`.
- Products: `GET/POST/PUT/DELETE /products`, `GET /products/{id}`, `POST /products/import`, `GET /products/export`.
- Categories: `GET/POST/PUT/DELETE /categories`.
- Price Lists: `GET/POST/PUT/DELETE /price-lists`.
- Clients: `GET/POST/PUT/DELETE /clients`, `GET /clients/{id}`, `POST /clients/import`, `GET /clients/export`.
- Addresses/Contacts: `GET/POST/PUT/DELETE /clients/{id}/addresses`, `/clients/{id}/contacts`.
- Stock: `GET /stock`, `GET /stock/alerts`, `POST /stock/movements`, `GET /stock/movements`.
- Inventories: `POST /inventories`, `POST /inventories/{id}/counts`, `POST /inventories/{id}/close`.
- Quotes: `GET/POST/PUT /quotes`, `POST /quotes/{id}/send`, `POST /quotes/{id}/version`, `GET /quotes/{id}/pdf`.
- Orders: `GET/POST/PUT /orders`, `POST /orders/{id}/reserve`, `POST /orders/{id}/cancel`, `GET /orders/{id}/pdf`.
- Dashboard: `GET /dashboard/kpi`.

Common patterns:
- Pagination: `?page, ?page_size`, sorting `?sort`, filters via query params.
- Error responses: standardized JSON `{code, message, details}`.
- RBAC: per-endpoint checks; action endpoints (workflows) guarded by role.

---

## 6. Security & RBAC

- JWT-based auth; sessions expire after inactivity (configurable, default 30 min).
- Roles: Admin, Direction, Commercial, Magasinier; fine-grained permissions per module/action.
- Rate limiting basic (optional for MVP) on critical endpoints.
- Audit logging: record `{user, action, resource, before/after, timestamp}`; non-repudiation.
- Input validation via Marshmallow; email uniqueness; business validations aligned with spec.

---

## 7. Stock Integrity & Concurrency

- Use DB transactions for movements and reservations.
- Enforce row-level locks on `StockItem` during updates (`with_for_update`) to avoid race conditions.
- Reservation on order confirmation: compute availability, decrement `reserved`; cancellation frees reserved.
- Inventory workflow: flag products under inventory to block movements; generate adjustments on close.

---

## 8. PDFs & Notifications

- PDF (quotes/orders): Jinja2 → HTML → WeasyPrint PDF; templates in `app/pdf_templates/`.
- Email sending (quotes, confirmations, reminders): Celery tasks; SMTP config via environment.
- Relance devis: scheduled tasks (Celery beat) for J+7/J+15.

---

## 9. Import/Export

- Products/Clients: CSV/XLS import with validation report; export endpoints for lists.
- Error report: downloadable CSV with row-level error details.
- Large files: stream processing; size limits and type checks.

---

## 10. Non-Functional

- Performance: <2s page responses typical; optimize DB queries; indexes on codes and foreign keys.
- Logging: request/response IDs; structured logs; error tracking.
- Configuration: `.env` + instance config; separate Dev/Prod settings.

---

## 11. DevOps & Environments

- Envs: `dev`, `test`, `prod`.
- Migrations: Alembic; CI step runs `alembic upgrade head` in test.
- CI: lint, tests, coverage; build PDF assets.
- Backups: DB backup strategy (outside MVP code), doc included.

---

## 12. Milestones & Tasks (8–10 weeks MVP)

Week 1–2: Foundations
- Bootstrap Flask app factory, configs, extensions.
- Setup PostgreSQL, SQLAlchemy models skeleton, Alembic.
- Implement Auth (JWT) + basic RBAC; error handling & logging.

Week 3–4: Products + Clients
- Products CRUD, categories, variants, price lists; validation & import/export.
- Clients CRUD, addresses, contacts, conditions; import/export.
- Unit/integration tests.

Week 5–6: Stock
- Stock view and movements (entrée/sortie/transfert/adjustment) with transactions/locks.
- Inventories workflow (create, counts, close + adjustments).
- Alerts & reordering rules basics.

Week 7: Sales (Quotes)
- Quote CRUD, numbering, lines, totals, versioning, PDF, send email.
- Workflow states and actions; relance tasks.

Week 8: Sales (Orders) + Reservation
- Order CRUD, verification stock/crédit (stub for credit), reservation on confirm.
- Cancel order releases reservation; PDF generation.

Week 9: Dashboard + Polish
- KPI endpoints (CA mock, stock alerts, active orders); optimize queries.
- Hardening: validation rules, edge cases, audit logs, pagination.

Week 10: Tests & Performance
- End-to-end tests; performance checks; documentation; deployment checklist.

---

## 13. Risks & Mitigations

- Concurrency on reservations: mitigate via row locks + clear workflow transitions.
- Large imports: stream processing and chunking; robust validation.
- PDF rendering fidelity: test templates across cases; cache assets.

---

## 14. Acceptance Criteria

- All MVP endpoints functional with validations and RBAC.
- Quotes/orders PDFs generated and emails sent.
- Stock movements reflect accurate physical/reserved counts under contention.
- Import/export for products/clients works with error reporting.
- Dashboard returns KPI with acceptable latency.
- Tests green (unit/integration); basic load checks within targets.