-- Create projects table
create table projects
(
    project_uuid uuid primary key default uuid_generate_v4(),
    title citext not null,
    description text,
    created_by uuid not null references people (person_uuid),
    active boolean not null default true,
    inserted timestamp not null default now(),
    updated timestamp
);

create trigger projects_set_updated_column
before update
on projects
for each row
execute procedure set_updated_column();

-- Create time entries table
create table time_entries
(
    time_entry_uuid uuid primary key default uuid_generate_v4(),
    project_uuid uuid not null references projects (project_uuid),
    person_uuid uuid not null references people (person_uuid),
    entry_date date not null default current_date,
    hours_worked float not null,
    description text,
    inserted timestamp not null default now(),
    updated timestamp
);

create trigger time_entries_set_updated_column
before update
on time_entries
for each row
execute procedure set_updated_column();

-- Create index for faster queries
create index time_entries_project_idx on time_entries (project_uuid);
create index time_entries_person_idx on time_entries (person_uuid);
create index time_entries_date_idx on time_entries (entry_date);

-- Create a view for easier reporting
create view time_entries_with_details as
select
    t.time_entry_uuid,
    t.project_uuid,
    p.title as project_title,
    t.person_uuid,
    pe.display_name as person_name,
    t.entry_date,
    t.hours_worked,
    t.description,
    t.inserted,
    t.updated
from
    time_entries t
    join projects p on t.project_uuid = p.project_uuid
    join people pe on t.person_uuid = pe.person_uuid;

-- Create a composite type for the view
create type time_entries_with_details_type as
(
    time_entry_uuid uuid,
    project_uuid uuid,
    project_title citext,
    person_uuid uuid,
    person_name text,
    entry_date date,
    hours_worked float,
    description text,
    inserted timestamp,
    updated timestamp
);
