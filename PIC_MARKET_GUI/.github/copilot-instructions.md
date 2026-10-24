# Repository Instructions

PIC-MARKET is a small Python/Tkinter checkout application paired with PIC firmware.

## Structure and boundaries

- `produits.py` owns the product catalogue and price formatting. Prices are integer centimes, and the catalogue must match the firmware catalogue.
- Architecture decision (option A): the reference catalogue lives in the PIC firmware. The PIC sends code + name + price (or "unknown code"); Python only looks up `CATALOGUE` for the simulator. GUI-only items (fruit, bread) go in a separate `ARTICLES_SANS_CODE` dict. All items are sold per unit.
- The student writes the application code themselves (30 % AI limit): provide guidance and review, not finished implementations, unless explicitly asked.
- `panier.py` contains UI-independent cart logic. Preserve one cart line per barcode and increase its quantity for repeated scans.
- `interface.py` owns the Tkinter window and presentation; keep widget updates on the Tkinter thread.
- `communication_usb.py` is a later USB HID stage. Do not implement or assume a frame format or confirmed VID/PID without firmware specifications. This project uses HID, not serial.
- The source comments and tests are primarily in French; follow the existing language and style in nearby code.

## Validation and commands

- Run the product tests with `py test_produits.py`.
- Run the cart tests with `py test_panier.py`.
- Launch the GUI with `py interface.py` when testing UI changes.
- The tests are standalone Python scripts using assertions; no test framework is currently configured.

Keep changes focused, follow the existing function contracts and tests, and avoid adding dependencies unless a task requires them.