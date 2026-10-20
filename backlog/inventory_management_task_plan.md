# Small Business Inventory Management System
## Frontend, Backend, and Database Task Plan

**Project stack:** React + Vite, Python + Flask, PostgreSQL  
**Project type:** Browser-based web application  
**Initial goal:** Build a reliable inventory system for a small business, starting locally and adding production deployment after the core features work.

---

## 1. Project Goals

The application should let authorized staff:

- View inventory and business activity from a dashboard.
- Create, view, edit, search, filter, and archive products.
- Organize products into categories.
- Record stock receipts, issues, and adjustments.
- Manage suppliers and purchase orders.
- Record sales and automatically deduct stock.
- Review stock movement history and business reports.
- Sign in with appropriate roles and permissions.
- Export useful reports and recover data from backups.

## 2. Suggested Build Order

1. Project setup and configuration
2. Database schema and migrations
3. Product and category API
4. React product management screens
5. Stock movement workflow
6. Supplier and purchase workflow
7. Sales workflow
8. Dashboard and reports
9. Authentication, authorization, and audit history
10. Testing, security review, backups, and deployment

Build and test one vertical slice at a time. For example, complete the database model, Flask endpoints, React screen, and tests for products before moving on to the next module.

---

# 3. Frontend Tasks — React

## F1. Frontend Project Setup

- [X] Create a React application with Vite.
- [X] Install and configure React Router.
- [X] Set up a shared Axios or Fetch API client.
- [X] Configure the API base URL through environment variables.
- [X] Create a consistent folder structure for pages, components, API functions, and styles.
- [X] Establish a responsive design system: colors, spacing, typography, buttons, inputs, cards, and tables.
- [X] Add loading, empty, success, and error states.
- [X] Confirm the application runs locally in the browser.


## F2. Application Layout and Navigation

- [ ] Build a persistent sidebar and top navigation bar.
- [ ] Add navigation for Dashboard, Products, Categories, Stock, Suppliers, Purchases, Sales, Reports, and Settings.
- [ ] Highlight the current page in the navigation.
- [ ] Add a mobile-friendly navigation layout.
- [ ] Display the signed-in user's name and role when authentication is implemented.
- [ ] Add confirmation dialogs for important or destructive actions.

## F3. Dashboard

- [ ] Display total active products.
- [ ] Display total units in stock.
- [ ] Display inventory cost value.
- [ ] Display low-stock and out-of-stock counts.
- [ ] Display sales totals for a selected period once sales are implemented.
- [ ] Show recent sales and stock movements.
- [ ] Add sales charts and stock alerts.
- [ ] Load all figures from the API; do not hardcode business statistics.
- [ ] Include loading, empty, and error states.

## F4. Products

- [ ] Build a paginated product table.
- [ ] Display SKU, name, category, cost price, selling price, quantity, reorder level, and status.
- [ ] Build a create-product form.
- [ ] Build an edit-product form.
- [ ] Build a product details view.
- [ ] Add search by SKU and name.
- [ ] Add filters for category and stock status.
- [ ] Add sorting for appropriate columns.
- [ ] Validate required fields and numeric inputs in the browser.
- [ ] Display backend validation errors beside the form or in a message.
- [ ] Prevent duplicate submissions while saving.
- [ ] Add archive/restore controls rather than deleting products used in historical transactions.
- [ ] Refresh the product list and related dashboard values after successful changes.

## F5. Categories

- [ ] Display categories.
- [ ] Add and edit categories.
- [ ] Prevent empty category names.
- [ ] Handle duplicate category names.
- [ ] Prevent unsafe deletion of categories that are still in use, or provide a reassignment workflow.

## F6. Stock Management

- [ ] Build stock-in, stock-out, and adjustment forms.
- [ ] Require a reason for manual adjustments.
- [ ] Show the current quantity before submitting a movement.
- [ ] Show a stock movement history table.
- [ ] Filter history by product, movement type, user, and date range.
- [ ] Clearly distinguish low-stock and out-of-stock products.
- [ ] Show a confirmation for consequential adjustments.
- [ ] Do not update quantities only in React; submit movements to the API.

## F7. Suppliers and Purchases

