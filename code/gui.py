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

    def refresh_emprunts(self):
        """Remplit le Treeview avec les emprunts actuels."""
        for row in self.emprunts_tree.get_children():
            self.emprunts_tree.delete(row)
        for emprunt in self.biblio.emprunts.values():
            user = self.biblio.utilisateurs.get(emprunt.id_utilisateur)
            livre = self.biblio.catalogue.livres.get(emprunt.id_livre)
            self.emprunts_tree.insert(
                "", tk.END, values=(
                emprunt.id,
                user.numero_carte if user else "Inconnu",
                livre.isbn if livre else "Inconnu",
                emprunt.date_emprunt.strftime("%d/%m/%Y"),
                emprunt.date_retour_prevue.strftime("%d/%m/%Y"),
                emprunt.date_retour_effective.strftime("%d/%m/%Y") if emprunt.date_retour_effective else "",
                "En cours" if emprunt.statut else "Terminé"
            )
        )


    def _filter_users(self, *args):
        txt = self.user_search_var.get().lower()
        self.user_listbox.delete(0, tk.END)
        for u in self.biblio.utilisateurs.values():
            if txt in f"{u.nom} {u.prenom} {u.numero_carte}".lower():
                self.user_listbox.insert(tk.END, f"{u.numero_carte} - {u.prenom} {u.nom}")
        if self.user_listbox.size():
            self.user_listbox.selection_set(0)


    def _filter_books(self, *args):
        txt = self.book_search_var.get().lower()
        self.book_listbox.delete(0, tk.END)
        for livre in self.biblio.catalogue.livres.values():
            if livre.est_disponible() and txt in f"{livre.titre} {livre.auteur} {livre.isbn}".lower():
                self.book_listbox.insert(tk.END, f"{livre.isbn} - {livre.titre}")
        if self.book_listbox.size():
            self.book_listbox.selection_set(0)


    def ajouter_emprunt_smart(self):
        """Crée l’emprunt avec l’utilisateur et le livre sélectionnés."""
        if not self.user_listbox.curselection() or not self.book_listbox.curselection():
            messagebox.showwarning("Sélection", "Veuillez choisir un utilisateur et un livre dans les listes.")
            return

        numero_carte = self.user_listbox.get(self.user_listbox.curselection()).split(" - ")[0]
        isbn = self.book_listbox.get(self.book_listbox.curselection()).split(" - ")[0]

        id_emprunt = self.biblio.emprunter_livre(numero_carte, isbn)
        if id_emprunt is None:
            messagebox.showerror("Erreur", "Impossible d’effectuer l’emprunt.")
        else:
            messagebox.showinfo("Succès", f"Emprunt n°{id_emprunt} enregistré.")
            self.refresh_emprunts()
            self._filter_users()
            self._filter_books()


    def retourner_emprunt(self):
        """Retourne l’emprunt sélectionné."""
        sel = self.emprunts_tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un emprunt à retourner.")
            return
        id_emprunt = int(self.emprunts_tree.item(sel[0], "values")[0])
        if self.biblio.retourner_livre(id_emprunt):
            messagebox.showinfo("Succès", "Retour effectué.")
            self.refresh_emprunts()
            self._filter_users()
            self._filter_books()
        else:
            messagebox.showerror("Erreur", "Retour impossible.")

if __name__ == "__main__":
    from classes.Bibliotheque import Bibliotheque

    biblio = Bibliotheque(nom="Bibliothèque Centrale", adresse="Ouagadougou")

    app = BiblioGUI(biblio)
    app.mainloop()
    biblio.fermer_connexion()
