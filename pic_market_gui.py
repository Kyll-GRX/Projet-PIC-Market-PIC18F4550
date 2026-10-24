#!/usr/bin/env python3
"""
PIC-MARKET - Python GUI (first defense version)

What it does:
  - receives barcodes from the PIC18F4550 over USB HID
  - looks the product up, adds it to the cart (same product -> quantity + 1)
  - refuses unknown products and ignores double scans
  - lets the user add fresh items (fruits, bread) with buttons
  - sends the result back to the PIC so it can drive the GLCD, LEDs and buzzer
  - reconnects by itself if the USB cable is unplugged

USB HID protocol: every report is 64 bytes of ASCII text, padded with zeros.
  PIC -> PC   SCAN:<barcode>                   a barcode was read (sent when CR is received)
  PC -> PIC   OK:<price>:<total>:<name>        known product, added to the cart
  PC -> PIC   UNK                              unknown product, not added
  PC -> PIC   ADD:<price>:<total>:<name>       item added from the GUI buttons
  PC -> PIC   TOT:<total>                      cart changed (line removed)
  PC -> PIC   RST                              transaction cancelled, back to the start
Prices are sent as text with two decimals, e.g. 2.50

Install: pip install hidapi      Run: python pic_market_gui.py
"""

import queue
import threading
import time
import tkinter as tk
from tkinter import ttk

try:
    import hid  # package "hidapi"
except ImportError:
    hid = None

# ---------------------------------------------------------------- settings
VENDOR_ID = 0x04D8      # Microchip default VID: change to the one in your USB descriptor
PRODUCT_ID = 0x003F     # Microchip "Simple HID" PID: change to yours
REPORT_SIZE = 64
ANTI_DOUBLE_SCAN_S = 0.8  # same barcode within this time is ignored (TS2.4 needs scans 1 s apart to work)

# Scanned products: barcode -> (name, price in cents). Put the barcodes of your test products here.
PRODUCTS = {
    "3017620422003": ("Nutella 400g", 399),
    "5449000000996": ("Coca-Cola 33cl", 120),
    "3228857000166": ("Harrys bread", 219),
    "3038350208605": ("Pasta 500g", 129),
    "7622210449283": ("Prince biscuits", 189),
}

# Fresh items added from the GUI: (name, price in cents)
GUI_ITEMS = [
    ("Apple", 50), ("Banana", 30), ("Orange", 60),
    ("Baguette", 110), ("Croissant", 120), ("Pain au chocolat", 130),
]


