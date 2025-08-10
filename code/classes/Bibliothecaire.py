from classes.Personne import Personne
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/bibliotheque.db")

class Bibliothecaire(Personne):
    def __init__(self, id: int, matricule: str, nom: str, prenom: str,
                 email: str, telephone: str = "", niveau_acces: str = "standard"):
        super().__init__(nom, prenom, email, telephone)
        self.id = id
        self.matricule = matricule
        self.niveau_acces = niveau_acces

    # --- Méthodes Métier ---
    def ajouter_livre(self, catalogue, livre) -> bool:
        return catalogue.ajouter_livre(livre)

    def supprimer_livre(self, catalogue, isbn: str) -> bool:
        return catalogue.supprimer_livre(isbn)

    def gerer_emprunt(self, emprunt) -> bool:
        return emprunt.finaliser_retour()

    def __repr__(self):
        return (f"Bibliothecaire(id={self.id}, matricule='{self.matricule}', "
                f"nom='{self.nom}', prenom='{self.prenom}', email='{self.email}', "
                f"telephone='{self.telephone}', niveau_acces='{self.niveau_acces}')")

    # --- Persistance SQLite ---
    @staticmethod
    def creer_table():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bibliothecaires (
                id INTEGER PRIMARY KEY,
                matricule TEXT UNIQUE,
                nom TEXT,
                prenom TEXT,
                email TEXT,
                telephone TEXT,
                niveau_acces TEXT,
                date_ajout TEXT
            )
        """)
        conn.commit()
        conn.close()

    def sauvegarder(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO bibliothecaires
            (id, matricule, nom, prenom, email, telephone, niveau_acces, date_ajout)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.id, self.matricule, self.nom, self.prenom,
            self.email, self.telephone, self.niveau_acces,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def charger_tous():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bibliothecaires")
        rows = cursor.fetchall()
        conn.close()
        return [
            Bibliothecaire(id=row[0], matricule=row[1], nom=row[2],
                           prenom=row[3], email=row[4], telephone=row[5],
                           niveau_acces=row[6])
            for row in rows
        ]

    @staticmethod
    def supprimer(matricule: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bibliothecaires WHERE matricule = ?", (matricule,))
        conn.commit()
        conn.close()
