"""Test du panier :  py test_panier.py"""
from panier import Panier, formater_prix

assert formater_prix(0) == "0,00 EUR"
assert formater_prix(5) == "0,05 EUR"
assert formater_prix(115) == "1,15 EUR"
assert formater_prix(1000) == "10,00 EUR"

p = Panier()
assert p.total() == 0 and p.liste_lignes() == []

p.ajouter("2000000000015", "Lait 1L", 115)
assert p.total() == 115

# Meme produit une 2e fois -> quantite 2, toujours 1 seule ligne
ligne = p.ajouter("2000000000015", "Lait 1L", 115)
assert ligne.quantite == 2
assert len(p.liste_lignes()) == 1
assert ligne.sous_total() == 230

# Autre produit -> nouvelle ligne, total recalcule
p.ajouter("2000000000039", "Pates 500g", 99)
assert len(p.liste_lignes()) == 2
assert p.total() == 329

print("Panier OK")
