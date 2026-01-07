import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from models import Record, Goal
from storage import load_data, save_data
from storage import load_archived_goals, save_archived_goals
from goals import load_goals, save_goals
from analytics import calculate_totals
from charts import expenses_by_category


class CoinKeeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coin Keeper")
        self.root.geometry("900x550")

        # Данные
        self.records = load_data()
        self.goals = load_goals()
        self.archived_goals = load_archived_goals()

        # notebook как self
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # вкладки
        self.finance_tab = ttk.Frame(self.notebook)
        self.goals_tab = ttk.Frame(self.notebook)
        self.archive_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.finance_tab, text="Финансы")
        self.notebook.add(self.goals_tab, text="Цели")
        self.notebook.add(self.archive_tab, text="🏆 Архив целей")

        self.build_finance_tab()
        self.build_goals_tab()
        self.build_archive_tab()

    # -------- ФИНАНСЫ --------
    def build_finance_tab(self):
        f = self.finance_tab
        top = ttk.Frame(f)
        top.pack(pady=10)

        self.type_var = tk.StringVar(value="Расход")
        ttk.Combobox(
            top, textvariable=self.type_var,
            values=["Доход", "Расход"], width=10).grid(row=0, column=0)

        self.category = ttk.Entry(top, width=20)
        self.category.grid(row=0, column=1, padx=5)
        self.amount = ttk.Entry(top, width=10)
        self.amount.grid(row=0, column=2, padx=5)
        ttk.Button(
            top, text="Добавить",
            command=self.add_record).grid(row=0, column=3)

        ttk.Button(
            top, text="График", command=lambda:
            expenses_by_category(self.records)).grid(row=0, column=4)

        self.table = ttk.Treeview(
            f,
            columns=("date", "type", "category", "amount"), show="headings")

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
            self.table.insert(
                "", "end",
                values=(r.date, r.type, r.category, f"{sign}{r.amount} ₽"))

        inc, exp, bal = calculate_totals(self.records)
        self.total_label.config(
            text=f"Доходы: {inc} ₽  Расходы: {exp} ₽  Баланс: {bal} ₽")

    # -------- ЦЕЛИ --------
    def build_goals_tab(self):
        f = self.goals_tab
        top = ttk.Frame(f)
        top.pack(pady=10)

        self.goal_name = ttk.Entry(top, width=20)
        self.goal_name.grid(row=0, column=0, padx=5)

        self.goal_target = ttk.Entry(top, width=10)
        self.goal_target.grid(row=0, column=1, padx=5)

        # Кнопки
        ttk.Button(
            top, text="Добавить цель",
            command=self.add_goal).grid(row=0, column=2)

        ttk.Button(
            f, text="Пополнить выбранную цель",
            command=self.add_to_goal).pack(pady=5)

        ttk.Button(
            f,
            text="Удалить выбранную цель",
            command=self.delete_goal
        ).pack(pady=5)

        # Создание прогресс бара цели
        self.goals_table = ttk.Treeview(
            f,
            columns=("name", "target", "saved", "percent"),
            show="headings", height=6)

        self.goals_table.heading("name", text="Цель")
        self.goals_table.heading("target", text="Цель ₽")
        self.goals_table.heading("saved", text="Накоплено ₽")
        self.goals_table.heading("percent", text="%")

        self.goals_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Обновление
        self.goals_table.bind(
            "<<TreeviewSelect>>",
            self.on_goal_select)

        # Под таблицей
        self.goal_progress = ttk.Progressbar(
            f,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.goal_progress.pack(pady=5)

        self.goal_progress_label = ttk.Label(f, text="Прогресс: 0%")
        self.goal_progress_label.pack()

        self.refresh_goals()

    def build_archive_tab(self):
        self.archive_table = ttk.Treeview(
            self.archive_tab,
            columns=("name", "target", "saved"),
            show="headings",
            height=8
        )

        self.archive_table.heading("name", text="Цель")
        self.archive_table.heading("target", text="Цель ₽")
        self.archive_table.heading("saved", text="Накоплено ₽")

        self.archive_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_archive()

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

    def delete_goal(self):
        selected = self.goals_table.focus()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите цель")
            return

        idx = self.goals_table.index(selected)
        goal = self.goals[idx]

        if not messagebox.askyesno(
            "Удаление",
            f"Удалить цель «{goal.name}»?"
        ):
            return

        goal = self.goals.pop(idx)
        self.archived_goals.append(goal)

        save_goals(self.goals)
        save_archived_goals(self.archived_goals)

        self.refresh_goals()
        self.refresh_archive()

        self.goal_progress["value"] = 0
        self.goal_progress_label.config(text="Прогресс: 0%")

    def add_to_goal(self):
        selected = self.goals_table.focus()
        if not selected:
            return

        idx = self.goals_table.index(selected)
        amount = simpledialog.askfloat("Пополнение", "Сумма:")

        if amount and amount > 0:
            self.goals[idx].saved += amount

        if self.goals[idx].saved >= self.goals[idx].target:
            goal = self.goals.pop(idx)
            self.archived_goals.append(goal)

            messagebox.showinfo(
                "Цель достигнута 🎉",
                f"Цель «{goal.name}» достигнута и отправлена в архив"
            )

        save_goals(self.goals)
        save_archived_goals(self.archived_goals)

        self.refresh_goals()
        self.refresh_archive()

        self.goal_progress["value"] = 0
        self.goal_progress_label.config(text="Прогресс: 0%")

    def refresh_goals(self):
        for i in self.goals_table.get_children():
            self.goals_table.delete(i)

        for g in self.goals:
            percent = round((g.saved / g.target) * 100, 1)
            self.goals_table.insert(
                "",
                "end",
                values=(g.name, g.target, g.saved, f"{percent}%"))

    def refresh_archive(self):
        for i in self.archive_table.get_children():
            self.archive_table.delete(i)

        for g in self.archived_goals:
            self.archive_table.insert(
                "",
                "end",
                values=(g.name, g.target, g.saved)
            )

    def on_goal_select(self, event):
        selected = self.goals_table.focus()
        if not selected:
            return

        idx = self.goals_table.index(selected)
        g = self.goals[idx]

        percent = (g.saved / g.target) * 100
        self.goal_progress["value"] = percent
        self.goal_progress_label.config(
            text=f"Прогресс: {round(percent, 1)}%"
        )


if __name__ == "__main__":
    root = tk.Tk()
    CoinKeeperApp(root)
    root.mainloop()
