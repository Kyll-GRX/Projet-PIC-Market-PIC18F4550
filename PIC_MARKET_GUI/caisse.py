"""
caisse.py - Logique de la caisse (sans Tkinter, donc testable seule).

    interface.py  --->  caisse.py  --->  communication_usb.py
    (affichage)                    --->  panier.py
                                   --->  produits.py (simulation)

Chaque action renvoie un resultat que l'interface affiche :
    ("reconnu", code, nom, prix)   produit ajoute au panier
    ("inconnu", code)              code refuse, panier inchange
    ("invalide",)                  trame USB illisible
"""
from communication_usb import CommunicationUSB
from panier import Panier
from produits import chercher_produit


class Caisse:
    def __init__(self, usb=None):
        self.panier = Panier()
        self.usb = usb if usb is not None else CommunicationUSB()   # faux USB pour les tests

    def traiter(self, resultat):
        """Applique un resultat au panier (seul "reconnu" le modifie) et le renvoie."""
        if resultat[0] == "reconnu":
            _, code, nom, prix = resultat
            self.panier.ajouter(code, nom, prix)
        return resultat

    def simuler_scan(self, code):
        """Fait ce que fait le PIC : cherche le code dans le catalogue."""
        code = code.strip()
        if not code:
            return None
        produit = chercher_produit(code)
        if produit is None:
            return self.traiter(("inconnu", code))
        nom, prix = produit
        return self.traiter(("reconnu", code, nom, prix))

    def lire_usb(self):
        """Renvoie la liste des resultats de toutes les trames arrivees.
        Si le PIC est absent, tente de le (re)ouvrir."""
        if not self.usb.est_connecte():
            self.usb.ouvrir()
            return []
        resultats = []
        trame = self.usb.lire_trame()
        while trame is not None:
            resultats.append(self.traiter(trame))
            trame = self.usb.lire_trame()
        return resultats

    def usb_connecte(self):
        return self.usb.est_connecte()

    def nouvelle_transaction(self):
        """Vide le panier et previent le PIC."""
        self.panier.vider()
        self.usb.envoyer_annulation()

    def fermer(self):
        self.usb.fermer()
