# Invoicing Feature Plan

## Database Schema

```sql
create table if not exists invoices (
    invoice_uuid uuid primary key default uuid_generate_v4(),
    invoice_number text,
    project_uuid uuid not null references projects(project_uuid),
    client_name text not null,
    client_address text,
    total_amount numeric(10,2) not null default 0.00,
    notes text,
    status text not null default 'draft',
    invoice_date date not null default current_date,
    due_date date,
    paid_date date,
    pdf_path text,
    inserted timestamp with time zone not null default now(),
    updated timestamp with time zone not null default now()
);

create table if not exists invoice_time_entries (
    invoice_uuid uuid not null references invoices(invoice_uuid) on delete cascade,
    time_entry_uuid uuid not null references time_entries(time_entry_uuid),
    primary key (invoice_uuid, time_entry_uuid)
);
```

## Data Access Layer

File: `/budgetbot/pg/invoices.py`

Classes:
- `Invoice` - Base invoice class with CRUD operations
- `InvoiceWithDetails` - Invoice with project details
- Key methods:
  - `create()` - Create a new invoice
  - `update()` - Update an existing invoice
  - `by_uuid()` - Get invoice by UUID
  - `get_all()` - Get all invoices, with optional filters
  - `add_time_entry()` - Add a time entry to an invoice
  - `remove_time_entry()` - Remove a time entry from an invoice
  - `get_time_entries()` - Get all time entries for an invoice
  - `update_total_from_time_entries()` - Calculate and update total amount
  - `mark_as_paid()` - Mark invoice as paid with optional paid date

## API Handlers

File: `/budgetbot/webapp/timetracking/handlers.py`

New handlers:
- `InvoiceListHandler` - List all invoices (`GET /invoices`)
- `InvoiceDetailHandler` - View a specific invoice (`GET /invoices/{uuid}`)
- `InvoiceNewFormHandler` - Form to create a new invoice (`GET /invoices/new`)
- `InvoiceEditFormHandler` - Form to edit an invoice (`GET /invoices/{uuid}/edit`)
- `InvoiceCreateHandler` - Create a new invoice (`POST /api/invoices/create`)
- `InvoiceUpdateHandler` - Update an invoice (`POST /api/invoices/{uuid}/update`)
- `InvoiceMarkAsPaidHandler` - Mark invoice as paid (`POST /api/invoices/{uuid}/mark-paid`)
- `InvoicesApiListHandler` - List invoices via API (`GET /api/invoices/list`)
- `UnbilledTimeEntriesHandler` - Get unbilled time entries (`GET /api/projects/{uuid}/unbilled-time-entries`)

## Templates

New templates needed:
- `timetracking/invoices.html` - List all invoices
- `timetracking/invoice-detail.html` - View a specific invoice
- `timetracking/invoice-form.html` - Form to create/edit invoices

Update existing templates:
- `timetracking/project-detail.html` - Add invoices section

## Frontend Features

- View list of all invoices with filtering options
- Create new invoices with client information
- Attach time entries to invoices
- Calculate invoice total based on time entries
- Update invoice status (draft, sent, paid)
- Mark invoices as paid with payment date
- View invoice details with time entries
- Add invoices section to project detail page

## PDF Generation (Future Enhancement)

In the future, we will add PDF generation capabilities:
- Generate invoice PDFs using a template
- Store PDF path in the database
- Allow downloading/viewing generated PDFs
- Email invoices directly to clients

## Implementation Plan

1. Create database schema
2. Implement data access layer
3. Create API handlers
4. Create templates and frontend
5. Update project details page to include invoices
6. Test functionality with various scenarios
7. Add PDF generation capabilities (future enhancement)

## Testing Checklist

- Create invoices for projects
- Add/remove time entries from invoices
- Calculate totals correctly
- Update invoice status
- Mark invoices as paid
- Filter invoices by project/status
- View invoice details