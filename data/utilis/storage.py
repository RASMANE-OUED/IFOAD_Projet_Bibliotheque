import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List

DB_PATH = Path("data/bibliotheque.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ========================
# Création / initialisation de la base
# ========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table livres
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livres (
            isbn TEXT PRIMARY KEY,
            titre TEXT,
            auteur TEXT,
            editeur TEXT,
            annee_publication INTEGER,
            categorie TEXT,
            nombre_pages INTEGER,
            disponible BOOLEAN,
            date_ajout TEXT
        )
    """)

    # Table utilisateurs
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

    # Table bibliothécaires
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bibliothecaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricule TEXT UNIQUE,
            nom TEXT,
            prenom TEXT,
            email TEXT,
            telephone TEXT,
            niveau_acces TEXT
        )
    """)

    # Table emprunts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emprunts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_utilisateur TEXT,
            id_livre TEXT,
            date_emprunt TEXT,
            date_retour_prevue TEXT,
            date_retour_effective TEXT,
            statut BOOLEAN,
            FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(numero_carte),
            FOREIGN KEY (id_livre) REFERENCES livres(isbn)
        )
    """)

    conn.commit()
    conn.close()


# ========================
# Classes
# ========================
class Personne:
    def __init__(self, nom: str, prenom: str, email: str, telephone: str = ""):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone


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
        self.disponibilite = disponibilite

    def save(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO livres
            (isbn, titre, auteur, editeur, annee_publication, categorie, nombre_pages, disponible, date_ajout)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.isbn, self.titre, self.auteur, self.editeur,
              self.annee_publication, self.categorie, self.nombre_pages,
              self.disponibilite, datetime.now().isoformat()))
        conn.commit()
        conn.close()


class Utilisateur(Personne):
    def __init__(self, numero_carte: str, nom: str, prenom: str, email: str,
                 telephone: str = "", statut: str = "ACTIF", historique: List[str] = None):
        super().__init__(nom, prenom, email, telephone)
        self.numero_carte = numero_carte
        self.statut = statut
        self.historique = historique if historique else []

    def save(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO utilisateurs
            (numero_carte, nom, prenom, email, telephone, statut, historique)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.numero_carte, self.nom, self.prenom, self.email,
              self.telephone, self.statut, ",".join(self.historique)))
        conn.commit()
        conn.close()


class Bibliothecaire(Personne):
    def __init__(self, matricule: str, nom: str, prenom: str, email: str,
                 telephone: str = "", niveau_acces: str = "standard"):
        super().__init__(nom, prenom, email, telephone)
        self.matricule = matricule
        self.niveau_acces = niveau_acces

    def save(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO bibliothecaires
            (matricule, nom, prenom, email, telephone, niveau_acces)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.matricule, self.nom, self.prenom, self.email,
              self.telephone, self.niveau_acces))
        conn.commit()
        conn.close()


class Emprunt:
    DUREE_STANDARD = 14  # jours

    def __init__(self, id_utilisateur: str, id_livre: str,
                 date_retour_prevue: datetime = None,
                 date_retour_effective: datetime = None,
                 statut: bool = True):
        self.id_utilisateur = id_utilisateur
        self.id_livre = id_livre
        self.date_retour_prevue = date_retour_prevue or (
            datetime.now().replace(microsecond=0))
        self.date_retour_effective = date_retour_effective
        self.statut = statut

    def save(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emprunts
            (id_utilisateur, id_livre, date_emprunt, date_retour_prevue, date_retour_effective, statut)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.id_utilisateur, self.id_livre, datetime.now().isoformat(),
              self.date_retour_prevue.isoformat(),
              self.date_retour_effective.isoformat() if self.date_retour_effective else None,
              self.statut))
        conn.commit()
        conn.close()


# ========================
# Exemple d’utilisation
# ========================
if __name__ == "__main__":
    init_db()

    # Ajouter un livre
    livre1 = Livre("978-1234567890", "Python pour débutants", "Alice Dupont",
                   "OpenAI Press", 2024, "Programmation", 300, True)
    livre1.save()

    # Ajouter un utilisateur
    user1 = Utilisateur("U001", "Dupont", "Jean", "jean.dupont@example.com")
    user1.save()

    # Ajouter un bibliothécaire
    biblio = Bibliothecaire("B001", "Martin", "Claire", "claire.martin@example.com")
    biblio.save()

    # Ajouter un emprunt
    emprunt1 = Emprunt("U001", "978-1234567890")
    emprunt1.save()

    print("Données insérées avec succès dans SQLite.")
