"""
interface.py - Fenetre principale de la caisse PIC-MARKET (Tkinter).

Lancer :  py interface.py

Contenu attendu (TS4.2 / TS4.3) :
  - statut de la connexion USB
  - dernier code-barres recu + reconnu / inconnu
  - tableau : Produit | Prix unitaire | Quantite | Sous-total
  - total general, recalcule apres chaque scan
  - bouton "Nouvelle transaction" (TS1.9)
  - zone de SIMULATION (en attendant l'USB HID)

Architecture choisie (OPTION A) : le catalogue est DANS LE PIC.
  - Le PIC decide lui-meme si le produit est connu (LED verte/rouge, buzzer, GLCD).
  - Il envoie ensuite a Python : code + nom + prix  (ou "code inconnu").
  - Python NE recherche donc PAS le produit : il affiche ce que le PIC envoie.
  - Seul le SIMULATEUR utilise chercher_produit(), pour imiter le PIC.

Regle d'or : cette classe ne fait QUE de l'affichage. Les calculs restent
dans panier.py (ajouter, total, vider), les prix sont formates avec
formater_prix(). Ne jamais faire de calcul de prix ici.
"""
import tkinter as tk
from tkinter import ttk

from panier import Panier
from produits import chercher_produit, formater_prix


class Caisse:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("PIC-MARKET")
        self.fenetre.geometry("1000x800")

        self.panier = Panier()
        self.creer_elements()

    # ------------------------------------------------------------ fenetre
    def creer_elements(self):
        """Cree tous les elements de la fenetre."""
        # Les noms Tkinter (tk.Label, ttk.Button, pack, config, text=, fg=...)
        # restent en anglais : ils viennent de la bibliotheque, on ne peut pas
        # les changer. Tout ce qu'on NOMME nous-memes est en francais.
        # Les elements s'empilent de haut en bas dans l'ordre des .pack().
        # Tous ceux qu'on modifiera plus tard sont stockes dans self.xxx
        # (sinon on ne peut plus les retrouver dans les autres methodes).

        # Statut USB deconnecte (rouge)
        self.etiquette_usb = tk.Label(self.fenetre, text="USB : deconnecte", fg="red")
        self.etiquette_usb.pack(anchor="w", padx=10, pady=5)

        # Dernier code recu (vert = reconnu, rouge = inconnu)
        self.etiquette_dernier_code = tk.Label(self.fenetre, text="Code : ", fg="black")
        self.etiquette_dernier_code.pack(anchor="w", padx=10, pady=5)

        # Zone de simulation (en attendant l'USB) : champ + bouton cote a cote.
        # Placee AVANT le tableau pour qu'elle reste visible quand il grandit.
        cadre_simulation = ttk.Frame(self.fenetre)
        cadre_simulation.pack(fill="x", padx=10, pady=5)

        ttk.Label(cadre_simulation, text="Code-barres :").pack(side="left")
        self.champ_code = ttk.Entry(cadre_simulation, width=20)
        self.champ_code.pack(side="left", padx=5)
        # Touche Entree = scanner. bind() envoie un argument "event" qu'on ignore.
        self.champ_code.bind("<Return>", lambda event: self.simuler_scan())
        self.champ_code.focus()

        ttk.Button(cadre_simulation, text="Simuler un scan",
                   command=self.simuler_scan).pack(side="left")

        # Tableau des achats (TS4.2 : nom, prix unitaire, quantite, sous-total)
        colonnes = ("produit", "prix", "quantite", "sous_total")
        self.tableau = ttk.Treeview(self.fenetre, columns=colonnes, show="headings")
        self.tableau.heading("produit", text="Produit :")
        self.tableau.heading("prix", text="Prix unitaire :")
        self.tableau.heading("quantite", text="Quantite :")
        self.tableau.heading("sous_total", text="Sous-total :")
        self.tableau.column("produit", width=250)
        self.tableau.column("prix", width=120, anchor="center")
        self.tableau.column("quantite", width=80, anchor="center")
        self.tableau.column("sous_total", width=120, anchor="center")
        self.tableau.pack(fill="both", expand=True, padx=10, pady=5)

        # Bas de fenetre : bouton a gauche, total a droite
        cadre_bas = ttk.Frame(self.fenetre)
        cadre_bas.pack(fill="x", padx=10, pady=10)

        ttk.Button(cadre_bas, text="Nouvelle transaction",
                   command=self.nouvelle_transaction).pack(side="left")

        self.etiquette_total = tk.Label(cadre_bas, text="TOTAL : " + formater_prix(0),
                                        font=("Arial", 20, "bold"))
        self.etiquette_total.pack(side="right")

        cadre_bouton_payer = ttk.LabelFrame(self.fenetre)
        cadre_bouton_payer.pack(fill="x", padx=10, pady=5)
        self.etiquette_payer = tk.Label(cadre_bouton_payer, text="PAYER : " + formater_prix(0),
                                        font=("Arial", 20, "bold"))
        self.etiquette_payer.pack(side="right")

    # actions
    def simuler_scan(self):
        """Fait ce que fera le PIC : chercher le code tape dans le catalogue,
        puis appeler produit_recu() ou produit_inconnu()."""
        code = self.champ_code.get().strip()
        if not code:
            return

        # Seul endroit ou l'interface utilise chercher_produit()
        # (option A : en vrai, c'est le PIC qui fait la recherche).
        produit = chercher_produit(code)
        if produit is None:
            self.produit_inconnu(code)
        else:
            nom, prix = produit
            self.produit_recu(code, nom, prix)

        self.champ_code.delete(0, "end")

    def produit_recu(self, code, nom, prix):
        """Un produit valide arrive (du simulateur, plus tard de l'USB)."""
        # Doit rester rapide (TS4.1 / TS4.3 : affichage < 500 ms).
        self.panier.ajouter(code, nom, prix)
        self.etiquette_dernier_code.config(
            text=f"Code : {code} - {nom} (reconnu)", fg="green")
        self.rafraichir_tableau()

    def produit_inconnu(self, code):
        """Code absent du catalogue : on l'affiche en rouge, le panier ne change pas."""
        self.etiquette_dernier_code.config(
            text=f"Code : {code} - INCONNU", fg="red")

    def ajouter_article(self, code):
        """(TODO 6) Un article sans code-barres (fruit, pain) choisi dans le GUI."""
        # TODO (bonus) :
        #   - recuperer (nom, prix) dans ARTICLES_SANS_CODE
        #   - REUTILISER self.produit_recu(code, nom, prix) : pas de code duplique,
        #     et comme c'est vendu a l'unite, le panier gere deja les quantites
        pass

    def nouvelle_transaction(self):
        """Vide le panier et remet l'affichage a zero (TS1.9)."""
        self.panier.vider()
        self.rafraichir_tableau()
        self.etiquette_dernier_code.config(text="Code : ", fg="black")
        # Plus tard (etape 5) : prevenir aussi le PIC avec envoyer_annulation()
        # pour qu'il remette son GLCD a zero.

    # ---------------------------------------------------------- affichage
    def rafraichir_tableau(self):
        """Efface le tableau puis le reremplit a partir du panier + met a jour le total."""
        # Tout effacer puis tout reremplir : simple, et l'ecran est toujours
        # egal au panier (TS4.3 : la quantite s'incremente sur la meme ligne).
        self.tableau.delete(*self.tableau.get_children())
        for ligne in self.panier.liste_lignes():
            self.tableau.insert("", "end", values=(
                ligne.nom,
                formater_prix(ligne.prix_unitaire),
                ligne.quantite,
                formater_prix(ligne.sous_total()),
            ))
        self.etiquette_total.config(text="TOTAL : " + formater_prix(self.panier.total()))


if __name__ == "__main__":
    fenetre = tk.Tk()
    Caisse(fenetre)
    fenetre.mainloop()
