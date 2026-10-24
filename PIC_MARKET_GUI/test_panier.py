"""Test de l'etape 2 :  py test_panier.py"""
from panier import Panier

p = Panier()
assert p.total() == 0 and p.liste_lignes() == []

# Un produit
p.ajouter("2000000000015", "Lait 1L", 115)
assert p.total() == 115

# Meme produit une 2e fois -> quantite 2, toujours 1 seule ligne (TS4.3)
ligne = p.ajouter("2000000000015", "Lait 1L", 115)
assert ligne.quantite == 2
assert len(p.liste_lignes()) == 1
assert ligne.sous_total() == 230

# Autre produit -> nouvelle ligne, total recalcule
p.ajouter("2000000000039", "Pates 500g", 99)
assert len(p.liste_lignes()) == 2
assert p.total() == 329

# Nouvelle transaction (TS1.9)
p.vider()
assert p.total() == 0 and p.liste_lignes() == []

print("Etape 2 OK")
