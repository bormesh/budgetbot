create table expense_categories
(
    title citext primary key,
    description text,
    inserted timestamp not null default now(),
    updated timestamp
);

create trigger expense_categories_set_updated_column
before update
on expense_categories
for each row
execute procedure set_updated_column();

insert into expense_categories
(title)
values
('office rent'),
('hosting fees'),
('cell phones'),
('marketing stuff (biz cards, shirts, etc)'),
('parking fees'),
('meals'),
('office supplies'),
('contract work');

create table vendors
(
    title citext primary key,
    description text,
    inserted timestamp not null default now(),
    updated timestamp
);

insert into vendors
(title)
values
('Micro Center'),
('Pho and Rice'),
('Linode'),
('Rackspace'),
('Sprint');

create trigger vendors_set_updated_column
before update
on vendors
for each row
execute procedure set_updated_column();

create table expenses
(
    expense_uuid uuid primary key default uuid_generate_v4(),

    description text not null,

    amount float not null,

    -- This means what accounting month we should use.
    accounting_date date not null,

    unique(description, amount, accounting_date),

    extra_notes text,

    client_uuid uuid references clients (client_uuid)
    on delete set null on update cascade,

    project_uuid uuid references projects (project_uuid)
    on delete set null on update cascade,

    vendor citext references vendors (title)
    on delete set null on update cascade,

    category citext references expense_categories (title)
    on delete set null on update cascade,

    -- Use this array to tell the database where to find related
    -- pictures of receipts, emailed PDFs, etc.
    attached_file_URLs citext[],

    invoice_id integer references invoices (invoice_id)
    on delete set null on update cascade,

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger expenses_set_updated_column
before update
on expenses
for each row
execute procedure set_updated_column();
