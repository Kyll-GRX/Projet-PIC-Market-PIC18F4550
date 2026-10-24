"""Test de la logique de la caisse (sans fenetre ni PIC) :  py test_caisse.py"""
from caisse import Caisse


class FauxUSB:
    """Remplace CommunicationUSB : renvoie les trames qu'on lui donne."""

    def __init__(self, trames=(), connecte=True):
        self.trames = list(trames)
        self.connecte = connecte
        self.annulations = 0

    def est_connecte(self):
        return self.connecte

    def ouvrir(self):
        return self.connecte

    def lire_trame(self):
        return self.trames.pop(0) if self.trames else None

    def envoyer_annulation(self):
        self.annulations += 1

    def fermer(self):
        self.connecte = False


# Trames du PIC : lues d'un coup, dans l'ordre ; seul "reconnu" remplit le panier
usb = FauxUSB([("reconnu", "2000000000015", "Lait 1L", 115),
               ("inconnu", "2000000000114"),
               ("invalide",),
               ("reconnu", "2000000000015", "Lait 1L", 115),
               ("reconnu", "2000000000039", "Pates 500g", 99)])
c = Caisse(usb=usb)
assert [r[0] for r in c.lire_usb()] == ["reconnu", "inconnu", "invalide", "reconnu", "reconnu"]
assert c.lire_usb() == []

# Le lait recu 2 fois tient sur une seule ligne
assert [(l.nom, l.quantite, l.sous_total()) for l in c.panier.liste_lignes()] == \
    [("Lait 1L", 2, 230), ("Pates 500g", 1, 99)]
assert c.panier.total() == 329

# Nouvelle transaction : panier vide et PIC prevenu
c.nouvelle_transaction()
assert c.panier.total() == 0 and usb.annulations == 1

# Simulation
c = Caisse(usb=FauxUSB(connecte=False))
assert c.simuler_scan(" 2000000000022 ") == ("reconnu", "2000000000022", "Cafe moulu 250g", 349)
assert c.simuler_scan("2000000000114") == ("inconnu", "2000000000114")
assert c.simuler_scan("") is None
assert c.panier.total() == 349

# PIC absent : rien n'est lu, aucune erreur
assert c.lire_usb() == []

print("Caisse OK")
