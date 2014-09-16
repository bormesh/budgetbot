create table types_of_work
(
    title citext primary key,
    description text,
    inserted timestamp not null default now(),
    updated timestamp
);

create trigger types_of_work_set_updated_column
before update
on types_of_work
for each row
execute procedure set_updated_column();

insert into types_of_work
(title)
values
('development'),
('meet with potential client'),
('meet with paying client');

create table timesheets
(

    workerbee_id integer not null references people (person_id),

    project_uuid uuid not null references projects (project_uuid)
    on delete cascade on update cascade,

    date_worked date not null,

    interval_worked interval not null,

    work_type citext not null references types_of_work (title)
    on delete cascade on update cascade,

    billable boolean not null,

    unique (workerbee_id, project_uuid, date_worked, interval_worked,
        work_type),

    extra_notes text,

    inserted timestamp not null default now(),
    updated timestamp

);

create trigger timesheet_set_updated_column
before update
on timesheets
for each row
execute procedure set_updated_column();
