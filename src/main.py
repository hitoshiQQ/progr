import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from models import Record
from storage import load_data, save_data
from analytics import calculate_totals
from charts import expenses_by_category


class CoinKeeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coin Keeper")
        self.root.geometry("800x500")

        self.records = load_data()

        # --- UI ---
        frame = ttk.Frame(root)
        frame.pack(padx=10, pady=10, fill="x")

        self.type_var = tk.StringVar(value="Расход")
        ttk.Combobox(frame, textvariable=self.type_var, values=["Доход", "Расход"], width=10).grid(row=0, column=0)

        self.category = ttk.Entry(frame, width=20)
        self.category.grid(row=0, column=1, padx=5)

        self.amount = ttk.Entry(frame, width=10)
        self.amount.grid(row=0, column=2, padx=5)

        ttk.Button(frame, text="Добавить", command=self.add_record).grid(row=0, column=3)
        ttk.Button(frame, text="График", command=self.show_chart).grid(row=0, column=4)

        self.table = ttk.Treeview(root, columns=("date", "type", "category", "amount"), show="headings")
        for col in self.table["columns"]:
            self.table.heading(col, text=col.capitalize())
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        self.total_label = ttk.Label(root, font=("Arial", 12, "bold"))
        self.total_label.pack(pady=5)

        self.refresh()

    def add_record(self):
        try:
            amount = float(self.amount.get())
            if amount <= 0:
                raise ValueError

            record = Record(
                date=datetime.now().strftime("%d.%m.%Y"),
                type=self.type_var.get(),
                category=self.category.get(),
                amount=amount
            )

            if not record.category:
                raise ValueError

            self.records.append(record)
            save_data(self.records)
            self.refresh()

            self.category.delete(0, tk.END)
            self.amount.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные данные")

    def refresh(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for r in self.records:
            sign = "+" if r.type == "Доход" else "-"
            self.table.insert("", "end", values=(r.date, r.type, r.category, f"{sign}{r.amount} ₽"))

        income, expense, balance = calculate_totals(self.records)
        self.total_label.config(text=f"Доходы: {income} ₽ Расходы: {expense} ₽ Баланс: {balance} ₽")

    def show_chart(self):
        expenses_by_category(self.records)


if __name__ == "__main__":
    root = tk.Tk()
    CoinKeeperApp(root)
    root.mainloop()
