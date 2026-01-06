import matplotlib.pyplot as plt


def expenses_by_category(records):
    categories = {}
    for r in records:
        if r.type == "Расход":
            categories[r.category] = categories.get(r.category, 0) + r.amount

    if not categories:
        return

    plt.figure(figsize=(6, 6))
    plt.pie(categories.values(), labels=categories.keys(), autopct="%1.1f%%")
    plt.title("Расходы по категориям")
    plt.show()
