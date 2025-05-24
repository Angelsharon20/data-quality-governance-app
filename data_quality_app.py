
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import re

class DataQualityApp:
    def __init__(self, root):  # Fixed __init__ method
        self.root = root
        self.root.title("Data Quality & Governance")
        self.data = []
        self.log = []
        self.errors = []

        # Notebook and Tabs
        self.tab_control = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)
        self.tab4 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text='Load Data')
        self.tab_control.add(self.tab2, text='Validate Data')
        self.tab_control.add(self.tab3, text='Secure Preview')
        self.tab_control.add(self.tab4, text='Fix Errors')
        self.tab_control.pack(expand=1, fill='both')

        self.build_tab1()
        self.build_tab2()
        self.build_tab3()
        self.build_tab4()

    # TAB 1 - LOAD FILE
    def build_tab1(self):
        ttk.Label(self.tab1, text="Upload CSV Sales Data").pack(pady=10)
        ttk.Button(self.tab1, text="Browse File", command=self.load_file).pack()
        self.file_label = ttk.Label(self.tab1, text="")
        self.file_label.pack()

    def load_file(self):
        file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, newline='') as file:
                    reader = csv.DictReader(file)
                    self.data = [row for row in reader]
                self.file_label.config(text=f"Loaded: {file_path}")
                messagebox.showinfo("Success", "Data Loaded Successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    # TAB 2 - VALIDATE
    def build_tab2(self):
        ttk.Label(self.tab2, text="Data Validation Rules").pack(pady=10)
        ttk.Button(self.tab2, text="Run Validation", command=self.validate_data).pack()
        self.log_text = tk.Text(self.tab2, height=20, width=100)
        self.log_text.pack()

    def validate_data(self):
        self.log = []
        self.errors = []

        for i, row in enumerate(self.data):
            issues = []
            row_errors = {}

            # Check sales
            try:
                sales = float(row.get("sales", "0"))
                if sales < 0:
                    issues.append("Negative sales")
                    row_errors["sales"] = row.get("sales", "")
            except:
                issues.append("Invalid sales")
                row_errors["sales"] = row.get("sales", "")

            # Check email
            email = row.get("email", "")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                issues.append("Invalid email format")
                row_errors["email"] = email

            if issues:
                self.log.append(f"Row {i+1}: {', '.join(issues)}")
                self.errors.append((i, row_errors))  # Store row index and fields with errors

        self.log_text.delete(1.0, tk.END)
        if self.log:
            for entry in self.log:
                self.log_text.insert(tk.END, entry + "\n")
        else:
            self.log_text.insert(tk.END, "All data passed validation.\n")

        self.show_error_entries()

    # TAB 3 - SECURE PREVIEW
    def build_tab3(self):
        self.preview_frame = ttk.Frame(self.tab3)
        self.auth_frame = ttk.Frame(self.tab3)

        self.auth_frame.pack(pady=20)

        ttk.Label(self.auth_frame, text="Enter ID:").grid(row=0, column=0, padx=5, pady=5)
        self.id_entry = ttk.Entry(self.auth_frame)
        self.id_entry.grid(row=0, column=1)

        ttk.Label(self.auth_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.pw_entry = ttk.Entry(self.auth_frame, show="*")
        self.pw_entry.grid(row=1, column=1)

        ttk.Button(self.auth_frame, text="Unlock", command=self.unlock_preview).grid(row=2, column=0, columnspan=2, pady=10)

        self.preview_text = tk.Text(self.preview_frame, height=20, width=100)

    def unlock_preview(self):
        uid = self.id_entry.get()
        pwd = self.pw_entry.get()

        if uid == "admin" and pwd == "1234":
            self.auth_frame.pack_forget()
            self.preview_frame.pack(pady=10)
            self.preview_text.pack()
            self.show_preview()
        else:
            messagebox.showerror("Access Denied", "Invalid ID or Password")

    def show_preview(self):
        self.preview_text.delete(1.0, tk.END)
        if self.data:
            headers = self.data[0].keys()
            self.preview_text.insert(tk.END, "\t".join(headers) + "\n")
            self.preview_text.insert(tk.END, "-" * 100 + "\n")
            for row in self.data[:10]:
                self.preview_text.insert(tk.END, "\t".join(row.values()) + "\n")
        else:
            self.preview_text.insert(tk.END, "No data loaded.")

    # TAB 4 - FIX ERRORS
    def build_tab4(self):
        self.error_frame = tk.Frame(self.tab4, bg="white")
        self.error_frame.pack(fill="both", expand=True)
        self.error_widgets = []

    def show_error_entries(self):
        for widget in self.error_frame.winfo_children():
            widget.destroy()
        self.error_widgets.clear()

        if not self.errors:
            ttk.Label(self.error_frame, text="No errors found. Run validation first.").pack(pady=20)
            return

        for index, error_fields in self.errors:
            row = self.data[index]
            frame = ttk.LabelFrame(self.error_frame, text=f"Row {index + 1}", padding=10)
            frame.pack(padx=10, pady=5, fill='x')

            row_widgets = {}
            for field, value in error_fields.items():
                ttk.Label(frame, text=field).pack(anchor='w')
                entry = ttk.Entry(frame, width=50)
                entry.insert(0, value)
                entry.pack(anchor='w')
                row_widgets[field] = entry

            def save_callback(row_idx=index, widgets=row_widgets):
                for field, entry in widgets.items():
                    self.data[row_idx][field] = entry.get()
                messagebox.showinfo("Fixed", f"Row {row_idx + 1} updated successfully.")

            ttk.Button(frame, text="Apply Fix", command=save_callback).pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = DataQualityApp(root)
    root.mainloop()
