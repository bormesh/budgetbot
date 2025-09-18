# Invoicing Feature Implementation

This document provides a technical overview of the invoicing feature implementation.

## Database Schema

The invoicing feature adds two new tables to the database:

1. `invoices` - Stores invoice details
   - `invoice_uuid` - Primary key
   - `invoice_number` - Optional reference number
   - `project_uuid` - Reference to a project
   - `client_name` - Client name
   - `client_address` - Optional client address
   - `total_amount` - Invoice total amount
   - `notes` - Optional notes
   - `status` - Status of the invoice (draft, sent, paid)
   - `invoice_date` - Invoice date
   - `due_date` - Optional due date
   - `paid_date` - Optional payment date
   - `pdf_path` - Optional path to PDF file
   - `inserted`/`updated` - Timestamp fields

2. `invoice_time_entries` - Junction table linking invoices and time entries
   - `invoice_uuid` - Reference to an invoice
   - `time_entry_uuid` - Reference to a time entry
   - Primary key is combination of both fields

The schema also includes:
- Indexes for efficient querying
- An update trigger for the `updated` timestamp
- Views for joined data retrieval

## Code Implementation

### Data Access Layer

The `invoices.py` module implements the data access layer with two main classes:

1. `Invoice` - Core invoice functionality
   - CRUD operations
   - Time entry management
   - Payment processing

2. `InvoiceWithDetails` - Extended invoice with project details
   - Inherits from Invoice
   - Includes project title, description, etc.

Key methods:
- `create()` - Create a new invoice
- `update()` - Update an existing invoice
- `by_uuid()` - Get invoice by UUID
- `get_all()` - List invoices with optional filtering
- `add_time_entry()` - Add time entry to invoice
- `remove_time_entry()` - Remove time entry from invoice
- `update_total_from_time_entries()` - Calculate total from entries
- `mark_as_paid()` - Mark invoice as paid

### Handlers Layer

The invoicing handlers provide web and API interfaces for the invoice functionality:

1. Web Handlers:
   - `InvoiceListHandler` - List all invoices
   - `InvoiceDetailHandler` - View invoice details
   - `InvoiceNewFormHandler` - New invoice form
   - `InvoiceEditFormHandler` - Edit invoice form

2. API Handlers:
   - `InvoiceCreateHandler` - Create a new invoice
   - `InvoiceUpdateHandler` - Update an existing invoice
   - `InvoiceMarkAsPaidHandler` - Mark invoice as paid
   - `InvoicesApiListHandler` - List invoices via API
   - `UnbilledTimeEntriesHandler` - Get unbilled time entries for a project

### Templates

The UI templates provide user interfaces for the invoicing feature:

1. `invoices.html` - Lists all invoices with filtering
2. `invoice-detail.html` - Shows invoice details and time entries
3. `invoice-form.html` - Form for creating/editing invoices
4. Updated `project-detail.html` - Added invoices section

## Usage Flow

1. User views a project and clicks "Create Invoice"
2. User fills out invoice details and selects time entries
3. System calculates total amount based on hours worked
4. User can edit invoice details and add/remove time entries
5. User can mark invoice as "sent" or "paid"
6. System tracks payment date when invoice is marked as paid
7. User can view all invoices with filtering options
8. User can download PDF invoice (future enhancement)

## Future Enhancements

1. PDF Generation
   - Generate PDF files from invoice data
   - Store PDF files on the server
   - Allow downloading generated PDFs

2. Email Integration
   - Send invoices directly to clients
   - Track email status

3. Reporting
   - Generate reports on invoicing status
   - Track payment history
   - Calculate revenue statistics