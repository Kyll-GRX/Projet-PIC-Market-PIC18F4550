"""
produits.py - Catalogue de test, identique a celui de main.c.

Sert au mode simulation : en vrai, c'est le PIC qui cherche le produit.
Les prix sont en centimes (entiers).
"""

# code-barres -> (nom, prix en centimes)
CATALOGUE = {
    "2000000000015": ("Lait 1L", 115),
    "2000000000022": ("Cafe moulu 250g", 349),
    "2000000000039": ("Pates 500g", 99),
    "2000000000046": ("Riz 1kg", 189),
    "2000000000053": ("Eau 1.5L", 45),
    "2000000000060": ("Chocolat noir", 225),
    "2000000000077": ("Beurre 250g", 259),
    "2000000000084": ("Oeufs x6", 199),
    "2000000000091": ("Yaourt nat x4", 139),
    "2000000000107": ("Jus orange 1L", 215),
}


def chercher_produit(code):
    """(nom, prix) du produit, ou None si le code n'est pas dans le catalogue."""
    return CATALOGUE.get(code)
