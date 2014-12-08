create view expense_categories_denormalized as

select (ec.*)::expense_categories as expense_category,
                   be.budgeted_amount,
                   be.effective, sum(e.amount) as amount_spent

                   from expense_categories ec

                   join budgeted_expenses as be
                   on be.expense_category = ec.title

                   left join expenses as e
                   on e.expense_category = ec.title

                   where now() <@ be.effective

                   group by (ec.*),
                   be.budgeted_amount, be.effective;

SELECT ec.*::expense_categories AS expense_category,
    be.budgeted_amount,
    be.effective,
    sum(e.amount) AS amount_spent,
    array_agg((e.*)::expenses) as expenses
   FROM expense_categories ec
     JOIN budgeted_expenses be ON be.expense_category = ec.title
     LEFT JOIN expenses e ON e.expense_category = ec.title
  GROUP BY ec.*, be.budgeted_amount, be.effective;