- [ ] Build supplier list, create, edit, and details screens.
- [ ] Build purchase order creation with multiple product lines.
- [ ] Calculate line totals and order totals in the interface for preview.
- [ ] Support draft, submitted, partially received, received, and cancelled statuses as appropriate.
- [ ] Build a receiving screen to record actual quantities received.
- [ ] Show ordered and received quantities.
- [ ] Update the UI after the server confirms receiving stock.

## F8. Sales

- [ ] Build a sales entry screen with product search.
- [ ] Allow multiple line items per sale.
- [ ] Display available stock and warn when a requested quantity exceeds it.
- [ ] Calculate subtotal and total for preview.
- [ ] Submit the sale to the API for authoritative validation and calculation.
- [ ] Display the completed sale receipt/details.
- [ ] Build a sales history page with date and status filters.
- [ ] Support cancellation or refunds through explicit workflows, not by silently deleting sales.

## F9. Reports and Export

- [ ] Add sales reports with date ranges.
- [ ] Add stock valuation and stock movement reports.
- [ ] Add low-stock and out-of-stock reports.
- [ ] Add best-selling products when sufficient sales data exists.
- [ ] Display chart labels, units, and date ranges clearly.
- [ ] Provide CSV downloads from server-generated report data.
- [ ] Ensure report totals match the underlying records.

## F10. Authentication and Accessibility

- [ ] Build login and logout screens.
- [ ] Handle expired sessions or tokens.
- [ ] Hide navigation options the current role cannot use, while still enforcing permissions on the backend.
- [ ] Make forms keyboard-accessible and provide visible labels.
- [ ] Use readable contrast, focus indicators, and meaningful error messages.
- [ ] Test the layout on desktop, tablet, and mobile widths.

## F11. Frontend Testing

- [ ] Test important components and form validation with Vitest and React Testing Library.
- [ ] Test loading, empty, error, and successful API states.
- [ ] Test product search, filtering, and pagination.
- [ ] Test critical user flows in a browser.
- [ ] Ensure production builds complete successfully.

**Frontend completion criteria:** Staff can use the browser interface to complete the supported workflows, and all displayed business data comes from the API.

---

# 4. Backend Tasks — Python and Flask

## B1. Backend Setup

- [ ] Create and activate a Python virtual environment.
- [ ] Install Flask, Flask-SQLAlchemy, Flask-Migrate, PostgreSQL driver, Flask-CORS, and a request validation library.
- [ ] Create a Flask application factory.
- [ ] Configure development and production settings.
- [ ] Load secrets and database connection settings from environment variables.
- [ ] Add a health endpoint.
- [ ] Set up structured logging and consistent JSON error responses.
- [ ] Pin or lock dependencies for reproducible installs.


## B2. API Conventions

- [ ] Use `/api/...` routes with consistent naming.
- [ ] Use JSON request and response bodies.
- [ ] Return appropriate HTTP status codes: 200, 201, 204, 400, 401, 403, 404, 409, and 500 where applicable.
- [ ] Validate every incoming field on the server.
- [ ] Return consistent error shapes, for example `{"error": "SKU already exists"}`.
- [ ] Add pagination, filtering, and sorting with safe allowlists.
- [ ] Avoid exposing stack traces or secrets to clients.
- [ ] Document endpoints and example payloads.

## B3. Products API

- [ ] `GET /api/products` — list products with pagination, search, filters, and sorting.
- [ ] `POST /api/products` — create a product.
- [ ] `GET /api/products/<id>` — retrieve product details.
- [ ] `PUT` or `PATCH /api/products/<id>` — update editable product fields.
- [ ] `POST /api/products/<id>/archive` — archive a product.
- [ ] Validate SKU uniqueness, required fields, price values, quantities, and category references.
- [ ] Prevent unsafe deletion of products referenced by historical transactions.
- [ ] Ensure responses serialize decimal prices safely, preferably as decimal strings.

## B4. Categories API

- [ ] `GET /api/categories`
- [ ] `POST /api/categories`
- [ ] `GET /api/categories/<id>`
- [ ] `PATCH /api/categories/<id>`
- [ ] Add validation and duplicate-name handling.
- [ ] Define what happens when a category is in use.

## B5. Inventory and Stock Movement API

