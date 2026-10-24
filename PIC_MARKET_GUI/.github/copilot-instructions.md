# Repository Instructions

PIC-MARKET is a small Python/Tkinter checkout GUI paired with PIC18F4550 firmware (`../PIC_MARKET.X`). The PIC owns the product catalogue and sends each scan over USB HID; the GUI displays it.

## Structure and boundaries

- `produits.py`: test catalogue, identical to the one in `main.c`, used only by the simulation mode.
- `panier.py`: UI-independent cart and `formater_prix()`. Prices are integer centimes. Preserve one cart line per barcode and increase its quantity for repeated scans.
- `communication_usb.py`: 64-byte HID reports with `hidapi` (non-blocking). Frame types: 0x01 recognised product, 0x02 unknown code (PIC -> PC), 0x10 cancel transaction (PC -> PIC). This format is a proposal not yet validated by the firmware team, and VID/PID are unconfirmed; keep format details in its constants, `decoder_trame()` and `creer_trame_annulation()`. This project uses HID, not serial.
- `caisse.py`: links USB, cart and catalogue, no Tkinter; actions return result tuples (`("reconnu", code, nom, prix)`, `("inconnu", code)`, `("invalide",)`). Tested with a fake USB in `test_caisse.py`.
- `interface.py`: Tkinter window only (USB status, last code, simulation, ticket, messages, total, "Nouvelle transaction"; "Payer" is displayed without action). Polls `Caisse.lire_usb()` every 50 ms with `after()`. Colours are constants at the top of the file.
- Scope: first defence only. Loyalty, payment, invoice, history, persistence (TS4.4-TS4.11), RFID and RTC are out of scope.
- Comments explain code only. Source, comments and tests are in French; names we choose are French, library names stay English.
- The student must be able to explain the code (30 % AI limit, AI use declared in `journal_ia.md`).

## Validation and commands

- `py test_produits.py`, `py test_panier.py`, `py test_communication_usb.py`, `py test_caisse.py` (standalone assertion scripts, no PIC needed).
- Launch the GUI with `py interface.py` (requires `py -m pip install hidapi`).
