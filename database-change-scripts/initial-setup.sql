/* For searching */
create extension pg_trgm;

create table budgetbot_schema_version
(
    script_path citext primary key,
    script_contents text,
    inserted timestamp not null default now(),
    updated timestamp
);

create or replace function set_updated_column ()
returns trigger
as
$$

begin

    NEW.updated = now();
    return NEW;

end;
$$
language plpgsql;

create trigger budgetbot_schema_version_set_updated_column
before update
on budgetbot_schema_version
for each row
execute procedure set_updated_column();
