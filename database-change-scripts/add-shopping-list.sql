create table shopping_categories
(
    title citext primary key,
    description text,
    inserted timestamp not null default now(),
    updated timestamp
);

create trigger shopping_categories_set_updated_column
before update
on shopping_categories
for each row
execute procedure set_updated_column();

insert into shopping_categories
(title)
values
('long term'),
('short term');


create table shopping_list_items
(

    item citext primary key,

    shopping_category citext not null references
    shopping_categories(title),

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger shopping_list_items_set_updated_column
before update
on shopping_list_items
for each row
execute procedure set_updated_column();

