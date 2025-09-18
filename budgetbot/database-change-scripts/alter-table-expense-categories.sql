alter table expense_categories add column expense_category_uuid not null default uuid4();
alter table expense_categories add column inserted_by uuid not null
references people (person_uuid) default (select person_uuid from people where email_address = 'rob@216software.com');

alter table expense_categories add column parent_category references expense_categories (expense_category_uuid);

alter table expense_categories drop expense_categories_pkey;
alter table expense_categories add primary key (expense_category_uuuid);

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



