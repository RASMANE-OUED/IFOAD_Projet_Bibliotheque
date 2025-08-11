import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from classes.Bibliotheque import Bibliotheque
from classes.Livre import Livre
from classes.Utilisateur import Utilisateur


class BibliothequeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Bibliothèque UJKZ")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f4f6f8")

        Path("data").mkdir(exist_ok=True)
        self.biblio = Bibliotheque(nom="Bibliothèque Centrale", adresse="Ouagadougou")

        self.setup_style()
        self.setup_ui()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    # ======= Styles =======
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background="#f4f6f8", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#2b4f81")], foreground=[("selected", "white")])

        style.configure("TLabel", background="#f4f6f8", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), background="#f4f6f8", foreground="#2b4f81", padding=5)

        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6, relief="flat",
                        background="#2b4f81", foreground="white")
        style.map("TButton", background=[("active", "#1f3a5f")], foreground=[('disabled', '#a3a3a3')])

        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#2b4f81")], foreground=[("selected", "white")])
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#e1e5eb", foreground="#2b4f81")

    # ======= Interface =======
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_livre_tab()
        self.create_utilisateur_tab()
        self.create_emprunt_tab()
        self.create_stats_tab()

        # Barre de statut + boutons
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(self.status_bar, text="Prêt", relief=tk.SUNKEN, anchor="w", background="#d0d4db")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bouton pour quitter l'application
        quit_btn = ttk.Button(self.status_bar, text="Quitter", command=self.root.quit, style="TButton")
        quit_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=2)

        # Bouton pour changer le mot de passe
        change_pwd_btn = ttk.Button(self.status_bar, text="Changer mot de passe", command=self.ouvrir_fenetre_changer_mdp,
                                    style="TButton")
        change_pwd_btn.pack(side=tk.RIGHT, padx=10, pady=2)

    # ======= Gestion onglets =======
    def on_tab_changed(self, event):
        selected_tab = event.widget.tab('current', 'text')
        if selected_tab == "Statistiques":
            self.update_stats()
        elif selected_tab == "Emprunts":
            self.refresh_emprunt_combos()
            self.refresh_emprunts()

    # --- Onglet Livres ---
    def create_livre_tab(self):
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text="Livres")

        form_frame = ttk.Frame(tab, style='TFrame')
        form_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Label(form_frame, text="ISBN:").grid(row=0, column=0, sticky="w")
        self.isbn_entry = ttk.Entry(form_frame)
        self.isbn_entry.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Titre:").grid(row=0, column=2, sticky="w")
        self.titre_entry = ttk.Entry(form_frame)
        self.titre_entry.grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="Auteur:").grid(row=1, column=0, sticky="w")
        self.auteur_entry = ttk.Entry(form_frame)
        self.auteur_entry.grid(row=1, column=1, padx=5)

        ttk.Label(form_frame, text="Catégorie:").grid(row=1, column=2, sticky="w")
        self.categorie_entry = ttk.Entry(form_frame)
        self.categorie_entry.grid(row=1, column=3, padx=5)

        add_btn = ttk.Button(form_frame, text="Ajouter Livre", command=self.ajouter_livre, style='TButton')
        add_btn.grid(row=0, column=4, rowspan=2, padx=10)

        self.livre_tree = ttk.Treeview(tab, columns=("isbn", "titre", "auteur", "categorie"), show="headings")
        for col in ("isbn", "titre", "auteur", "categorie"):
            self.livre_tree.heading(col, text=col.capitalize())
            self.livre_tree.column(col, width=250)
        self.livre_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_livres()

    def ajouter_livre(self):
        isbn = self.isbn_entry.get().strip()
        titre = self.titre_entry.get().strip()
        auteur = self.auteur_entry.get().strip()
        categorie = self.categorie_entry.get().strip()
        if not isbn or not titre or not auteur:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        livre = Livre(isbn=isbn, titre=titre, auteur=auteur, editeur="Inconnu",
                      annee_publication=2025, categorie=categorie, nombre_pages=100)
        if self.biblio.ajouter_livre(livre):
            messagebox.showinfo("Succès", "Livre ajouté avec succès.")
            self.refresh_livres()
            self.clear_livre_form()
        else:
            messagebox.showerror("Erreur", "Ce livre existe déjà.")

    def refresh_livres(self):
        for row in self.livre_tree.get_children():
            self.livre_tree.delete(row)
        for i, livre in enumerate(self.biblio.catalogue.livres.values()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.livre_tree.insert("", tk.END,
                                   values=(livre.isbn, livre.titre, livre.auteur, livre.categorie),
                                   tags=(tag,))
        self.livre_tree.tag_configure('evenrow', background='white')
        self.livre_tree.tag_configure('oddrow', background='#f0f4ff')

    def clear_livre_form(self):
        self.isbn_entry.delete(0, tk.END)
        self.titre_entry.delete(0, tk.END)
        self.auteur_entry.delete(0, tk.END)
        self.categorie_entry.delete(0, tk.END)

    # --- Onglet Utilisateurs ---
    def create_utilisateur_tab(self):
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text="Utilisateurs")

        form_frame = ttk.Frame(tab, style='TFrame')
        form_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Label(form_frame, text="N° Carte:").grid(row=0, column=0, sticky="w")
        self.num_carte_entry = ttk.Entry(form_frame)
        self.num_carte_entry.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Nom:").grid(row=0, column=2, sticky="w")
        self.nom_entry = ttk.Entry(form_frame)
        self.nom_entry.grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="Prénom:").grid(row=1, column=0, sticky="w")
        self.prenom_entry = ttk.Entry(form_frame)
        self.prenom_entry.grid(row=1, column=1, padx=5)

        ttk.Label(form_frame, text="Email:").grid(row=1, column=2, sticky="w")
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=1, column=3, padx=5)

        add_btn = ttk.Button(form_frame, text="Ajouter Utilisateur", command=self.ajouter_utilisateur, style='TButton')
        add_btn.grid(row=0, column=4, rowspan=2, padx=10)

        self.user_tree = ttk.Treeview(tab, columns=("numero", "nom", "prenom", "email"), show="headings")
        for col in ("numero", "nom", "prenom", "email"):
            self.user_tree.heading(col, text=col.capitalize())
            self.user_tree.column(col, width=250)
        self.user_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_utilisateurs()

    def ajouter_utilisateur(self):
        numero = self.num_carte_entry.get().strip()
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        email = self.email_entry.get().strip()
        if not numero or not nom or not prenom or not email:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        user = Utilisateur(numero_carte=numero, nom=nom, prenom=prenom, email=email)
        if self.biblio.inscrire_utilisateur(user):
            messagebox.showinfo("Succès", "Utilisateur ajouté.")
            self.refresh_utilisateurs()
            self.clear_user_form()
        else:
            messagebox.showerror("Erreur", "Cet utilisateur existe déjà.")

    def refresh_utilisateurs(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        for i, user in enumerate(self.biblio.utilisateurs.values()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.user_tree.insert("", tk.END,
                                  values=(user.numero_carte, user.nom, user.prenom, user.email),
                                  tags=(tag,))
        self.user_tree.tag_configure('evenrow', background='white')
        self.user_tree.tag_configure('oddrow', background='#f0f4ff')

    def clear_user_form(self):
        self.num_carte_entry.delete(0, tk.END)
        self.nom_entry.delete(0, tk.END)
        self.prenom_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

    # --- Onglet Emprunts ---
# --- Onglet Emprunts (version recherche intelligente) ---
    def create_emprunt_tab(self):
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text="Emprunts")

        form = ttk.Frame(tab, style='TFrame')
        form.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    # --- Utilisateur ---
        ttk.Label(form, text="Utilisateur :").grid(row=0, column=0, sticky="w")
        self.user_search_var = tk.StringVar()
        self.user_entry = ttk.Entry(form, textvariable=self.user_search_var, width=30)
        self.user_entry.grid(row=0, column=1, padx=5)
        self.user_listbox = tk.Listbox(form, height=4, width=30, exportselection=False)
        self.user_listbox.grid(row=1, column=1, padx=5, pady=2)

    # --- Livre ---
        ttk.Label(form, text="Livre :").grid(row=0, column=2, sticky="w")
        self.book_search_var = tk.StringVar()
        self.book_entry = ttk.Entry(form, textvariable=self.book_search_var, width=30)
        self.book_entry.grid(row=0, column=3, padx=5)
        self.book_listbox = tk.Listbox(form, height=4, width=30, exportselection=False)
        self.book_listbox.grid(row=1, column=3, padx=5, pady=2)

    # Boutons
        ttk.Button(form, text="Faire Emprunt",
               command=self.ajouter_emprunt_smart, style='TButton').grid(row=0, column=4, padx=10)
        ttk.Button(tab, text="Retourner le livre sélectionné",
               command=self.retourner_emprunt, style='TButton').pack(pady=5)

    # --- Treeview ---
        cols = ("id", "utilisateur", "livre", "date_emprunt",
            "date_retour_prevue", "date_retour_effective", "statut")
        self.emprunts_tree = ttk.Treeview(tab, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.emprunts_tree.heading(c, text=c.replace("_", " ").capitalize())
            self.emprunts_tree.column(c, width=120, anchor=tk.W)
        self.emprunts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Bind Enter et rafraîchissement
        self.user_entry.bind('<Return>', lambda e: self.user_listbox.focus_set())
        self.book_entry.bind('<Return>', lambda e: self.book_listbox.focus_set())
        self.user_listbox.bind('<Return>', lambda e: self.ajouter_emprunt_smart())
        self.book_listbox.bind('<Return>', lambda e: self.ajouter_emprunt_smart())

    # initialisation
        self.user_search_var.trace_add("write", self._filter_users)
        self.book_search_var.trace_add("write", self._filter_books)
        self.refresh_emprunts()

# Méthode pour rafraîchir la liste des emprunts
    def _refresh_emprunts(self):
       # Vider le treeview
        for item in self.emprunts_tree.get_children():
            self.emprunts_tree.delete(item)
    
    # Remplir avec les emprunts actuels
        for emp in self.biblio.emprunts.values():
            user = self.biblio.utilisateurs.get(emp.numero_carte, None)
            livre = self.biblio.catalogue.livres.get(emp.isbn, None)
        
            user_str = f"{user.prenom} {user.nom}" if user else "Inconnu"
            livre_str = livre.titre if livre else "Inconnu"
        
            statut = "En cours" if emp.date_retour_effective is None else "Retourné"
        
            self.emprunts_tree.insert("", tk.END, values=(
            emp.id_emprunt,
            user_str,
            livre_str,
            emp.date_emprunt.strftime("%Y-%m-%d") if emp.date_emprunt else "",
            emp.date_retour_prevue.strftime("%Y-%m-%d") if emp.date_retour_prevue else "",
            emp.date_retour_effective.strftime("%Y-%m-%d") if emp.date_retour_effective else "",
            statut
        ))

# Méthode pour mettre à jour l'entry quand on sélectionne dans la listbox
    def _update_entry_from_listbox(self, listbox, entry):
        selection = listbox.curselection()
        if selection:
            entry.delete(0, tk.END)
            entry.insert(0, listbox.get(selection[0]))

# ---------- Méthodes de filtrage ----------
    def _filter_users(self, *args):
        text = self.user_search_var.get().lower()
        self.user_listbox.delete(0, tk.END)
        for uc in self.biblio.utilisateurs.values():
            needle = f"{uc.nom} {uc.prenom} {uc.numero_carte}".lower()
            if text in needle:
                self.user_listbox.insert(tk.END, f"{uc.numero_carte} - {uc.prenom} {uc.nom}")

    def _filter_books(self, *args):
        text = self.book_search_var.get().lower()
        self.book_listbox.delete(0, tk.END)
        for livre in self.biblio.catalogue.livres.values():
            if not livre.est_disponible():
                continue
            needle = f"{livre.titre} {livre.auteur} {livre.isbn}".lower()
            if text in needle:
                self.book_listbox.insert(tk.END, f"{livre.isbn} - {livre.titre}")

# ---------- Ajout d'emprunt avec sélection depuis les listes ----------
    def ajouter_emprunt_smart(self):
        user_sel = self.user_listbox.curselection()
        book_sel = self.book_listbox.curselection()
        if not user_sel or not book_sel:
            messagebox.showwarning("Sélection", "Veuillez choisir un utilisateur et un livre dans les listes.")
            return

        numero_carte = self.user_listbox.get(user_sel[0]).split(" - ")[0]
        isbn = self.book_listbox.get(book_sel[0]).split(" - ")[0]

        id_emprunt = self.biblio.emprunter_livre(numero_carte, isbn)
        if id_emprunt is None:
            messagebox.showerror("Erreur", "Emprunt impossible.")
        else:
            messagebox.showinfo("Succès", f"Emprunt n°{id_emprunt} enregistré.")
            self._refresh_emprunts()
            self._filter_users()   # rafraîchit aussi les listes
            self._filter_books()
        
    def retourner_emprunt(self):
        selected = self.emprunts_tree.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un emprunt à retourner.")
            return
        values = self.emprunts_tree.item(selected[0], "values")
        id_emprunt = int(values[0])
        if self.biblio.retourner_livre(id_emprunt):
            messagebox.showinfo("Succès", "Retour effectué.")
            self._refresh_emprunts()
            self._filter_users()
            self._filter_books()
        else:
            messagebox.showerror("Erreur", "Retour impossible.")

    # --- Onglet Statistiques ---
    def create_stats_tab(self):
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text="Statistiques")
        main_frame = ttk.Frame(tab, style='TFrame')
        main_frame.pack(expand=True, padx=20, pady=20)
        ttk.Label(main_frame, text="Statistiques de la Bibliothèque", font=("Helvetica", 16, "bold"),
                  foreground="#2b4f81", background="#f4f6f8").pack(pady=(0, 20))
        stats_frame = ttk.Frame(main_frame, style='TFrame')
        stats_frame.pack(fill=tk.BOTH, expand=True)
        self.stats_labels = {}
        row_count = 0
        stats_data = [
            ("📚 Total de Livres", "total_livres"),
            ("👥 Total d'Utilisateurs", "total_utilisateurs"),
            ("📖 Total d'Emprunts", "total_emprunts"),
            ("✅ Livres Disponibles", "livres_disponibles"),
            ("⏳ Emprunts en Cours", "emprunts_en_cours"),
            ("🚫 Utilisateurs Bloqués", "utilisateurs_bloques"),
            ("💰 Amendes Totales", "amendes_totales")
        ]
        for emoji_label, key in stats_data:
            ttk.Label(stats_frame, text=f"• {emoji_label} :", font=("Helvetica", 11)).grid(row=row_count, column=0, sticky="w",
                                                                                            pady=5, padx=10)
            self.stats_labels[key] = ttk.Label(stats_frame, text="Chargement...", font=("Helvetica", 11, "bold"),
                                                foreground="#4a4a4a")
            self.stats_labels[key].grid(row=row_count, column=1, sticky="w", pady=5, padx=10)
            row_count += 1

    def update_stats(self):
        rapport = self.biblio.generer_rapport()
        emprunts_en_cours = len([e for e in self.biblio.emprunts.values() if e.statut])
        utilisateurs_bloques = len([u for u in self.biblio.utilisateurs.values() if u.statut == "BLOQUÉ"])
        total_amendes = 0.0
        for emprunt in self.biblio.emprunts_en_retard():
            total_amendes += self.biblio.calculer_amende(emprunt.id)
        if hasattr(self, 'stats_labels'):
            self.stats_labels["total_livres"].config(text=str(rapport['total_livres']))
            self.stats_labels["total_utilisateurs"].config(text=str(rapport['total_utilisateurs']))
            self.stats_labels["total_emprunts"].config(text=str(rapport['total_emprunts']))
            self.stats_labels["livres_disponibles"].config(text=str(rapport['livres_disponibles']))
            self.stats_labels["emprunts_en_cours"].config(text=str(emprunts_en_cours))
            self.stats_labels["utilisateurs_bloques"].config(text=str(utilisateurs_bloques))
            self.stats_labels["amendes_totales"].config(text=f"{total_amendes:.2f} FCFA")

    # --- Fenêtre de changement de mot de passe ---
    def ouvrir_fenetre_changer_mdp(self):
        fen = tk.Toplevel(self.root)
        fen.title("Changer le mot de passe")
        fen.geometry("350x250")
        fen.resizable(False, False)

        frame = ttk.Frame(fen, padding="15")
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Ancien mot de passe :").pack(anchor='w', pady=(0, 5))
        ancien_mdp_entry = ttk.Entry(frame, show="*")
        ancien_mdp_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Nouveau mot de passe :").pack(anchor='w', pady=(0, 5))
        nouveau_mdp_entry = ttk.Entry(frame, show="*")
        nouveau_mdp_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Confirmer nouveau mot de passe :").pack(anchor='w', pady=(0, 5))
        confirmer_mdp_entry = ttk.Entry(frame, show="*")
        confirmer_mdp_entry.pack(fill=tk.X, pady=(0, 10))

        def valider_changement():
            ancien = ancien_mdp_entry.get()
            nouveau = nouveau_mdp_entry.get()
            confirmer = confirmer_mdp_entry.get()
            username = "admin"  # Mettez le nom d'utilisateur actuel, "admin" par défaut

            if ancien != "1234":
                messagebox.showerror("Erreur", "Ancien mot de passe incorrect.")
                return
            
            if not nouveau:
                messagebox.showerror("Erreur", "Le nouveau mot de passe ne peut pas être vide.")
                return
            
            if nouveau != confirmer:
                messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
                return

            # Si tout est bon, vous pourriez ici mettre à jour le mot de passe
            # self.biblio.changer_mot_de_passe(username, nouveau)
            messagebox.showinfo("Succès", "Mot de passe modifié avec succès.")
            fen.destroy()

        ttk.Button(frame, text="Valider", command=valider_changement).pack(pady=10)


# --- Fenêtre de Connexion au démarrage ---
def show_login():
    login_root = tk.Tk()
    login_root.title("Connexion")
    login_root.geometry("350x220")
    login_root.resizable(False, False)

    username_var = tk.StringVar()
    password_var = tk.StringVar()

    def check_credentials():
        username = username_var.get()
        password = password_var.get()
        
        if username == "admin" and password == "1234":
            login_root.destroy()
            main_root = tk.Tk()
            BibliothequeApp(main_root)
            main_root.mainloop()
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")

    main_frame = ttk.Frame(login_root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Nom d'utilisateur:").pack(anchor='w', pady=(0, 5))
    ttk.Entry(main_frame, textvariable=username_var).pack(fill=tk.X, pady=(0, 10))

    ttk.Label(main_frame, text="Mot de passe:").pack(anchor='w', pady=(0, 5))
    ttk.Entry(main_frame, textvariable=password_var, show="*").pack(fill=tk.X, pady=(0, 10))

    ttk.Button(main_frame, text="Se connecter", command=check_credentials).pack(pady=10)

    login_root.mainloop()

if __name__ == "__main__":
    show_login()