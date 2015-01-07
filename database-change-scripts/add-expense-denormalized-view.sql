create view expense_categories_denormalized as

select (ec.*)::expense_categories as expense_category,
                   be.budgeted_amount,
                   be.effective, sum(e.amount) as amount_spent
                   from expense_categories ec
                   join budgeted_expenses as be
                   on be.expense_category = ec.title
                   left join expenses as e
                   on (e.expense_category = ec.title and e.expense_date <@ be.effective)
                   group by (ec.*),
                   be.budgeted_amount, be.effective;


