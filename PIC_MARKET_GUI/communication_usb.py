"""
communication_usb.py - Echange de trames USB HID avec le PIC.

Bibliotheque : hidapi  (py -m pip install hidapi)

Rapports de 64 octets, octet 0 = type de trame :
  PIC -> PC  0x01 produit reconnu
               octets 1 a 20   : code-barres ASCII, complete par des 0
               octets 21 a 36  : nom ASCII, complete par des 0
               octets 37 et 38 : prix en centimes, uint16 little-endian (37 = poids faible)
  PIC -> PC  0x02 code inconnu
               octets 1 a 20   : code-barres ASCII, complete par des 0
  PC -> PIC  0x10 annuler la transaction, reste a 0
"""
import hid

VID = 0x04D8           # a confirmer avec le descripteur USB du firmware
PID = 0x600A
TAILLE_RAPPORT = 64

TYPE_PRODUIT_RECONNU = 0x01
TYPE_PRODUIT_INCONNU = 0x02
TYPE_ANNULER = 0x10

CHAMP_CODE = (1, 20)   # (premier octet, taille)
CHAMP_NOM = (21, 16)
CHAMP_PRIX = 37


def _lire_texte(rapport, champ):
    """Texte ASCII d'un champ, coupe au premier octet 0."""
    debut, taille = champ
    octets = bytes(rapport[debut:debut + taille]).split(b"\x00")[0]
    return octets.decode("ascii", errors="replace")


def decoder_trame(rapport):
    """Rapport recu -> ("reconnu", code, nom, prix), ("inconnu", code) ou ("invalide",)."""
    if len(rapport) < TAILLE_RAPPORT:
        return ("invalide",)
    code = _lire_texte(rapport, CHAMP_CODE)
    if rapport[0] == TYPE_PRODUIT_RECONNU:
        nom = _lire_texte(rapport, CHAMP_NOM)
        prix = rapport[CHAMP_PRIX] + rapport[CHAMP_PRIX + 1] * 256
        return ("reconnu", code, nom, prix)
    if rapport[0] == TYPE_PRODUIT_INCONNU:
        return ("inconnu", code)
    return ("invalide",)


def creer_trame_annulation():
    trame = [0] * TAILLE_RAPPORT
    trame[0] = TYPE_ANNULER
    return trame


class CommunicationUSB:
    def __init__(self):
        self.peripherique = None

    def est_connecte(self):
        return self.peripherique is not None

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

    def lire_trame(self):
        """Prochaine trame decodee, ou None s'il n'y a rien (ou si le PIC est absent)."""
        if not self.est_connecte():
            return None
        try:
            rapport = self.peripherique.read(TAILLE_RAPPORT)
        except OSError:
            self.fermer()                          # cable debranche
            return None
        return decoder_trame(rapport) if rapport else None

    def envoyer_annulation(self):
        if not self.est_connecte():
            return
        try:
            # 1er octet = numero de rapport pour hidapi (0), non transmis au PIC
            self.peripherique.write([0x00] + creer_trame_annulation())
        except OSError:
            self.fermer()

    def fermer(self):
        if self.peripherique is not None:
            try:
                self.peripherique.close()
            except OSError:
                pass
        self.peripherique = None
