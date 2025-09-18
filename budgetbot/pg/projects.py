# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import datetime
import logging
import textwrap

import psycopg2.extras

log = logging.getLogger(__name__)

class ProjectFactory(psycopg2.extras.CompositeCaster):
    def make(self, values):
        d = dict(zip(self.attnames, values))
        return Project(**d)

class TimeEntryFactory(psycopg2.extras.CompositeCaster):
    def make(self, values):
        d = dict(zip(self.attnames, values))
        return TimeEntry(**d)

class TimeEntryWithDetailsFactory(psycopg2.extras.CompositeCaster):
    def make(self, values):
        d = dict(zip(self.attnames, values))
        return TimeEntryWithDetails(**d)

class Project(object):
    def __init__(self, project_uuid, title, description, 
                 created_by, active, inserted, updated):
        self.project_uuid = project_uuid
        self.title = title
        self.description = description
        self.created_by = created_by
        self.active = active
        self.inserted = inserted
        self.updated = updated

    def __repr__(self):
        return '<{0}.{1} ({2}:{3}) at 0x{4:x}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.project_uuid,
            self.title,
            id(self))

    @property
    def __jsondata__(self):
        return {k:v for (k, v) in self.__dict__.items()
            if k in set([
                'project_uuid',
                'title',
                'description',
                'created_by',
                'active',
                'inserted'])}
                
    @classmethod
    def get_all(cls, pgconn, active_only=True):
        """
        Get all projects, optionally filtering by active status.
        """
        
        cursor = pgconn.cursor()
        
        if active_only:
            cursor.execute(textwrap.dedent("""
                select (p.*)::projects as p
                from projects p
                where active = true
                order by title
                """))
        else:
            cursor.execute(textwrap.dedent("""
                select (p.*)::projects as p
                from projects p
                order by title
                """))
        
        if cursor.rowcount:
            return [row.p for row in cursor]
        else:
            return []

    @classmethod
    def by_uuid(cls, pgconn, project_uuid):
        """
        Get a project by its UUID.
        """
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            select (p.*)::projects as p
            from projects p
            where project_uuid = %(project_uuid)s
            """), {'project_uuid': project_uuid})
        
        if cursor.rowcount:
            return cursor.fetchone().p
        else:
            raise KeyError(f"No project with UUID {project_uuid} found")

    @classmethod
    def create(cls, pgconn, title, description, created_by):
        """
        Create a new project.
        """
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            insert into projects
            (title, description, created_by)
            values
            (%(title)s, %(description)s, %(created_by)s)
            returning (projects.*)::projects as p
            """), {
                'title': title,
                'description': description,
                'created_by': created_by
            })
        
        if cursor.rowcount:
            return cursor.fetchone().p
        else:
            return None

    def update(self, pgconn, title=None, description=None, active=None):
        """
        Update this project.
        """
        
        update_parts = []
        params = {'project_uuid': self.project_uuid}
        
        if title is not None:
            update_parts.append("title = %(title)s")
            params['title'] = title
        
        if description is not None:
            update_parts.append("description = %(description)s")
            params['description'] = description
        
        if active is not None:
            update_parts.append("active = %(active)s")
            params['active'] = active
        
        if not update_parts:
            return self
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            update projects
            set {update_parts}
            where project_uuid = %(project_uuid)s
            returning (projects.*)::projects as p
            """).format(update_parts=", ".join(update_parts)), params)
        
        if cursor.rowcount:
            return cursor.fetchone().p
        else:
            raise KeyError(f"No project with UUID {self.project_uuid} found")


class TimeEntry(object):
    def __init__(self, time_entry_uuid, project_uuid, person_uuid,
                 entry_date, hours_worked, description, inserted, updated):
        self.time_entry_uuid = time_entry_uuid
        self.project_uuid = project_uuid
        self.person_uuid = person_uuid
        self.entry_date = entry_date
        self.hours_worked = hours_worked
        self.description = description
        self.inserted = inserted
        self.updated = updated

    def __repr__(self):
        return '<{0}.{1} ({2}:{3}h) at 0x{4:x}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.time_entry_uuid,
            self.hours_worked,
            id(self))

    @property
    def __jsondata__(self):
        return {k:v for (k, v) in self.__dict__.items()
            if k in set([
                'time_entry_uuid',
                'project_uuid',
                'person_uuid',
                'entry_date',
                'hours_worked',
                'description',
                'inserted'])}

    @classmethod
    def create(cls, pgconn, project_uuid, person_uuid, hours_worked, entry_date=None, description=None):
        """
        Create a new time entry.
        """
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            insert into time_entries
            (project_uuid, person_uuid, hours_worked, entry_date, description)
            values
            (%(project_uuid)s, %(person_uuid)s, %(hours_worked)s, 
             %(entry_date)s, %(description)s)
            returning (time_entries.*)::time_entries as te
            """), {
                'project_uuid': project_uuid,
                'person_uuid': person_uuid,
                'hours_worked': hours_worked,
                'entry_date': entry_date or datetime.date.today(),
                'description': description
            })
        
        if cursor.rowcount:
            return cursor.fetchone().te
        else:
            return None

    @classmethod
    def by_uuid(cls, pgconn, time_entry_uuid):
        """
        Get a time entry by its UUID.
        """
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            select (te.*)::time_entries as te
            from time_entries te
            where time_entry_uuid = %(time_entry_uuid)s
            """), {'time_entry_uuid': time_entry_uuid})
        
        if cursor.rowcount:
            return cursor.fetchone().te
        else:
            raise KeyError(f"No time entry with UUID {time_entry_uuid} found")

    def update(self, pgconn, hours_worked=None, entry_date=None, description=None):
        """
        Update this time entry.
        """
        
        update_parts = []
        params = {'time_entry_uuid': self.time_entry_uuid}
        
        if hours_worked is not None:
            update_parts.append("hours_worked = %(hours_worked)s")
            params['hours_worked'] = hours_worked
        
        if entry_date is not None:
            update_parts.append("entry_date = %(entry_date)s")
            params['entry_date'] = entry_date
        
        if description is not None:
            update_parts.append("description = %(description)s")
            params['description'] = description
        
        if not update_parts:
            return self
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            update time_entries
            set {update_parts}
            where time_entry_uuid = %(time_entry_uuid)s
            returning (time_entries.*)::time_entries as te
            """).format(update_parts=", ".join(update_parts)), params)
        
        if cursor.rowcount:
            return cursor.fetchone().te
        else:
            raise KeyError(f"No time entry with UUID {self.time_entry_uuid} found")

    @classmethod
    def for_project(cls, pgconn, project_uuid, limit=100, offset=0):
        """
        Get time entries for a specific project.
        """
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            select (te.*)::time_entries as te
            from time_entries te
            where project_uuid = %(project_uuid)s
            order by entry_date desc, inserted desc
            limit %(limit)s offset %(offset)s
            """), {
                'project_uuid': project_uuid,
                'limit': limit,
                'offset': offset
            })
        
        if cursor.rowcount:
            return [row.te for row in cursor]
        else:
            return []

    @classmethod
    def for_person(cls, pgconn, person_uuid, limit=100, offset=0):
        """
        Get time entries for a specific person.
        """
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            select (te.*)::time_entries as te
            from time_entries te
            where person_uuid = %(person_uuid)s
            order by entry_date desc, inserted desc
            limit %(limit)s offset %(offset)s
            """), {
                'person_uuid': person_uuid,
                'limit': limit,
                'offset': offset
            })
        
        if cursor.rowcount:
            return [row.te for row in cursor]
        else:
            return []


