import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from models import Record, Goal
from storage import load_data, save_data
from goals import load_goals, save_goals
from analytics import calculate_totals
from charts import expenses_by_category


class CoinKeeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coin Keeper")
        self.root.geometry("900x550")

        self.records = load_data()
        self.goals = load_goals()

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.finance_tab = ttk.Frame(notebook)
        self.goals_tab = ttk.Frame(notebook)

        notebook.add(self.finance_tab, text="Финансы")
        notebook.add(self.goals_tab, text="Цели")

        self.build_finance_tab()
        self.build_goals_tab()

    # -------- ФИНАНСЫ --------
    def build_finance_tab(self):
        f = self.finance_tab
        top = ttk.Frame(f)
        top.pack(pady=10)

        self.type_var = tk.StringVar(value="Расход")
        ttk.Combobox(top, textvariable=self.type_var, values=["Доход", "Расход"], width=10).grid(row=0, column=0)
        self.category = ttk.Entry(top, width=20)
        self.category.grid(row=0, column=1, padx=5)
        self.amount = ttk.Entry(top, width=10)
        self.amount.grid(row=0, column=2, padx=5)
        ttk.Button(top, text="Добавить", command=self.add_record).grid(row=0, column=3)
        ttk.Button(top, text="График", command=lambda: expenses_by_category(self.records)).grid(row=0, column=4)

        self.table = ttk.Treeview(f, columns=("date", "type", "category", "amount"), show="headings")
        for c in self.table["columns"]:
            self.table.heading(c, text=c.capitalize())
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        self.total_label = ttk.Label(f, font=("Arial", 12, "bold"))
        self.total_label.pack()
        self.refresh_finance()

    def add_record(self):
        try:
            amt = float(self.amount.get())
            if amt <= 0 or not self.category.get():
                raise ValueError
            self.records.append(Record(
                date=datetime.now().strftime("%d.%m.%Y"),
                type=self.type_var.get(),
                category=self.category.get(),
                amount=amt
            ))
            save_data(self.records)
            self.refresh_finance()
            self.category.delete(0, tk.END)
            self.amount.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные")

    def refresh_finance(self):
        for i in self.table.get_children():
            self.table.delete(i)
        for r in self.records:
            sign = "+" if r.type == "Доход" else "-"
            self.table.insert("", "end", values=(r.date, r.type, r.category, f"{sign}{r.amount} ₽"))
        inc, exp, bal = calculate_totals(self.records)
        self.total_label.config(text=f"Доходы: {inc} ₽  Расходы: {exp} ₽  Баланс: {bal} ₽")

    # -------- ЦЕЛИ --------
    def build_goals_tab(self):
        f = self.goals_tab
        top = ttk.Frame(f)
        top.pack(pady=10)

        self.goal_name = ttk.Entry(top, width=20)
        self.goal_name.grid(row=0, column=0, padx=5)
        self.goal_target = ttk.Entry(top, width=10)
        self.goal_target.grid(row=0, column=1, padx=5)
        ttk.Button(top, text="Добавить цель", command=self.add_goal).grid(row=0, column=2)

        self.goals_table = ttk.Treeview(f, columns=("name", "target", "saved", "progress"), show="headings")
        for c in self.goals_table["columns"]:
            self.goals_table.heading(c, text=c.capitalize())
        self.goals_table.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(f, text="Пополнить выбранную цель", command=self.add_to_goal).pack(pady=5)
        self.refresh_goals()

    def add_goal(self):
        try:
            target = float(self.goal_target.get())
            if target <= 0 or not self.goal_name.get():
                raise ValueError
            self.goals.append(Goal(self.goal_name.get(), target))
            save_goals(self.goals)
            self.refresh_goals()
            self.goal_name.delete(0, tk.END)
            self.goal_target.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная цель")

    def add_to_goal(self):
        selected = self.goals_table.focus()
        if not selected:
            return
        idx = self.goals_table.index(selected)
        amount = simpledialog.askfloat("Пополнение", "Сумма:")
        if amount and amount > 0:
            self.goals[idx].saved += amount
            save_goals(self.goals)
            self.refresh_goals()

    def refresh_goals(self):
        for i in self.goals_table.get_children():
            self.goals_table.delete(i)
        for g in self.goals:
            progress = round((g.saved / g.target) * 100, 1)
            self.goals_table.insert("", "end", values=(g.name, g.target, g.saved, f"{progress}%"))


if __name__ == "__main__":
    root = tk.Tk()
    CoinKeeperApp(root)
    root.mainloop()
