import tkinter as tk
from tkinter import ttk, messagebox
from model.ticket_model import Ticket
import pickle
import os
from model.airline_data import *


DATA_FILE = "tickets.pkl"

class TicketApp:
    def __init__(self, window):
        self.window = window
        self.window.title("مدیریت بلیط هواپیما")
        self.window.geometry("1000x550")
        self.tickets = []
        self.selected = None

        self.vars = {
            "id": tk.IntVar(value=1),
            "source": tk.StringVar(),
            "dest": tk.StringVar(),
            "seat": tk.StringVar(),
            "start": tk.StringVar(),
            "end": tk.StringVar(),
            "airline": tk.StringVar(),
            "filter_city": tk.StringVar(value="همه"),
            "filter_date": tk.StringVar(value="همه")
        }

        self.build_ui()
        self.load_from_file()
        self.refresh()

    def build_ui(self):
        labels = ["ID", "Source", "Destination", "Seat", "Start", "End", "Airline"]
        for i, label in enumerate(labels):
            tk.Label(self.window, text=label).place(x=10, y=10 + i * 30)

        tk.Entry(self.window, textvariable=self.vars["id"], state="readonly", width=5).place(x=80, y=10)
        ttk.Combobox(self.window, textvariable=self.vars["source"], values=cities, width=12).place(x=80, y=40)
        ttk.Combobox(self.window, textvariable=self.vars["dest"], values=cities, width=12).place(x=80, y=70)
        tk.Entry(self.window, textvariable=self.vars["seat"], width=5).place(x=80, y=100)
        tk.Entry(self.window, textvariable=self.vars["start"], width=18).place(x=80, y=130)
        tk.Entry(self.window, textvariable=self.vars["end"], width=18).place(x=80, y=160)
        ttk.Combobox(self.window, textvariable=self.vars["airline"], values=airlines, width=14).place(x=80, y=190)

        tk.Button(self.window, text="Save", command=self.save).place(x=10, y=230)
        tk.Button(self.window, text="Edit", command=self.edit).place(x=60, y=230)
        tk.Button(self.window, text="Remove", command=self.delete).place(x=120, y=230)

        # جدول بلیط‌ها
        self.table = ttk.Treeview(self.window, columns=(1,2,3,4,5,6,7), show="headings")
        headers = ["ID", "Source", "Destination", "Seat", "Start", "End", "Airline"]
        widths =  [50, 100, 100, 60, 150, 150, 120]

        for i, (title, width) in enumerate(zip(headers, widths), 1):
            self.table.heading(i, text=title)
            self.table.column(i, width=width, anchor='center')

        self.table.place(x=250, y=20, height=400)
        self.table.bind("<<TreeviewSelect>>", self.load_selected)

        # فیلترها
        tk.Label(self.window, text="City Filter:").place(x=250, y=440)
        ttk.Combobox(self.window, textvariable=self.vars["filter_city"], values=["همه"] + cities, width=15)\
            .place(x=320, y=440)

        tk.Label(self.window, text="Date Filter:").place(x=500, y=440)
        self.date_filter_cb = ttk.Combobox(self.window, textvariable=self.vars["filter_date"], values=["همه"], width=15)
        self.date_filter_cb.place(x=580, y=440)

        self.vars["filter_city"].trace_add("write", self.on_filter_change)
        self.vars["filter_date"].trace_add("write", self.on_filter_change)

    def get_form_data(self):
        return Ticket(
            id=self.vars["id"].get(),
            source=self.vars["source"].get(),
            destination=self.vars["dest"].get(),
            seat_no=self.vars["seat"].get(),
            start=self.vars["start"].get(),
            end=self.vars["end"].get(),
            airline=self.vars["airline"].get()
        )

    def save(self):
        ticket = self.get_form_data()
        ticket.id = self.get_next_id()
        if not ticket.validate():
            return messagebox.showerror("خطا", "اطلاعات نامعتبر است.")
        self.tickets.append(ticket.__dict__)
        self.vars["id"].set(ticket.id + 1)
        self.save_to_file()
        self.refresh()

    def edit(self):
        if self.selected is None:
            return
        ticket = self.get_form_data()
        if not ticket.validate():
            return messagebox.showerror("خطا", "اطلاعات وارد شده معتبر نیست.")
        for i, t in enumerate(self.tickets):
            if t["id"] == ticket.id:
                self.tickets[i] = ticket.__dict__
                break
        self.save_to_file()
        self.refresh()

    def delete(self):
        if self.selected is None:
            return
        tid = int(self.vars["id"].get())
        self.tickets = [t for t in self.tickets if t["id"] != tid]
        self.save_to_file()
        self.refresh()

    def refresh(self):
        self.table.delete(*self.table.get_children())
        self.update_date_filter()
        for t in self.tickets:
            ticket = Ticket(**t)
            if self.pass_filter(ticket):
                self.table.insert("", "end", values=ticket.to_tuple())
        self.clear_form()

    def update_date_filter(self):
        dates = sorted({t["start"].split(" ")[0] for t in self.tickets})
        self.date_filter_cb["values"] = ["همه"] + dates

    def pass_filter(self, ticket):
        city = self.vars["filter_city"].get()
        date = self.vars["filter_date"].get()
        return (
            (city == "همه" or city in [ticket.source, ticket.destination]) and
            (date == "همه" or ticket.start.startswith(date))
        )

    def clear_form(self):
        for key in ["source", "dest", "seat", "start", "end", "airline"]:
            self.vars[key].set("")
        self.selected = None

    def load_selected(self, event):
        selected = self.table.selection()
        if not selected:
            return
        values = self.table.item(selected[0])["values"]
        keys = ["id", "source", "dest", "seat", "start", "end", "airline"]
        for i, key in enumerate(keys):
            self.vars[key].set(values[i])
        self.selected = selected[0]

    def get_next_id(self):
        return 1 if not self.tickets else max(t["id"] for t in self.tickets) + 1

    def save_to_file(self):
        with open(DATA_FILE, "wb") as f:
            pickle.dump(self.tickets, f)

    def load_from_file(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f:
                self.tickets = pickle.load(f)

    def on_filter_change(self, *args):
        self.refresh()


# اجرای برنامه
window = tk.Tk()
app = TicketApp(window)
window.mainloop()
