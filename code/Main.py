import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from classes.Bibliotheque import Bibliotheque
from classes.Livre import Livre
from classes.Utilisateur import Utilisateur
from classes.Emprunt import Emprunt

class BibliothequeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Bibliothèque UJKZ")
        self.root.geometry("1200x700")

        # Initialisation de la base
        Path("data").mkdir(exist_ok=True)
       # Bibliotheque.creer_table()
        Livre.creer_table()
        Utilisateur.creer_table()
        Emprunt.creer_table()

        self.biblio = Bibliotheque(nom="Bibliothèque Centrale", adresse="Ouagadougou")
        self.biblio.creer_table()
        # Style
        self.setup_style()

        # Interface
        self.setup_ui()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10), padding=5)
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_livre_tab()
        self.create_utilisateur_tab()
        self.create_emprunt_tab()
        self.create_stats_tab()

        self.status_bar = ttk.Label(self.root, text="Prêt", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X)

    # ========================= Onglet Livres =========================
    def create_livre_tab(self):

        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Gestion des Livres")
    
        # Contrôles de recherche
        search_frame = ttk.Frame(frame)
        search_frame.pack(pady=10, padx=10, fill=tk.X)
    
        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_livres)
    
        ttk.Button(search_frame, text="Ajouter Livre", 
              command=self.show_add_livre_dialog).pack(side=tk.RIGHT)
    
    # ----liste des livres)
        columns = ("isbn", "titre", "auteur", "disponible")
        self.livre_tree = ttk.Treeview(frame, columns=columns, show='headings')
    
        self.livre_tree.heading("isbn", text="ISBN")
        self.livre_tree.heading("titre", text="Titre")
        self.livre_tree.heading("auteur", text="Auteur")
        self.livre_tree.heading("disponible", text="Disponible")
    
        self.livre_tree.column("isbn", width=150)
        self.livre_tree.column("titre", width=300)
        self.livre_tree.column("auteur", width=200)
        self.livre_tree.column("disponible", width=100)
    
        self.livre_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
        # Barre de défilement
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.livre_tree.yview)
        self.livre_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Charger les données
        self.load_livres()

    def show_add_livre_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un nouveau livre")
        dialog.geometry("500x400")
    
    # Formulaire
        fields = [
        ("ISBN", "entry"),
        ("Titre", "entry"),
        ("Auteur", "entry"),
        ("Éditeur", "entry"),
        ("Année Publication", "entry"),
        ("Catégorie", "combobox", ["Informatique", "Littérature", "Science", "Histoire"]),
        ("Nombre Pages", "entry")
    ]
    
        entries = {}
        for i, (label, field_type, *options) in enumerate(fields):
            ttk.Label(dialog, text=label+":").grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
        
            if field_type == "entry":
                entry = ttk.Entry(dialog)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
                entries[label.lower().replace(" ", "_")] = entry
            elif field_type == "combobox":
                cb = ttk.Combobox(dialog, values=options[0])
                cb.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
                entries[label.lower().replace(" ", "_")] = cb
    
    # Boutons
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=len(fields)+1, columnspan=2, pady=10)
    
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Enregistrer", 
              command=lambda: self.save_new_livre(dialog, entries)).pack(side=tk.LEFT, padx=5)

    def save_new_livre(self, dialog, entries):
        try:
            livre = Livre(
            isbn=entries['isbn'].get(),
            titre=entries['titre'].get(),
            auteur=entries['auteur'].get(),
            editeur=entries['éditeur'].get(),
            annee_publication=int(entries['année_publication'].get()),
            categorie=entries['catégorie'].get(),
            nombre_pages=int(entries['nombre_pages'].get())
        )
            self.biblio.ajouter_livre(livre)
            self.load_livres()
            dialog.destroy()
            messagebox.showinfo("Succès", "Livre ajouté avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {str(e)}")

    # ========================= Onglet Utilisateurs =========================

    def create_utilisateur_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Utilisateurs")
    
    # Contrôles
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
    
        ttk.Button(control_frame, text="Nouvel Utilisateur",
              command=self.show_add_user_dialog).pack(side=tk.LEFT)
    
    # Liste des utilisateurs
        columns = ("numero", "nom", "prenom", "email")
        self.user_tree = ttk.Treeview(frame, columns=columns, show='headings')
    
        for col in columns:
            self.user_tree.heading(col, text=col.capitalize())
            self.user_tree.column(col, width=150)
    
        self.user_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.load_utilisateurs()

    def show_add_user_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouvel Utilisateur")
    
    # Formulaire avec validation
        fields = [
        ("Numéro Carte", "entry", r'^U\d{3}$', "Format: U001, U002..."),
        ("Nom", "entry"),
        ("Prénom", "entry"),
        ("Email", "entry", r'^[^@]+@[^@]+\.[^@]+$', "Email invalide")
    ]
    
        entries = {}
        for i, (label, field_type, *options) in enumerate(fields):
            ttk.Label(dialog, text=label+":").grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label.lower().replace(" ", "_")] = entry
        
            if options:
            # Ajouter le texte d'aide
                help_label = ttk.Label(dialog, text=options[1], foreground="gray")
                help_label.grid(row=i, column=2, padx=5, sticky=tk.W)
    
    # Boutons
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=len(fields)+1, columnspan=3, pady=10)
    
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Enregistrer",
              command=lambda: self.save_new_user(dialog, entries, fields)).pack(side=tk.LEFT, padx=5)

    def save_new_user(self, dialog, entries, fields):
        try:
        # Validation
            for (label, _, *pattern) in fields:
                key = label.lower().replace(" ", "_")
                if pattern and not re.match(pattern[0], entries[key].get()):
                    raise ValueError(f"{label} invalide")
        
            user = Utilisateur(
            numero_carte=entries['numéro_carte'].get(),
            nom=entries['nom'].get(),
            prenom=entries['prénom'].get(),
            email=entries['email'].get()
        )
            self.biblio.inscrire_utilisateur(user)
            self.load_utilisateurs()
            dialog.destroy()
            messagebox.showinfo("Succès", "Utilisateur enregistré!")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    def load_utilisateurs(self):
    # Exemple de chargement depuis la base
        utilisateurs = Utilisateur.get_all()  
        for user in utilisateurs:
            print(user.nom, user.email)  


    # ========================= Onglet Emprunts =========================

    def create_emprunt_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Gestion des Emprunts")
    
    # Panneau de contrôle
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=10)
    
        ttk.Button(control_frame, text="Nouvel Emprunt",
              command=self.show_emprunt_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Enregistrer Retour",
              command=self.enregistrer_retour).pack(side=tk.LEFT, padx=5)
    
    # Liste des emprunts
        columns = ("id", "utilisateur", "livre", "date_emprunt", "statut")
        self.emprunt_tree = ttk.Treeview(frame, columns=columns, show='headings')
    
        self.emprunt_tree.heading("id", text="ID")
        self.emprunt_tree.heading("utilisateur", text="Utilisateur")
        self.emprunt_tree.heading("livre", text="Livre")
        self.emprunt_tree.heading("date_emprunt", text="Date Emprunt")
        self.emprunt_tree.heading("statut", text="Statut")
    
        self.emprunt_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.load_emprunts()

    def show_emprunt_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouvel Emprunt")
    
    # Sélection utilisateur
        ttk.Label(dialog, text="Utilisateur:").grid(row=0, column=0, padx=5, pady=5)
        self.user_combo = ttk.Combobox(dialog)
        self.user_combo.grid(row=0, column=1, padx=5, pady=5)
        self.user_combo['values'] = [f"{u.numero_carte} - {u.prenom} {u.nom}" 
                                for u in self.biblio.utilisateurs.values()]
    
    # Sélection livre (uniquement disponibles)
        ttk.Label(dialog, text="Livre:").grid(row=1, column=0, padx=5, pady=5)
        self.livre_combo = ttk.Combobox(dialog)
        self.livre_combo.grid(row=1, column=1, padx=5, pady=5)
        self.update_livre_combo()
    
    # Boutons
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=2, columnspan=2, pady=10)
    
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Enregistrer",
              command=lambda: self.save_emprunt(dialog)).pack(side=tk.LEFT, padx=5)

    def save_emprunt(self, dialog):
        try:
            user_num = self.user_combo.get().split(" - ")[0]
            isbn = self.livre_combo.get().split(" - ")[0]
        
            emprunt_id = self.biblio.emprunter_livre(user_num, isbn)
            self.load_emprunts()
            self.load_livres()  # Rafraîchir la disponibilité
            dialog.destroy()
            messagebox.showinfo("Succès", f"Emprunt enregistré (ID: {emprunt_id})")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ========================= Onglet Statistiques =========================

    def create_stats_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Statistiques")
    
    # Conteneur pour les graphiques
        self.stats_container = ttk.Frame(frame)
        self.stats_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Bouton rafraîchir
        ttk.Button(frame, text="Rafraîchir", command=self.update_stats).pack(pady=5)
    
        self.update_stats()

    def update_stats(self):
    # Nettoyer le conteneur
        for widget in self.stats_container.winfo_children():
            widget.destroy()
    
        stats = self.biblio.generer_rapport()
    
    # Statistiques textuelles
        stats_frame = ttk.Frame(self.stats_container)
        stats_frame.pack(fill=tk.X, pady=10)
    
        for i, (k, v) in enumerate(stats.items()):
            ttk.Label(stats_frame, text=f"{k.replace('_', ' ').title()}:").grid(row=i, column=0, sticky=tk.W)
            ttk.Label(stats_frame, text=str(v), font=('Helvetica', 10, 'bold')).grid(row=i, column=1, sticky=tk.W)
    
    # Graphique (nécessite matplotlib)
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Graphique 1: Livres par catégorie
            categories = {}
            for livre in self.biblio.catalogue.livres.values():
                categories[livre.categorie] = categories.get(livre.categorie, 0) + 1
        
            ax1.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
            ax1.set_title('Livres par catégorie')
        
        # Graphique 2: Statut des emprunts
            status_counts = {'En cours': 0, 'Terminé': 0}
            for emp in self.biblio.emprunts.values():
                status_counts['En cours' if emp.statut else 'Terminé'] += 1
        
            ax2.bar(status_counts.keys(), status_counts.values(), color=['green', 'blue'])
            ax2.set_title('Statut des emprunts')
        
        # Intégration dans Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.stats_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        except ImportError:
            ttk.Label(self.stats_container, 
                 text="Matplotlib non installé - les graphiques sont désactivés",
                 foreground="red").pack()

# ================= Fonctions Utilitaires   =============================

    def load_livres(self):
        """Rafraîchir la liste des livres"""
        self.livre_tree.delete(*self.livre_tree.get_children())
        for livre in self.biblio.catalogue.livres.values():
            self.livre_tree.insert("", tk.END, values=(
            livre.isbn,
            livre.titre,
            livre.auteur,
            "Oui" if livre.disponible else "Non"
        ))

    def search_livres(self, event=None):
        """Filtrer la liste des livres"""
        query = self.search_entry.get().lower()
        for child in self.livre_tree.get_children():
            values = self.livre_tree.item(child)['values']
            if any(query in str(v).lower() for v in values):
                self.livre_tree.item(child, tags=('visible',))
            else:
                self.livre_tree.item(child, tags=('hidden',))
        self.livre_tree.tag_configure('hidden', foreground='gray')

    def update_livre_combo(self):
        """Mettre à jour la liste des livres disponibles"""
        livres_dispo = [f"{l.isbn} - {l.titre}" 
                   for l in self.biblio.catalogue.livres.values() 
                   if l.disponible]
        self.livre_combo['values'] = livres_dispo
        if livres_dispo:
            self.livre_combo.current(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = BibliothequeApp(root)
    root.mainloop()
