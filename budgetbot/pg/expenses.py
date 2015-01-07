# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import textwrap

import psycopg2.extras

log = logging.getLogger(__name__)

class Expenses(object):

    def __init__(self, expense_uuid,
        amount, expense_date, attached_file_urls,
        expense_category, extra_notes,
        person_id, inserted, updated):

        self.expense_uuid = expense_uuid
        self.expense_date = expense_date
        self.amount = amount
        self.extra_notes = extra_notes
        self.expense_category = expense_category
        self.attached_file_urls = attached_file_urls
        self.person_id = person_id
        self.inserted = inserted
        self.updated = updated

    def __repr__(self):
        return '<{0}.{1} ({2}:{3}) at 0x{4:x}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.expense_uuid,
            self.amount,
            id(self))
    @property
    def __jsondata__(self):

        return {k:v for (k, v) in self.__dict__.items()
            if k in set([
                'expense_uuid',
                'expense_date',
                'amount',
                'extra_notes',
                'expense_category',
                'self.person_id'])}



    @classmethod
    def get_all(cls, pgconn):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            select (e.*):expenses as expense

            from expense e

            order by e.inserted
        """))

        if cursor.rowcount:
            return [row.expense for row in cursor.fetchall()]

class ExpenseFactory(psycopg2.extras.CompositeCaster):

    def make(self, values):
        d = dict(zip(self.attnames, values))
        return Expenses(**d)


class ExpenseCategoriesDenormalizedFactory(psycopg2.extras.CompositeCaster):

    def make(self, values):
        d = dict(zip(self.attnames, values))
        return ExpenseCategoriesDenormalized(**d)

class ExpenseCategoriesDenormalized(object):

    def __init__(self, expense_category, budgeted_amount,
                       effective, amount_spent, expenses):

        self.expense_category = expense_category
        self.budgeted_amount = budgeted_amount
        self.effective = effective
        self.amount_spent = amount_spent
        self.expenses = expenses

    @classmethod
    def get_all_with_budgets(cls, pgconn):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""

            select (ecd.*)::expense_categories_denormalized
                   from expense_categories_denormalized ecd
                   where now()::date <@ ecd.effective

        """))

        if cursor.rowcount:
            return [row.ecd for row in cursor.fetchall()]

    @property
    def __jsondata__(self):

        return {k:v for (k, v) in self.__dict__.items()
            if k in set([
                'expense_category',
                'budgeted_amount',
                'effective',
                'amount_spent',
                'expenses'])}



class ExpenseCategories(object):

    def __init__(self, title, description,
                 inserted, updated):

        self.title = title
        self.description = description

        self.inserted = inserted
        self.updated = updated

    def __repr__(self):
        return '<{0}.{1} ({2}) at 0x{3:x}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.title,
            id(self))


    @classmethod
    def get_all(cls, pgconn):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            select (ec.*)::expense_categories as category

            from expense_categories ec

            order by ec.title
        """))

        if cursor.rowcount:
            return [row.category for row in cursor.fetchall()]

    @property
    def __jsondata__(self):

        return {k:v for (k, v) in self.__dict__.items()
            if k in set([
                'title',
                'description',
                'inserted'])}


class ExpenseCategoryFactory(psycopg2.extras.CompositeCaster):

    def make(self, values):
        d = dict(zip(self.attnames, values))
        return ExpenseCategories(**d)

class BudgetedExpenses(object):

    def __init__(self, title, budgeted_expense_id,
                 expense_category, budgeted_amount,
                 effective, inserted,updated):

        self.budgeted_expense_id = budgeted_expense_id
        self.expense_category = expense_category
        self.budgeted_amount = budgeted_amount

        self.effective = effective

        self.inserted = inserted
        self.updated = updated

    def __repr__(self):
        return '<{0}.{1} ({2}:{3}) at 0x{4:x}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.expense_category,
            self.budgeted_amount,
            id(self))


    @classmethod
    def get_all(cls, pgconn):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            select (be.*)::budgeted_expenses as budg_exp

            from budgeted_expenses be

            where now()::date <@ be.effective

            order by be.expense_category
        """))

        if cursor.rowcount:
            return [row.budg_exp for row in cursor.fetchall()]


