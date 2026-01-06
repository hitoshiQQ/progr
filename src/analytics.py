def calculate_totals(records):
    income = 0
    expense = 0

    for r in records:
        if r.type == "Доход":
            income += r.amount
        elif r.type == "Расход":
            expense += r.amount

    return income, expense, income - expense
