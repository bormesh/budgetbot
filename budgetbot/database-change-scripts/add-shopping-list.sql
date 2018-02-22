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

create table stores
(
    store citext primary key,

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger stores_set_updated_column
before update
on stores
for each row
execute procedure set_updated_column();

insert into stores
(store)
values
('grocery'),
('pharmacy'),
('baumarkt' ),
('ikea'),
('department store'),
('clothing'),
('electronics'),
('unknown');

create table shopping_list_items
(

    item citext primary key,

    shopping_category citext not null references
    shopping_categories(title),

    store citext not null references
    stores (store),


    inserted timestamp not null default now(),
    updated timestamp
);

create trigger shopping_list_items_set_updated_column
before update
on shopping_list_items
for each row
execute procedure set_updated_column();


