"""
interface.py - Fenetre de la caisse PIC-MARKET (Tkinter).

Lancer :  py interface.py

Toutes les 50 ms, on lit les produits envoyes par le PIC, puis on redessine
le ticket (nom, prix unitaire, quantite, sous-total) et le total.
Les boutons Nouvelle transaction et Payer sont affiches mais n'ont pas
encore d'action.
"""
import tkinter as tk
from tkinter import ttk

from caisse import Caisse
from panier import formater_prix

PERIODE_LECTURE_USB = 50        # ms

FOND = "#eef1f5"
BANDEAU = "#1f2a44"
AFFICHEUR = "#111827"
CHIFFRES = "#4ade80"
BLANC = "#ffffff"
GRIS = "#9ca3af"
BLEU = "#2563eb"
VERT = "#16a34a"
ORANGE = "#ea580c"


class FenetreCaisse:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("PIC-MARKET")
        self.fenetre.geometry("1000x800")
        self.fenetre.configure(bg=FOND)

        self.caisse = Caisse()

        self.configurer_style()
        self.creer_elements()

        self.fenetre.protocol("WM_DELETE_WINDOW", self.quitter)   # clic sur la croix
        self.surveiller_usb()

    def configurer_style(self):
        """ttk ne prend pas font= / bg= directement : on passe par Style."""
        style = ttk.Style()
        style.theme_use("clam")         # theme qui accepte les couleurs
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"),
                        background=BANDEAU, foreground=BLANC)
        style.map("Treeview", background=[("selected", BLEU)])

    def creer_elements(self):
        # Bandeau du haut
        bandeau = tk.Frame(self.fenetre, bg=BANDEAU)
        bandeau.pack(fill="x")
        tk.Label(bandeau, text="PIC-MARKET", bg=BANDEAU, fg=BLANC,
                 font=("Arial", 22, "bold")).pack(side="left", padx=15, pady=10)

        # La barre du bas est placee AVANT le ticket : le ticket prend ensuite
        # toute la place restante entre le bandeau et la barre.
        self.creer_barre_bas()
        self.creer_ticket()

    def creer_ticket(self):
        """Tableau des produits sur toute la largeur."""
        cadre_tableau = tk.Frame(self.fenetre)
        cadre_tableau.pack(fill="both", expand=True, padx=10, pady=10)

        colonnes = ("produit", "prix", "quantite", "sous_total")
        self.tableau = ttk.Treeview(cadre_tableau, columns=colonnes, show="headings")
        self.tableau.heading("produit", text="Produit")
        self.tableau.heading("prix", text="Prix unitaire")
        self.tableau.heading("quantite", text="Quantite")
        self.tableau.heading("sous_total", text="Sous-total")
        self.tableau.column("produit", width=350)
        self.tableau.column("prix", width=150, anchor="center")
        self.tableau.column("quantite", width=100, anchor="center")
        self.tableau.column("sous_total", width=150, anchor="center")
        self.tableau.tag_configure("paire", background="#f3f4f6")   # lignes zebrees

        defilement = ttk.Scrollbar(cadre_tableau, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=defilement.set)
        defilement.pack(side="right", fill="y")
        self.tableau.pack(side="left", fill="both", expand=True)

    def creer_barre_bas(self):
        """Total a gauche, boutons a droite (sans action, pas de command= pour l'instant)."""
        barre = tk.Frame(self.fenetre, bg=AFFICHEUR)
        barre.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

        tk.Label(barre, text="TOTAL", bg=AFFICHEUR, fg=BLANC,
                 font=("Arial", 24, "bold")).pack(side="left", padx=15, pady=10)
        self.etiquette_total = tk.Label(barre, text=formater_prix(0), bg=AFFICHEUR,
                                        fg=CHIFFRES, font=("Consolas", 32, "bold"))
        self.etiquette_total.pack(side="left", padx=15)

        # side="right" : le premier bouton place est le plus a droite
        tk.Button(barre, text="PAYER", font=("Arial", 18, "bold"), bg=VERT, fg=BLANC,
                  activebackground=VERT, relief="flat", width=10
                  ).pack(side="right", fill="y", padx=10, pady=10)
        tk.Button(barre, text="Nouvelle\ntransaction", font=("Arial", 12, "bold"), bg=ORANGE,
                  fg=BLANC, activebackground=ORANGE, relief="flat", width=12
                  ).pack(side="right", fill="y", pady=10)

    def surveiller_usb(self):
        """Lit le PIC, met a jour le ticket si besoin, puis se relance dans 50 ms."""
        codes = self.caisse.lire_usb()
        if codes:
            self.rafraichir_ticket(dernier_code=codes[-1])
        # after() rappelle la methode sans bloquer la fenetre (contrairement a sleep)
        self.fenetre.after(PERIODE_LECTURE_USB, self.surveiller_usb)

    def rafraichir_ticket(self, dernier_code):
        """Efface le ticket, le reremplit a partir du panier et met a jour le total."""
        self.tableau.delete(*self.tableau.get_children())
        for i, ligne in enumerate(self.caisse.panier.liste_lignes()):
            tags = ("paire",) if i % 2 == 0 else ()
            # iid = code : permet de retrouver la ligne d'un produit
            self.tableau.insert("", "end", iid=ligne.code, tags=tags, values=(
                ligne.nom,
                formater_prix(ligne.prix_unitaire),
                ligne.quantite,
                formater_prix(ligne.sous_total()),
            ))
        self.tableau.selection_set(dernier_code)   # surligne le dernier produit recu
        self.tableau.see(dernier_code)             # et fait defiler jusqu'a lui
        self.etiquette_total.config(text=formater_prix(self.caisse.panier.total()))

    def quitter(self):
        self.caisse.fermer()
        self.fenetre.destroy()


if __name__ == "__main__":
    fenetre = tk.Tk()
    FenetreCaisse(fenetre)
    fenetre.mainloop()
