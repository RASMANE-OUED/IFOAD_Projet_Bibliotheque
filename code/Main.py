import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
from classes.Bibliotheque import Bibliotheque
from classes.Livre import Livre
from classes.Utilisateur import Utilisateur
from classes.Emprunt import Emprunt


class BibliothequeApp:

    def __init__(self, root, biblio):
        self.root = root
        self.root.title("Gestion de Bibliothèque UJKZ")
        self.root.state('zoomed')
        self.root.configure(bg="#f4f6f8")

        self.biblio = biblio
        self.biblio.charger_donnees()  # Chargement des données à l'initialisation

        self.setup_style()
        self.setup_ui()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)


    # ===== Styles =====
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background="#f4f6f8", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#2b4f81")], foreground=[("selected", "white")])

        style.configure("TLabel", background="white", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), background="#f4f6f8", foreground="#2b4f81", padding=5)

        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6, relief="flat",
                        background="#2b4f81", foreground="white")
        style.map("TButton", background=[("active", "#1f3a5f")], foreground=[('disabled', '#a3a3a3')])

        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#2b4f81")], foreground=[("selected", "white")])
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#e1e5eb", foreground="#2b4f81")

    # ===== Interface =====
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

        # Bouton Quitter avec fermeture propre via destroy()
        quit_btn = ttk.Button(self.status_bar, text="Quitter", command=self.on_quit, style="TButton")
        quit_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=2)

        change_pwd_btn = ttk.Button(self.status_bar, text="Changer mot de passe", command=self.ouvrir_fenetre_changer_mdp, style="TButton")
        change_pwd_btn.pack(side=tk.RIGHT, padx=10, pady=2)

    def on_quit(self):
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.biblio.sauvegarder_donnees()  # Sauvegarde avant fermeture
            self.root.destroy()  # Ferme proprement l'application

    # ===== Gestion onglets =====
    def on_tab_changed(self, event):
        selected_tab = event.widget.tab('current', 'text')
        if selected_tab == "Statistiques & Historique":
            self.update_stats()
        elif selected_tab == "Emprunts":
            self._filter_users()
            self._filter_books()
            self.refresh_emprunts()
        elif selected_tab == "Livres":
            self.refresh_livres()
        elif selected_tab == "Utilisateurs":
            self.refresh_utilisateurs()

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

        # Boutons Ajouter, Modifier, Supprimer
        btn_frame = ttk.Frame(form_frame, style='TFrame')
        btn_frame.grid(row=0, column=4, rowspan=2, padx=10)
        ttk.Button(btn_frame, text="Ajouter Livre", command=self.ajouter_livre, style='TButton').pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="Modifier Livre", command=self.modifier_livre, style='TButton').pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="Supprimer Livre", command=self.supprimer_livre, style='TButton').pack(pady=2, fill=tk.X)

        self.livre_tree = ttk.Treeview(tab, columns=("isbn", "titre", "auteur", "categorie"), show="headings")
        for col in ("isbn", "titre", "auteur", "categorie"):
            self.livre_tree.heading(col, text=col.capitalize())
            self.livre_tree.column(col, width=250)
        self.livre_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.livre_tree.bind("<<TreeviewSelect>>", self.charger_livre_selectionne)
        self.refresh_livres()

    def charger_livre_selectionne(self, event):
        selected_item = self.livre_tree.selection()
        if not selected_item:
            return
        item_values = self.livre_tree.item(selected_item, "values")
        self.clear_livre_form()
        self.isbn_entry.insert(0, item_values[0])
        self.titre_entry.insert(0, item_values[1])
        self.auteur_entry.insert(0, item_values[2])
        self.categorie_entry.insert(0, item_values[3])

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
            self.biblio.sauvegarder_donnees()
            messagebox.showinfo("Succès", "Livre ajouté avec succès.")
            self.refresh_livres()
            self.clear_livre_form()
        else:
            messagebox.showerror("Erreur", "Ce livre existe déjà.")

    def modifier_livre(self):
        selected_item = self.livre_tree.selection()
        if not selected_item:
            messagebox.showwarning("Modification", "Veuillez sélectionner un livre à modifier.")
            return
        old_isbn = self.livre_tree.item(selected_item, "values")[0]
        new_isbn = self.isbn_entry.get().strip()
        titre = self.titre_entry.get().strip()
        auteur = self.auteur_entry.get().strip()
        categorie = self.categorie_entry.get().strip()
        if not new_isbn or not titre or not auteur:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        livre_modifie = Livre(isbn=new_isbn, titre=titre, auteur=auteur, editeur="Inconnu",
                              annee_publication=2025, categorie=categorie, nombre_pages=100)
        if self.biblio.modifier_livre(old_isbn, livre_modifie):
            self.biblio.sauvegarder_donnees()
            messagebox.showinfo("Succès", "Livre modifié avec succès.")
            self.refresh_livres()
            self.clear_livre_form()
        else:
            messagebox.showerror("Erreur", "La modification a échoué. Vérifiez que l'ISBN n'existe pas déjà.")

    def supprimer_livre(self):
        selected_item = self.livre_tree.selection()
        if not selected_item:
            messagebox.showwarning("Suppression", "Veuillez sélectionner un livre à supprimer.")
            return
        isbn = self.livre_tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Confirmer la suppression", f"Voulez-vous vraiment supprimer le livre avec l'ISBN {isbn} ?"):
            if self.biblio.supprimer_livre(isbn):
                self.biblio.sauvegarder_donnees()
                messagebox.showinfo("Succès", "Livre supprimé avec succès.")
                self.refresh_livres()
                self.clear_livre_form()
            else:
                messagebox.showerror("Erreur", "Suppression impossible. Le livre est peut-être emprunté.")

    def refresh_livres(self):
        for row in self.livre_tree.get_children():
            self.livre_tree.delete(row)
        for i, livre in enumerate(self.biblio.catalogue.values()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.livre_tree.insert("", tk.END, values=(livre.isbn, livre.titre, livre.auteur, livre.categorie), tags=(tag,))
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

        btn_frame = ttk.Frame(form_frame, style='TFrame')
        btn_frame.grid(row=0, column=4, rowspan=2, padx=10)
        ttk.Button(btn_frame, text="Ajouter Utilisateur", command=self.ajouter_utilisateur, style='TButton').pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="Modifier Utilisateur", command=self.modifier_utilisateur, style='TButton').pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="Supprimer Utilisateur", command=self.supprimer_utilisateur, style='TButton').pack(pady=2, fill=tk.X)

        self.user_tree = ttk.Treeview(tab, columns=("numero", "nom", "prenom", "email"), show="headings")
        for col in ("numero", "nom", "prenom", "email"):
            self.user_tree.heading(col, text=col.capitalize())
            self.user_tree.column(col, width=250)
        self.user_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.user_tree.bind("<<TreeviewSelect>>", self.charger_utilisateur_selectionne)
        self.refresh_utilisateurs()

    def charger_utilisateur_selectionne(self, event):
        selected_item = self.user_tree.selection()
        if not selected_item:
            return
        item_values = self.user_tree.item(selected_item, "values")
        self.clear_user_form()
        self.num_carte_entry.insert(0, item_values[0])
        self.nom_entry.insert(0, item_values[1])
        self.prenom_entry.insert(0, item_values[2])
        self.email_entry.insert(0, item_values[3])

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
            self.biblio.sauvegarder_donnees()
            messagebox.showinfo("Succès", "Utilisateur ajouté.")
            self.refresh_utilisateurs()
            self.clear_user_form()
        else:
            messagebox.showerror("Erreur", "Cet utilisateur existe déjà.")

    def modifier_utilisateur(self):
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showwarning("Modification", "Veuillez sélectionner un utilisateur à modifier.")
            return
        old_numero = self.user_tree.item(selected_item, "values")[0]
        new_numero = self.num_carte_entry.get().strip()
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        email = self.email_entry.get().strip()
        if not new_numero or not nom or not prenom or not email:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        user_modifie = Utilisateur(numero_carte=new_numero, nom=nom, prenom=prenom, email=email)
        if self.biblio.modifier_utilisateur(old_numero, user_modifie):
            self.biblio.sauvegarder_donnees()
            messagebox.showinfo("Succès", "Utilisateur modifié avec succès.")
            self.refresh_utilisateurs()
            self.clear_user_form()
        else:
            messagebox.showerror("Erreur", "La modification a échoué.")

    def supprimer_utilisateur(self):
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showwarning("Suppression", "Veuillez sélectionner un utilisateur à supprimer.")
            return
        numero = self.user_tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Confirmer la suppression", f"Voulez-vous vraiment supprimer l'utilisateur avec le numéro {numero} ?"):
            if self.biblio.supprimer_utilisateur(numero):
                self.biblio.sauvegarder_donnees()
                messagebox.showinfo("Succès", "Utilisateur supprimé avec succès.")
                self.refresh_utilisateurs()
                self.clear_user_form()
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.")

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

        form = ttk.Frame(tab, style='TFrame')
        form.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        search_frame = ttk.LabelFrame(form, text="Recherche d'emprunts")
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Utilisateur (N° Carte):").grid(row=0, column=0, sticky="w")
        self.search_user_entry = ttk.Entry(search_frame, width=20)
        self.search_user_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(search_frame, text="Livre (ISBN):").grid(row=0, column=2, sticky="w")
        self.search_book_entry = ttk.Entry(search_frame, width=20)
        self.search_book_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(search_frame, text="Statut:").grid(row=0, column=4, sticky="w")
        self.search_status_var = tk.StringVar()
        self.search_status_combo = ttk.Combobox(search_frame, textvariable=self.search_status_var, values=["", "En cours", "Terminé", "En retard"], state="readonly", width=15)
        self.search_status_combo.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(search_frame, text="Rechercher", command=self.rechercher_emprunts, style='TButton').grid(row=0, column=6, padx=10)

        emprunt_frame = ttk.LabelFrame(form, text="Nouvel Emprunt")
        emprunt_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(emprunt_frame, text="Utilisateur :").grid(row=0, column=0, sticky="w")
        self.user_search_var = tk.StringVar()
        self.user_entry = ttk.Entry(emprunt_frame, textvariable=self.user_search_var, width=30)
        self.user_entry.grid(row=0, column=1, padx=5)
        self.user_listbox = tk.Listbox(emprunt_frame, height=4, width=30, exportselection=False)
        self.user_listbox.grid(row=1, column=1, padx=5, pady=2)
        self.user_search_var.trace_add("write", self._filter_users)

        ttk.Label(emprunt_frame, text="Livre :").grid(row=0, column=2, sticky="w")
        self.book_search_var = tk.StringVar()
        self.book_entry = ttk.Entry(emprunt_frame, textvariable=self.book_search_var, width=30)
        self.book_entry.grid(row=0, column=3, padx=5)
        self.book_listbox = tk.Listbox(emprunt_frame, height=4, width=30, exportselection=False)
        self.book_listbox.grid(row=1, column=3, padx=5, pady=2)
        self.book_search_var.trace_add("write", self._filter_books)

        ttk.Button(emprunt_frame, text="Faire Emprunt", command=self.ajouter_emprunt_smart, style='TButton').grid(row=0, column=4, rowspan=2, padx=10)

        cols = ("id", "utilisateur", "livre", "date_emprunt", "date_retour_prevue", "date_retour_effective", "statut")
        self.emprunts_tree = ttk.Treeview(tab, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.emprunts_tree.heading(c, text=c.replace("_", " ").capitalize())
            self.emprunts_tree.column(c, width=120, anchor=tk.W)
        self.emprunts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Button(tab, text="Retourner le livre sélectionné", command=self.retourner_emprunt, style='TButton').pack(pady=5)
        self.refresh_emprunts()

    def rechercher_emprunts(self):
        user_query = self.search_user_entry.get().strip().lower()
        book_query = self.search_book_entry.get().strip().lower()
        status_query = self.search_status_var.get()

        self.refresh_emprunts(
            user_filter=user_query,
            book_filter=book_query,
            status_filter=status_query
        )

    def refresh_emprunts(self, user_filter="", book_filter="", status_filter=""):
        for row in self.emprunts_tree.get_children():
            self.emprunts_tree.delete(row)

        for i, emprunt in enumerate(self.biblio.emprunts.values()):
            utilisateur = self.biblio.utilisateurs.get(emprunt.id_utilisateur)
            livre = self.biblio.catalogue.get(emprunt.id_livre)

            if not utilisateur or not livre:
                continue

            user_match = user_filter in f"{utilisateur.nom} {utilisateur.prenom} {utilisateur.numero_carte}".lower()
            book_match = book_filter in f"{livre.titre} {livre.auteur} {livre.isbn}".lower()

            statut = "En cours"
            if emprunt.date_retour_effective:
                statut = "Terminé"
            elif emprunt.date_retour_prevue and datetime.now().date() > emprunt.date_retour_prevue.date():
                statut = "En retard"

            status_match = status_filter == "" or status_filter == statut

            if user_match and book_match and status_match:
                date_emprunt = emprunt.date_emprunt.strftime("%Y-%m-%d") if emprunt.date_emprunt else "N/A"
                date_retour_prevue = emprunt.date_retour_prevue.strftime("%Y-%m-%d") if emprunt.date_retour_prevue else "N/A"
                date_retour_effective = emprunt.date_retour_effective.strftime("%Y-%m-%d") if emprunt.date_retour_effective else "N/A"

                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.emprunts_tree.insert("", tk.END, values=(
                    emprunt.id, utilisateur.numero_carte, livre.isbn, date_emprunt, date_retour_prevue, date_retour_effective, statut), tags=(tag,))

        self.emprunts_tree.tag_configure('evenrow', background='white')
        self.emprunts_tree.tag_configure('oddrow', background='#f0f4ff')

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
        for livre in self.biblio.catalogue.values():
            if not livre.est_disponible():
                continue
            needle = f"{livre.titre} {livre.auteur} {livre.isbn}".lower()
            if text in needle:
                self.book_listbox.insert(tk.END, f"{livre.isbn} - {livre.titre}")

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
            self.biblio.sauvegarder_donnees()
            messagebox.showinfo("Succès", f"Emprunt n°{id_emprunt} enregistré.")
            self.refresh_emprunts()
            self._filter_users()
            self._filter_books()

    def retourner_emprunt(self):
        selected = self.emprunts_tree.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un emprunt à retourner.")
            return
        values = self.emprunts_tree.item(selected[0], "values")
        id_emprunt = int(values[0])
        if self.biblio.retourner_livre(id_emprunt):
            self.biblio.sauvegarder_donnees()
            messagebox.showinfo("Succès", "Retour effectué.")
            self.refresh_emprunts()
            self._filter_users()
            self._filter_books()
        else:
            messagebox.showerror("Erreur", "Retour impossible.")


    # --- Onglet Statistiques & Historique ---
    def create_stats_tab(self):
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text="Statistiques & Historique")

        main_frame = ttk.Frame(tab, style='TFrame')
        main_frame.pack(expand=True, padx=20, pady=20, fill=tk.BOTH)

        # Statistiques
        stats_frame = ttk.Frame(main_frame, style='TFrame', padding=20, relief="groove")
        stats_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        ttk.Label(stats_frame, text="📊 Statistiques de la Bibliothèque",
                  font=("Helvetica", 16, "bold"), foreground="#2b4f81",
                  background="white").grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")

        self.stats_labels = {}
        stats_data = [
            ("📚 Total de Livres :", "total_livres"),
            ("✅ Livres Disponibles :", "livres_disponibles"),
            ("📖 Total d'Emprunts :", "total_emprunts"),
            ("⏳ Emprunts en Cours :", "emprunts_en_cours"),
            ("👥 Total d'Utilisateurs :", "total_utilisateurs"),
            ("🚫 Utilisateurs Bloqués :", "utilisateurs_bloques"),
            ("💰 Amendes Totales :", "amendes_totales")
        ]

        for i, (label_text, key) in enumerate(stats_data):
            ttk.Label(stats_frame, text=label_text, font=("Helvetica", 12),
                      background="white", foreground="#4a4a4a").grid(row=i + 1, column=0, sticky="w", pady=5, padx=10)
            self.stats_labels[key] = ttk.Label(stats_frame, text="Chargement...", font=("Helvetica", 12, "bold"),
                                               background="white", foreground="#2b4f81")
            self.stats_labels[key].grid(row=i + 1, column=1, sticky="w", pady=5, padx=10)

        # Historique des transactions
        history_frame = ttk.Frame(main_frame, style='TFrame', padding=20, relief="groove")
        history_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)

        ttk.Label(history_frame, text="⏱️ Historique des Transactions Récentes",
                  font=("Helvetica", 16, "bold"), foreground="#2b4f81", background="white").pack(pady=(0, 20), fill=tk.X)

        history_cols = ("date", "type", "description")
        self.history_tree = ttk.Treeview(history_frame, columns=history_cols, show="headings", height=15)
        for c in history_cols:
            self.history_tree.heading(c, text=c.capitalize())
            self.history_tree.column(c, width=150)
        self.history_tree.pack(fill=tk.BOTH, expand=True)

    def update_stats(self):
        rapport = self.biblio.generer_rapport()

        emprunts_en_cours = sum(1 for e in self.biblio.emprunts.values() if e.statut is True)
        utilisateurs_bloques = sum(1 for u in self.biblio.utilisateurs.values() if hasattr(u, 'est_bloque') and u.est_bloque())
        total_amendes = sum(self.biblio.calculer_amende(e.id) for e in self.biblio.emprunts_en_retard())

        if hasattr(self, 'stats_labels'):
            self.stats_labels["total_livres"].config(text=str(rapport.get('total_livres', 0)))
            self.stats_labels["livres_disponibles"].config(text=str(rapport.get('livres_disponibles', 0)))
            self.stats_labels["total_emprunts"].config(text=str(rapport.get('total_emprunts', 0)))
            self.stats_labels["emprunts_en_cours"].config(text=str(emprunts_en_cours))
            self.stats_labels["total_utilisateurs"].config(text=str(rapport.get('total_utilisateurs', 0)))
            self.stats_labels["utilisateurs_bloques"].config(text=str(utilisateurs_bloques))
            self.stats_labels["amendes_totales"].config(text=f"{total_amendes:.2f} FCFA")

        self.refresh_history()

    def refresh_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        transactions = []
        for emp in self.biblio.emprunts.values():
            user = self.biblio.utilisateurs.get(emp.id_utilisateur)
            livre = self.biblio.catalogue.get(emp.id_livre)
            if not user or not livre:
                continue

            user_name = f"{user.prenom} {user.nom}"
            livre_title = livre.titre

            transactions.append({
                "date": emp.date_emprunt,
                "type": "Emprunt",
                "description": f"Livre '{livre_title}' par '{user_name}'"
            })
            if emp.date_retour_effective:
                transactions.append({
                    "date": emp.date_retour_effective,
                    "type": "Retour",
                    "description": f"Livre '{livre_title}' par '{user_name}'"
                })

        transactions.sort(key=lambda x: x['date'], reverse=True)

        for i, tx in enumerate(transactions[:20]):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.history_tree.insert("", tk.END, values=(
                tx['date'].strftime("%Y-%m-%d %H:%M"),
                tx['type'],
                tx['description']
            ), tags=(tag,))
        self.history_tree.tag_configure('evenrow', background='white')
        self.history_tree.tag_configure('oddrow', background='#f0f4ff')


    # --- Fenêtre changement mot de passe ---
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
            username = "admin"  # Adaptable

            if not self.biblio.verifier_identifiants(username, ancien):
                messagebox.showerror("Erreur", "Ancien mot de passe incorrect.")
                return
            if not nouveau:
                messagebox.showerror("Erreur", "Le nouveau mot de passe ne peut pas être vide.")
                return
            if nouveau != confirmer:
                messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
                return

            if self.biblio.changer_mot_de_passe(username, nouveau):
                self.biblio.sauvegarder_donnees()
                messagebox.showinfo("Succès", "Mot de passe modifié avec succès.")
                fen.destroy()
            else:
                messagebox.showerror("Erreur", "Erreur lors du changement de mot de passe.")

        ttk.Button(frame, text="Valider", command=valider_changement).pack(pady=10)


def show_login():
    login_root = tk.Tk()
    login_root.title("Connexion")
    login_root.geometry("350x220")
    login_root.resizable(False, False)

    Path("data").mkdir(exist_ok=True)
    biblio = Bibliotheque(nom="Bibliothèque Centrale", adresse="Ouagadougou")
    biblio.charger_donnees()

    username_var = tk.StringVar()
    password_var = tk.StringVar()

    def check_credentials():
        username = username_var.get()
        password = password_var.get()
        if biblio.verifier_identifiants(username, password):
            messagebox.showinfo("Succès", f"Bienvenue {username} !")
            login_root.destroy()
            main_root = tk.Tk()
            app = BibliothequeApp(main_root, biblio)
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
