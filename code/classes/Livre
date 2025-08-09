from datetime import datetime

class Livre:
    def __init__(self, isbn: str, titre: str, auteur: str, editeur: str,
                 annee_publication: int, categorie: str, nombre_pages: int,
                 disponibilite: bool = True):
        self.isbn = isbn
        self.titre = titre
        self.auteur = auteur
        self.editeur = editeur
        self.annee_publication = annee_publication
        self.categorie = categorie
        self.nombre_pages = nombre_pages
        self.disponible = disponibilite
        self.date_ajout = datetime.now()

    def __repr__(self):
        return (f"Livre(isbn='{self.isbn}', titre='{self.titre}', auteur='{self.auteur}', "
                f"editeur='{self.editeur}', annee={self.annee_publication}, "
                f"categorie='{self.categorie}', pages={self.nombre_pages}, "
                f"disponible={self.disponible})")

    def est_disponible(self) -> bool:
        return self.disponible

    def marquer_emprunte(self):
        self.disponible = False

    def marquer_disponible(self):
        self.disponible = True

    def get_details(self) -> dict:
        return {
            "ISBN": self.isbn,
            "Titre": self.titre,
            "Auteur": self.auteur,
            "Éditeur": self.editeur,
            "Année": self.annee_publication,
            "Catégorie": self.categorie,
            "Pages": self.nombre_pages,
            "Disponible": self.disponible,
            "Ajouté le": self.date_ajout.strftime("%Y-%m-%d %H:%M")
        }
