
import threading
import tkinter as tk
from queue import Empty, Queue
from tkinter import ttk

from h1_monitor import HLServiceMonitor
from h1_logger import hl_save_measurement

import csv
from pathlib import Path
import matplotlib.pyplot as plt

services = [
    HLServiceMonitor("Google", "https://www.google.com", "HTTPS"),
    HLServiceMonitor("Gmail", "https://mail.google.com", "HTTPS"),
    HLServiceMonitor("Cloudflare DNS", "1.1.1.1", "PING"),
    HLServiceMonitor("Wikipédia", "https://www.wikipedia.org", "HTTPS")
]

root = tk.Tk()
root.title("Network & Service Monitor")
root.geometry("900x650")
root.minsize(700, 420)
root.configure(bg="#111827")

app = ttk.Frame(root, padding=20)
app.pack(fill="both", expand=True)

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Treeview",
    rowheight=38,
    font=("Segoe UI", 10)
)
style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 10, "bold")
)

title = ttk.Label(
    app,
    text="Network & Service Monitor",
    font=("Segoe UI", 20, "bold")
)
title.pack(anchor="w", pady=(0, 8))

subtitle = ttk.Label(
    app,
    text="Nyilvános hálózati szolgáltatások elérhetőségének figyelése",
    font=("Segoe UI", 10)
)
subtitle.pack(anchor="w", pady=(0, 20))

columns = ("name", "method", "status", "time", "checked")

table = ttk.Treeview(
    app,
    columns=columns,
    show="headings",
    height=5
)

table.heading("name", text="Szolgáltatás")
table.heading("method", text="Módszer")
table.heading("status", text="Állapot")
table.heading("time", text="Válaszidő")
table.heading("checked", text="Utolsó ellenőrzés")

table.column("name", width=190)
table.column("method", width=100, anchor="center")
table.column("status", width=130, anchor="center")
table.column("time", width=110, anchor="center")
table.column("checked", width=200, anchor="center")

table.tag_configure("online", foreground="#15803d")
table.tag_configure("offline", foreground="#dc2626")

table.pack(fill="x", expand=False)

for service in services:
    table.insert(
        "",
        "end",
        iid=service.name,
        values=(service.name, service.method, "Nincs adat", "-", "-")
    )

status_label = ttk.Label(
    app,
    text="A rendszer készen áll az ellenőrzésre.",
    font=("Segoe UI", 10)
)
status_label.pack(anchor="w", pady=15)

results_queue = Queue()
checking = False
auto_check = tk.BooleanVar(value=False)

def update_table(result):
    name = result["name"]
    status = "ONLINE" if result["online"] else "OFFLINE"
    response_time = result["response_time"]
    display_time = f"{response_time} ms" if response_time is not None else "-"

    table.item(
        name,
        values=(
            name,
            next(s.method for s in services if s.name == name),
            status,
            display_time,
            result["timestamp"]
        ),
        tags=("online" if result["online"] else "offline",)
    )


def run_checks():
    for service in services:
        result = service.check()
        results_queue.put(result)

    results_queue.put(None)


def start_check():
    global checking

    if checking:
        return

    checking = True
    check_button.config(state="disabled")
    status_label.config(text="Ellenőrzés folyamatban...")

    worker = threading.Thread(target=run_checks, daemon=True)
    worker.start()

def automatic_check():
    if auto_check.get():
        start_check()

    root.after(10000, automatic_check)

def process_results():
    global checking

    try:
        while True:
            result = results_queue.get_nowait()

            if result is None:
                checking = False
                check_button.config(state="normal")
                status_label.config(text="Az ellenőrzés befejeződött.")
            else:
                update_table(result)
                hl_save_measurement(result)

    except Empty:
        pass

    root.after(100, process_results)


def show_chart():
    file_path = Path(__file__).resolve().parent / "data" / "measurements.csv"

    if not file_path.exists():
        status_label.config(text="Még nincsenek mentett mérési adatok.")
        return

    measurements = {}

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            name = row["Szolgáltatás"]
            response_time = row["Válaszidő (ms)"]

            if not response_time:
                continue

            if name not in measurements:
                measurements[name] = []

            measurements[name].append(float(response_time))

    if not measurements:
        status_label.config(text="Nincs megjeleníthető válaszidő.")
        return

    plt.figure(figsize=(10, 5))

    for name, values in measurements.items():
        values = values[-20:]
        plt.plot(
            range(1, len(values) + 1),
            values,
            marker="o",
            label=name
        )

    plt.title("Szolgáltatások válaszideje")
    plt.xlabel("Utolsó mérések sorszáma")
    plt.ylabel("Válaszidő (ms)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)


def add_service():
    window = tk.Toplevel(root)
    window.title("Új szolgáltatás hozzáadása")
    window.geometry("380x270")
    window.resizable(False, False)

    ttk.Label(window, text="Szolgáltatás neve:").pack(pady=(15, 5))
    name_entry = ttk.Entry(window, width=35)
    name_entry.pack()

    ttk.Label(window, text="Cím (URL vagy IP):").pack(pady=(10, 5))
    address_entry = ttk.Entry(window, width=35)
    address_entry.pack()

    ttk.Label(window, text="Ellenőrzés módja:").pack(pady=(10, 5))
    method_var = tk.StringVar(value="HTTPS")

    method_box = ttk.Combobox(
        window,
        textvariable=method_var,
        values=["HTTPS", "PING"],
        state="readonly",
        width=32
    )
    method_box.pack()

    def save_service():
        name = name_entry.get().strip()
        address = address_entry.get().strip()
        method = method_var.get()

        if not name or not address:
            status_label.config(text="A név és a cím megadása kötelező.")
            return

        if any(service.name == name for service in services):
            status_label.config(text="Ez a szolgáltatásnév már létezik.")
            return

        if method == "HTTPS" and not address.startswith(("http://", "https://")):
            address = "https://" + address

        if method == "PING" and (
            "://" in address or "/" in address or " " in address
        ):
            status_label.config(text="PING esetén IP-címet vagy hosztnevet adj meg.")
            return

        services.append(HLServiceMonitor(name, address, method))

        table.insert(
            "",
            "end",
            iid=name,
            values=(name, method, "Nincs adat", "-", "-")
        )

        status_label.config(text=f"Új szolgáltatás hozzáadva: {name}")
        window.destroy()

    ttk.Button(
        window,
        text="Hozzáadás",
        command=save_service
    ).pack(pady=20)


check_button = ttk.Button(
    app,
    text="Ellenőrzés indítása",
    command=start_check
)
check_button.pack(anchor="e", pady=10)

auto_checkbox = ttk.Checkbutton(
    app,
    text="Automatikus ellenőrzés (10 másodperc)",
    variable=auto_check
)
auto_checkbox.pack(anchor="e", pady=5)


chart_button = ttk.Button(
    app,
    text="Válaszidőgrafikon megjelenítése",
    command=show_chart
)
chart_button.pack(anchor="e", pady=5)

add_button = ttk.Button(
    app,
    text="Új szolgáltatás hozzáadása",
    command=add_service
)
add_button.pack(anchor="e", pady=5)

root.after(100, process_results)
root.after(10000, automatic_check)
root.mainloop()