- [ ] `GET /api/stock-movements` — paginated movement history with filters.
- [ ] `POST /api/stock-movements` — record a permitted stock-in, stock-out, or adjustment.
- [ ] Validate product existence, movement type, quantity, and reason.
- [ ] Record the actor and timestamp.
- [ ] Update the product quantity and insert the movement record in one database transaction.
- [ ] Prevent negative stock unless the business explicitly chooses to support it.
- [ ] Protect against concurrent updates causing overselling or lost stock changes.
- [ ] Keep an auditable history; do not silently rewrite past movements.

## B6. Suppliers and Purchase Orders

- [ ] Create supplier CRUD endpoints.
- [ ] Create purchase order endpoints and purchase order line items.
- [ ] Validate supplier and product references.
- [ ] Support order status transitions.
- [ ] Implement receiving of full or partial quantities.
- [ ] Increase inventory only for quantities actually received.
- [ ] Record stock movements for received goods.
- [ ] Make receiving operations transactional and safe against duplicate submissions.

## B7. Sales API

- [ ] `GET /api/sales` — list sales with filters and pagination.
- [ ] `POST /api/sales` — create a sale with multiple line items.
- [ ] `GET /api/sales/<id>` — retrieve sale details.
- [ ] Validate every product and quantity.
- [ ] Calculate prices and totals on the server; do not trust client-calculated totals.
- [ ] Use a transaction for the sale, sale items, stock deductions, and movement records.
- [ ] Safely coordinate concurrent sales of the same product.
- [ ] Save the actual sale price and cost snapshot on each line item.
- [ ] Add explicit cancellation/refund workflows with appropriate stock and financial records.
- [ ] Make retry behavior safe so network retries cannot create duplicate sales.

## B8. Dashboard and Reports API

- [ ] `GET /api/dashboard` — return aggregate inventory metrics.
- [ ] `GET /api/reports/sales` — return sales totals for a date range.
- [ ] `GET /api/reports/inventory` — return stock quantity and valuation data.
- [ ] `GET /api/reports/low-stock` — return products at or below reorder level.
- [ ] `GET /api/reports/stock-movements` — return movement summaries.
- [ ] Implement CSV export with safe escaping.
- [ ] Use database queries and aggregates instead of loading every record into Python.
- [ ] Define the business meaning of revenue, gross profit, refunds, and stock valuation.

## B9. Authentication and Authorization

- [ ] Implement login and logout.
- [ ] Hash passwords with a suitable password-hashing library.
- [ ] Define roles such as Admin, Manager, and Cashier.
- [ ] Enforce permissions in every protected backend endpoint.
- [ ] Choose a browser authentication strategy carefully. If using cookies, configure secure, HttpOnly, SameSite cookies and CSRF protection as appropriate. If using tokens, define secure storage, expiration, refresh, and revocation behavior.
- [ ] Apply login rate limiting and safe error messages.
- [ ] Validate authorization for exports, stock adjustments, sales, and user management.
- [ ] Never rely on frontend route hiding as access control.

## B10. Backend Testing and Reliability

- [ ] Write unit tests for validation and business services.
- [ ] Write API tests for successful and rejected requests.
- [ ] Test duplicate SKU and invalid category handling.
- [ ] Test stock never becomes negative in supported workflows.
- [ ] Test rollback when part of a sale or receiving operation fails.
- [ ] Test concurrent stock changes.
- [ ] Test role-based access control.
- [ ] Add request IDs and useful error logs.
- [ ] Disable debug mode in production.
- [ ] Restrict CORS to approved origins.
- [ ] Add health checks for application and database readiness.

**Backend completion criteria:** All business rules are enforced on the server, invalid requests are rejected, and multi-step stock and sales operations are transaction-safe.

---

# 5. Database Tasks — PostgreSQL

## D1. Database Setup and Configuration

- [X] Install PostgreSQL and a database administration tool such as pgAdmin.
- [X] Create a database named `inventory_db`.
- [X] Create a dedicated application database user with only the required privileges.
- [ ] Store the connection string in environment variables.
- [ ] Configure development, testing, and production databases separately.
- [ ] Set up Flask-Migrate/Alembic migrations.
- [ ] Add a documented database initialization process.
- [ ] Never commit credentials or production data to source control.

