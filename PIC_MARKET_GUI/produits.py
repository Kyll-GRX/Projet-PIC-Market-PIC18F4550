"""
produits.py - Catalogue des produits de PIC-MARKET (cote Python).

DONNEES DE TEST : produits et codes-barres fictifs.

Les prix sont en CENTIMES (nombres entiers) :
  - pas d'erreur d'arrondi (en Python, 0.1 + 0.2 == 0.3 est False)
  - c'est le meme format que celui envoye par le PIC
"""

# OPTION A : le catalogue de reference est DANS LE PIC (firmware C).
# Ce dictionnaire doit etre IDENTIQUE a celui du firmware (memes codes,
# memes noms, memes prix). Il sert au simulateur et aux tests.
#   - Toute modification ici = la meme modification dans le firmware.
#   - Noms SANS ACCENTS : le GLCD et le C ne gerent pas bien les accents.
#     TODO : "Café 250g" -> "Cafe 250g" (test_produits.py attend deja "Cafe")
#
# code-barres, nom, prix centimes
CATALOGUE = {
    "2000000000015": ("Lait 1L", 115),
    "2000000000022": ("Café 250g", 349),
    "2000000000039": ("Pates 500g", 99),
    "2000000000046": ("Riz 1kg", 189),
    "2000000000053": ("Eau 1.5L", 45),
    "2000000000060": ("Chocolat noir", 225),
    "2000000000077": ("Beurre 250g", 259),
    "2000000000084": ("Oeufs", 199),
    "2000000000091": ("Yaourt", 139),
    "2000000000107": ("Jus orange 1L", 215),
}


# TODO (bonus soutenance 1) : ARTICLES_SANS_CODE
# Fruits, pain... choisis par des BOUTONS du GUI (fonctionnalite n°2), vendus
# a l'UNITE. Le PIC ne les scanne jamais : ils n'existent que cote Python,
# donc on les met dans un dictionnaire SEPARE (CATALOGUE reste = firmware).
#   - meme format que CATALOGUE : code -> (nom, prix_centimes)
#   - codes inventes et lisibles, ex : "PAIN_BAGUETTE", "FRUIT_POMME"
#     (ils ne peuvent pas entrer en conflit avec un vrai code-barres a 13 chiffres)
#   - 3 a 6 articles suffisent
#   - interface.py creera un bouton par article avec une boucle (voir TODO 6)
#   - pense a ajouter quelques assert dans test_produits.py


def chercher_produit(code):
    """Retourne le tuple (nom, prix_centimes) du produit,
    ou None si le code n'est pas dans le catalogue.

    Exemple : chercher_produit("2000000000015") -> ("Lait 1L", 115)
    """
    return CATALOGUE.get(code)


def formater_prix(centimes):
    """Transforme un prix en centimes en texte lisible.

    Exemples : 115 -> "1,15 EUR"    99 -> "0,99 EUR"    5 -> "0,05 EUR"
    """
    euros = centimes // 100
    centimes_restants = centimes % 100
    return f"{euros},{centimes_restants:02d} EUR"
