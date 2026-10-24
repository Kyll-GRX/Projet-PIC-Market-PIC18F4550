"""
caisse.py - Relie l'USB au panier (sans Tkinter, donc testable seul).

    interface.py  --->  caisse.py  --->  communication_usb.py
    (affichage)                    --->  panier.py
"""
from communication_usb import CommunicationUSB
from panier import Panier


class Caisse:
    def __init__(self, usb=None):
        self.panier = Panier()
        self.usb = usb if usb is not None else CommunicationUSB()   # faux USB pour les tests

    def lire_usb(self):
        """Ajoute au panier tous les produits arrives et renvoie la liste de leurs codes."""
        codes = []
        produit = self.usb.lire_produit()
        while produit is not None:
            code, nom, prix = produit
            self.panier.ajouter(code, nom, prix)
            codes.append(code)
            produit = self.usb.lire_produit()
        return codes

    def fermer(self):
        self.usb.fermer()
