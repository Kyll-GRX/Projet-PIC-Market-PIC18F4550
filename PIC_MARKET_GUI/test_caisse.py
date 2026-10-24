"""Test du lien USB -> panier (sans PIC) :  py test_caisse.py"""
from caisse import Caisse


class FauxUSB:
    """Remplace CommunicationUSB : renvoie les produits qu'on lui donne."""

    def __init__(self, produits):
        self.produits = produits

    def lire_produit(self):
        return self.produits.pop(0) if self.produits else None

    def fermer(self):
        pass


usb = FauxUSB([("2000000000015", "Lait 1L", 115),
               ("2000000000039", "Pates 500g", 99),
               ("2000000000015", "Lait 1L", 115)])
c = Caisse(usb=usb)

# Tous les produits arrives sont lus d'un coup, dans l'ordre
assert c.lire_usb() == ["2000000000015", "2000000000039", "2000000000015"]
assert c.lire_usb() == []

# Le lait scanne 2 fois tient sur une seule ligne
lignes = c.panier.liste_lignes()
assert [(l.nom, l.quantite, l.sous_total()) for l in lignes] == \
    [("Lait 1L", 2, 230), ("Pates 500g", 1, 99)]
assert c.panier.total() == 329

print("Caisse OK")
