import matplotlib.pyplot as plt


def expenses_by_category(records):
    data = {}
    for r in records:
        if r.type == "Расход":
            data[r.category] = data.get(r.category, 0) + r.amount
    if not data:
        return
    plt.pie(data.values(), labels=data.keys(), autopct="%1.1f%%")
    plt.title("Расходы по категориям")
    plt.show()
