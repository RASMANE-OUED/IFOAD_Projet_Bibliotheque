import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from classes.Bibliotheque import Bibliotheque
from classes.Livre import Livre
from classes.Utilisateur import Utilisateur

class BibliothequeApp:
    def __init__(self, root):
        self.root = root
        self.root.title(" Gestion de Bibliothèque UJKZ")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f4f6f8")

        Path("data").mkdir(exist_ok=True)
        self.biblio = Bibliotheque(nom="Bibliothèque Centrale", adresse="Ouagadougou")

        self.setup_style()
        self.setup_ui()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background="#f4f6f8", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#2b4f81")], foreground=[("selected", "white")])

        style.configure("TLabel", background="#f4f6f8", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), background="#2b4f81", foreground="white", padding=5)

        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6, relief="flat", background="#2b4f81", foreground="white")
        style.map("TButton", background=[("active", "#1f3a5f")])

        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#2b4f81")], foreground=[("selected", "white")])

        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#e1e5eb", foreground="#2b4f81")

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_livre_tab()
        self.create_utilisateur_tab()
        self.create_emprunt_tab()
        self.create_stats_tab()

        self.status_bar = ttk.Label(self.root, text="Prêt", relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # --- Onglet Livres ---
    def create_livre_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Livres")

        form_frame = ttk.Frame(tab)
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

        add_btn = ttk.Button(form_frame, text="Ajouter Livre", command=self.ajouter_livre)
        add_btn.grid(row=0, column=4, rowspan=2, padx=10)

        # Tableau
        self.livre_tree = ttk.Treeview(tab, columns=("isbn", "titre", "auteur", "categorie"), show="headings")
        for col in ("isbn", "titre", "auteur", "categorie"):
            self.livre_tree.heading(col, text=col.capitalize())
            self.livre_tree.column(col, width=200)
        self.livre_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_livres()

    def ajouter_livre(self):
        isbn = self.isbn_entry.get()
        titre = self.titre_entry.get()
        auteur = self.auteur_entry.get()
        categorie = self.categorie_entry.get()

        if not isbn or not titre or not auteur:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        livre = Livre(isbn=isbn, titre=titre, auteur=auteur, editeur="Inconnu",
                      annee_publication=2025, categorie=categorie, nombre_pages=100)
        if self.biblio.ajouter_livre(livre):
            messagebox.showinfo("Succès", "Livre ajouté avec succès.")
            self.refresh_livres()
        else:
            messagebox.showerror("Erreur", "Ce livre existe déjà.")

    def refresh_livres(self):
        for row in self.livre_tree.get_children():
            self.livre_tree.delete(row)
        for livre in self.biblio.catalogue.livres.values():
            self.livre_tree.insert("", tk.END, values=(livre.isbn, livre.titre, livre.auteur, livre.categorie))

    # --- Onglet Utilisateurs ---
    def create_utilisateur_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Utilisateurs")

        form_frame = ttk.Frame(tab)
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

        add_btn = ttk.Button(form_frame, text="Ajouter Utilisateur", command=self.ajouter_utilisateur)
        add_btn.grid(row=0, column=4, rowspan=2, padx=10)

        self.user_tree = ttk.Treeview(tab, columns=("numero", "nom", "prenom", "email"), show="headings")
        for col in ("numero", "nom", "prenom", "email"):
            self.user_tree.heading(col, text=col.capitalize())
            self.user_tree.column(col, width=200)
        self.user_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_utilisateurs()

    def ajouter_utilisateur(self):
        numero = self.num_carte_entry.get()
        nom = self.nom_entry.get()
        prenom = self.prenom_entry.get()
        email = self.email_entry.get()

        if not numero or not nom or not prenom or not email:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        user = Utilisateur(numero_carte=numero, nom=nom, prenom=prenom, email=email)
        if self.biblio.inscrire_utilisateur(user):
            messagebox.showinfo("Succès", "Utilisateur ajouté.")
            self.refresh_utilisateurs()
        else:
            messagebox.showerror("Erreur", "Cet utilisateur existe déjà.")

    def refresh_utilisateurs(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        for user in self.biblio.utilisateurs.values():
            self.user_tree.insert("", tk.END, values=(user.numero_carte, user.nom, user.prenom, user.email))

    # --- Onglet Emprunts ---
    def create_emprunt_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Emprunts")

        ttk.Label(tab, text="Fonction emprunts à implémenter...").pack()

    # --- Onglet Statistiques ---
    def create_stats_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Statistiques")

        self.stats_label = ttk.Label(tab, text="", style="Header.TLabel")
        self.stats_label.pack(fill=tk.BOTH, expand=True)

        self.update_stats()

    def update_stats(self):
        rapport = self.biblio.generer_rapport()
        self.stats_label.config(text=str(rapport))
        self.root.after(10000, self.update_stats)  # Mise à jour toutes les 10s


if __name__ == "__main__":
    root = tk.Tk()
    app = BibliothequeApp(root)
    root.mainloop()
