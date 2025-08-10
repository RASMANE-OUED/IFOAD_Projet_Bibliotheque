import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path("data/bibliotheque.db")

class Emprunt:
    DUREE_STANDARD = 14  # jours

    def __init__(self, id: int, id_utilisateur: str, id_livre: str,
                 date_emprunt: datetime = None,
                 date_retour_prevue: datetime = None,
                 date_retour_effective: datetime = None,
                 statut: bool = True):
        self.id = id
        self.id_utilisateur = id_utilisateur
        self.id_livre = id_livre
        self.date_emprunt = date_emprunt or datetime.now()
        self.date_retour_prevue = date_retour_prevue or self.date_emprunt.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=self.DUREE_STANDARD)
        self.date_retour_effective = date_retour_effective
        self.statut = statut  # True = EN COURS, False = TERMINÉ

    def finaliser_retour(self):
        self.date_retour_effective = datetime.now()
        self.statut = False
        self.mettre_a_jour_db()

    def est_en_retard(self) -> bool:
        if not self.date_retour_effective:
            return datetime.now() > self.date_retour_prevue
        return self.date_retour_effective > self.date_retour_prevue

    def __repr__(self):
        return (f"Emprunt(id={self.id}, id_utilisateur={self.id_utilisateur}, id_livre={self.id_livre}, "
                f"date_emprunt={self.date_emprunt.strftime('%Y-%m-%d')}, "
                f"date_retour_prevue={self.date_retour_prevue.strftime('%Y-%m-%d')}, "
                f"date_retour_effective={self.date_retour_effective.strftime('%Y-%m-%d') if self.date_retour_effective else 'Non retourné'}, "
                f"statut={'EN COURS' if self.statut else 'TERMINÉ'})")

    # ------------------------
    #   PERSISTANCE SQLITE
    # ------------------------

    @staticmethod
    def creer_table():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emprunts (
                id INTEGER PRIMARY KEY,
                id_utilisateur TEXT,
                id_livre TEXT,
                date_emprunt TEXT,
                date_retour_prevue TEXT,
                date_retour_effective TEXT,
                statut INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def sauvegarder_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO emprunts
            (id, id_utilisateur, id_livre, date_emprunt, date_retour_prevue, date_retour_effective, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.id,
            self.id_utilisateur,
            self.id_livre,
            self.date_emprunt.strftime("%Y-%m-%d %H:%M:%S"),
            self.date_retour_prevue.strftime("%Y-%m-%d %H:%M:%S"),
            self.date_retour_effective.strftime("%Y-%m-%d %H:%M:%S") if self.date_retour_effective else None,
            1 if self.statut else 0
        ))
        conn.commit()
        conn.close()

    def mettre_a_jour_db(self):
        self.sauvegarder_db()

    @staticmethod
    def charger_tous():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emprunts")
        rows = cursor.fetchall()
        conn.close()

        emprunts = []
        for row in rows:
            emprunts.append(
                Emprunt(
                    id=row[0],
                    id_utilisateur=row[1],
                    id_livre=row[2],
                    date_emprunt=datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S"),
                    date_retour_prevue=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S"),
                    date_retour_effective=datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S") if row[5] else None,
                    statut=bool(row[6])
                )
            )
        return emprunts

    @staticmethod
    def supprimer_db(emprunt_id: int):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emprunts WHERE id = ?", (emprunt_id,))
        conn.commit()
        conn.close()

