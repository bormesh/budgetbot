
-- The only thing that goes in the cookie should be the session ID and
-- the signature.  Everything else goes in here.  Deal with it.
create table webapp_sessions
(
    session_id serial primary key,
    expires timestamp not null default now() + interval '60 minutes',

    person_id integer
    references people (person_id)
    on delete cascade
    on update cascade,

    news_message text,
    redirect_to_url text,

    inserted timestamp not null default now(),
    updated timestamp
);

create trigger webapp_sessions_set_updated_column
before update
on webapp_sessions
for each row
execute procedure set_updated_column();


create table webapp_session_data
(
    session_id integer not null
    references webapp_sessions (session_id)
    on delete cascade
    on update cascade,

    -- namespace is a crappy name and when I figure out a better name,
    -- I'll rename this column.

    -- The point is to allow you to separate data into separate
    -- categories.

    -- For example, each HTML form could store the user's submitted data
    -- (for redrawing later) in a separate namespace.

    namespace text not null,

    primary key (session_id, namespace),
    session_data hstore,
    inserted timestamp not null default now(),
    updated timestamp
);

create trigger webapp_session_data_set_updated_column
before update
on webapp_session_data
for each row
execute procedure set_updated_column();

