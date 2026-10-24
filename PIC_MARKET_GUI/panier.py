"""
panier.py - Panier de PIC-MARKET.

Ne depend ni de l'interface ni de l'USB : on peut le tester tout seul
(voir test_panier.py).

Choix : les lignes sont rangees dans un DICTIONNAIRE  code -> LignePanier.
Un code-barres = une seule ligne, donc scanner 2 fois le meme produit
augmente la quantite au lieu de creer une nouvelle ligne (TS4.3).
"""


class LignePanier:
    """Une ligne du panier : un produit et sa quantite."""

    def __init__(self, code, nom, prix_unitaire):
        self.code = code
        self.nom = nom
        self.prix_unitaire = prix_unitaire
        self.quantite = 1

    def sous_total(self):
        """Prix unitaire x quantite (en centimes)."""
        return self.prix_unitaire * self.quantite


class Panier:
    """Ensemble des lignes de la transaction en cours."""

    def __init__(self):
        self.lignes = {}   # code-barres -> LignePanier

    def ajouter(self, code, nom, prix_unitaire):
        """Ajoute un produit.
        - code deja present  -> quantite + 1
        - code absent        -> nouvelle LignePanier
        Retourne la ligne concernee.
        """
        if code in self.lignes:
            self.lignes[code].quantite += 1
        else:
            self.lignes[code] = LignePanier(code, nom, prix_unitaire)
        return self.lignes[code]

    def liste_lignes(self):
        """Retourne la liste des lignes (dans l'ordre d'ajout)."""
        return list(self.lignes.values())

    def total(self):
        """Somme des sous-totaux de toutes les lignes (en centimes)."""
        return sum(ligne.sous_total() for ligne in self.lignes.values())

    def vider(self):
        """Annule la transaction : le panier redevient vide (TS1.9)."""
        self.lignes.clear()
