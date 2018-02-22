/* Delete everything and then rewrite */

alter table shopping_lists add column removed boolean default false;

