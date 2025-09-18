# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import datetime
import json
import logging
import textwrap
import uuid

log = logging.getLogger(__name__)

class Invoice:
    """
    Class representing an invoice in the system.
    """

    def __init__(self, invoice_uuid, invoice_number, project_uuid, client_name,
                 client_address, total_amount, notes, status, invoice_date,
                 due_date, paid_date, pdf_path, inserted, updated):
        self.invoice_uuid = invoice_uuid
        self.invoice_number = invoice_number
        self.project_uuid = project_uuid
        self.client_name = client_name
        self.client_address = client_address
        self.total_amount = total_amount
        self.notes = notes
        self.status = status
        self.invoice_date = invoice_date
        self.due_date = due_date
        self.paid_date = paid_date
        self.pdf_path = pdf_path
        self.inserted = inserted
        self.updated = updated

    @property
    def __jsondata__(self):
        """
        Return a dictionary representation of the object for JSON serialization.
        """
        return {
            'invoice_uuid': str(self.invoice_uuid),
            'invoice_number': self.invoice_number,
            'project_uuid': str(self.project_uuid),
            'client_name': self.client_name,
            'client_address': self.client_address,
            'total_amount': float(self.total_amount),
            'notes': self.notes,
            'status': self.status,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'pdf_path': self.pdf_path,
            'inserted': self.inserted.isoformat() if self.inserted else None,
            'updated': self.updated.isoformat() if self.updated else None
        }

    @classmethod
    def factory(cls, row):
        """
        Factory method to create an Invoice from a database row.
        """
        return cls(
            invoice_uuid=row[0],
            invoice_number=row[1],
            project_uuid=row[2],
            client_name=row[3],
            client_address=row[4],
            total_amount=row[5],
            notes=row[6],
            status=row[7],
            invoice_date=row[8],
            due_date=row[9],
            paid_date=row[10],
            pdf_path=row[11],
            inserted=row[12],
            updated=row[13]
        )

    @classmethod
    def by_uuid(cls, pgconn, invoice_uuid):
        """
        Get an invoice by UUID.
        """
        if isinstance(invoice_uuid, str):
            invoice_uuid = uuid.UUID(invoice_uuid)

        sql = textwrap.dedent("""
            select
                invoice_uuid,
                invoice_number,
                project_uuid,
                client_name,
                client_address,
                total_amount,
                notes,
                status,
                invoice_date,
                due_date,
                paid_date,
                pdf_path,
                inserted,
                updated
            from
                invoices
            where
                invoice_uuid = %(invoice_uuid)s
        """)

        with pgconn.cursor() as cur:
            cur.execute(sql, {'invoice_uuid': invoice_uuid})
            row = cur.fetchone()

            if not row:
                raise KeyError(f"No invoice found with UUID {invoice_uuid}")

            return cls.factory(row)

    @classmethod
    def get_all(cls, pgconn, project_uuid=None, status=None, limit=100, offset=0):
        """
        Get all invoices, optionally filtered by project_uuid and/or status.
        """
        sql_params = {}
        where_clauses = []

        sql = textwrap.dedent("""
            select
                invoice_uuid,
                invoice_number,
                project_uuid,
                client_name,
                client_address,
                total_amount,
                notes,
                status,
                invoice_date,
                due_date,
                paid_date,
                pdf_path,
                inserted,
                updated
            from
                invoices
        """)

        if project_uuid:
            where_clauses.append("project_uuid = %(project_uuid)s")
            sql_params['project_uuid'] = project_uuid

        if status:
            where_clauses.append("status = %(status)s")
            sql_params['status'] = status

        if where_clauses:
            sql += " where " + " and ".join(where_clauses)

        sql += " order by invoice_date desc limit %(limit)s offset %(offset)s"
        sql_params['limit'] = limit
        sql_params['offset'] = offset

        with pgconn.cursor() as cur:
            cur.execute(sql, sql_params)
            return [cls.factory(row) for row in cur.fetchall()]

    @classmethod
    def create(cls, pgconn, project_uuid, client_name, client_address=None,
               invoice_number=None, total_amount=0.00, notes=None, status='draft',
               invoice_date=None, due_date=None, paid_date=None, pdf_path=None):
        """
        Create a new invoice.
        """
        if isinstance(project_uuid, str):
            project_uuid = uuid.UUID(project_uuid)

        if invoice_date is None:
            invoice_date = datetime.date.today()

        sql = textwrap.dedent("""
            insert into invoices (
                invoice_number,
                project_uuid,
                client_name,
                client_address,
                total_amount,
                notes,
                status,
                invoice_date,
                due_date,
                paid_date,
                pdf_path
            ) values (
                %(invoice_number)s, 
                %(project_uuid)s, 
                %(client_name)s, 
                %(client_address)s, 
                %(total_amount)s, 
                %(notes)s, 
                %(status)s, 
                %(invoice_date)s, 
                %(due_date)s, 
                %(paid_date)s, 
                %(pdf_path)s
            ) returning
                invoice_uuid,
                invoice_number,
                project_uuid,
                client_name,
                client_address,
                total_amount,
                notes,
                status,
                invoice_date,
                due_date,
                paid_date,
                pdf_path,
                inserted,
                updated
        """)

        params = {
            'invoice_number': invoice_number,
            'project_uuid': project_uuid,
            'client_name': client_name,
            'client_address': client_address,
            'total_amount': total_amount,
            'notes': notes,
            'status': status,
            'invoice_date': invoice_date,
            'due_date': due_date,
            'paid_date': paid_date,
            'pdf_path': pdf_path
        }

        with pgconn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            pgconn.commit()
            return cls.factory(row)

    def update(self, pgconn, invoice_number=None, client_name=None,
               client_address=None, total_amount=None, notes=None,
               status=None, invoice_date=None, due_date=None, 
               paid_date=None, pdf_path=None):
        """
        Update an existing invoice.
        """
        updates = []
        params = {'invoice_uuid': self.invoice_uuid}

        if invoice_number is not None:
            updates.append("invoice_number = %(invoice_number)s")
            params['invoice_number'] = invoice_number
            self.invoice_number = invoice_number

        if client_name is not None:
            updates.append("client_name = %(client_name)s")
            params['client_name'] = client_name
            self.client_name = client_name

        if client_address is not None:
            updates.append("client_address = %(client_address)s")
            params['client_address'] = client_address
            self.client_address = client_address

        if total_amount is not None:
            updates.append("total_amount = %(total_amount)s")
            params['total_amount'] = total_amount
            self.total_amount = total_amount

        if notes is not None:
            updates.append("notes = %(notes)s")
            params['notes'] = notes
            self.notes = notes

        if status is not None:
            updates.append("status = %(status)s")
            params['status'] = status
            self.status = status

        if invoice_date is not None:
            updates.append("invoice_date = %(invoice_date)s")
            params['invoice_date'] = invoice_date
            self.invoice_date = invoice_date

        if due_date is not None:
            updates.append("due_date = %(due_date)s")
            params['due_date'] = due_date
            self.due_date = due_date

        if paid_date is not None:
            updates.append("paid_date = %(paid_date)s")
            params['paid_date'] = paid_date
            self.paid_date = paid_date

        if pdf_path is not None:
            updates.append("pdf_path = %(pdf_path)s")
            params['pdf_path'] = pdf_path
            self.pdf_path = pdf_path

        if not updates:
            return self

        sql = textwrap.dedent(f"""
            update invoices
            set {", ".join(updates)}
            where invoice_uuid = %(invoice_uuid)s
            returning
                invoice_uuid,
                invoice_number,
                project_uuid,
                client_name,
                client_address,
                total_amount,
                notes,
                status,
                invoice_date,
                due_date,
                paid_date,
                pdf_path,
                inserted,
                updated
        """)

        with pgconn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            pgconn.commit()
            return self.__class__.factory(row)

    def add_time_entry(self, pgconn, time_entry_uuid):
        """
        Add a time entry to this invoice.
        """
        if isinstance(time_entry_uuid, str):
            time_entry_uuid = uuid.UUID(time_entry_uuid)

        sql = textwrap.dedent("""
            insert into invoice_time_entries (
                invoice_uuid,
                time_entry_uuid
            ) values (
                %(invoice_uuid)s, %(time_entry_uuid)s
            ) on conflict do nothing
            returning invoice_uuid, time_entry_uuid
        """)

        params = {
            'invoice_uuid': self.invoice_uuid,
            'time_entry_uuid': time_entry_uuid
        }

        with pgconn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            pgconn.commit()
            return row is not None

    def remove_time_entry(self, pgconn, time_entry_uuid):
        """
        Remove a time entry from this invoice.
        """
        if isinstance(time_entry_uuid, str):
            time_entry_uuid = uuid.UUID(time_entry_uuid)

        sql = textwrap.dedent("""
            delete from invoice_time_entries
            where invoice_uuid = %(invoice_uuid)s and time_entry_uuid = %(time_entry_uuid)s
            returning invoice_uuid
        """)

        params = {
            'invoice_uuid': self.invoice_uuid,
            'time_entry_uuid': time_entry_uuid
        }

        with pgconn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            pgconn.commit()
            return row is not None

    def get_time_entries(self, pgconn):
        """
        Get all time entries associated with this invoice.
        """
        from budgetbot.pg import projects

        sql = textwrap.dedent("""
            select (te.*)::time_entries as te
            from
                invoice_time_entries ite
                join time_entries te on ite.time_entry_uuid = te.time_entry_uuid
            where
                ite.invoice_uuid = %(invoice_uuid)s
            order by
                te.entry_date
        """)

        with pgconn.cursor() as cur:
            cur.execute(sql, {'invoice_uuid': self.invoice_uuid})
            return [row.te for row in cur.fetchall()]

    def get_time_entries_with_details(self, pgconn):
        """
        Get all time entries associated with this invoice, with person details.
        """
        from budgetbot.pg import projects

        sql = textwrap.dedent("""
            select (ted.*)::time_entries_with_details as ted
            from
                invoice_time_entries ite
                join time_entries_with_details ted on ite.time_entry_uuid = ted.time_entry_uuid
            where
                ite.invoice_uuid = %(invoice_uuid)s
            order by
                ted.entry_date
        """)

        with pgconn.cursor() as cur:
            cur.execute(sql, {'invoice_uuid': self.invoice_uuid})
            return [row.ted for row in cur.fetchall()]

    def update_total_from_time_entries(self, pgconn, hourly_rate=100.00):
        """
        Update the total amount based on the time entries and hourly rate.
        """
        sql = textwrap.dedent("""
            select sum(te.hours_worked)
            from invoice_time_entries ite
            join time_entries te on ite.time_entry_uuid = te.time_entry_uuid
            where ite.invoice_uuid = %(invoice_uuid)s
        """)

        with pgconn.cursor() as cur:
            cur.execute(sql, {'invoice_uuid': self.invoice_uuid})
            total_hours = cur.fetchone()[0] or 0
            total_amount = total_hours * hourly_rate

            return self.update(pgconn, total_amount=total_amount)

    def mark_as_paid(self, pgconn, paid_date=None):
        """
        Mark this invoice as paid.
        """
        if paid_date is None:
            paid_date = datetime.date.today()

        return self.update(pgconn, status='paid', paid_date=paid_date)


