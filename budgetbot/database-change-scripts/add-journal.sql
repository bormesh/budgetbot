create table journal_entries(

    journal_id serial primary key,

    entry text not null,

    person_uuid uuid not null references people (person_uuid),

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger journal_entries_set_updated_column
before update
on journal_entries
for each row
execute procedure set_updated_column();
