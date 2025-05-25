# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import datetime
import json
import logging
import re
import textwrap
import uuid

from budgetbot.pg import projects
from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response

log = logging.getLogger(__name__)

module_template_prefix = 'timetracking'
module_template_package = 'budgetbot.webapp.timetracking.templates'

# Project handlers

class ProjectsListHandler(Handler):
    """
    Handler for displaying the projects list page.
    """

    route_strings = set(['GET /projects'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        all_projects = projects.Project.get_all(self.cw.get_pgconn())

        return Response.tmpl('timetracking/projects.html',
			user=req.user,
			projects=all_projects
        )

class ProjectDetailHandler(Handler):
    """
    Handler for displaying a specific project's details.
    """

    route_pattern = re.compile(r'GET /projects/(?P<project_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$')

    def route(self, req):

        match = self.route_pattern == req.line_one

        if match:
            req['project_uuid'] = match.groupdict()['project_uuid']
            return self.handle
    @Handler.require_login
    def handle(self, req):
        project_uuid = req['project_uuid']
        try:
            project = projects.Project.by_uuid(
                self.cw.get_pgconn(), project_uuid)
        except KeyError:
            return self.not_found(req)

        time_entries = projects.TimeEntryWithDetails.for_project(
            self.cw.get_pgconn(), project_uuid)

        return Response.tmpl('timetracking/project-detail.html',
            user= req.user,
            project= project,
            time_entries= time_entries
        )

class ProjectNewFormHandler(Handler):
    """
    Handler for the form to create a new project.
    """

    route_strings = set(['GET /projects/new'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        j = self.cw.get_jinja2_environment()
        t = j.get_template('timetracking/project-form.html')

        return Response.tmpl(t,
            user= req.user,
            project= None
        )

class ProjectEditFormHandler(Handler):
    """
    Handler for the form to edit an existing project.
    """

    route_pattern = re.compile(r'GET /projects/(?P<project_uuid>[0-9a-f-]+)/edit/?$')

    def route(self, req):

        match = self.route_pattern == req.line_one

        if match:
            req['project_uuid'] = match.groupdict()['project_uuid']
            return self.handle

    @Handler.require_login
    def handle(self, req):
        project_uuid = req.match_info.get('project_uuid')
        if not project_uuid:
            return self.not_found(req)

        try:
            uuid.UUID(project_uuid)
        except ValueError:
            return self.not_found(req)

        try:
            project = projects.Project.by_uuid(
                self.cw.get_pgconn(), project_uuid)
        except KeyError:
            return self.not_found(req)

        j = self.cw.get_jinja2_environment()
        t = j.get_template('timetracking/project-form.html')

        return Response.tmpl(t, {
            'user': req.user,
            'project': project
        })

class ProjectCreateHandler(Handler):
    """
    Handler for creating a new project.
    """

    route_strings = set([r'POST /api/projects/create'])
    route = Handler.check_route_strings

    required_json_keys = ['title']

    @Handler.require_login
    @Handler.require_json
    def handle(self, req):
        title = req.json.get('title')
        description = req.json.get('description', '')

        try:
            project = projects.Project.create(
                self.cw.get_pgconn(),
                title=title,
                description=description,
                created_by=req.user.person_uuid
            )

            return Response.json({
                'success': True,
                'message': 'Project created successfully',
                'project': project.__jsondata__
            })

        except Exception as e:
            log.error(f"Error creating project: {e}")
            return Response.json({
                'success': False,
                'message': 'Error creating project'
            })

class ProjectUpdateHandler(Handler):
    """
    Handler for updating an existing project.
    """

    route_pattern =\
        re.compile(r'/api/projects/(?P<project_uuid>[0-9a-f-]+)/update/?$')

    def route(self, req):

        match = self.route_pattern == req.line_one

        if match:
            req['project_uuid'] = match.groupdict()['project_uuid']
            return self.handle

    @Handler.require_login
    @Handler.require_json
    def handle(self, req):
        project_uuid = req.match_info.get('project_uuid')
        if not project_uuid:
            return Response.json({
                'success': False,
                'message': 'Project UUID is required'
            })

        try:
            project = projects.Project.by_uuid(
                self.cw.get_pgconn(), project_uuid)

            title = req.json.get('title', None)
            description = req.json.get('description', None)
            active = req.json.get('active', None)

            if active is not None:
                active = bool(active)

            updated_project = project.update(
                self.cw.get_pgconn(),
                title=title,
                description=description,
                active=active
            )

            return Response.json({
                'success': True,
                'message': 'Project updated successfully',
                'project': updated_project.__jsondata__
            })

        except KeyError:
            return Response.json({
                'success': False,
                'message': 'Project not found'
            })
        except Exception as e:
            log.error(f"Error updating project: {e}")
            return Response.json({
                'success': False,
                'message': 'Error updating project'
            })

class ProjectsApiListHandler(Handler):
    """
    Handler for listing projects via API.
    """

    route_pattern = re.compile(r'GET /api/projects/list/?$')
    def route(self, req):
        match = self.route_pattern == req.line_one

        if match:
            return self.handle

    @Handler.require_login
    def handle(self, req):
        active_only = True #req.GET.get('active_only', 'true').lower() == 'true'

        try:
            all_projects = projects.Project.get_all(
                self.cw.get_pgconn(), active_only=active_only)

            return Response.json({
                'success': True,
                'projects': [p.__jsondata__ for p in all_projects]
            })

        except Exception as e:
            log.error(f"Error listing projects: {e}")
            return Response.json({
                'success': False,
                'message': 'Error listing projects'
            })

# Time entry handlers

class TimeEntryNewFormHandler(Handler):
    """
    Handler for the form to create a new time entry.
    """

    route_strings = set([r'GET /time-entries/new'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        all_projects = projects.Project.get_all(self.cw.get_pgconn())

        j = self.cw.get_jinja2_environment()
        t = j.get_template('timetracking/time-entry-form.html')

        return Response.tmpl(t,
            user= req.user,
            time_entry= None,
            projects= all_projects
        )

class TimeEntryEditFormHandler(Handler):
    """
    Handler for the form to edit an existing time entry.
    """

    route_pattern =\
    re.compile(r'GET /time-entries/(?P<time_entry_uuid>[0-9a-f-]+)/edit/?$')

    def route(self, req):

        match = self.route_pattern == req.line_one

        if match:
            req['time_entry_uuid'] = match.groupdict()['time_entry_uuid']
            return self.handle

    @Handler.require_login
    def handle(self, req):
        time_entry_uuid = req['time_entry_uuid']
        if not time_entry_uuid:
            return self.not_found(req)

        try:
            uuid.UUID(time_entry_uuid)
        except ValueError:
            return self.not_found(req)

        try:
            time_entry = projects.TimeEntry.by_uuid(
                self.cw.get_pgconn(), time_entry_uuid)

            # Check if the time entry belongs to the current user
            if time_entry.person_uuid != req.user.person_uuid:
                return self.not_found(req)

        except KeyError:
            return self.not_found(req)

        all_projects = projects.Project.get_all(self.cw.get_pgconn())

        j = self.cw.get_jinja2_environment()
        t = j.get_template('timetracking/time-entry-form.html')

        return Response.tmpl(t,
            user= req.user,
            time_entry= time_entry,
            projects= all_projects
        )

class TimeEntryCreateHandler(Handler):
    """
    Handler for creating a new time entry.
    """

    route_strings = set(['POST /api/time-entries/create'])
    route = Handler.check_route_strings

    required_json_keys = ['project_uuid', 'hours_worked']

    @Handler.require_login
    @Handler.require_json
    def handle(self, req):
        project_uuid = req.json.get('project_uuid')

        try:
            hours_worked = float(req.json.get('hours_worked'))
        except (TypeError, ValueError):
            return Response.json({
                'success': False,
                'message': 'Hours worked must be a number'
            })

        entry_date = req.json.get('entry_date')
        description = req.json.get('description', '')

        # If entry_date is provided as a string, convert to date object
        if entry_date and isinstance(entry_date, str):
            try:
                entry_date = datetime.datetime.strptime(entry_date, '%Y-%m-%d').date()
            except ValueError:
                return Response.json({
                    'success': False,
                    'message': 'Invalid date format, use YYYY-MM-DD'
                })

        try:
            time_entry = projects.TimeEntry.create(
                self.cw.get_pgconn(),
                project_uuid=project_uuid,
                person_uuid=req.user.person_uuid,
                hours_worked=hours_worked,
                entry_date=entry_date,
                description=description
            )

            return Response.json({
                'success': True,
                'message': 'Time entry created successfully',
                'time_entry': time_entry
            })

        except Exception as e:
            log.error(f"Error creating time entry: {e}")
            return Response.json({
                'success': False,
                'message': 'Error creating time entry'
            })

class TimeEntryUpdateHandler(Handler):
    """
    Handler for updating an existing time entry.
    """

    route_pattern = r'/api/time-entries/(?P<time_entry_uuid>[0-9a-f-]+)/update/?$'

    def route(self, req):

        match = self.route_pattern == req.line_one

        if match:
            req['time_entry_uuid'] = match.groupdict()['time_entry_uuid']
            return self.handle


    @Handler.require_login
    @Handler.require_json
    def handle(self, req):
        time_entry_uuid = req.match_info.get('time_entry_uuid')
        if not time_entry_uuid:
            return Response.json({
                'success': False,
                'message': 'Time entry UUID is required'
            })

        try:
            time_entry = projects.TimeEntry.by_uuid(
                self.cw.get_pgconn(), time_entry_uuid)

            # Check if the time entry belongs to the current user
            if time_entry.person_uuid != req.user.person_uuid:
                return Response.json({
                    'success': False,
                    'message': 'You can only edit your own time entries'
                })

            hours_worked = req.json.get('hours_worked')
            if hours_worked is not None:
                try:
                    hours_worked = float(hours_worked)
                except (TypeError, ValueError):
                    return Response.json({
                        'success': False,
                        'message': 'Hours worked must be a number'
                    })

            entry_date = req.json.get('entry_date')
            # If entry_date is provided as a string, convert to date object
            if entry_date and isinstance(entry_date, str):
                try:
                    entry_date = datetime.datetime.strptime(entry_date, '%Y-%m-%d').date()
                except ValueError:
                    return Response.json({
                        'success': False,
                        'message': 'Invalid date format, use YYYY-MM-DD'
                    })

            description = req.json.get('description')

            updated_time_entry = time_entry.update(
                self.cw.get_pgconn(),
                hours_worked=hours_worked,
                entry_date=entry_date,
                description=description
            )

            return Response.json({
                'success': True,
                'message': 'Time entry updated successfully',
                'time_entry': updated_time_entry.__jsondata__
            })

        except KeyError:
            return Response.json({
                'success': False,
                'message': 'Time entry not found'
            })
        except Exception as e:
            log.error(f"Error updating time entry: {e}")
            return Response.json({
                'success': False,
                'message': 'Error updating time entry'
            })

class TimeEntriesForProjectHandler(Handler):
    """
    Handler for listing time entries for a specific project.
    """

    route_pattern =\
    re.compile(r'/api/projects/(?P<project_uuid>[0-9a-f-]+)/time-entries/?$')

    def route(self, req):

        match = self.route_pattern == req.line_one

        if match:
            req['project_uuid'] = match.groupdict()['project_uuid']
            return self.handle

    @Handler.require_login
    def handle(self, req):
        project_uuid = req.match_info.get('project_uuid')
        if not project_uuid:
            return Response.json({
                'success': False,
                'message': 'Project UUID is required'
            })

        try:
            limit = int(req.GET.get('limit', '100'))
            offset = int(req.GET.get('offset', '0'))
        except ValueError:
            limit = 100
            offset = 0

        try:
            time_entries = projects.TimeEntryWithDetails.for_project(
                self.cw.get_pgconn(), project_uuid, limit, offset)

            return Response.json({
                'success': True,
                'time_entries': [te.__jsondata__ for te in time_entries]
            })

        except Exception as e:
            log.error(f"Error listing time entries for project: {e}")
            return Response.json({
                'success': False,
                'message': 'Error listing time entries'
            })

class TimeEntriesForPersonHandler(Handler):
    """
    Handler for listing time entries for the current user.
    """

    route_strings = set(['GET /api/my-time-entries'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        person_uuid = req.user.person_uuid

        try:
            limit = int(req.GET.get('limit', '100'))
            offset = int(req.GET.get('offset', '0'))
        except ValueError:
            limit = 100
            offset = 0

        try:
            time_entries = projects.TimeEntryWithDetails.for_person(
                self.cw.get_pgconn(), person_uuid, limit, offset)

            return Response.json({
                'success': True,
                'time_entries': [te.__jsondata__ for te in time_entries]
            })

        except Exception as e:
            log.error(f"Error listing time entries for person: {e}")
            return Response.json({
                'success': False,
                'message': 'Error listing time entries'
            })

class MyTimeEntriesPageHandler(Handler):
    """
    Handler for the page displaying the current user's time entries.
    """

    route_strings = set(['GET /my-time-entries'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        person_uuid = req.user.person_uuid

        time_entries = projects.TimeEntryWithDetails.for_person(
            self.cw.get_pgconn(), person_uuid, limit=100)

        j = self.cw.get_jinja2_environment()
        t = j.get_template('timetracking/my-time-entries.html')

        return Response.tmpl(t,
            user= req.user,
            time_entries= time_entries
        )