class InvoiceWithDetails(Invoice):
    """
    Class representing an invoice with project details.
    """

    def __init__(self, invoice_uuid, invoice_number, project_uuid, client_name,
                 client_address, total_amount, notes, status, invoice_date,
                 due_date, paid_date, pdf_path, inserted, updated,
                 project_title, project_description, project_created_by):
        super().__init__(
            invoice_uuid, invoice_number, project_uuid, client_name,
            client_address, total_amount, notes, status, invoice_date,
            due_date, paid_date, pdf_path, inserted, updated
        )
        self.project_title = project_title
        self.project_description = project_description
        self.project_created_by = project_created_by

    @property
    def __jsondata__(self):
        """
        Return a dictionary representation of the object for JSON serialization.
        """
        data = super().__jsondata__
        data.update({
            'project_title': self.project_title,
            'project_description': self.project_description,
            'project_created_by': str(self.project_created_by)
        })
        return data

    @classmethod
    def factory(cls, row):
        """
        Factory method to create an InvoiceWithDetails from a database row.
        """
        return cls(
            invoice_uuid=row[0],
            invoice_number=row[1],
            project_uuid=row[2],
            client_name=row[3],
            client_address=row[4],
            total_amount=row[5],
            notes=row[6],
            status=row[7],
            invoice_date=row[8],
            due_date=row[9],
            paid_date=row[10],
            pdf_path=row[11],
            inserted=row[12],
            updated=row[13],
            project_title=row[14],
            project_description=row[15],
            project_created_by=row[16]
        )

    @classmethod
    def by_uuid(cls, pgconn, invoice_uuid):
        """
        Get an invoice with details by UUID.
        """
        if isinstance(invoice_uuid, str):
            invoice_uuid = uuid.UUID(invoice_uuid)

        sql = textwrap.dedent("""
            select
                invoice_uuid,
                invoice_number,
                project_uuid,
                client_name,
                client_address,
                total_amount,
                notes,
                status,
                invoice_date,
                due_date,
                paid_date,
                pdf_path,
                inserted,
                updated,
                project_title,
                project_description,
                project_created_by
            from
                invoices_with_details
            where
                invoice_uuid = %(invoice_uuid)s
        """)

        with pgconn.cursor() as cur:
            cur.execute(sql, {'invoice_uuid': invoice_uuid})
            row = cur.fetchone()

            if not row:
                raise KeyError(f"No invoice found with UUID {invoice_uuid}")

            return cls.factory(row)

    @classmethod
    def get_all(cls, pgconn, project_uuid=None, status=None, limit=100, offset=0):
        """
        Get all invoices with details, optionally filtered by project_uuid and/or status.
        """
        sql_params = {}
        where_clauses = []

        sql = textwrap.dedent("""
            select
                invoice_uuid,
                invoice_number,
                project_uuid,
                client_name,
                client_address,
                total_amount,
                notes,
                status,
                invoice_date,
                due_date,
                paid_date,
                pdf_path,
                inserted,
                updated,
                project_title,
                project_description,
                project_created_by
            from
                invoices_with_details
        """)

        if project_uuid:
            where_clauses.append("project_uuid = %(project_uuid)s")
            sql_params['project_uuid'] = project_uuid

        if status:
            where_clauses.append("status = %(status)s")
            sql_params['status'] = status

        if where_clauses:
            sql += " where " + " and ".join(where_clauses)

        sql += " order by invoice_date desc limit %(limit)s offset %(offset)s"
        sql_params['limit'] = limit
        sql_params['offset'] = offset

        with pgconn.cursor() as cur:
            cur.execute(sql, sql_params)
            return [cls.factory(row) for row in cur.fetchall()]