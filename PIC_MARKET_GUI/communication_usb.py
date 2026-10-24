"""
communication_usb.py - Lien USB HID entre le PIC et Python.  (ETAPE 5 - plus tard)

A NE PAS COMMENCER AVANT que le firmware USB HID du PIC fonctionne.

Rappels :
  - HID, PAS un port COM : on n'utilise pas pyserial ici.
  - Bibliotheque : hidapi   ->  py -m pip install hidapi   (puis : import hid)
  - Rapports de 64 octets (guide "USB HID pour EasyPIC 7" du cours).
  - VID / PID : ceux de l'exemple du cours (Microchip) -> A CONFIRMER
    avec le descripteur USB du firmware.
  - La lecture est bloquante -> elle tournera dans un thread separe ;
    seul le thread de Tkinter a le droit de modifier la fenetre.
  - Le format des trames (octet de type, code, nom, prix...) sera defini
    ensemble avec l'equipe firmware.

Decision prise : OPTION A (catalogue dans le PIC).
  - Le PIC envoie "produit reconnu : code + nom + prix" ou "code inconnu".
  - Python n'interroge PAS son catalogue pour les scans reels.
  - Schema prevu pour l'etape 5 (ne pas coder avant) :
      thread USB : lire_trame() -> decoder -> mettre le resultat dans une
                   queue.Queue (le thread ne touche JAMAIS la fenetre)
      Tkinter    : fenetre.after(50, ...) vide la queue et appelle
                   Caisse.produit_recu() / Caisse.produit_inconnu()
    Ainsi interface.py n'a rien a changer : le simulateur et l'USB
    appellent les memes methodes.
"""

VID = 0x04D8           # A CONFIRMER
PID = 0x600A           # A CONFIRMER
TAILLE_RAPPORT = 64    # octets


class CommunicationUSB:

    def ouvrir(self):
        """Ouvre le peripherique HID. Retourne True si ca a marche."""
        # TODO (etape 5)
        pass

    def lire_trame(self):
        """Lit un rapport de 64 octets (ou None si rien n'est arrive)."""
        # TODO (etape 5)
        pass

    def envoyer_annulation(self):
        """Envoie au PIC l'ordre d'annuler la transaction (TS1.5 / TS1.9)."""
        # TODO (etape 5)
        pass

    def fermer(self):
        # TODO (etape 5)
        pass
