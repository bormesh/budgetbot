create view expense_categories_denormalized as

SELECT ec.*::expense_categories AS expense_category,
    be.budgeted_amount,
    be.effective,
    sum(e.amount) AS amount_spent,
    array_agg((e.*)::expenses) as expenses
   FROM expense_categories ec
     JOIN budgeted_expenses be ON be.expense_category = ec.title
     LEFT JOIN expenses e ON e.expense_category = ec.title and e.expense_date <@ be.effective
  GROUP BY ec.*, be.budgeted_amount, be.effective;

