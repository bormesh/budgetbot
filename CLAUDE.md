# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Run Commands
- Install dependencies: `pip install -r requirements.txt`
- Run development server: `budgetbot/scripts/run-dev-webapp`
- Run production server: `budgetbot/scripts/run-webapp prod.yaml`
- Rebuild database: `budgetbot/scripts/rebuild-database config.yaml`
- Upgrade database: `budgetbot/scripts/upgrade-database config.yaml`

## Code Style Guidelines
- Python: 4-space indentation, expand tabs
- File header: `# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:`
- Use explicit imports, no wildcard imports
- Logger convention: `log = logging.getLogger(__name__)`
- Error handling: Use explicit exceptions with descriptive messages
- Database queries: Use named parameterized queries with textwrap.dedent for multiline SQL (e.g., `%(param_name)s`)
- Use decorators for common patterns (`@Handler.require_login`, `@Handler.require_json`)
- Naming: snake_case for variables/functions, CamelCase for classes
- DocStrings: Use triple-quoted strings for function docstrings
- Config wrapper pattern for environment-specific configuration
- Response.json: Use dict() syntax for creating response dictionaries (e.g., `dict(success=True, message="Success")`)

## Handler Pattern
- Use single-responsibility handler classes - one handler class per action (e.g., `ProjectCreateHandler`)
- Structure REST API URLs following resource patterns (e.g., `/api/projects/create`, `/api/time-entries/{uuid}/update`)
- Implement proper error handling in API responses with consistent success/failure JSON format
- Use class-level URL patterns with named capture groups for URL parameters
- For route patterns, use the re.compile() method and follow this pattern:
  ```python
  route_pattern = re.compile(r'GET /resources/(?P<resource_uuid>[0-9a-f-]+)/?')
  
  def route(self, req):
      match = self.route_pattern == req.line_one
      if match:
          req['resource_uuid'] = match.groupdict()['resource_uuid']
          return self.handle
  ```

## Database Schema
- Use UUID primary keys for all new tables (e.g., `project_uuid uuid primary key default uuid_generate_v4()`)
- Include `inserted` and `updated` timestamp columns on all tables
- Create triggers to maintain the `updated` column automatically
- Register composite types in `configwrapper.py` for PostgreSQL composite types
- Create appropriate indexes for foreign keys and frequently queried columns
- Use views for complex joins that are frequently needed
- Include proper cascade behavior for related tables
- For PostgreSQL composite types, use casting pattern: `(table.*)::composite_type as alias`
- Access composite type results with `row.alias` pattern, not factory methods

## Project Modules

### Time Tracking Module
- Projects have a title, description, created_by, and active status
- Time entries belong to a project and person with hours_worked and entry_date
- Each person can only edit their own time entries
- Access time entries with TimeEntryWithDetails for joined data
- Project detail pages show tabbed view: unbilled, billed, and all time entries
- Unbilled entries are shown by default for better workflow management

### Invoicing Module
- Invoices link to a project and contain client information
- Invoices can have time entries attached via invoice_time_entries junction table
- Invoices track status (draft, sent, paid) with appropriate dates
- PDF files can be attached to invoices using PDFManager
- Time entries become "billed" when associated with an invoice
- Use InvoiceWithDetails for queries that need project information

## File Storage
- PDF storage path is configured in the config wrapper
- File operations are handled by specialized manager classes
- Always validate file types and sanitize filenames
- Store files with UUID-based names to prevent conflicts
- Ensure proper file permissions and directory creation

## API Response Format
Always use a consistent response format for API endpoints:
```python
return Response.json(dict(
    success=True,  # or False for errors
    message="Human-readable message",
    data=result_object  # Optional, only for success responses
))
```