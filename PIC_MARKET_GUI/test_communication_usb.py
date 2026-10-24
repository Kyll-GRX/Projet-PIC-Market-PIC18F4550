"""Test du decodage des trames USB (sans PIC) :  py test_communication_usb.py"""
from communication_usb import (CHAMP_CODE, CHAMP_NOM, CHAMP_PRIX, TAILLE_RAPPORT,
                               TYPE_PRODUIT, decoder_trame)


def fabriquer_rapport(code, nom, prix, type_trame=TYPE_PRODUIT):
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


assert decoder_trame(fabriquer_rapport("2000000000015", "Lait 1L", 115)) == \
    ("2000000000015", "Lait 1L", 115)

# Code de 20 caracteres, nom de 15 caracteres, prix > 255
assert decoder_trame(fabriquer_rapport("12345678901234567890", "Cafe moulu 250g", 65535)) == \
    ("12345678901234567890", "Cafe moulu 250g", 65535)

# Rapports ignores
assert decoder_trame([]) is None
assert decoder_trame(fabriquer_rapport("123", "X", 1, type_trame=0x7F)) is None

print("Trames USB OK")
