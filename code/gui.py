import tkinter as tk
from tkinter import ttk, messagebox
from classes.Bibliotheque import Bibliotheque
from classes.Livre import Livre

class BiblioGUI(tk.Tk):
    def __init__(self, bibliotheque):
        super().__init__()
        self.title("Gestion Bibliothèque")
        self.geometry("700x400")
        self.biblio = bibliotheque
        
        self.create_widgets()
        self.afficher_livres()

    def create_widgets(self):
        # Liste des livres
        self.tree = ttk.Treeview(self, columns=("isbn", "titre", "auteur", "disponible"), show="headings")
        self.tree.heading("isbn", text="ISBN")
        self.tree.heading("titre", text="Titre")
        self.tree.heading("auteur", text="Auteur")
        self.tree.heading("disponible", text="Disponible")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Formulaire pour ajouter un livre
        form_frame = tk.Frame(self)
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(form_frame, text="ISBN").grid(row=0, column=0)
        tk.Label(form_frame, text="Titre").grid(row=0, column=2)
        tk.Label(form_frame, text="Auteur").grid(row=0, column=4)

        self.entry_isbn = tk.Entry(form_frame)
        self.entry_isbn.grid(row=0, column=1)
        self.entry_titre = tk.Entry(form_frame)
        self.entry_titre.grid(row=0, column=3)
        self.entry_auteur = tk.Entry(form_frame)
        self.entry_auteur.grid(row=0, column=5)

        btn_ajouter = tk.Button(form_frame, text="Ajouter livre", command=self.ajouter_livre)
        btn_ajouter.grid(row=0, column=6, padx=10)

    def afficher_livres(self):
        # Vide la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Ajoute les livres du catalogue
        for livre in self.biblio.lister_livres():
            dispo = "Oui" if livre.est_disponible() else "Non"
            self.tree.insert("", "end", values=(livre.isbn, livre.titre, livre.auteur, dispo))

    def ajouter_livre(self):
        isbn = self.entry_isbn.get().strip()
        titre = self.entry_titre.get().strip()
        auteur = self.entry_auteur.get().strip()

        if not isbn or not titre or not auteur:
            messagebox.showwarning("Erreur", "Remplir tous les champs")
            return

        if isbn in [l.isbn for l in self.biblio.lister_livres()]:
            messagebox.showwarning("Erreur", "ISBN déjà existant")
            return
        
        # Création d'un livre simple, avec valeurs par défaut pour les autres champs
        nouveau_livre = Livre(
            isbn=isbn,
            titre=titre,
            auteur=auteur,
            editeur="Inconnu",
            annee_publication=2025,
            categorie="Inconnue",
            nombre_pages=0
        )

        if self.biblio.ajouter_livre(nouveau_livre):
            messagebox.showinfo("Succès", "Livre ajouté")
            self.afficher_livres()
            self.entry_isbn.delete(0, tk.END)
            self.entry_titre.delete(0, tk.END)
            self.entry_auteur.delete(0, tk.END)
        else:
            messagebox.showerror("Erreur", "Impossible d'ajouter le livre")

if __name__ == "__main__":
    from classes.Bibliotheque import Bibliotheque

    biblio = Bibliotheque(nom="Bibliothèque Centrale", adresse="Ouagadougou")

    app = BiblioGUI(biblio)
    app.mainloop()
    biblio.fermer_connexion()
