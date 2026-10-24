"""
panier.py - Panier de PIC-MARKET.

Les lignes sont rangees dans un dictionnaire  code -> LignePanier :
scanner 2 fois le meme produit augmente la quantite au lieu de creer
une nouvelle ligne.
Les prix sont en centimes (entiers) pour eviter les erreurs d'arrondi.
"""


def formater_prix(centimes):
    """115 -> "1,15 EUR"    5 -> "0,05 EUR" """
    return f"{centimes // 100},{centimes % 100:02d} EUR"


class LignePanier:
    """Une ligne du panier : un produit et sa quantite."""

    def __init__(self, code, nom, prix_unitaire):
        self.code = code
        self.nom = nom
        self.prix_unitaire = prix_unitaire
        self.quantite = 1

    def sous_total(self):
        return self.prix_unitaire * self.quantite


class Panier:
    def __init__(self):
        self.lignes = {}   # code-barres -> LignePanier

    def ajouter(self, code, nom, prix_unitaire):
        """Code deja present -> quantite + 1, sinon nouvelle ligne."""
        if code in self.lignes:
            self.lignes[code].quantite += 1
        else:
            self.lignes[code] = LignePanier(code, nom, prix_unitaire)
        return self.lignes[code]

    def liste_lignes(self):
        """Lignes dans l'ordre d'ajout."""
        return list(self.lignes.values())

    def total(self):
        return sum(ligne.sous_total() for ligne in self.lignes.values())

    def vider(self):
        self.lignes.clear()
