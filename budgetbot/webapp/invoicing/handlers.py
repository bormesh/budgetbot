# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import datetime
import json
import logging
import os
import re
import textwrap
import uuid

from budgetbot.pg import projects, invoices
from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response
from budgetbot.webapp.invoicing.pdf import PDFManager

log = logging.getLogger(__name__)

module_template_prefix = 'invoicing'
module_template_package = 'budgetbot.webapp.invoicing.templates'

class InvoiceListHandler(Handler):
    """
    Handler for displaying the invoices list page.
    """

    route_strings = set(['GET /invoices'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        # Get filter parameters
        project_uuid = req.wz_req.args.get('project')
        status = req.wz_req.args.get('status')

        # Get all invoices with optional filters
        all_invoices = invoices.InvoiceWithDetails.get_all(
            self.cw.get_pgconn(),
            project_uuid=project_uuid,
            status=status
        )

        return Response.tmpl('timetracking/invoices.html',
            user=req.user,
            invoices=all_invoices,
            filters=dict(
                project_uuid=project_uuid,
                status=status
            )
        )

class InvoiceDetailHandler(Handler):
    """
    Handler for displaying a specific invoice's details.
    """

    route_pattern = re.compile(r'GET /invoices/(?P<invoice_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?')

    def route(self, req):
        match = self.route_pattern == req.line_one
        if match:
            req['invoice_uuid'] = match.groupdict()['invoice_uuid']
            return self.handle

    @Handler.require_login
    def handle(self, req):
        invoice_uuid = req['invoice_uuid']
        try:
            invoice = invoices.InvoiceWithDetails.by_uuid(
                self.cw.get_pgconn(), invoice_uuid)
        except KeyError:
            return self.not_found(req)

        time_entries = invoice.get_time_entries_with_details(self.cw.get_pgconn())

        # Generate PDF URL if a PDF is attached
        pdf_url = None
        if invoice.pdf_path:
            pdf_manager = PDFManager(self.cw)
            pdf_url = pdf_manager.get_pdf_url(invoice.pdf_path)

        return Response.tmpl('timetracking/invoice-detail.html',
            user=req.user,
            invoice=invoice,
            time_entries=time_entries,
            pdf_url=pdf_url
        )

class InvoiceNewFormHandler(Handler):
    """
    Handler for the form to create a new invoice.
    """

    route_strings = set(['GET /invoices/new'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        all_projects = projects.Project.get_all(self.cw.get_pgconn())

        # Pre-select a project if provided in query params
        selected_project_uuid = req.wz_req.args.get('project')

        j = self.cw.get_jinja2_environment()
        t = j.get_template('timetracking/invoice-form.html')

        return Response.tmpl(t,
            user=req.user,
            invoice=None,
            projects=all_projects,
            selected_project_uuid=selected_project_uuid
        )

class InvoiceEditFormHandler(Handler):
    """
    Handler for the form to edit an existing invoice.
    """

    route_pattern = re.compile(r'GET /invoices/(?P<invoice_uuid>[0-9a-f-]+)/edit/?')

    def route(self, req):
        match = self.route_pattern == req.line_one
        if match:
            req['invoice_uuid'] = match.groupdict()['invoice_uuid']
            return self.handle

    @Handler.require_login
    def handle(self, req):
        invoice_uuid = req['invoice_uuid']
        if not invoice_uuid:
            return self.not_found(req)

        try:
            uuid.UUID(invoice_uuid)
        except ValueError:
            return self.not_found(req)

        try:
            invoice = invoices.InvoiceWithDetails.by_uuid(
                self.cw.get_pgconn(), invoice_uuid)
        except KeyError:
            return self.not_found(req)

        all_projects = projects.Project.get_all(self.cw.get_pgconn())

        # Generate PDF URL if a PDF is attached
        pdf_url = None
        if invoice.pdf_path:
            pdf_manager = PDFManager(self.cw)
            pdf_url = pdf_manager.get_pdf_url(invoice.pdf_path)

        j = self.cw.get_jinja2_environment()
        t = j.get_template('timetracking/invoice-form.html')

        return Response.tmpl(t,
            user=req.user,
            invoice=invoice,
            projects=all_projects,
            selected_project_uuid=str(invoice.project_uuid),
            pdf_url=pdf_url
        )

class InvoiceCreateHandler(Handler):
    """
    Handler for creating a new invoice.
    """

    route_strings = set(['POST /api/invoices/create'])
    route = Handler.check_route_strings

    required_json_keys = ['project_uuid', 'client_name']

    @Handler.require_login
    @Handler.require_json
    def handle(self, req):
        project_uuid = req.json.get('project_uuid')
        client_name = req.json.get('client_name')
        client_address = req.json.get('client_address', '')
        invoice_number = req.json.get('invoice_number')
        total_amount = req.json.get('total_amount', 0.00)
        notes = req.json.get('notes', '')
        status = req.json.get('status', 'draft')

        try:
            total_amount = float(total_amount)
        except (TypeError, ValueError):
            total_amount = 0.00

        invoice_date = req.json.get('invoice_date')
        due_date = req.json.get('due_date')
        paid_date = req.json.get('paid_date')
        pdf_path = req.json.get('pdf_path')

        # Convert date strings to date objects
        if invoice_date and isinstance(invoice_date, str):
            try:
                invoice_date = datetime.datetime.strptime(invoice_date, '%Y-%m-%d').date()
            except ValueError:
                return Response.json(dict(
                    success=False,
                    message='Invalid invoice date format, use YYYY-MM-DD'
                ))

        if due_date and isinstance(due_date, str):
            try:
                due_date = datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                return Response.json(dict(
                    success=False,
                    message='Invalid due date format, use YYYY-MM-DD'
                ))

        if paid_date and isinstance(paid_date, str):
            try:
                paid_date = datetime.datetime.strptime(paid_date, '%Y-%m-%d').date()
            except ValueError:
                return Response.json(dict(
                    success=False,
                    message='Invalid paid date format, use YYYY-MM-DD'
                ))

        try:
            invoice = invoices.Invoice.create(
                self.cw.get_pgconn(),
                project_uuid=project_uuid,
                client_name=client_name,
                client_address=client_address,
                invoice_number=invoice_number,
                total_amount=total_amount,
                notes=notes,
                status=status,
                invoice_date=invoice_date,
                due_date=due_date,
                paid_date=paid_date,
                pdf_path=pdf_path
            )

            # Add time entries if provided
            time_entry_uuids = req.json.get('time_entry_uuids', [])
            for time_entry_uuid in time_entry_uuids:
                invoice.add_time_entry(self.cw.get_pgconn(), time_entry_uuid)

            # Update total if requested
            if req.json.get('calculate_total', False):
                hourly_rate = float(req.json.get('hourly_rate', 100.00))
                invoice = invoice.update_total_from_time_entries(
                    self.cw.get_pgconn(), hourly_rate)

            return Response.json(dict(
                success=True,
                message='Invoice created successfully',
                invoice=invoice
            ))

        except Exception as e:
            log.error(f"Error creating invoice: {e}")
            return Response.json(dict(
                success=False,
                message=f'Error creating invoice: {str(e)}'
            ))

class InvoiceUpdateHandler(Handler):
    """
    Handler for updating an existing invoice.
    """

    route_pattern = re.compile(r'POST /api/invoices/(?P<invoice_uuid>[0-9a-f-]+)/update/?')

    def route(self, req):
        match = self.route_pattern == req.line_one
        if match:
            req['invoice_uuid'] = match.groupdict()['invoice_uuid']
            return self.handle

    @Handler.require_login
    @Handler.require_json
    def handle(self, req):
        invoice_uuid = req['invoice_uuid']
        if not invoice_uuid:
            return Response.json(dict(
                success=False,
                message='Invoice UUID is required'
            ))

        try:
            invoice = invoices.Invoice.by_uuid(
                self.cw.get_pgconn(), invoice_uuid)

            invoice_number = req.json.get('invoice_number')
            client_name = req.json.get('client_name')
            client_address = req.json.get('client_address')
            total_amount = req.json.get('total_amount')
            notes = req.json.get('notes')
            status = req.json.get('status')
            pdf_path = req.json.get('pdf_path')

            if total_amount is not None:
                try:
                    total_amount = float(total_amount)
                except (TypeError, ValueError):
                    return Response.json(dict(
                        success=False,
                        message='Total amount must be a number'
                    ))

            invoice_date = req.json.get('invoice_date')
            due_date = req.json.get('due_date')
            paid_date = req.json.get('paid_date')

            # Convert date strings to date objects
            if invoice_date and isinstance(invoice_date, str):
                try:
                    invoice_date = datetime.datetime.strptime(invoice_date, '%Y-%m-%d').date()
                except ValueError:
                    return Response.json(dict(
                        success=False,
                        message='Invalid invoice date format, use YYYY-MM-DD'
                    ))

            if due_date and isinstance(due_date, str):
                try:
                    due_date = datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
                except ValueError:
                    return Response.json(dict(
                        success=False,
                        message='Invalid due date format, use YYYY-MM-DD'
                    ))

            if paid_date and isinstance(paid_date, str):
                try:
                    paid_date = datetime.datetime.strptime(paid_date, '%Y-%m-%d').date()
                except ValueError:
                    return Response.json(dict(
                        success=False,
                        message='Invalid paid date format, use YYYY-MM-DD'
                    ))

            # Special case: if status is being set to 'paid' and no paid_date is provided,
            # set paid_date to today
            if status == 'paid' and paid_date is None and invoice.status != 'paid':
                paid_date = datetime.date.today()

            updated_invoice = invoice.update(
                self.cw.get_pgconn(),
                invoice_number=invoice_number,
                client_name=client_name,
                client_address=client_address,
                total_amount=total_amount,
                notes=notes,
                status=status,
                invoice_date=invoice_date,
                due_date=due_date,
                paid_date=paid_date,
                pdf_path=pdf_path
            )

            # Update time entries if provided
            time_entry_uuids = req.json.get('time_entry_uuids')
            if time_entry_uuids is not None:
                # Get current time entries
                current_time_entries = updated_invoice.get_time_entries(self.cw.get_pgconn())
                current_time_entry_uuids = {str(te.time_entry_uuid) for te in current_time_entries}

                # Add new entries
                for time_entry_uuid in time_entry_uuids:
                    if time_entry_uuid not in current_time_entry_uuids:
                        updated_invoice.add_time_entry(self.cw.get_pgconn(), time_entry_uuid)

                # Remove entries not in the new list
                for time_entry in current_time_entries:
                    if str(time_entry.time_entry_uuid) not in time_entry_uuids:
                        updated_invoice.remove_time_entry(
                            self.cw.get_pgconn(), time_entry.time_entry_uuid)

            # Update total if requested
            if req.json.get('calculate_total', False):
                hourly_rate = float(req.json.get('hourly_rate', 100.00))
                updated_invoice = updated_invoice.update_total_from_time_entries(
                    self.cw.get_pgconn(), hourly_rate)

            return Response.json(dict(
                success=True,
                message='Invoice updated successfully',
                invoice=updated_invoice
            ))

        except KeyError:
            return Response.json(dict(
                success=False,
                message='Invoice not found'
            ))
        except Exception as e:
            log.error(f"Error updating invoice: {e}")
            return Response.json(dict(
                success=False,
                message=f'Error updating invoice: {str(e)}'
            ))

class InvoiceMarkAsPaidHandler(Handler):
    """
    Handler for marking an invoice as paid.
    """

    route_pattern = re.compile(r'POST /api/invoices/(?P<invoice_uuid>[0-9a-f-]+)/mark-paid/?')

    def route(self, req):
        match = self.route_pattern == req.line_one
        if match:
            req['invoice_uuid'] = match.groupdict()['invoice_uuid']
            return self.handle

    @Handler.require_login
    @Handler.require_json
    def handle(self, req):
        invoice_uuid = req['invoice_uuid']
        if not invoice_uuid:
            return Response.json(dict(
                success=False,
                message='Invoice UUID is required'
            ))

        try:
            invoice = invoices.Invoice.by_uuid(
                self.cw.get_pgconn(), invoice_uuid)

            paid_date = req.json.get('paid_date')

            # Convert paid_date string to date object if provided
            if paid_date and isinstance(paid_date, str):
                try:
                    paid_date = datetime.datetime.strptime(paid_date, '%Y-%m-%d').date()
                except ValueError:
                    return Response.json(dict(
                        success=False,
                        message='Invalid paid date format, use YYYY-MM-DD'
                    ))

            updated_invoice = invoice.mark_as_paid(
                self.cw.get_pgconn(), paid_date=paid_date)

            return Response.json(dict(
                success=True,
                message='Invoice marked as paid',
                invoice=updated_invoice
            ))

        except KeyError:
            return Response.json(dict(
                success=False,
                message='Invoice not found'
            ))
        except Exception as e:
            log.error(f"Error marking invoice as paid: {e}")
            return Response.json(dict(
                success=False,
                message=f'Error marking invoice as paid: {str(e)}'
            ))

class InvoicesApiListHandler(Handler):
    """
    Handler for listing invoices via API.
    """

    route_pattern = re.compile(r'GET /api/invoices/list/?')

    def route(self, req):
        match = self.route_pattern == req.line_one
        if match:
            return self.handle

    @Handler.require_login
    def handle(self, req):
        project_uuid = req.wz_req.args.get('project_uuid')
        status = req.wz_req.args.get('status')

        try:
            limit = int(req.wz_req.args.get('limit', '100'))
            offset = int(req.wz_req.args.get('offset', '0'))
        except ValueError:
            limit = 100
            offset = 0

        try:
            all_invoices = invoices.InvoiceWithDetails.get_all(
                self.cw.get_pgconn(), project_uuid=project_uuid,
                status=status, limit=limit, offset=offset)

            return Response.json(dict(
                success=True,
                invoices=all_invoices
            ))

        except Exception as e:
            log.error(f"Error listing invoices: {e}")
            return Response.json(dict(
                success=False,
                message='Error listing invoices'
            ))

class UnbilledTimeEntriesHandler(Handler):
    """
    Handler for listing unbilled time entries for a project.
    """

    route_pattern = re.compile(r'GET /api/projects/(?P<project_uuid>[0-9a-f-]+)/unbilled-time-entries/?')

    def route(self, req):
        match = self.route_pattern == req.line_one
        if match:
            req['project_uuid'] = match.groupdict()['project_uuid']
            return self.handle

    @Handler.require_login
    def handle(self, req):
        project_uuid = req['project_uuid']
        if not project_uuid:
            return Response.json(dict(
                success=False,
                message='Project UUID is required'
            ))

        try:
            # Get all time entries for the project
            all_time_entries = projects.TimeEntryWithDetails.for_project(
                self.cw.get_pgconn(), project_uuid)

            # Get all time entries that have been billed
            sql = textwrap.dedent("""
                select time_entry_uuid
                from invoice_time_entries
                join time_entries using (time_entry_uuid)
                where project_uuid = %(project_uuid)s
            """)

            with self.cw.get_pgconn().cursor() as cur:
                cur.execute(sql, {'project_uuid': project_uuid})
                billed_entries = {row[0] for row in cur.fetchall()}

            # Filter out billed entries
            unbilled_entries = [
                te for te in all_time_entries
                if te.time_entry_uuid not in billed_entries
            ]

            return Response.json(dict(
                success=True,
                time_entries=unbilled_entries
            ))

        except Exception as e:
            log.error(f"Error listing unbilled time entries: {e}")
            return Response.json(dict(
                success=False,
                message='Error listing unbilled time entries'
            ))

class PDFUploadHandler(Handler):
    """
    Handler for uploading PDF files for invoices.
    """

    route_pattern = re.compile(r'POST /api/invoices/(?P<invoice_uuid>[0-9a-f-]+)/upload-pdf/?')

    def route(self, req):
        match = self.route_pattern == req.line_one
        if match:
            req['invoice_uuid'] = match.groupdict()['invoice_uuid']
            return self.handle

    @Handler.require_login
    def handle(self, req):
        invoice_uuid = req['invoice_uuid']

        try:
            # Validate invoice exists
            invoice = invoices.Invoice.by_uuid(self.cw.get_pgconn(), invoice_uuid)

            # Check if we received the PDF file
            if 'pdf_file' not in req.FILES:
                return Response.json(dict(
                    success=False,
                    message='No PDF file uploaded'
                ))

            uploaded_file = req.FILES['pdf_file']

            # Basic validation of file type
            original_filename = uploaded_file.filename
            if not original_filename.lower().endswith('.pdf'):
                return Response.json(dict(
                    success=False,
                    message='Uploaded file must be a PDF'
                ))

            # Initialize PDF manager
            pdf_manager = PDFManager(self.cw)

            # If invoice already has a PDF, delete it
            if invoice.pdf_path:
                pdf_manager.delete_pdf(invoice.pdf_path)

            # Save the new PDF
            new_filename = pdf_manager.save_pdf(
                uploaded_file.file,
                original_filename,
                invoice_uuid
            )

            # Update the invoice with the new PDF path
            updated_invoice = invoice.update(
                self.cw.get_pgconn(),
                pdf_path=new_filename
            )

            # Generate URL for the PDF
            pdf_url = pdf_manager.get_pdf_url(new_filename)

            return Response.json(dict(
                success=True,
                message='PDF uploaded successfully',
                invoice=updated_invoice,
                pdf_url=pdf_url
            ))

        except KeyError:
            return Response.json(dict(
                success=False,
                message='Invoice not found'
            ))
        except Exception as e:
            log.error(f"Error uploading PDF: {e}")
            return Response.json(dict(
                success=False,
                message=f'Error uploading PDF: {str(e)}'
            ))

class PDFDeleteHandler(Handler):
    """
    Handler for deleting PDF files from invoices.
    """

    route_pattern = re.compile(r'POST /api/invoices/(?P<invoice_uuid>[0-9a-f-]+)/delete-pdf/?')

    def route(self, req):
        match = self.route_pattern == req.line_one
        if match:
            req['invoice_uuid'] = match.groupdict()['invoice_uuid']
            return self.handle

    @Handler.require_login
    def handle(self, req):
        invoice_uuid = req['invoice_uuid']

        try:
            # Validate invoice exists
            invoice = invoices.Invoice.by_uuid(self.cw.get_pgconn(), invoice_uuid)

            # Check if invoice has a PDF to delete
            if not invoice.pdf_path:
                return Response.json(dict(
                    success=False,
                    message='No PDF attached to this invoice'
                ))

            # Initialize PDF manager
            pdf_manager = PDFManager(self.cw)

            # Delete the PDF file
            success = pdf_manager.delete_pdf(invoice.pdf_path)

            if success:
                # Update the invoice to remove the PDF path
                updated_invoice = invoice.update(
                    self.cw.get_pgconn(),
                    pdf_path=None
                )

                return Response.json(dict(
                    success=True,
                    message='PDF deleted successfully',
                    invoice=updated_invoice
                ))
            else:
                return Response.json(dict(
                    success=False,
                    message='Failed to delete PDF file'
                ))

        except KeyError:
            return Response.json(dict(
                success=False,
                message='Invoice not found'
            ))
        except Exception as e:
            log.error(f"Error deleting PDF: {e}")
            return Response.json(dict(
                success=False,
                message=f'Error deleting PDF: {str(e)}'
            ))

class PDFServeHandler(Handler):
    """
    Handler for serving PDF files.
    """

    route_pattern = re.compile(r'GET /pdfs/(?P<filename>[^/]+)/?')

    def route(self, req):
        match = self.route_pattern == req.line_one
        if match:
            req['filename'] = match.groupdict()['filename']
            return self.handle

    @Handler.require_login
    def handle(self, req):
        filename = req['filename']

        # Initialize PDF manager
        pdf_manager = PDFManager(self.cw)

        # Get the file path
        file_path = pdf_manager.get_file_path(filename)

        # Check if file exists
        if not os.path.exists(file_path):
            return self.not_found(req)

        # Serve the file
        try:
            with open(file_path, 'rb') as f:
                pdf_data = f.read()

            return Response(
                body=pdf_data,
                content_type='application/pdf',
                headers={
                    'Content-Disposition': f'inline; filename="{filename}"'
                }
            )

        except Exception as e:
            log.error(f"Error serving PDF file: {e}")
            return Response.plain(
                body="Error serving PDF file",
                status=500
            )
