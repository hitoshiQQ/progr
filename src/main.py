import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from datetime import date

from models import Record, Goal
from storage import load_data, save_data
from storage import load_archived_goals, save_archived_goals
from goals import load_goals, save_goals
from analytics import calculate_totals
from storage import load_categories, save_categories
# from analytics import calculate_totals
# from charts import expenses_by_category


class CoinKeeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coin Keeper")

        # Размер окна
        self.root.geometry("900x600")
        self.root.minsize(900, 900)

        # Глобальный стиль
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            ".",
            font=("Segoe UI", 10),
            background="#f5f6fa"
        )

        style.configure(
            "TLabelframe",
            background="#f5f6fa"
        )
        style.configure(
            "TLabelframe.Label",
            font=("Segoe UI", 10, "bold"),
            foreground="#2f3640"
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=6
        )

        style.configure(
            "TEntry",
            padding=6
        )

        style.configure(
            "TCombobox",
            padding=6
        )

        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=28,
            background="white",
            fieldbackground="white"
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=(15, 6)
        )

        # Данные
        self.all_records = load_data()   # Все данные
        self.records = []                # Текущий месяц
        self.monthly_archive = {}        # Архив месяцев

        self.split_records_by_month()

        self.goals = load_goals()
        self.archived_goals = load_archived_goals()

        self.categories = load_categories()

        # Верхняя панель
        self.build_top_bar()

        # notebook как self
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # вкладки
        self.finance_tab = ttk.Frame(self.notebook)
        self.analytics_tab = ttk.Frame(self.notebook)
        self.goals_tab = ttk.Frame(self.notebook)
        self.archive_tab = ttk.Frame(self.notebook)
        self.finance_archive_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.finance_tab, text="💰 Финансы")
        self.notebook.add(self.analytics_tab, text="📊 Аналитика")
        self.notebook.add(self.goals_tab, text="🎯 Цели")
        self.notebook.add(self.archive_tab, text="🏆 Архив целей")
        self.notebook.add(self.finance_archive_tab, text="📁 Архив финансов")

        self.build_finance_tab()
        self.build_analytics_tab()
        self.build_settings_panel()
        self.build_goals_tab()
        self.build_archive_tab()
        self.build_finance_archive_tab()

    # -------- СЛУЖЕБНЫЕ ФУНКЦИИ --------
    def toggle_settings_panel(self):
        if self.settings_visiable:
            self.settings_panel.place_forget()
        else:
            self.settings_panel.place(
                relx=1.0,
                y=0,
                anchor="ne",
                height=self.root.winfo_height()
            )
            self.settings_panel.lift()

        self.settings_visiable = not self.settings_visiable

    def apply_theme(self):
        style = ttk.Style()

        if self.theme_var.get() == "dark":
            self.root.configure(bg="#1e1e1e")

            style.configure(
                "TFrame",
                background="#1e1e1e"
            )
            style.configure(
                "TLabel",
                background="#1e1e1e",
                foreground="white"
            )
            style.configure(
                "Treeview",
                background="#2b2b2b",
                foreground="white",
                fieldbackground="#2b2b2b"
            )
            style.configure(
                "Treeview.Heading",
                background="#3a3a3a",
                foreground="white"
            )

        else:
            self.root.configure(bg="#f5f5f5")

            style.configure("TFrame", background="#f5f5f5")
            style.configure("TLabel", background="#f5f5f5", foreground="black")
            style.configure(
                "Treeview",
                background="white",
                foreground="black",
                fieldbackground="white"
            )
            style.configure(
                "Treeview.Heading",
                background="#eaeaea",
                foreground="black"
            )

    def apply_resolution(self):
        self.root.geometry(self.resolution_var.get())

    def build_top_bar(self):
        self.top_bar = ttk.Frame(self.root)
        self.top_bar.pack(fill="x")

        ttk.Label(
            self.top_bar,
            text="💰 CoinKeeper",
            font=("Segoe UI", 14, "bold")
        ).pack(side="left", padx=10, pady=5)

        ttk.Button(
            self.top_bar,
            text="⚙",
            width=3,
            command=self.toggle_settings_panel
        ).pack(side="right", padx=10)

    # -------- НАСТРОЙКИ --------
    def build_settings_panel(self):
        self.settings_panel = ttk.Frame(
            self.root,
            width=260,
            relief="ridge",
            padding=10
        )
        self.settings_panel.place_forget()
        self.settings_visiable = False

        # =======================
        # 🔝 Header + ✖
        # =======================
        header = ttk.Frame(self.settings_panel)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header,
            text="⚙ Настройки",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="✖",
            width=3,
            command=self.toggle_settings_panel
        ).pack(side="right")

        # =======================
        # 🌗 Тема
        # =======================
        ttk.Label(self.settings_panel, text="Тема:").pack(anchor="w")

        self.theme_var = tk.StringVar(value="light")

        ttk.Radiobutton(
            self.settings_panel,
            text="🌞 Светлая",
            variable=self.theme_var,
            value="light",
            command=self.apply_theme
        ).pack(anchor="w")

        ttk.Radiobutton(
            self.settings_panel,
            text="🌙 Тёмная",
            variable=self.theme_var,
            value="dark",
            command=self.apply_theme
        ).pack(anchor="w")

        # =======================
        # 📐 Размер окна
        # =======================
        ttk.Label(
            self.settings_panel,
            text="Размер окна:",
            padding=(0, 10, 0, 0)
        ).pack(anchor="w")

        self.resolution_var = tk.StringVar(value="900x600")

        ttk.Combobox(
            self.settings_panel,
            textvariable=self.resolution_var,
            values=[
                "800x500",
                "900x600",
                "1024x700",
                "1200x800"
            ],
            state="readonly",
            width=12
        ).pack(anchor="w")

        ttk.Button(
            self.settings_panel,
            text="Применить",
            command=self.apply_resolution
        ).pack(pady=10)

    # -------- СПЛИТ ПО МЕСЯЦАМ --------
    def split_records_by_month(self):
        self.records.clear()
        self.monthly_archive.clear()

        current_month = date.today().strftime("%Y-%m")

        for r in self.all_records:
            record_month = r.date[:7]  # YYYY-MM

            if record_month == current_month:
                self.records.append(r)
            else:
                self.monthly_archive.setdefault(record_month, []).append(r)

    def build_finance_archive_tab(self):
        f = self.finance_archive_tab

        self.archive_table = ttk.Treeview(
            f,
            columns=("month", "income", "expense", "result"),
            show="headings"
        )

        self.archive_table.heading("month", text="Месяц")
        self.archive_table.heading("income", text="Доход ₽")
        self.archive_table.heading("expense", text="Расход ₽")
        self.archive_table.heading("result", text="Итог ₽")

        self.archive_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_finance_archive()

    def refresh_finance_archive(self):
        for i in self.archive_table.get_children():
            self.archive_table.delete(i)

        for month, records in sorted(
            self.monthly_archive.items(),
            reverse=True
        ):
            income = sum(r.amount for r in records if r.type == "Доход")
            expense = sum(r.amount for r in records if r.type == "Расход")

            self.archive_table.insert(
                "",
                "end",
                values=(
                    month,
                    f"{income:.2f}",
                    f"{expense:.2f}",
                    f"{income - expense:.2f}"
                )
            )

    def show_month_records(self, event=None):
        month = self.months_list.get()

        for i in self.archive_table.get_children():
            self.archive_table.delete(i)

        for r in self.monthly_archive.get(month, []):
            self.archive_table.insert(
                "",
                "end",
                values=(r.date, r.type, r.amount, r.category)
            )

    # -------- КАТЕГОРИИ --------
    def update_category_list(self, *_):
        t = self.type_var.get()
        self.category["values"] = self.categories.get(t, [])
        self.category.set("")

    def add_category(self):
        new_cat = simpledialog.askstring(
            "Новая категория",
            "Введите название категории:"
        )

        if not new_cat:
            return

        t = self.type_var.get()

        if new_cat in self.categories[t]:
            messagebox.showinfo("Инфо", "Такая категория уже существует")
            return

        self.categories[t].append(new_cat)
        save_categories(self.categories)

        self.update_category_list()
        self.category.set(new_cat)

        months = set()

        for r in self.all_records:
            # r.date = "DD.MM.YYYY"
            month_key = r.date[3:10]  # MM.YYYY
            months.add(month_key)

        months = sorted(months, reverse=True)

        month_names = {
            "01": "Январь", "02": "Февраль", "03": "Март",
            "04": "Апрель", "05": "Май", "06": "Июнь",
            "07": "Июль", "08": "Август", "09": "Сентябрь",
            "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь"
        }

        result = ["Все"]
        for m in months:
            mm, yyyy = m.split(".")
            result.append(f"{month_names[mm]} {yyyy}")

        return result

    # -------- ФИНАНСЫ --------
    def build_finance_tab(self):
        f = self.finance_tab
        # =======================
        # ➕ Новая операция
        # =======================
        add_frame = ttk.Frame(f, padding=15)
        add_frame.pack(fill="x", padx=20, pady=(15, 10))

        ttk.Label(
            add_frame,
            text="➕ Новая операция",
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 10))

        ttk.Label(add_frame, text="Тип:").grid(row=1, column=0, padx=5)
        self.type_var = tk.StringVar(value="Расход")

        type_combo = ttk.Combobox(
            add_frame,
            textvariable=self.type_var,
            values=["Доход", "Расход"],
            state="readonly",
            width=10
        )
        type_combo.grid(row=1, column=1, padx=5)
        self.type_var.trace_add("write", self.update_category_list)

        ttk.Label(add_frame, text="Категория:").grid(row=1, column=2, padx=5)
        self.category = ttk.Combobox(
            add_frame,
            values=self.categories[self.type_var.get()],
            width=18
        )
        self.category.grid(row=1, column=3, padx=5)

        ttk.Button(
            add_frame,
            text="➕",
            width=3,
            command=self.add_category
        ).grid(row=1, column=4, padx=3)

        ttk.Label(add_frame, text="Сумма ₽:").grid(row=1, column=5, padx=5)
        self.amount = ttk.Entry(add_frame, width=10)
        self.amount.grid(row=1, column=6, padx=5)

        ttk.Button(
            add_frame,
            text="✔ Добавить",
            command=self.add_record
        ).grid(row=1, column=7, padx=10)

        ttk.Button(
            add_frame,
            text="📊 График",
            command=self.show_chart
        ).grid(row=1, column=8, padx=5)

        # =======================
        # 🔎 Фильтры
        # =======================
        filter_frame = ttk.Frame(f, padding=15)
        filter_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(
            filter_frame,
            text="🔎 Фильтр",
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 10))

        ttk.Label(filter_frame, text="Дата с:").grid(row=1, column=0, padx=5)
        self.filter_date_from = ttk.Entry(filter_frame, width=12)
        self.filter_date_from.grid(row=1, column=1, padx=5)

        ttk.Label(filter_frame, text="по:").grid(row=0, column=2)
        self.filter_date_to = ttk.Entry(filter_frame, width=12)
        self.filter_date_to.grid(row=1, column=3, padx=5)

        ttk.Label(filter_frame, text="Тип:").grid(row=1, column=4, padx=5)
        self.filter_type = tk.StringVar(value="Все")
        ttk.Combobox(
            filter_frame,
            textvariable=self.filter_type,
            values=["Все", "Доход", "Расход"],
            state="readonly",
            width=10
        ).grid(row=1, column=5, padx=5)

        ttk.Label(filter_frame, text="Категория:").grid(
            row=1, column=6, padx=5
        )
        self.filter_category = ttk.Entry(filter_frame, width=15)
        self.filter_category.grid(row=1, column=7, padx=5)

        ttk.Button(
            filter_frame,
            text="Применить",
            command=self.refresh_finance
        ).grid(row=1, column=8, padx=10)

        ttk.Button(
            filter_frame,
            text="Сброс",
            command=self.reset_filters
        ).grid(row=1, column=9)

        # =======================
        # 📋 История операций
        # =======================
        table_frame = ttk.LabelFrame(f, padding=10)
        table_frame.pack(fill="both", padx=20, pady=5)

        ttk.Label(
            table_frame,
            text="📋 История операций",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.finance_table = ttk.Treeview(
            table_frame,
            columns=("date", "type", "category", "amount"),
            show="headings",
            height=10
        )

        # Цвета строк
        self.finance_table.tag_configure(
            "income", foreground="#2ecc71"
        )
        self.finance_table.tag_configure(
            "expense", foreground="#e74c3c"
        )

        self.finance_table.heading("date", text="Дата")
        self.finance_table.heading("type", text="Тип")
        self.finance_table.heading("category", text="Категория")
        self.finance_table.heading("amount", text="Сумма ₽")

        self.finance_table.column("date", width=100, anchor="center")
        self.finance_table.column("type", width=80, anchor="center")
        self.finance_table.column("category", width=220)
        self.finance_table.column("amount", width=120, anchor="e")

        self.finance_table.pack(fill="both")

        # =======================
        # 📊 Итоги
        # =======================
        summary = ttk.LabelFrame(f, padding=15)
        summary.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            summary,
            text="📊 Итоги",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.summary_label = ttk.Label(
            summary,
            text="Доходы: 0 ₽   Расходы: 0 ₽   Баланс: 0 ₽",
            font=("Segoe UI", 16, "bold"),
            foreground="#273c75"
        )
        self.summary_label.pack()

        self.summary_sub = ttk.Label(
            summary,
            font=("Segoe UI", 10),
            foreground="#636e72"
        )
        self.summary_sub.pack()

        self.refresh_finance()

    def add_record(self):
        try:
            amt = float(self.amount.get())
            if amt <= 0 or not self.category.get():
                raise ValueError

            record = Record(
                date=datetime.now().strftime("%Y-%m-%d"),
                type=self.type_var.get(),
                category=self.category.get(),
                amount=amt
            )

            # Добавляем ТОЛЬКО в all_records
            self.all_records.append(record)

            # Сохраняем ВСЕ данные
            save_data(self.all_records)

            # Пересобираем месяц + архив
            self.split_records_by_month()

            # Обновляем интерфейс
            self.refresh_finance()
            self.refresh_finance_archive()

            # Очистка полей
            self.category.delete(0, tk.END)
            self.amount.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные")

    def refresh_finance(self):
        for i in self.finance_table.get_children():
            self.finance_table.delete(i)

        filtered = self.records

        # --- фильтр по типу ---
        if self.filter_type.get() != "Все":
            filtered = [
                r for r in filtered
                if r.type == self.filter_type.get()
            ]

        # --- фильтр по категории ---
        if self.filter_category.get():
            filtered = [
                r for r in filtered
                if self.filter_category.get().lower() in r.category.lower()
            ]

        # --- фильтр по дате ---
        try:
            if self.filter_date_from.get():
                date_from = self.parse_date(self.filter_date_from.get())
                filtered = [
                    r for r in filtered
                    if self.parse_date(r.date) >= date_from
                ]

            if self.filter_date_to.get():
                date_to = self.parse_date(self.filter_date_to.get())
                filtered = [
                    r for r in filtered
                    if self.parse_date(r.date) <= date_to
                ]
        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Дата должна быть в формате ДД.ММ.ГГГГ"
            )
            return

        # --- вывод таблицы ---
        for r in filtered:
            sign = "+" if r.type == "Доход" else "-"
            tag = "income" if r.type == "Доход" else "expense"

            self.finance_table.insert(
                "",
                "end",
                values=(
                    r.date,
                    r.type,
                    r.category,
                    f"{sign}{r.amount:.2f} ₽"
                ),
                tags=(tag,)
            )

        # --- итоги (месяц / всё время) ---
        month_income, month_expense, _ = calculate_totals(self.records)
        total_income, total_expense, total_balance = calculate_totals(
            self.all_records
            )

        self.summary_label.config(
            text=f"Баланс: {total_balance:.2f} ₽"
        )
        self.summary_sub.config(
            text=(
                f"Доходы (мес): {month_income:.2f} ₽    "
                f"Расходы (мес): {month_expense:.2f} ₽"
            )
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

    def reset_filters(self):
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.filter_category.delete(0, tk.END)
        self.filter_type.set("Все")
        self.refresh_finance()

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
            goal.completed_date = date.today().strftime("%d.%m.%Y")
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

    # -------- АРХИВ --------
    def build_archive_tab(self):
        self.goals_archive_table = ttk.Treeview(
            self.archive_tab,
            columns=("name", "target", "saved", "date"),
            show="headings",
            height=8
        )

        self.goals_archive_table.heading("name", text="Цель")
        self.goals_archive_table.heading("target", text="Цель ₽")
        self.goals_archive_table.heading("saved", text="Накоплено ₽")
        self.goals_archive_table.heading("date", text="Дата завершения")

        self.goals_archive_table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.refresh_archive()

    def refresh_archive(self):
        for i in self.goals_archive_table.get_children():
            self.goals_archive_table.delete(i)

        for g in self.archived_goals:
            self.goals_archive_table.insert(
                "",
                "end",
                values=(g.name, g.target, g.saved, g.completed_date or "-")
            )

    # -------- АНАЛИТИКА --------
    def build_analytics_tab(self):
        f = self.analytics_tab

        # =======================
        # 📆 Период
        # =======================
        period_frame = ttk.Frame(f, padding=15)
        period_frame.pack(fill="x", padx=20, pady=15)

        ttk.Label(
            period_frame,
            text="📆 Период",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 10))

        controls = ttk.Frame(period_frame)
        controls.pack(anchor="center")

        self.analytics_period = tk.StringVar(value="Месяц")
        self.analytics_date = date.today().replace(day=1)

        ttk.Combobox(
            controls,
            textvariable=self.analytics_period,
            values=["Месяц", "Год"],
            state="readonly",
            width=10
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            controls,
            text="◀",
            command=lambda: self.shift_analytics_period(-1)
        ).grid(row=0, column=1)

        self.analytics_label = ttk.Label(
            controls,
            text=self.format_analytics_period(),
            font=("Segoe UI", 12, "bold")
        )
        self.analytics_label.grid(row=0, column=2, padx=15)

        ttk.Button(
            controls,
            text="▶",
            command=lambda: self.shift_analytics_period(+1)
        ).grid(row=0, column=3)

        # =======================
        # Итог
        # =======================
        summary = ttk.LabelFrame(f, padding=20)
        summary.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            summary,
            text="📊 Итоги периода",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 10))

        self.analytics_summary = ttk.Label(
            summary,
            font=("Segoe UI", 16, "bold"),
            foreground="#273c75"
        )
        self.analytics_summary.pack()

        self.analytics_compare = ttk.Label(
            summary,
            font=("Segoe UI", 10),
            foreground="#636e72"
        )
        self.analytics_compare.pack()

        self.refresh_analytics()

    def shift_analytics_period(self, step):
        if self.analytics_period.get() == "Месяц":
            month = self.analytics_date.month + step
            year = self.analytics_date.year

            if month < 1:
                month = 12
                year -= 1
            elif month > 12:
                month = 1
                year += 1

            self.analytics_date = self.analytics_date.replace(
                year=year, month=month
            )
        else:
            self.analytics_date = self.analytics_date.replace(
                year=self.analytics_date.year + step
            )

        self.analytics_label.config(
            text=self.format_analytics_period()
        )

        self.refresh_analytics()

    def format_analytics_period(self):
        if self.analytics_period.get() == "Месяц":
            return self.analytics_date.strftime("%B %Y").capitalize()
        else:
            return str(self.analytics_date.year)

    def refresh_analytics(self):
        income = expense = 0

        for r in self.all_records:
            d = date.fromisoformat(r.date)

            if self.analytics_period.get() == "Месяц":
                if (d.year, d.month) != (
                    self.analytics_date.year,
                    self.analytics_date.month
                ):
                    continue
            else:
                if d.year != self.analytics_date.year:
                    continue

            if r.type == "Доход":
                income += r.amount
            else:
                expense += r.amount

        balance = income - expense

        self.analytics_summary.config(
            text=(
               f"Доходы: {income:.2f} ₽   "
               f"Расходы: {expense:.2f} ₽   "
               f"Баланс: {balance:.2f} ₽"
            )
        )

        self.analytics_compare.config(
            text="Сравнение с предыдущим периодом — скоро 👀"
        )

    # -------- ПАРСЕРЫ --------
    def parse_date(self, date_str):
        for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        raise ValueError


if __name__ == "__main__":
    root = tk.Tk()
    CoinKeeperApp(root)
    root.mainloop()
