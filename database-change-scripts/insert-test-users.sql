insert into people
(
    email_address,
    display_name,
    salted_hashed_password,
    person_status,
    is_superuser
)
values


(
    'rob@216software.com',
    'Rob',
    crypt('abc123', gen_salt('md5')),
    'confirmed',
    false
),

(
    'deborah.riemann@googlemail.com',
    'Debby',
    crypt('abc123', gen_salt('md5')),
    'confirmed',
    false
)
;
