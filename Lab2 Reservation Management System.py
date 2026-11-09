import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ==========================================
# DATABASE CONFIGURATION - BEACH RESORT
# ==========================================
DB_NAME = "beach_resort.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_table():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resort_bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_name TEXT NOT NULL,
                contact TEXT NOT NULL,
                checkin_date TEXT NOT NULL,
                checkout_date TEXT NOT NULL,
                cottage_type TEXT NOT NULL,
                booking_status TEXT NOT NULL DEFAULT 'Pending',
                special_requests TEXT
            )
        """)

# ==========================================
# BEACH RESORT BOOKING MANAGEMENT SYSTEM
# ==========================================
class ResortBookingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Beach Resort Reservation Management System")
        self.root.geometry("1150x700")
        self.root.minsize(950, 600)

        # Color theme (ocean‑sand style like the hotel navy‑gold layout)
        self.OCEAN_BLUE = "#0F4C81"
        self.SAND_GOLD = "#E6C270"
        self.DARK_SAND = "#C4A250"
        self.CREAM = "#FFF9E8"
        self.WHITE = "#FFFFFF"

        self.selected_id = None
        self.configure_theme()
        self.create_widgets()
        self.load_bookings()

    def configure_theme(self):
        self.root.configure(bg=self.CREAM)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.CREAM)
        style.configure("TLabel", background=self.CREAM)
        style.configure("TLabelframe", background=self.CREAM)
        style.configure("TLabelframe.Label", background=self.CREAM, foreground=self.OCEAN_BLUE, font=("Arial",10,"bold"))
        style.configure("Treeview.Heading", background=self.OCEAN_BLUE, foreground=self.SAND_GOLD, font=("Arial",9,"bold"))
        style.map("Treeview.Heading", background=[("active","#0A3459")])
        style.configure("Treeview", background=self.WHITE, fieldbackground=self.WHITE, rowheight=26)
        style.configure("Sand.TButton", background=self.SAND_GOLD, foreground="#222222", font=("Arial",9,"bold"))
        style.map("Sand.TButton", background=[("active", self.DARK_SAND)])

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="BEACH RESORT RESERVATION MANAGEMENT SYSTEM",
            font=("Arial",20,"bold"),
            bg=self.OCEAN_BLUE,
            fg=self.SAND_GOLD,
            pady=15
        )
        title.pack(fill="x")

        form = ttk.LabelFrame(self.root, text="Booking Details", padding=12)
        form.pack(fill="x", padx=15, pady=10)

        ttk.Label(form, text="Guest Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(form, width=28)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Contact Number:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.contact_entry = ttk.Entry(form, width=25)
        self.contact_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Check‑in Date (YYYY‑MM‑DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.checkin_entry = ttk.Entry(form, width=28)
        self.checkin_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Check‑out Date (YYYY‑MM‑DD):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.checkout_entry = ttk.Entry(form, width=25)
        self.checkout_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(form, text="Cottage Type:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.cottage_box = ttk.Combobox(form, values=["Standard Cottage","Garden Cottage","Beach Front Cottage","VIP Ocean Cottage"], width=26, state="readonly")
        self.cottage_box.grid(row=2, column=1, padx=5, pady=5)
        self.cottage_box.set("Beach Front Cottage")

        ttk.Label(form, text="Booking Status:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.status_box = ttk.Combobox(form, values=["Pending","Confirmed","Checked‑in","Checked‑out","Cancelled"], state="readonly", width=22)
        self.status_box.grid(row=2, column=3, padx=5, pady=5)
        self.status_box.set("Pending")

        ttk.Label(form, text="Special Requests:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.request_entry = ttk.Entry(form, width=75)
        self.request_entry.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        buttons = ttk.Frame(self.root)
        buttons.pack(fill="x", padx=15, pady=5)
        ttk.Button(buttons, text="Add Booking", style="Sand.TButton", command=self.add_booking).pack(side="left", padx=4)
        ttk.Button(buttons, text="Update Selected", style="Sand.TButton", command=self.update_booking).pack(side="left", padx=4)
        ttk.Button(buttons, text="Delete Selected", style="Sand.TButton", command=self.delete_booking).pack(side="left", padx=4)
        ttk.Button(buttons, text="Clear Form", style="Sand.TButton", command=self.clear_form).pack(side="left", padx=4)

        search_frame = ttk.LabelFrame(self.root, text="Search Bookings", padding=10)
        search_frame.pack(fill="x", padx=15, pady=8)
        ttk.Label(search_frame, text="Name or Booking ID:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=35)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Search", style="Sand.TButton", command=self.search_bookings).pack(side="left", padx=4)
        ttk.Button(search_frame, text="Show All", style="Sand.TButton", command=self.load_bookings).pack(side="left", padx=4)

        table_frame = ttk.LabelFrame(self.root, text="Booking Records", padding=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0,12))

        columns = ("bid", "gname", "contact", "cin", "cout", "ctype", "status", "req")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {"bid":"Booking ID", "gname":"Guest Name", "contact":"Contact", "cin":"Check‑in", "cout":"Check‑out", "ctype":"Cottage Type", "status":"Status", "req":"Special Requests"}
        widths = {"bid":55, "gname":160, "contact":110, "cin":100, "cout":100, "ctype":130, "status":95, "req":180}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.select_booking)

        self.count_label = ttk.Label(self.root, text="Total bookings: 0")
        self.count_label.pack(anchor="w", padx=20, pady=(0,8))

    def get_form_data(self):
        gname = self.name_entry.get().strip()
        contact = self.contact_entry.get().strip()
        cin = self.checkin_entry.get().strip()
        cout = self.checkout_entry.get().strip()
        ctype = self.cottage_box.get().strip()
        status = self.status_box.get()
        req = self.request_entry.get().strip()

        if not gname or not contact or not cin or not cout:
            messagebox.showwarning("Missing Info", "Fill guest name, contact, check‑in and check‑out dates first.")
            return None
        try:
            datetime.strptime(cin, "%Y‑%m‑%d")
        except ValueError:
            messagebox.showerror("Wrong Date", "Use format YYYY‑MM‑DD for check‑in")
            return None
        try:
            datetime.strptime(cout, "%Y‑%m‑%d")
        except ValueError:
            messagebox.showerror("Wrong Date", "Use format YYYY‑MM‑DD for check‑out")
            return None
        return (gname, contact, cin, cout, ctype, status, req)

    def add_booking(self):
        data = self.get_form_data()
        if data is None: return
        try:
            with connect_db() as conn:
                conn.execute("INSERT INTO resort_bookings (guest_name, contact, checkin_date, checkout_date, cottage_type, booking_status, special_requests) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
            messagebox.showinfo("Success", "New resort booking saved!")
            self.clear_form()
            self.load_bookings()
        except sqlite3.Error as err:
            messagebox.showerror("Database Error", str(err))

    def load_bookings(self):
        self.display_records()

    def display_records(self, query=None, params=()):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            with connect_db() as conn:
                if query:
                    rows = conn.execute(query, params).fetchall()
                else:
                    rows = conn.execute("SELECT booking_id, guest_name, contact, checkin_date, checkout_date, cottage_type, booking_status, special_requests FROM resort_bookings ORDER BY checkin_date").fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            self.count_label.config(text=f"Total bookings: {len(rows)}")
        except sqlite3.Error as err:
            messagebox.showerror("Database Error", str(err))

    def search_bookings(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_bookings()
            return
        if keyword.isdigit():
            q = "SELECT booking_id, guest_name, contact, checkin_date, checkout_date, cottage_type, booking_status, special_requests FROM resort_bookings WHERE guest_name LIKE ? OR booking_id = ? ORDER BY checkin_date"
            p = (f"%{keyword}%", int(keyword))
        else:
            q = "SELECT booking_id, guest_name, contact, checkin_date, checkout_date, cottage_type, booking_status, special_requests FROM resort_bookings WHERE guest_name LIKE ? ORDER BY checkin_date"
            p = (f"%{keyword}%",)
        self.display_records(q, p)

    def select_booking(self, event=None):
        selected = self.tree.selection()
        if not selected: return
        vals = self.tree.item(selected[0], "values")
        self.selected_id = int(vals[0])
        self.name_entry.delete(0, tk.END); self.name_entry.insert(0, vals[1])
        self.contact_entry.delete(0, tk.END); self.contact_entry.insert(0, vals[2])
        self.checkin_entry.delete(0, tk.END); self.checkin_entry.insert(0, vals[3])
        self.checkout_entry.delete(0, tk.END); self.checkout_entry.insert(0, vals[4])
        self.cottage_box.set(vals[5])
        self.status_box.set(vals[6])
        self.request_entry.delete(0, tk.END); self.request_entry.insert(0, vals[7] or "")

    def update_booking(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Pick a booking from the table first.")
            return
        data = self.get_form_data()
        if data is None: return
        if not messagebox.askyesno("Confirm Update", "Update this resort booking?"): return
        try:
            with connect_db() as conn:
                conn.execute("UPDATE resort_bookings SET guest_name=?, contact=?, checkin_date=?, checkout_date=?, cottage_type=?, booking_status=?, special_requests=? WHERE booking_id=?", data + (self.selected_id,))
            messagebox.showinfo("Success", "Booking updated!")
            self.clear_form()
            self.load_bookings()
        except sqlite3.Error as err:
            messagebox.showerror("Database Error", str(err))

    def delete_booking(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Pick a booking from the table first.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete this resort booking?"): return
        try:
            with connect_db() as conn:
                conn.execute("DELETE FROM resort_bookings WHERE booking_id=?", (self.selected_id,))
            messagebox.showinfo("Success", "Booking removed!")
            self.clear_form()
            self.load_bookings()
        except sqlite3.Error as err:
            messagebox.showerror("Database Error", str(err))

    def clear_form(self):
        self.selected_id = None
        for entry in (self.name_entry, self.contact_entry, self.checkin_entry, self.checkout_entry, self.request_entry, self.search_entry):
            entry.delete(0, tk.END)
        self.cottage_box.set("Beach Front Cottage")
        self.status_box.set("Pending")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

if __name__== "__main__":
    create_table()
    root = tk.Tk()
    app = ResortBookingSystem(root)
    root.mainloop()
