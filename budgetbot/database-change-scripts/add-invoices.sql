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

create index invoices_project_uuid_idx on invoices(project_uuid);
create index invoices_invoice_number_idx on invoices(invoice_number);
create index invoices_status_idx on invoices(status);

create table if not exists invoice_time_entries (
    invoice_uuid uuid not null references invoices(invoice_uuid) on delete cascade,
    time_entry_uuid uuid not null references time_entries(time_entry_uuid),
    primary key (invoice_uuid, time_entry_uuid)
);

create index invoice_time_entries_invoice_uuid_idx on invoice_time_entries(invoice_uuid);
create index invoice_time_entries_time_entry_uuid_idx on invoice_time_entries(time_entry_uuid);

-- Create a trigger to update the 'updated' timestamp whenever an invoice is modified
create or replace function update_invoices_updated() returns trigger as $$
begin
    new.updated = now();
    return new;
end;
$$ language plpgsql;

create trigger update_invoices_updated_trigger
before update on invoices
for each row
execute function update_invoices_updated();

-- View to get invoice details with project information
create or replace view invoices_with_details as
select
    i.*,
    p.title as project_title,
    p.description as project_description,
    p.created_by as project_created_by
from
    invoices i
    join projects p on i.project_uuid = p.project_uuid;

-- View to get invoice with all time entries
create or replace view invoice_with_time_entries as
select
    i.*,
    te.time_entry_uuid,
    te.person_uuid,
    te.entry_date,
    te.hours_worked,
    te.description as entry_description,
    p.display_name as person_name
from
    invoices i
    join invoice_time_entries ite on i.invoice_uuid = ite.invoice_uuid
    join time_entries te on ite.time_entry_uuid = te.time_entry_uuid
    join people p on te.person_uuid = p.person_uuid;
