"""Test du decodage des trames USB (sans PIC) :  py test_communication_usb.py"""
from communication_usb import (CHAMP_CODE, CHAMP_NOM, CHAMP_PRIX, TAILLE_RAPPORT,
                               TYPE_ANNULER, TYPE_PRODUIT_INCONNU, TYPE_PRODUIT_RECONNU,
                               creer_trame_annulation, decoder_trame)


def fabriquer_rapport(type_trame, code="", nom="", prix=0):
    """Construit un rapport de 64 octets comme le ferait le PIC."""
    rapport = [0] * TAILLE_RAPPORT
    rapport[0] = type_trame
    for i, octet in enumerate(code.encode("ascii")):
        rapport[CHAMP_CODE[0] + i] = octet
    for i, octet in enumerate(nom.encode("ascii")):
        rapport[CHAMP_NOM[0] + i] = octet
    rapport[CHAMP_PRIX] = prix % 256
    rapport[CHAMP_PRIX + 1] = prix // 256
    return rapport


assert decoder_trame(fabriquer_rapport(TYPE_PRODUIT_RECONNU, "2000000000015", "Lait 1L", 115)) \
    == ("reconnu", "2000000000015", "Lait 1L", 115)

# Code de 20 caracteres, nom de 15 caracteres, prix > 255
assert decoder_trame(fabriquer_rapport(TYPE_PRODUIT_RECONNU, "12345678901234567890",
                                       "Cafe moulu 250g", 65535)) \
    == ("reconnu", "12345678901234567890", "Cafe moulu 250g", 65535)

assert decoder_trame(fabriquer_rapport(TYPE_PRODUIT_INCONNU, "2000000000114")) \
    == ("inconnu", "2000000000114")

# Trames invalides
assert decoder_trame([1, 2, 3]) == ("invalide",)
assert decoder_trame(fabriquer_rapport(0x7F, "123")) == ("invalide",)

# Trame d'annulation envoyee au PIC
t = creer_trame_annulation()
assert len(t) == TAILLE_RAPPORT and t[0] == TYPE_ANNULER and sum(t[1:]) == 0

print("Trames USB OK")