## D2. Core Tables

### `users`

Suggested fields:

- `id` — primary key
- `name`
- `email` — unique
- `password_hash`
- `role`
- `is_active`
- `created_at`
- `updated_at`

### `categories`

- `id` — primary key
- `name` — unique where appropriate
- `description`
- `created_at`
- `updated_at`

### `products`

- `id` — primary key
- `sku` — unique and required
- `name`
- `description`
- `category_id` — foreign key
- `cost_price` — `NUMERIC(12,2)`
- `selling_price` — `NUMERIC(12,2)`
- `quantity` — integer, non-negative
- `reorder_level` — integer, non-negative
- `is_active` or `archived_at`
- `created_at`
- `updated_at`

### `suppliers`

- `id` — primary key
- `name`
- `contact_person`
- `email`
- `phone`
- `address`
- `created_at`
- `updated_at`

### `stock_movements`

- `id` — primary key
- `product_id` — foreign key
- `user_id` — foreign key, nullable only if the workflow permits it
- `movement_type` — such as receipt, sale, adjustment, or return
- `quantity_change` — signed integer
- `reason`
- `reference_type` and `reference_id` where useful
- `created_at`

### `sales`

- `id` — primary key
- `sale_number` — unique
- `user_id` — foreign key
- `status`
- `subtotal`
- `discount_amount` if supported
- `tax_amount` if supported
- `total_amount`
- `sold_at`
- `created_at`

### `sale_items`

- `id` — primary key
- `sale_id` — foreign key
- `product_id` — foreign key
- `quantity`
- `unit_price` — sale-time price snapshot
- `unit_cost` — cost snapshot for gross-profit reporting
- `line_total`

### `purchase_orders`

- `id` — primary key
- `purchase_number` — unique
- `supplier_id` — foreign key
- `user_id` — foreign key
- `status`
- `order_date`
- `expected_date`
- `received_at` when fully received
- `total_amount`
- `created_at`
- `updated_at`

### `purchase_order_items`

- `id` — primary key
- `purchase_order_id` — foreign key
- `product_id` — foreign key
- `quantity_ordered`
- `quantity_received`
- `unit_cost`
- `line_total`

### Optional future tables

- `customers` — if customer records are needed.
- `sale_refunds` and `sale_refund_items` — if refund workflows are supported.
- `audit_logs` — security-sensitive actions and administrative changes.
- `businesses` — if the system will support multiple businesses.
- `locations` and `inventory_balances` — if the system will support multiple stores or warehouses.
- `product_batches` — if batch or expiry-date tracking is required.

## D3. Relationships and Constraints

- [ ] One category can have many products.
- [ ] One sale has many sale items.
- [ ] One product can appear in many sale items.
- [ ] One supplier can have many purchase orders.
- [ ] One purchase order has many purchase order items.
- [ ] One product can have many stock movements.
- [ ] Add foreign keys to preserve referential integrity.
- [ ] Add unique constraints for SKU, email, sale number, and purchase number.
- [ ] Add check constraints for non-negative prices, quantities, and reorder levels.
- [ ] Decide on `ON DELETE` behavior deliberately; preserve historical business records.
- [ ] Use `NUMERIC` for money, not floating-point columns.
- [ ] Use timestamps consistently, preferably storing UTC and converting for display.
- [ ] Decide whether SKU uniqueness is global or scoped to a business.
- [ ] Consider case-insensitive uniqueness for email, SKU, and category names where appropriate.

## D4. Indexes and Query Performance

- [ ] Index foreign key columns used frequently in joins and filters.
- [ ] Index product SKU.
- [ ] Add appropriate indexes for product name search.
- [ ] Index sale date and purchase order date.
- [ ] Index stock movements by product and creation time.
- [ ] Add indexes for commonly used status filters.
- [ ] Use `EXPLAIN ANALYZE` to investigate slow queries when sample data grows.
- [ ] Avoid adding unnecessary indexes before understanding query patterns.

## D5. Data Integrity and Transaction Rules

