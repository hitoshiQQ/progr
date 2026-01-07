import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from models import Record, Goal
from storage import load_data, save_data
from storage import load_archived_goals, save_archived_goals
from goals import load_goals, save_goals
# from analytics import calculate_totals
# from charts import expenses_by_category


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
        # =======================
        # ➕ Новая операция
        # =======================
        add_frame = ttk.LabelFrame(f, text="➕ Новая операция", padding=10)
        add_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(add_frame, text="Тип:").grid(row=0, column=0, padx=5)
        self.type_var = tk.StringVar(value="Расход")
        ttk.Combobox(
            add_frame,
            textvariable=self.type_var,
            values=["Доход", "Расход"],
            state="readonly",
            width=10
        ).grid(row=0, column=1, padx=5)

        ttk.Label(add_frame, text="Категория:").grid(row=0, column=2, padx=5)
        self.category = ttk.Entry(add_frame, width=20)
        self.category.grid(row=0, column=3, padx=5)

        ttk.Label(add_frame, text="Сумма ₽:").grid(row=0, column=4, padx=5)
        self.amount = ttk.Entry(add_frame, width=10)
        self.amount.grid(row=0, column=5, padx=5)

        ttk.Button(
            add_frame,
            text="✔ Добавить",
            command=self.add_record
        ).grid(row=0, column=6, padx=10)

        ttk.Button(
            add_frame,
            text="📊 График",
            command=self.show_chart
        ).grid(row=0, column=7, padx=5)

        # =======================
        # 📋 История операций
        # =======================
        table_frame = ttk.LabelFrame(f, text="📋 История операций", padding=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.finance_table = ttk.Treeview(
            table_frame,
            columns=("date", "type", "category", "amount"),
            show="headings",
            height=10
        )

        self.finance_table.heading("date", text="Дата")
        self.finance_table.heading("type", text="Тип")
        self.finance_table.heading("category", text="Категория")
        self.finance_table.heading("amount", text="Сумма ₽")

        self.finance_table.column("date", width=100, anchor="center")
        self.finance_table.column("type", width=80, anchor="center")
        self.finance_table.column("category", width=220)
        self.finance_table.column("amount", width=120, anchor="e")

        self.finance_table.pack(fill="both", expand=True)

        # =======================
        # 📊 Итоги
        # =======================
        summary = ttk.LabelFrame(f, text="📊 Итоги", padding=10)
        summary.pack(fill="x", padx=15, pady=10)

        self.summary_label = ttk.Label(
            summary,
            text="Доходы: 0 ₽   Расходы: 0 ₽   Баланс: 0 ₽",
            font=("Segoe UI", 10, "bold")
        )
        self.summary_label.pack(anchor="center")

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
        for i in self.finance_table.get_children():
            self.finance_table.delete(i)

        income = expense = 0

        for r in self.records:
            sign = "+" if r.type == "Доход" else "-"
            amount = r.amount

            if r.type == "Доход":
                income += amount
            else:
                expense += amount

            self.finance_table.insert(
                "",
                "end",
                values=(
                    r.date,
                    r.type,
                    r.category,
                    f"{sign}{amount:.2f} ₽"
                )
            )

        balance = income - expense
        self.summary_label.config(
            text=f"Доходы: {income:.2f} ₽   Расходы: {expense:.2f} ₽   Баланс: {balance:.2f} ₽"
        )

    def show_chart(self):
        if not self.records:
            messagebox.showinfo("График", "Нет данных для построения графика")
            return

        income = {}
        expense = {}

        for r in self.records:
            if r.type == "Доход":
                income[r.category] = income.get(r.category, 0) + r.amount
            else:
                expense[r.category] = expense.get(r.category, 0) + r.amount

        # График доходов (круг)
        if income:
            plt.figure()
            plt.title("Доходы по категориям")
            plt.pie(
                income.values(),
                labels=income.keys(),
                autopct="%1.1f%%",  # отображение процентов
                startangle=90
            )
            plt.axis("equal")  # делает круг ровным
            plt.show()

        # График расходов (круг)
        if expense:
            plt.figure()
            plt.title("Расходы по категориям")
            plt.pie(
                expense.values(),
                labels=expense.keys(),
                autopct="%1.1f%%",
                startangle=90
            )
            plt.axis("equal")
            plt.show()

    # -------- ЦЕЛИ --------
    def build_goals_tab(self):
        f = self.goals_tab
        # =======================
        # 🏁 Блок добавления цели
        # =======================
        add_frame = ttk.LabelFrame(f, text="🏁 Новая цель", padding=10)
        add_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(add_frame, text="Название:").grid(row=0, column=0, padx=5)
        self.goal_name = ttk.Entry(add_frame, width=25)
        self.goal_name.grid(row=0, column=1, padx=5)

        ttk.Label(add_frame, text="Сумма ₽:").grid(row=0, column=2, padx=5)
        self.goal_target = ttk.Entry(add_frame, width=12)
        self.goal_target.grid(row=0, column=3, padx=5)

        ttk.Button(
            add_frame,
            text="➕ Добавить цель",
            command=self.add_goal
        ).grid(row=0, column=4, padx=10)

        # =======================
        # 📋 Таблица целей
        # =======================
        table_frame = ttk.LabelFrame(f, text="📋 Активные цели", padding=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.goals_table = ttk.Treeview(
            table_frame,
            columns=("name", "target", "saved", "percent"),
            show="headings",
            height=8
        )

        self.goals_table.heading("name", text="Цель")
        self.goals_table.heading("target", text="Цель ₽")
        self.goals_table.heading("saved", text="Накоплено ₽")
        self.goals_table.heading("percent", text="%")

        self.goals_table.column("name", width=200)
        self.goals_table.column("target", width=100, anchor="center")
        self.goals_table.column("saved", width=120, anchor="center")
        self.goals_table.column("percent", width=80, anchor="center")

        self.goals_table.pack(fill="both", expand=True)

        self.goals_table.bind("<<TreeviewSelect>>", self.on_goal_select)

        # =======================
        # 🎛 Кнопки действий
        # =======================
        actions = ttk.Frame(f)
        actions.pack(pady=5)

        ttk.Button(
            actions,
            text="💰 Пополнить",
            command=self.add_to_goal
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            actions,
            text="🗑 Удалить",
            command=self.delete_goal
        ).grid(row=0, column=1, padx=5)

        # =======================
        # 📊 Прогресс
        # =======================
        progress_frame = ttk.LabelFrame(f, text="📊 Прогресс цели", padding=10)
        progress_frame.pack(fill="x", padx=15, pady=10)

        self.goal_progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate"
        )
        self.goal_progress.pack(fill="x", padx=5, pady=5)

        self.goal_progress_label = ttk.Label(
            progress_frame,
            text="Прогресс: 0%",
            anchor="center"
        )
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