def fmt(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


# ---------------------------------------------------------------- USB HID link
class HidLink(threading.Thread):
    """Background thread: opens the PIC, reads reports, writes queued messages, reconnects."""

    def __init__(self, inbox: queue.Queue):
        super().__init__(daemon=True)
        self.inbox = inbox            # messages for the GUI: ("status", bool) / ("msg", text) / ("log", text)
        self.outbox = queue.Queue()   # texts to send to the PIC
        self.stop_event = threading.Event()

    def send(self, text: str):
        self.outbox.put(text)

    def stop(self):
        self.stop_event.set()

    def run(self):
        if hid is None:
            self.inbox.put(("log", "hidapi is not installed: run  pip install hidapi"))
            return
        dev = None
        while not self.stop_event.is_set():
            if dev is None:
                self._drop_outbox()            # no board: nothing to send
                dev = self._open()
                if dev is None:
                    time.sleep(1)
                    continue
            try:
                self._flush_outbox(dev)
                data = dev.read(REPORT_SIZE, 50)   # waits max 50 ms
                if data:
                    text = bytes(data).split(b"\0", 1)[0].decode("ascii", "replace").strip()
                    if text:
                        self.inbox.put(("msg", text))
            except (OSError, IOError, ValueError) as exc:
                self.inbox.put(("log", f"USB connection lost ({exc})"))
                try:
                    dev.close()
                except Exception:
                    pass
                dev = None
                self.inbox.put(("status", False))
        if dev is not None:
            dev.close()

    def _open(self):
        try:
            dev = hid.device()
            dev.open(VENDOR_ID, PRODUCT_ID)
        except (OSError, IOError):
            return None
        self.inbox.put(("status", True))
        self.inbox.put(("log", "PIC connected"))
        return dev

    def _flush_outbox(self, dev):
        while True:
            try:
                text = self.outbox.get_nowait()
            except queue.Empty:
                return
            payload = text.encode("ascii", "replace")[:REPORT_SIZE].ljust(REPORT_SIZE, b"\0")
            if dev.write([0x00] + list(payload)) < 0:   # first byte = report ID 0
                raise OSError("write failed")
            self.inbox.put(("log", f">> {text}"))

    def _drop_outbox(self):
        while not self.outbox.empty():
            self.outbox.get_nowait()


# ---------------------------------------------------------------- GUI
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PIC-MARKET")
        self.geometry("1000x620")
        self.minsize(850, 520)

        self.cart = {}            # key -> [name, unit price (cents), quantity]
        self.last_scan = ("", 0.0)
        self.inbox = queue.Queue()
        self.link = HidLink(self.inbox)

        self._build_ui()
        self.link.start()
        self.after(20, self._poll)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=28, font=("Helvetica", 12))
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        style.configure("Item.TButton", font=("Helvetica", 12), padding=8)

        top = ttk.Frame(self, padding=(12, 10))
        top.pack(fill="x")
        ttk.Label(top, text="PIC-MARKET", font=("Helvetica", 20, "bold")).pack(side="left")
        self.usb_label = tk.Label(top, text="USB: not connected", fg="#b3261e", font=("Helvetica", 12))
        self.usb_label.pack(side="right")

        body = ttk.Frame(self, padding=(12, 0))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        # cart (TS4.2: name, unit price, quantity, subtotal)
        cols = ("name", "unit", "qty", "sub")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", selectmode="browse")
        for col, text, width, anchor in [("name", "Product", 300, "w"), ("unit", "Unit price", 110, "e"),
                                         ("qty", "Qty", 70, "center"), ("sub", "Subtotal", 110, "e")]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor, stretch=(col == "name"))
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.total_label = ttk.Label(body, text="Total: 0.00 €", font=("Helvetica", 24, "bold"))
        self.total_label.grid(row=1, column=0, sticky="e", pady=8)

        # fresh items
        side = ttk.Frame(body, padding=(14, 0, 0, 0))
        side.grid(row=0, column=1, rowspan=2, sticky="n")
        ttk.Label(side, text="Fruits and bread", font=("Helvetica", 13, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        for i, (name, price) in enumerate(GUI_ITEMS):
            ttk.Button(side, text=f"{name}\n{fmt(price)} €", style="Item.TButton", width=14,
                       command=lambda n=name, p=price: self.add_gui_item(n, p)
                       ).grid(row=1 + i // 2, column=i % 2, padx=3, pady=3, sticky="ew")

        # bottom controls
        bottom = ttk.Frame(self, padding=(12, 6))
        bottom.pack(fill="x")
        ttk.Label(bottom, text="Barcode (manual test)").pack(side="left")
        self.code_var = tk.StringVar()
        entry = ttk.Entry(bottom, textvariable=self.code_var, width=18)
        entry.pack(side="left", padx=6)
        entry.bind("<Return>", lambda _e: self._manual_scan())
        ttk.Button(bottom, text="Add", command=self._manual_scan).pack(side="left")
        ttk.Button(bottom, text="New sale", command=self.new_sale).pack(side="right")
        ttk.Button(bottom, text="Remove line", command=self.remove_line).pack(side="right", padx=6)

        self.status = tk.Label(self, text="Ready - scan a product", anchor="w",
                               font=("Helvetica", 12), padx=12)
        self.status.pack(fill="x")

        self.log = tk.Text(self, height=5, state="disabled", font=("Courier", 10))
        self.log.pack(fill="x", padx=12, pady=(4, 10))

    # ------------------------------------------------------------ helpers
    def set_status(self, text, kind="ok"):
        colors = {"ok": "#1b7f3b", "error": "#b3261e", "warn": "#9a6700", "info": "#333333"}
        self.status.configure(text=text, fg=colors[kind])

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", time.strftime("%H:%M:%S ") + text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def total(self):
        return sum(unit * qty for _name, unit, qty in self.cart.values())

    def refresh_total(self):
        self.total_label.configure(text=f"Total: {fmt(self.total())} €")

    # ------------------------------------------------------------ cart
    def add_to_cart(self, key, name, price):
        if key in self.cart:
            self.cart[key][2] += 1          # TS4.3: same product -> quantity + 1
        else:
            self.cart[key] = [name, price, 1]
        name, unit, qty = self.cart[key]
        values = (name, f"{fmt(unit)} €", qty, f"{fmt(unit * qty)} €")
        if self.tree.exists(key):
            self.tree.item(key, values=values)
        else:
            self.tree.insert("", "end", iid=key, values=values)
        self.tree.selection_set(key)
        self.tree.see(key)
        self.refresh_total()

    def handle_barcode(self, code, from_pic=True):
        code = code.strip()
        if not code:
            return
        now = time.monotonic()
        last_code, last_time = self.last_scan
        if from_pic and code == last_code and now - last_time < ANTI_DOUBLE_SCAN_S:
            self.set_status(f"Double scan ignored ({code})", "warn")
            return
        self.last_scan = (code, now)

        product = PRODUCTS.get(code)
        if product is None:
            self.link.send("UNK")
            self.set_status(f"Unknown product {code} - not added to the cart", "error")
            return
        name, price = product
        self.add_to_cart(code, name, price)
        self.link.send(f"OK:{fmt(price)}:{fmt(self.total())}:{name[:40]}")
        self.set_status(f"{name} added - {fmt(price)} €")

    def add_gui_item(self, name, price):
        self.add_to_cart("gui:" + name, name, price)
        self.link.send(f"ADD:{fmt(price)}:{fmt(self.total())}:{name[:40]}")
        self.set_status(f"{name} added - {fmt(price)} €")

    def remove_line(self):
        sel = self.tree.selection()
        if not sel:
            self.set_status("Select a line to remove", "info")
            return
        key = sel[0]
        name = self.cart.pop(key)[0]
        self.tree.delete(key)
        self.refresh_total()
        self.link.send(f"TOT:{fmt(self.total())}")
        self.set_status(f"{name} removed", "info")

    def new_sale(self):
        self.cart.clear()
        self.tree.delete(*self.tree.get_children())
        self.refresh_total()
        self.link.send("RST")
        self.set_status("New sale - scan a product", "info")

    def _manual_scan(self):
        self.handle_barcode(self.code_var.get(), from_pic=False)
        self.code_var.set("")

    # ------------------------------------------------------------ USB events
    def _poll(self):
        try:
            while True:
                kind, value = self.inbox.get_nowait()
                if kind == "status":
                    self.usb_label.configure(text="USB: PIC connected" if value else "USB: not connected",
                                             fg="#1b7f3b" if value else "#b3261e")
                elif kind == "log":
                    self.write_log(value)
                elif kind == "msg":
                    self.write_log(f"<< {value}")
                    if value.startswith("SCAN:"):
                        self.handle_barcode(value[5:])
        except queue.Empty:
            pass
        self.after(20, self._poll)

    def _on_close(self):
        self.link.stop()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
