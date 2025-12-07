<!-- Copilot / AI agent instructions for the EVA4 repo -->
# EVA4 — AI Agent Instructions

Short, actionable guidance for an AI coding agent working on this Django + DRF monolith.

- **Quick dev bootstrap (Windows PowerShell)**:

```powershell
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo   # creates demo data (use --reset)
python manage.py runserver
```

- **Project shape / big picture**:
  - Monolithic Django project. Apps live under `apps/` (e.g. `apps.accounts`, `apps.core`, `apps.inventory`, `apps.sales`, `apps.shop`, `apps.reports`).
  - Multi‑tenant by `Company` (see `apps/core/models.py`). Most business models are scoped to a `company` FK.
  - Custom user model: `AUTH_USER_MODEL = 'accounts.User'` (see `apps/accounts/models.py`) — includes `role` and optional `company` (super_admin has `company=None`).
  - Subscription/plan gating lives in `apps/core/models.py` (`Plan`, `PlanFeature`, `Subscription`) — use `Plan.has_feature()` and `Subscription.reports_enabled()` when gating features.

- **Auth / API behavior**:
  - JWT using SimpleJWT is configured in `config/settings.py` (`rest_framework_simplejwt`). API endpoints: `/api/token/` and `/api/token/refresh/`.
  - DRF `DEFAULT_AUTHENTICATION_CLASSES` includes JWT and `SessionAuthentication`. HTML views use standard Django sessions.

- **Important code patterns / conventions**:
  - Role-based creation and permissions are enforced at serializer/permission level. Example: `apps/accounts/serializers.py`'s `UserSerializer.validate()` restricts which roles can create which users.
  - Company scoping: when adding or querying business objects, filter by `company` explicitly. Seed script (`seed_demo`) and many views/models assume a `company` field exists.
  - Bulk operations: demo data and heavy data paths use `bulk_create` / `bulk_update` for performance (see `apps/accounts/management/commands/seed_demo.py`).
  - Inventory flows: purchases / sales / orders update `Inventory` and create `InventoryMovement` records — replicate this pattern for any inventory-affecting endpoint.
  - RUT validation and Spanish locale: repo uses Chilean RUT validator (`apps/core/validators.py`) and `LANGUAGE_CODE='es-cl'`.

- **Developer workflows (discovered)**:
  - Local dev uses SQLite by default. To use Postgres set `DB_ENGINE` and other vars in `.env` (see `.env.example`).
  - Deploy notes and service configs are in `deploy/` (example `gunicorn.service` and `nginx.conf`).
  - Demo data: `python manage.py seed_demo --reset` (see `apps/accounts/management/commands/seed_demo.py`) — useful for smoke tests.

- **Where to look for implementation examples**:
  - Role checks & user creation: `apps/accounts/serializers.py` and `apps/accounts/models.py`.
  - Plan/feature gating: `apps/core/models.py` (`Plan`, `PlanFeature`, `Subscription`).
  - Inventory/purchase/sale flows & bulk data: `apps/accounts/management/commands/seed_demo.py` (large, concrete examples of creating purchases/sales/orders and inventory movements).
  - API and view wiring: `config/urls.py`, each app's `urls.py`, and `templates/` for HTML pages.

- **Quick rules for AI edits**:
  - When adding or changing models, always add or update migrations and review `seed_demo` so demo data remains consistent.
  - Preserve company scoping: new queries or endpoints must not leak across companies — scope by `company` or `request.user.company` as appropriate.
  - Follow existing role semantics: use the existing role constants on the `User` model (e.g. `ROLE_SUPER_ADMIN`, `ROLE_ADMIN_CLIENTE`, `ROLE_GERENTE`, `ROLE_VENDEDOR`).
  - Use the project's validators (RUT) and i18n conventions rather than adding ad-hoc checks.

- **Tests & verification**:
  - There are unit tests in `apps/core/tests/` (e.g. `test_plans_and_subscriptions.py`) — run them after logic changes.
  - Smoke test with `seed_demo` and logging into the UI (users / roles listed in `README.md`).

If anything here is unclear or you want me to expand an example (e.g. company-scoped query patterns, common permission checks, or a short checklist for PRs), tell me which section and I'll iterate.
