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

        # Barre de statut + bouton changement mot de passe
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(self.status_bar, text="Prêt", relief=tk.SUNKEN, anchor="w", background="#d0d4db")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

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
    def create_emprunt_tab(self):
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text="Emprunts")

        form_frame = ttk.Frame(tab, style='TFrame')
        form_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Label(form_frame, text="Utilisateur (N° carte) :").grid(row=0, column=0, sticky="w")
        self.emprunt_user_var = tk.StringVar()
        self.emprunt_user_combo = ttk.Combobox(form_frame, textvariable=self.emprunt_user_var, state="readonly")
        self.emprunt_user_combo.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Livre (ISBN) :").grid(row=0, column=2, sticky="w")
        self.emprunt_livre_var = tk.StringVar()
        self.emprunt_livre_combo = ttk.Combobox(form_frame, textvariable=self.emprunt_livre_var, state="readonly")
        self.emprunt_livre_combo.grid(row=0, column=3, padx=5)

        emprunter_btn = ttk.Button(form_frame, text="Faire Emprunt", command=self.ajouter_emprunt, style='TButton')
        emprunter_btn.grid(row=0, column=4, padx=10)

        colonnes = ("id", "utilisateur", "livre", "date_emprunt", "date_retour_prevue", "date_retour_effective", "statut")
        self.emprunts_tree = ttk.Treeview(tab, columns=colonnes, show="headings", selectmode="browse")
        for col in colonnes:
            self.emprunts_tree.heading(col, text=col.replace("_", " ").capitalize())
            self.emprunts_tree.column(col, width=130, anchor=tk.W)
        self.emprunts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        retourner_btn = ttk.Button(tab, text="Retourner le livre sélectionné", command=self.retourner_emprunt, style='TButton')
        retourner_btn.pack(pady=5)

        self.refresh_emprunt_combos()
        self.refresh_emprunts()

    def refresh_emprunt_combos(self):
        self.emprunt_user_combo['values'] = list(self.biblio.utilisateurs.keys())
        livres_disponibles = [livre.isbn for livre in self.biblio.catalogue.livres.values() if livre.est_disponible()]
        self.emprunt_livre_combo['values'] = livres_disponibles
        if livres_disponibles:
            self.emprunt_livre_var.set(livres_disponibles[0])
        if self.biblio.utilisateurs:
            self.emprunt_user_var.set(next(iter(self.biblio.utilisateurs.keys())))

    def refresh_emprunts(self):
        for row in self.emprunts_tree.get_children():
            self.emprunts_tree.delete(row)
        for i, emprunt in enumerate(self.biblio.emprunts.values()):
            utilisateur = self.biblio.utilisateurs.get(emprunt.id_utilisateur)
            livre = self.biblio.catalogue.livres.get(emprunt.id_livre)
            date_emprunt = emprunt.date_emprunt.strftime("%Y-%m-%d") if emprunt.date_emprunt else "N/A"
            date_retour_prevue = emprunt.date_retour_prevue.strftime("%Y-%m-%d") if emprunt.date_retour_prevue else "N/A"
            date_retour_effective = emprunt.date_retour_effective.strftime("%Y-%m-%d") if emprunt.date_retour_effective else "N/A"
            statut = "En cours" if emprunt.statut else "Terminé"
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.emprunts_tree.insert("", tk.END, values=(
                emprunt.id,
                utilisateur.numero_carte if utilisateur else "Inconnu",
                livre.isbn if livre else "Inconnu",
                date_emprunt,
                date_retour_prevue,
                date_retour_effective,
                statut), tags=(tag,))
        self.emprunts_tree.tag_configure('evenrow', background='white')
        self.emprunts_tree.tag_configure('oddrow', background='#f0f4ff')

    def ajouter_emprunt(self):
        numero_carte = self.emprunt_user_var.get()
        isbn = self.emprunt_livre_var.get()
        if not numero_carte or not isbn:
            messagebox.showwarning("Validation", "Veuillez sélectionner un utilisateur et un livre.")
            return
        id_emprunt = self.biblio.emprunter_livre(numero_carte, isbn)
        if id_emprunt is None:
            messagebox.showerror("Erreur", "Impossible d'effectuer l'emprunt. Vérifiez la disponibilité et le statut de l'utilisateur.")
        else:
            messagebox.showinfo("Succès", f"Emprunt réalisé avec ID {id_emprunt}.")
            self.refresh_emprunts()
            self.refresh_emprunt_combos()
            self.update_stats()

    def retourner_emprunt(self):
        selected = self.emprunts_tree.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un emprunt à retourner.")
            return
        values = self.emprunts_tree.item(selected[0], "values")
        id_emprunt = int(values[0])
        if self.biblio.retourner_livre(id_emprunt):
            messagebox.showinfo("Succès", "Retour effectué.")
            self.refresh_emprunts()
            self.refresh_emprunt_combos()
            self.update_stats()
        else:
            messagebox.showerror("Erreur", "Retour impossible, emprunt déjà terminé ou invalide.")

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
            self.stats_labels["amendes_totales"].config(text=f"{total_amendes:.2f} €")

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

            # La vérification des identifiants se fait ici
            # Note: J'ai ajouté une méthode `verifier_identifiants` dans votre classe Bibliotheque
            # pour que cette vérification soit possible. Assurez-vous que cette méthode existe
            # dans la classe Bibliotheque de votre projet.
            # Example:
            # def verifier_identifiants(self, username, password):
            #     return username == "admin" and password == "1234"

            if ancien != "1234": # Remplacez "1234" par la logique de vérification
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
        
        # Identifiants en dur, à remplacer par une logique de vérification
        # provenant de votre classe Bibliotheque si vous l'avez implémentée.
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

# Point d'entrée de l'application
if __name__ == "__main__":
    show_login()