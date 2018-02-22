/* Delete everything and then rewrite */


delete from shopping_list_items;
delete from shopping_categories;
delete from stores;

drop table shopping_list_items;
drop table shopping_categories;
drop table stores;

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
('other');

create table shopping_lists
(
    shopping_list_id serial primary key,
    shopping_list_name citext not null,

    store citext not null references stores(store),

    creator_uuid uuid not null references people(person_uuid),

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger shopping_lists_set_updated_column
before update
on shopping_lists
for each row
execute procedure set_updated_column();

/* We can connect other users to our shopping lists */
create table shopping_lists_people
(
    shopping_list_id integer not null
    references shopping_lists (shopping_list_id),

    person_uuid uuid not null
    references people (person_uuid),

    primary key (shopping_list_id, person_uuid),

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger shopping_lists_people_set_updated_column
before update
on shopping_lists_people
for each row
execute procedure set_updated_column();


create table items(
    item citext primary key,

    inserted_by uuid references people(person_uuid),

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger items_set_updated_column
before update
on items
for each row
execute procedure set_updated_column();


create table shopping_list_items
(
    item citext not null references items(item),

    shopping_list_id integer not null references
    shopping_lists(shopping_list_id),

    inserted_by uuid references people(person_uuid),

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger shopping_list_items_set_updated_column
before update
on shopping_list_items
for each row
execute procedure set_updated_column();


