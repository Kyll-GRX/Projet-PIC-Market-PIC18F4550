"""Test de l'etape 1 :  py test_produits.py"""
from produits import CATALOGUE, chercher_produit, formater_prix

produits_attendus = {
	"2000000000015": ("Lait 1L", 115),
	"2000000000022": ("Cafe 250g", 349),
	"2000000000039": ("Pates 500g", 99),
	"2000000000046": ("Riz 1kg", 189),
	"2000000000053": ("Eau 1.5L", 45),
	"2000000000060": ("Chocolat noir", 225),
	"2000000000077": ("Beurre 250g", 259),
	"2000000000084": ("Oeufs", 199),
	"2000000000091": ("Yaourt", 139),
	"2000000000107": ("Jus orange 1L", 215),
}

assert CATALOGUE == produits_attendus
for code, produit in produits_attendus.items():
	assert chercher_produit(code) == produit

assert chercher_produit("0000") is None

assert formater_prix(115) == "1,15 EUR"
assert formater_prix(99) == "0,99 EUR"
assert formater_prix(5) == "0,05 EUR"
assert formater_prix(1000) == "10,00 EUR"

print("Etape 1 OK")
