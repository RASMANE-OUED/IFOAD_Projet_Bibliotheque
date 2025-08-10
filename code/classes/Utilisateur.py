import sqlite3
from pathlib import Path
from typing import List
from classes.Personne import Personne

DB_PATH = Path("data/bibliotheque.db")

class Utilisateur(Personne):
    def __init__(self, numero_carte: str, nom: str, prenom: str, email: str,
                 telephone: str = "", statut: str = "ACTIF", historique: List[str] = None):
        super().__init__(nom, prenom, email, telephone)
        self.numero_carte = numero_carte
        self.statut = statut
        self.historique = historique if historique is not None else []
        self.emprunts_actifs = []

    def emprunter_livre(self, livre) -> bool:
        if self.statut != "ACTIF" or len(self.emprunts_actifs) >= 5:
            return False
        if not livre.est_disponible():
            return False
        self.emprunts_actifs.append(livre)
        self.historique.append(f"Emprunt: {livre.titre}")
        livre.marquer_emprunte()
        self.mettre_a_jour_db()
        return True

    def retourner_livre(self, livre) -> bool:
        if livre not in self.emprunts_actifs:
            return False
        self.emprunts_actifs.remove(livre)
        self.historique.append(f"Retour: {livre.titre}")
        livre.marquer_disponible()
        self.mettre_a_jour_db()
        return True

    def consulter_emprunts(self) -> List[str]:
        return [livre.titre for livre in self.emprunts_actifs]

    def __repr__(self):
        return (f"Utilisateur(numero_carte={self.numero_carte}, nom={self.nom}, "
                f"prenom={self.prenom}, email={self.email}, statut={self.statut})")

    # ------------------------
    #   PERSISTANCE SQLITE
    # ------------------------

    @staticmethod
    def creer_table():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                numero_carte TEXT PRIMARY KEY,
                nom TEXT,
                prenom TEXT,
                email TEXT,
                telephone TEXT,
                statut TEXT,
                historique TEXT
            )
        """)
        conn.commit()
        conn.close()

    def sauvegarder_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO utilisateurs
            (numero_carte, nom, prenom, email, telephone, statut, historique)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.numero_carte,
            self.nom,
            self.prenom,
            self.email,
            self.telephone,
            self.statut,
            "|".join(self.historique)  # Historique stocké en chaîne séparée par |
        ))
        conn.commit()
        conn.close()

    def mettre_a_jour_db(self):
        self.sauvegarder_db()

    @staticmethod
    def charger_tous():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM utilisateurs")
        rows = cursor.fetchall()
        conn.close()

        utilisateurs = []
        for row in rows:
            historique = row[6].split("|") if row[6] else []
            utilisateurs.append(
                Utilisateur(
                    numero_carte=row[0],
                    nom=row[1],
                    prenom=row[2],
                    email=row[3],
                    telephone=row[4],
                    statut=row[5],
                    historique=historique
                )
            )
        return utilisateurs

    @staticmethod
    def supprimer_db(numero_carte: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM utilisateurs WHERE numero_carte = ?", (numero_carte,))
        conn.commit()
        conn.close()
