# Project Time Tracking Feature Plan (IMPLEMENTED)

> **Status: Completed on April 24, 2025**  
> This feature has been fully implemented according to the plan below with the following modifications:
> - Used single-responsibility handler classes instead of multi-action handlers
> - Added more detailed frontend templates with proper error handling
> - Improved the API URL structure to follow RESTful patterns

## Database Changes
1. Create new tables:
   - `projects` table:
     ```sql
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
     ```

   - `time_entries` table:
     ```sql
     create table time_entries
     (
         time_entry_uuid uuid primary key default uuid_generate_v4(),
         project_uuid uuid not null references projects (project_uuid),
         person_uuid uuid not null references people (person_uuid),
         start_time timestamp not null,
         end_time timestamp,
         description text,
         inserted timestamp not null default now(),
         updated timestamp
     );

     create trigger time_entries_set_updated_column
     before update
     on time_entries
     for each row
     execute procedure set_updated_column();
     ```

## Backend Components
1. Database schema changes:
   - Create SQL migration script for new tables: `add-projects-timetracking.sql`
   - Update `script-run-order.yaml` to include the new migration

2. Python modules:
   - Add `projects.py` in `budgetbot/pg/` for project database operations
   - Add `timeentries.py` in `budgetbot/pg/` for time entry operations
   - Register composite types for projects and time entries in `configwrapper.py`:
     ```python
     from budgetbot.pg.projects import ProjectFactory, TimeEntryFactory

     psycopg2.extras.register_composite('projects', pgconn,
       factory=ProjectFactory)

     psycopg2.extras.register_composite('time_entries', pgconn,
       factory=TimeEntryFactory)
     ```

3. Handlers:
   - Create `budgetbot/webapp/timetracking/` package with:
     - `__init__.py`
     - `handlers.py`
     - `templates/` directory
   - Implement handlers for projects and time entries CRUD operations
   - Update dispatcher.py to include the new handlers:
     ```python
     self.handlers.extend(self.make_handlers_from_module_string(
         'budgetbot.webapp.timetracking.handlers'))
     ```

## Frontend Components
1. Templates:
   - Project list view: `timetracking/templates/projects.html`
   - Project detail view: `timetracking/templates/project-detail.html`
   - Add/edit project form: `timetracking/templates/project-form.html`
   - Add/edit time entry form: `timetracking/templates/time-entry-form.html`

2. JavaScript:
   - Create ViewModels in `static/viewmodels/`:
     - `projectsviewmodel.js`: List and manage projects
     - `timetrackingviewmodel.js`: Track time with start/stop functionality
     - `timereportsviewmodel.js`: Time reports and visualizations

## Implementation Plan
1. Database schema changes
2. Backend API implementation
3. Frontend templates and basic UI
4. Time tracking UI with enhanced features