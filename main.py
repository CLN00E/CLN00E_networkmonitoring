
import threading
import tkinter as tk
from queue import Empty, Queue
from tkinter import ttk

from h1_monitor import HLServiceMonitor


services = [
    HLServiceMonitor("Google", "https://www.google.com", "HTTPS"),
    HLServiceMonitor("Gmail", "https://mail.google.com", "HTTPS"),
    HLServiceMonitor("Cloudflare DNS", "1.1.1.1", "PING"),
    HLServiceMonitor("Wikipédia", "https://www.wikipedia.org", "HTTPS")
]

root = tk.Tk()
root.title("Network & Service Monitor")
root.geometry("900x520")
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
    height=8
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

table.pack(fill="both", expand=True)

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

    except Empty:
        pass

    root.after(100, process_results)


check_button = ttk.Button(
    app,
    text="Ellenőrzés indítása",
    command=start_check
)
check_button.pack(anchor="e", pady=10)

root.after(100, process_results)
root.mainloop()
