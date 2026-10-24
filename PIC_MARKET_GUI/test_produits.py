"""Test du catalogue :  py test_produits.py"""
from produits import CATALOGUE, chercher_produit

assert len(CATALOGUE) == 10
assert chercher_produit("2000000000015") == ("Lait 1L", 115)
assert chercher_produit("2000000000022") == ("Cafe moulu 250g", 349)
assert chercher_produit("2000000000114") is None        # code de test inconnu

# Noms affichables sur le GLCD et prix entiers
for code, (nom, prix) in CATALOGUE.items():
    assert len(code) <= 20 and code.isdigit()
    assert len(nom) <= 15 and nom.isascii()
    assert isinstance(prix, int) and prix > 0

print("Produits OK")
