"""
interface.py - Fenetre de la caisse PIC-MARKET (Tkinter).

Lancer :  py interface.py

Toutes les 50 ms, on lit les trames du PIC (ou on retente la connexion),
puis on met a jour le ticket, le total, le dernier code et les messages.
Le bouton Payer est affiche mais n'a pas encore d'action.
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
GRIS = "#6b7280"
BLEU = "#2563eb"
VERT = "#16a34a"
ROUGE = "#dc2626"
ROUGE_CLAIR = "#f87171"         # lisible sur le bandeau sombre
ORANGE = "#ea580c"


class FenetreCaisse:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("PIC-MARKET")
        self.fenetre.geometry("1000x800")
        self.fenetre.configure(bg=FOND)

        self.caisse = Caisse()
        self.etait_connecte = False     # pour detecter connexion / deconnexion

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

    # ================================================================ creation
    def creer_elements(self):
        self.creer_bandeau()
        self.creer_dernier_code()
        self.creer_simulation()
        # Barre du bas et messages places AVANT le ticket : le ticket prend
        # ensuite toute la place restante.
        self.creer_barre_bas()
        self.creer_messages()
        self.creer_ticket()

    def creer_bandeau(self):
        bandeau = tk.Frame(self.fenetre, bg=BANDEAU)
        bandeau.pack(fill="x")
        tk.Label(bandeau, text="PIC-MARKET", bg=BANDEAU, fg=BLANC,
                 font=("Arial", 22, "bold")).pack(side="left", padx=15, pady=10)
        # "●" = pastille de couleur
        self.etiquette_usb = tk.Label(bandeau, text="● USB : Déconnecté", bg=BANDEAU,
                                      fg=ROUGE_CLAIR, font=("Arial", 13, "bold"))
        self.etiquette_usb.pack(side="right", padx=15)

    def creer_dernier_code(self):
        self.etiquette_dernier_code = tk.Label(self.fenetre, bg=FOND, font=("Arial", 14, "bold"))
        self.etiquette_dernier_code.pack(anchor="w", padx=10, pady=(10, 0))
        self.afficher_dernier_code("-", "", "black")

    def creer_simulation(self):
        cadre = tk.LabelFrame(self.fenetre, text=" Mode simulation (sans PIC) ", bg=FOND,
                              font=("Arial", 10, "bold"), padx=5, pady=5)
        cadre.pack(fill="x", padx=10, pady=5)

        self.champ_code = tk.Entry(cadre, font=("Consolas", 13), width=25)
        self.champ_code.pack(side="left", padx=(0, 5))
        # Touche Entree = simuler. bind() envoie un argument "event" qu'on ignore.
        self.champ_code.bind("<Return>", lambda event: self.simuler_scan())
        tk.Button(cadre, text="Simuler un scan", bg=BLEU, fg=BLANC, relief="flat",
                  font=("Arial", 11), command=self.simuler_scan).pack(side="left")

    def creer_ticket(self):
        cadre_tableau = tk.Frame(self.fenetre)
        cadre_tableau.pack(fill="both", expand=True, padx=10, pady=5)

        colonnes = ("produit", "prix", "quantite", "sous_total")
        self.tableau = ttk.Treeview(cadre_tableau, columns=colonnes, show="headings")
        self.tableau.heading("produit", text="Produit")
        self.tableau.heading("prix", text="Prix unitaire")
        self.tableau.heading("quantite", text="Quantité")
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

    def creer_messages(self):
        """Zone de messages (erreurs USB, trame invalide...), juste au-dessus de la barre."""
        self.etiquette_message = tk.Label(self.fenetre, text="", bg=BLANC, fg=GRIS,
                                          font=("Arial", 11), anchor="w", relief="solid", bd=1)
        self.etiquette_message.pack(side="bottom", fill="x", padx=10, pady=(0, 5), ipady=4)

    def creer_barre_bas(self):
        """Total a gauche, boutons a droite."""
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
                  fg=BLANC, activebackground=ORANGE, relief="flat", width=12,
                  command=self.nouvelle_transaction).pack(side="right", fill="y", pady=10)

    # ================================================================ actions
    def simuler_scan(self):
        resultat = self.caisse.simuler_scan(self.champ_code.get())
        self.champ_code.delete(0, "end")
        if resultat is not None:
            self.afficher_resultat(resultat)

    def surveiller_usb(self):
        """Lit les trames du PIC, met a jour le statut USB, puis se relance dans 50 ms."""
        for resultat in self.caisse.lire_usb():
            self.afficher_resultat(resultat)

        connecte = self.caisse.usb_connecte()
        if connecte != self.etait_connecte:          # l'etat vient de changer
            if connecte:
                self.etiquette_usb.config(text="● USB : Connecté", fg=CHIFFRES)
                self.afficher_message("USB connecté.", VERT)
            else:
                self.etiquette_usb.config(text="● USB : Déconnecté", fg=ROUGE_CLAIR)
                self.afficher_message("USB déconnecté : reconnexion automatique en cours...",
                                      ROUGE)
            self.etait_connecte = connecte

        # after() rappelle la methode sans bloquer la fenetre (contrairement a sleep)
        self.fenetre.after(PERIODE_LECTURE_USB, self.surveiller_usb)

    def nouvelle_transaction(self):
        self.caisse.nouvelle_transaction()
        self.rafraichir_ticket()
        self.afficher_dernier_code("-", "", "black")
        self.afficher_message("Nouvelle transaction.", GRIS)

    def quitter(self):
        self.caisse.fermer()
        self.fenetre.destroy()

    # ================================================================ affichage
    def afficher_resultat(self, resultat):
        """Affiche un resultat renvoye par la caisse (voir caisse.py)."""
        if resultat[0] == "reconnu":
            _, code, nom, prix = resultat
            self.afficher_dernier_code(code, f"Produit reconnu : {nom}", VERT)
            self.rafraichir_ticket(dernier_code=code)
        elif resultat[0] == "inconnu":
            self.afficher_dernier_code(resultat[1], "Code inconnu", ROUGE)
        else:
            self.afficher_message("Trame USB invalide ignorée.", ROUGE)

    def afficher_dernier_code(self, code, statut, couleur):
        texte = f"Dernier code : {code}" + (f"   —   {statut}" if statut else "")
        self.etiquette_dernier_code.config(text=texte, fg=couleur)

    def afficher_message(self, texte, couleur):
        self.etiquette_message.config(text="  " + texte, fg=couleur)

    def rafraichir_ticket(self, dernier_code=None):
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
        if dernier_code is not None:
            self.tableau.selection_set(dernier_code)   # surligne le dernier produit recu
            self.tableau.see(dernier_code)             # et fait defiler jusqu'a lui
        self.etiquette_total.config(text=formater_prix(self.caisse.panier.total()))


if __name__ == "__main__":
    fenetre = tk.Tk()
    FenetreCaisse(fenetre)
    fenetre.mainloop()
