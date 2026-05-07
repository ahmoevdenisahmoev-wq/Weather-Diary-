import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
import os

class WeatherDiary:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌤️ Weather Diary — Дневник погоды")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        self.entries = []  # список словарей
        self.create_widgets()
        self.load_data()  # загрузка из JSON при старте

    def create_widgets(self):
        # ==================== ФОРМА ВВОДА ====================
        frame_input = ttk.LabelFrame(self.root, text="Добавить новую запись", padding=10)
        frame_input.pack(fill="x", padx=10, pady=10)

        # Дата
        ttk.Label(frame_input, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", pady=5)
        self.date_entry = ttk.Entry(frame_input, width=15)
        self.date_entry.grid(row=0, column=1, pady=5, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Температура
        ttk.Label(frame_input, text="Температура (°C):").grid(row=0, column=2, sticky="w", pady=5)
        self.temp_entry = ttk.Entry(frame_input, width=10)
        self.temp_entry.grid(row=0, column=3, pady=5, padx=5)

        # Описание
        ttk.Label(frame_input, text="Описание погоды:").grid(row=1, column=0, sticky="w", pady=5)
        self.desc_entry = ttk.Entry(frame_input, width=50)
        self.desc_entry.grid(row=1, column=1, columnspan=3, pady=5, padx=5, sticky="ew")

        # Осадки
        ttk.Label(frame_input, text="Осадки:").grid(row=2, column=0, sticky="w", pady=5)
        self.precip_var = tk.StringVar(value="Нет")
        precip_combo = ttk.Combobox(frame_input, textvariable=self.precip_var, 
                                   values=["Нет", "Да"], state="readonly", width=10)
        precip_combo.grid(row=2, column=1, pady=5, padx=5)

        # Кнопка добавить
        ttk.Button(frame_input, text="➕ Добавить запись", command=self.add_entry).grid(
            row=2, column=2, columnspan=2, pady=5, padx=5, sticky="e")

        # ==================== ФИЛЬТРЫ ====================
        frame_filter = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        frame_filter.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_filter, text="Дата:").pack(side="left", padx=5)
        self.filter_date = ttk.Entry(frame_filter, width=12)
        self.filter_date.pack(side="left", padx=5)

        ttk.Label(frame_filter, text="Температура выше (°C):").pack(side="left", padx=10)
        self.filter_temp = ttk.Entry(frame_filter, width=8)
        self.filter_temp.pack(side="left", padx=5)

        ttk.Button(frame_filter, text="Применить фильтры", command=self.apply_filters).pack(side="left", padx=10)
        ttk.Button(frame_filter, text="Сбросить", command=self.reset_filters).pack(side="left")

        # ==================== ТАБЛИЦА ====================
        frame_table = ttk.LabelFrame(self.root, text="Записи о погоде", padding=10)
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=15)

        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")

        self.tree.column("date", width=100)
        self.tree.column("temp", width=120)
        self.tree.column("desc", width=400)
        self.tree.column("precip", width=80)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ==================== КНОПКИ УПРАВЛЕНИЯ ====================
        btn_frame = ttk.Frame(self.root)



        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_from_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 Очистить все записи", command=self.clear_all).pack(side="left", padx=5)

    def add_entry(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        # Валидация
        if not date:
            messagebox.showerror("Ошибка", "Укажите дату!")
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return

        if not temp_str:
            messagebox.showerror("Ошибка", "Укажите температуру!")
            return
        try:
            temperature = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return

        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым!")
            return

        self.entries.insert(0, {
            "date": date,
            "temperature": temperature,
            "description": desc,
            "precipitation": precip
        })

        self.refresh_table()
        self.save_data()  # автосохранение
        self.clear_form()
        messagebox.showinfo("Успешно", "Запись добавлена!")

    def refresh_table(self, data=None):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        if data is None:
            data = self.entries

        for entry in data:
            self.tree.insert("", "end", values=(
                entry["date"],
                f"{entry['temperature']:.1f}",
                entry["description"],
                entry["precipitation"]
            ))

    def apply_filters(self):
        filter_date = self.filter_date.get().strip()
        filter_temp_str = self.filter_temp.get().strip()

        filtered = self.entries

        if filter_date:
            filtered = [e for e in filtered if e["date"] == filter_date]

        if filter_temp_str:
            try:
                min_temp = float(filter_temp_str)
                filtered = [e for e in filtered if e["temperature"] > min_temp]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура для фильтра должна быть числом!")
                return

        self.refresh_table(filtered)

    def reset_filters(self):
        self.filter_date.delete(0, tk.END)
        self.filter_temp.delete(0, tk.END)
        self.refresh_table()

    def clear_form(self):
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    def save_data(self):
        try:
            with open("weather_data.json", "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_data(self):
        if os.path.exists("weather_data.json"):
            try:
                with open("weather_data.json", "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
                self.refresh_table()
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось загрузить данные:\n{e}")

    def save_to_json(self):
        if not self.entries:
            messagebox.showinfo("Инфо", "Нет данных для сохранения")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files",


"*.json")],

initialfile=f"weather_diary_{datetime.now().strftime('%Y-%m-%d')}.json"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.entries, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Успешно", "Файл сохранён!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def load_from_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.entries = loaded
                self.save_data()
                self.refresh_table()
                messagebox.showinfo("Успешно", "Данные загружены!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def clear_all(self):
        if messagebox.askyesno("Подтверждение", "Вы действительно хотите удалить ВСЕ записи?"):
            self.entries.clear()
            self.save_data()
            self.refresh_table()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WeatherDiary()
    app.run()