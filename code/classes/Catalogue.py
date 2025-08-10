import sqlite3
from pathlib import Path
from datetime import datetime
from classes.Livre import Livre

DB_PATH = Path("data/bibliotheque.db")

class Catalogue:
    def __init__(self):
        self.livres = {}  # clé = ISBN, valeur = Livre

    # --- Gestion en mémoire ---
    def ajouter_livre(self, livre) -> bool:
        if livre.isbn in self.livres:
            return False
        self.livres[livre.isbn] = livre
        return True

    def supprimer_livre(self, isbn: str) -> bool:
        return self.livres.pop(isbn, None) is not None

    def rechercher_par_titre(self, titre: str):
        return [livre for livre in self.livres.values() if titre.lower() in livre.titre.lower()]

    def rechercher_par_auteur(self, auteur: str):
        return [livre for livre in self.livres.values() if auteur.lower() in livre.auteur.lower()]

    def rechercher_par_categorie(self, categorie: str):
        return [livre for livre in self.livres.values() if livre.categorie.lower() == categorie.lower()]

    def recherche_avancee(self, criteres: dict):
        resultats = list(self.livres.values())
        for cle, valeur in criteres.items():
            resultats = [livre for livre in resultats if getattr(livre, cle, "").lower() == valeur.lower()]
        return resultats

    def lister_livres_disponibles(self):
        return [livre for livre in self.livres.values() if livre.est_disponible()]

    # --- Persistance SQLite ---
    @staticmethod
    def creer_table():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS catalogue (
                isbn TEXT PRIMARY KEY,
                titre TEXT,
                auteur TEXT,
                categorie TEXT,
                disponible INTEGER,
                date_ajout TEXT
            )
        """)
        conn.commit()
        conn.close()

    def sauvegarder_livre(self, livre):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO catalogue
            (isbn, titre, auteur, categorie, disponible, date_ajout)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            livre.isbn,
            livre.titre,
            livre.auteur,
            livre.categorie,
            1 if livre.est_disponible() else 0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def charger_tous():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT isbn, titre, auteur, categorie, disponible FROM catalogue")
        rows = cursor.fetchall()
        conn.close()
        return [
            Livre(isbn=row[0], titre=row[1], auteur=row[2], categorie=row[3], disponible=bool(row[4]))
            for row in rows
        ]

    @staticmethod
    def supprimer_livre_db(isbn: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM catalogue WHERE isbn = ?", (isbn,))
        conn.commit()
        conn.close()
