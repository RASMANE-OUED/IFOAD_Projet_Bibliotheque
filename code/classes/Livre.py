import sqlite3
from pathlib import Path
from datetime import datetime
import re

DB_PATH = Path("data/bibliotheque.db")

class Livre:
    def __init__(self, isbn: str, titre: str, auteur: str, editeur: str,
                 annee_publication: int, categorie: str, nombre_pages: int,
                 disponibilite: bool = True, date_ajout: datetime = None):
        self.isbn = isbn
        self.titre = titre
        self.auteur = auteur
        self.editeur = editeur
        self.annee_publication = annee_publication
        self.categorie = categorie
        self.nombre_pages = nombre_pages
        self.disponible = disponibilite
        self.date_ajout = date_ajout or datetime.now()

    def __repr__(self):
        return (f"Livre(isbn='{self.isbn}', titre='{self.titre}', auteur='{self.auteur}', "
                f"editeur='{self.editeur}', annee={self.annee_publication}, "
                f"categorie='{self.categorie}', pages={self.nombre_pages}, "
                f"disponible={self.disponible})")

    def est_disponible(self) -> bool:
        return self.disponible

    def marquer_emprunte(self):
        self.disponible = False
        self.mettre_a_jour_db()

    def marquer_disponible(self):
        self.disponible = True
        self.mettre_a_jour_db()

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

    # ------------------------
    #   PERSISTANCE SQLITE
    # ------------------------

    @staticmethod
    def creer_table():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livres (
                isbn TEXT PRIMARY KEY,
                titre TEXT,
                auteur TEXT,
                editeur TEXT,
                annee_publication INTEGER,
                categorie TEXT,
                nombre_pages INTEGER,
                disponible INTEGER,
                date_ajout TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO livres
            (isbn, titre, auteur, editeur, annee_publication, categorie, nombre_pages, disponible, date_ajout)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.isbn,
            self.titre,
            self.auteur,
            self.editeur,
            self.annee_publication,
            self.categorie,
            self.nombre_pages,
            1 if self.disponible else 0,
            self.date_ajout.strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

    def mettre_a_jour_db(self):
        self.sauvegarder_db()

    @staticmethod
    def charger_tous():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres")
        rows = cursor.fetchall()
        conn.close()

        livres = []
        for row in rows:
            livres.append(
                Livre(
                    isbn=row[0],
                    titre=row[1],
                    auteur=row[2],
                    editeur=row[3],
                    annee_publication=row[4],
                    categorie=row[5],
                    nombre_pages=row[6],
                    disponibilite=bool(row[7]),
                    date_ajout=datetime.strptime(row[8], "%Y-%m-%d %H:%M:%S")
                )
            )
        return livres


    def get_livres_disponibles(self) -> list[dict]:
        """Format spécial pour Combobox"""
        return [
            {"isbn": livre.isbn, "titre": livre.titre}
            for livre in self.catalogue.livres.values() 
            if livre.disponible
        ]
    
    def get_utilisateurs_formates(self) -> list[dict]:
        """Format pour la liste déroulante"""
        return [
            {"numero": u.numero_carte, "nom_complet": f"{u.prenom} {u.nom}"}
            for u in self.utilisateurs.values()
        ]
    
    def get_emprunts_actifs(self) -> list[dict]:
        """Pour l'affichage dans Treeview"""
        return [
            {
                "id": emp.id,
                "utilisateur": self.utilisateurs[emp.id_utilisateur].prenom,
                "livre": self.catalogue.livres[emp.id_livre].titre,
                "date": emp.date_emprunt.strftime("%d/%m/%Y"),
                "statut": "Actif" if emp.statut else "Terminé"
            }
            for emp in self.emprunts.values()
        ]
    
    def rechercher_livres(self, critere: str) -> list[dict]:
        """Recherche multi-critères"""
        critere = critere.lower()
        resultats = []
        for livre in self.catalogue.livres.values():
            if (critere in livre.titre.lower() or 
                critere in livre.auteur.lower() or 
                critere in livre.isbn.lower()):
                resultats.append({
                    "isbn": livre.isbn,
                    "titre": livre.titre,
                    "auteur": livre.auteur,
                    "disponible": "Oui" if livre.disponible else "Non"
                })
        return resultats

    @staticmethod
    def supprimer_db(isbn: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livres WHERE isbn = ?", (isbn,))
        conn.commit()
        conn.close()
