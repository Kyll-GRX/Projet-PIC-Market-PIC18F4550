"""
communication_usb.py - Lecture des trames USB HID envoyees par le PIC.

Bibliotheque : hidapi  (py -m pip install hidapi)

Trame "produit" de 64 octets :
    octet  0        : type = 0x01
    octets 1 a 20   : code-barres ASCII, complete par des 0
    octets 21 a 36  : nom ASCII, complete par des 0
    octets 37 et 38 : prix en centimes, uint16 little-endian (37 = poids faible)
"""
import hid

VID = 0x04D8           # a confirmer avec le descripteur USB du firmware
PID = 0x600A
TAILLE_RAPPORT = 64

TYPE_PRODUIT = 0x01
CHAMP_CODE = (1, 20)   # (premier octet, taille)
CHAMP_NOM = (21, 16)
CHAMP_PRIX = 37


def _lire_texte(rapport, champ):
    """Texte ASCII d'un champ, coupe au premier octet 0."""
    debut, taille = champ
    octets = bytes(rapport[debut:debut + taille]).split(b"\x00")[0]
    return octets.decode("ascii", errors="replace")


def decoder_trame(rapport):
    """Rapport recu -> (code, nom, prix), ou None si ce n'est pas une trame produit."""
    if len(rapport) < TAILLE_RAPPORT or rapport[0] != TYPE_PRODUIT:
        return None
    code = _lire_texte(rapport, CHAMP_CODE)
    nom = _lire_texte(rapport, CHAMP_NOM)
    prix = rapport[CHAMP_PRIX] + rapport[CHAMP_PRIX + 1] * 256
    return (code, nom, prix)


class CommunicationUSB:
    def __init__(self):
        self.peripherique = None

    def ouvrir(self):
        """Ouvre le PIC en lecture non bloquante. Retourne True si ca a marche."""
        try:
            self.peripherique = hid.device()
            self.peripherique.open(VID, PID)
            self.peripherique.set_nonblocking(1)   # read() rend [] au lieu d'attendre
            return True
        except OSError:
            self.peripherique = None
            return False

    def lire_produit(self):
        """(code, nom, prix) du prochain produit recu, ou None s'il n'y a rien."""
        if self.peripherique is None and not self.ouvrir():
            return None
        try:
            rapport = self.peripherique.read(TAILLE_RAPPORT)
        except OSError:
            self.fermer()                          # cable debranche : on rouvrira
            return None
        return decoder_trame(rapport) if rapport else None

    def fermer(self):
        if self.peripherique is not None:
            self.peripherique.close()
        self.peripherique = None