- [ ] A product quantity must not be changed by sales without a corresponding movement record.
- [ ] Stock deduction, sale creation, sale item creation, and movement creation must commit or roll back together.
- [ ] Receiving purchase order items and increasing stock must commit or roll back together.
- [ ] Protect against duplicate sale submissions.
- [ ] Use suitable row locking or atomic updates for concurrent stock changes.
- [ ] Define how returns, refunds, voids, and cancelled orders affect stock and reports.
- [ ] Choose a consistent approach to stock valuation, such as average cost or FIFO, if financial accuracy requires it.
- [ ] Preserve historical prices and costs on completed transactions.

## D6. Migrations, Seed Data, Backups, and Recovery

- [ ] Create the initial migration.
- [ ] Test applying migrations to a clean database.
- [ ] Test upgrades from an earlier schema.
- [ ] Create optional development seed data for categories, products, and suppliers.
- [ ] Keep test data separate from real business data.
- [ ] Configure regular database backups.
- [ ] Test restoring a backup into a separate database.
- [ ] Document retention, access, and recovery procedures.
- [ ] Plan safe migrations before deploying schema changes.

**Database completion criteria:** The schema enforces key relationships and constraints, transactional workflows preserve stock integrity, and the database can be backed up and restored.

---

# 6. Cross-Component API Contract

Agree on request and response formats before implementing each feature across all three layers.

| Feature | Frontend responsibility | Backend responsibility | Database responsibility |
|---|---|---|---|
| Products | Forms, table, search, filters | Validation and CRUD endpoints | Product and category records |
| Stock | Movement form and history | Validate and apply movements | Quantity and movement records |
| Purchases | Order creation and receiving UI | Order status and receiving logic | Purchase orders and items |
| Sales | Cart, totals preview, receipt | Validate sale and deduct stock | Sales, items, and movements |
| Dashboard | KPI cards and charts | Aggregate and return metrics | Efficient aggregate queries |
| Reports | Date filters and exports UI | Report generation and authorization | Accurate historical records |
| Authentication | Login and role-aware navigation | Authentication and permissions | Users and role-related data |

Suggested initial API endpoints:

```text
GET    /api/health

GET    /api/products
POST   /api/products
GET    /api/products/<id>
PATCH  /api/products/<id>
POST   /api/products/<id>/archive

GET    /api/categories
POST   /api/categories
PATCH  /api/categories/<id>

GET    /api/stock-movements
POST   /api/stock-movements

GET    /api/suppliers
POST   /api/suppliers
PATCH  /api/suppliers/<id>

GET    /api/purchases
POST   /api/purchases
POST   /api/purchases/<id>/receive

GET    /api/sales
POST   /api/sales
GET    /api/sales/<id>

GET    /api/dashboard
GET    /api/reports/sales
GET    /api/reports/inventory
GET    /api/reports/low-stock

POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me
```

The exact endpoints may change as the design evolves. Document any changes so the frontend and backend remain aligned.

---

# 7. Definition of Done

A task is complete only when:

- [ ] The frontend works in the browser and handles loading, success, empty, and error states.
- [ ] The backend validates inputs and enforces authorization where needed.
- [ ] Database changes are made through migrations.
- [ ] Important business operations are transactional.
- [ ] Tests cover the happy path and important failure cases.
- [ ] No credentials or sensitive data are committed to Git.
- [ ] The feature has been tested with realistic sample data.
- [ ] Any relevant setup or API documentation has been updated.

# 8. First Sprint — Start Here

Complete these tasks in order:

1. [ ] Install Node.js, Python, PostgreSQL, and VS Code.
2. [ ] Create the `frontend` and `backend` directories.
3. [ ] Start the React app using Vite.
4. [ ] Set up a Flask virtual environment and install dependencies.
5. [ ] Create `inventory_db` and configure the database connection.
6. [ ] Add the Flask health endpoint and verify it in a browser.
7. [ ] Create the initial database migration and product model.
8. [ ] Implement `GET /api/products` and `POST /api/products`.
9. [ ] Build the React product table and add-product form.
10. [ ] Verify that a product saves to PostgreSQL and remains after refreshing the browser.
11. [ ] Add tests for duplicate SKUs and invalid product data.
12. [ ] Commit the working milestone to Git.

**First milestone:** A user can open the browser, create a product, see it in the product list, and retrieve it again from PostgreSQL after refreshing the page.
