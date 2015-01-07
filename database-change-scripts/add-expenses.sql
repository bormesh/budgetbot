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
('rob lunch'),
('debby lunch'),
('going out dinner'),
('groceries'),
('entertainment'),
('fuel'),
('travel'),
('shopping'),
('other');


create table budgeted_expenses
(

    budgeted_expense_id serial primary key,

    expense_category citext not null references
    expense_categories(title),

    budgeted_amount float not null,

    effective tstzrange not null
    default daterange(now()::date, (now()::date + interval '30 days')::date)
);

alter table budgeted_expenses add constraint no_overlapping_budgeted_expenses
exclude using gist (
    cast (expense_category as text) with =,
    effective with &&);

-- When you insert a new budgeted category
-- this one updates the tstzrange for
-- the previous budget to be no longer effective.
create or replace function set_budgeted_expenses_in_use ()
returns trigger
as
$$

begin

update budgeted_expenses
set effective = tstzrange(lower(effective), now())
where now() <@ effective
and expense_category = NEW.expense_category;
return NEW;

end;
$$
language plpgsql;

create trigger budgeted_expenses_update_in_use
before insert
on budgeted_expenses
for each row
execute procedure set_budgeted_expenses_in_use();

insert into budgeted_expenses
(expense_category, budgeted_amount)
values

('rob lunch', 180),
('debby lunch', 60),
('going out dinner', 240),
('groceries', 450),
('entertainment', 100),
('fuel', 150),
('travel', 200),
('shopping', 250),
('other', 50);

create table expenses
(
    expense_uuid uuid primary key default uuid_generate_v4(),

    amount float not null default 0.0,

    expense_category citext not null references
    expense_categories (title),

    person_id integer not null
    references people (person_id),

    -- This means what accounting month we should use.
    expense_date date not null,

    extra_notes text,

    -- Use this array to tell the database where to find related
    -- pictures of receipts, emailed PDFs, etc.
    attached_file_URLs citext[],

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger expenses_set_updated_column
before update
on expenses
for each row
execute procedure set_updated_column();