class TimeEntryWithDetails(object):
    def __init__(self, time_entry_uuid, project_uuid, project_title,
                 person_uuid, person_name, entry_date, hours_worked, 
                 description, inserted, updated):
        self.time_entry_uuid = time_entry_uuid
        self.project_uuid = project_uuid
        self.project_title = project_title
        self.person_uuid = person_uuid
        self.person_name = person_name
        self.entry_date = entry_date
        self.hours_worked = hours_worked
        self.description = description
        self.inserted = inserted
        self.updated = updated

    def __repr__(self):
        return '<{0}.{1} ({2}:{3}h) at 0x{4:x}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.time_entry_uuid,
            self.hours_worked,
            id(self))

    @property
    def __jsondata__(self):
        return {k:v for (k, v) in self.__dict__.items()
            if k in set([
                'time_entry_uuid',
                'project_uuid',
                'project_title',
                'person_uuid',
                'person_name',
                'entry_date',
                'hours_worked',
                'description',
                'inserted'])}

    @classmethod
    def get_recent(cls, pgconn, limit=20):
        """
        Get recent time entries across all projects and people.
        """
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            select (ted.*)::time_entries_with_details as ted
            from time_entries_with_details ted
            order by entry_date desc, inserted desc
            limit %(limit)s
            """), {'limit': limit})
        
        if cursor.rowcount:
            return [row.ted for row in cursor]
        else:
            return []

    @classmethod
    def for_project(cls, pgconn, project_uuid, limit=100, offset=0):
        """
        Get detailed time entries for a specific project.
        """
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            select (ted.*)::time_entries_with_details as ted
            from time_entries_with_details ted
            where project_uuid = %(project_uuid)s
            order by entry_date desc, inserted desc
            limit %(limit)s offset %(offset)s
            """), {
                'project_uuid': project_uuid,
                'limit': limit,
                'offset': offset
            })
        
        if cursor.rowcount:
            return [row.ted for row in cursor]
        else:
            return []

    @classmethod
    def for_person(cls, pgconn, person_uuid, limit=100, offset=0):
        """
        Get detailed time entries for a specific person.
        """
        
        cursor = pgconn.cursor()
        
        cursor.execute(textwrap.dedent("""
            select (ted.*)::time_entries_with_details as ted
            from time_entries_with_details ted
            where person_uuid = %(person_uuid)s
            order by entry_date desc, inserted desc
            limit %(limit)s offset %(offset)s
            """), {
                'person_uuid': person_uuid,
                'limit': limit,
                'offset': offset
            })
        
        if cursor.rowcount:
            return [row.ted for row in cursor]
        else:
            return []