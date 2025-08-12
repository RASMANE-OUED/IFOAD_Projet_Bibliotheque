import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional

# Classes métiers minimales en interne
class Livre:
    def __init__(self, isbn, titre, auteur, editeur="Inconnu", annee_publication=2025, categorie="", nombre_pages=100):
        self.isbn = isbn
        self.titre = titre
        self.auteur = auteur
        self.editeur = editeur
        self.annee_publication = annee_publication
        self.categorie = categorie
        self.nombre_pages = nombre_pages
        self.disponible = True

    def est_disponible(self):
        return self.disponible

    def marquer_emprunte(self):
        self.disponible = False

    def marquer_disponible(self):
        self.disponible = True


class Utilisateur:
    def __init__(self, numero_carte, nom, prenom, email, statut="ACTIF"):
        self.numero_carte = numero_carte
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.statut = statut
        self.emprunts_actifs = []

    def est_bloque(self):
        return self.statut.upper() == "BLOQUÉ"


class Emprunt:
    def __init__(self, id, id_utilisateur, id_livre, date_emprunt, date_retour_prevue,
                 date_retour_effective=None, statut=True):
        self.id = id
        self.id_utilisateur = id_utilisateur
        self.id_livre = id_livre
        self.date_emprunt = date_emprunt
        self.date_retour_prevue = date_retour_prevue
        self.date_retour_effective = date_retour_effective
        self.statut = statut  # True = emprunt actif, False = retourné

    def est_en_retard(self):
        now = datetime.now()
        if self.statut and self.date_retour_prevue and now > self.date_retour_prevue:
            return True
        return False

    def finaliser_retour(self):
        self.date_retour_effective = datetime.now()
        self.statut = False


def hacher_mot_de_passe(mdp: str) -> str:
    return hashlib.sha256(mdp.encode()).hexdigest()


class Bibliotheque:
    def __init__(self, nom="Bibliothèque Centrale", adresse="Ouagadougou"):
        self.nom = nom
        self.adresse = adresse

        self.conn = sqlite3.connect("data/bibliotheque.db")
        self.conn.row_factory = sqlite3.Row

        # Dictionnaires pour stocker objets métier en mémoire
        self.catalogue = {}       # isbn -> Livre
        self.utilisateurs = {}    # numero_carte -> Utilisateur
        self.emprunts = {}        # id emprunt -> Emprunt

        # Configuration
        self.config = {
            "max_emprunts": 5,
            "duree_emprunt": 14,  # jours
            "amende_par_jour": 0.5,
        }

        # Comptes utilisateurs pour connexion (username -> mot de passe hashé)
        # Synchronisé avec la table SQLite "comptes"
        self.comptes = {}

        self.next_emprunt_id = 1

        self.creer_tables()
        self.charger_donnees()

    def creer_tables(self):
        cursor = self.conn.cursor()

        # Table comptes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comptes (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)

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
                disponible INTEGER
            )
        """)

        # Table utilisateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                numero_carte TEXT PRIMARY KEY,
                nom TEXT,
                prenom TEXT,
                email TEXT,
                statut TEXT
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
                statut INTEGER,
                FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(numero_carte),
                FOREIGN KEY (id_livre) REFERENCES livres(isbn)
            )
        """)

        # Insérer admin par défaut si inexistant
        cursor.execute("SELECT COUNT(*) as count FROM comptes WHERE username = ?", ("admin",))
        if cursor.fetchone()["count"] == 0:
            mdp_hash = hacher_mot_de_passe("1234")
            cursor.execute("INSERT INTO comptes (username, password_hash) VALUES (?, ?)", ("admin", mdp_hash))

        self.conn.commit()

    def charger_donnees(self):
        cursor = self.conn.cursor()

        # Charger livres
        cursor.execute("SELECT * FROM livres")
        for row in cursor.fetchall():
            livre = Livre(
                isbn=row["isbn"],
                titre=row["titre"],
                auteur=row["auteur"],
                editeur=row["editeur"],
                annee_publication=row["annee_publication"],
                categorie=row["categorie"],
                nombre_pages=row["nombre_pages"]
            )
            livre.disponible = bool(row["disponible"])
            self.catalogue[livre.isbn] = livre

        # Charger utilisateurs
        cursor.execute("SELECT * FROM utilisateurs")
        for row in cursor.fetchall():
            user = Utilisateur(
                numero_carte=row["numero_carte"],
                nom=row["nom"],
                prenom=row["prenom"],
                email=row["email"],
                statut=row["statut"]
            )
            self.utilisateurs[user.numero_carte] = user

        # Charger emprunts
        cursor.execute("SELECT * FROM emprunts")
        max_id = 0
        for row in cursor.fetchall():
            emprunt = Emprunt(
                id=row["id"],
                id_utilisateur=row["id_utilisateur"],
                id_livre=row["id_livre"],
                date_emprunt=datetime.fromisoformat(row["date_emprunt"]),
                date_retour_prevue=datetime.fromisoformat(row["date_retour_prevue"]),
                date_retour_effective=datetime.fromisoformat(row["date_retour_effective"]) if row["date_retour_effective"] else None,
                statut=bool(row["statut"])
            )
            self.emprunts[emprunt.id] = emprunt
            if emprunt.id > max_id:
                max_id = emprunt.id
            # Associe emprunt aux utilisateur et livre
            if emprunt.id_utilisateur in self.utilisateurs:
                if emprunt.statut:
                    self.utilisateurs[emprunt.id_utilisateur].emprunts_actifs.append(emprunt)
            if emprunt.id_livre in self.catalogue:
                self.catalogue[emprunt.id_livre].disponible = not emprunt.statut
        self.next_emprunt_id = max_id + 1

        # Charger comptes
        cursor.execute("SELECT * FROM comptes")
        for row in cursor.fetchall():
            self.comptes[row["username"]] = row["password_hash"]

    # --- Méthodes comptes ---
    def verifier_identifiants(self, username: str, mot_de_passe: str) -> bool:
        mdp_hash = hacher_mot_de_passe(mot_de_passe)
        return username in self.comptes and self.comptes[username] == mdp_hash

    def changer_mot_de_passe(self, username: str, nouveau_mdp: str) -> bool:
        if username not in self.comptes:
            return False
        mdp_hash = hacher_mot_de_passe(nouveau_mdp)
        cursor = self.conn.cursor()
        cursor.execute("UPDATE comptes SET password_hash = ? WHERE username = ?", (mdp_hash, username))
        self.conn.commit()
        self.comptes[username] = mdp_hash
        return True

    # --- Livres ---
    def ajouter_livre(self, livre: Livre) -> bool:
        if livre.isbn in self.catalogue:
            return False
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO livres (isbn, titre, auteur, editeur, annee_publication, categorie, nombre_pages, disponible)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (livre.isbn, livre.titre, livre.auteur, livre.editeur, livre.annee_publication,
              livre.categorie, livre.nombre_pages, 1))
        self.conn.commit()
        self.catalogue[livre.isbn] = livre
        return True

    def modifier_livre(self, old_isbn: str, nouveau_livre: Livre) -> bool:
        if old_isbn not in self.catalogue:
            return False
        if old_isbn != nouveau_livre.isbn and nouveau_livre.isbn in self.catalogue:
            return False
        cursor = self.conn.cursor()
        if old_isbn != nouveau_livre.isbn:
            cursor.execute("DELETE FROM livres WHERE isbn = ?", (old_isbn,))
        cursor.execute("""
            INSERT OR REPLACE INTO livres (isbn, titre, auteur, editeur, annee_publication, categorie, nombre_pages, disponible)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nouveau_livre.isbn, nouveau_livre.titre, nouveau_livre.auteur, nouveau_livre.editeur,
              nouveau_livre.annee_publication, nouveau_livre.categorie, nouveau_livre.nombre_pages,
              int(nouveau_livre.est_disponible())))
        self.conn.commit()
        if old_isbn != nouveau_livre.isbn:
            del self.catalogue[old_isbn]
        self.catalogue[nouveau_livre.isbn] = nouveau_livre
        return True

    def supprimer_livre(self, isbn: str) -> bool:
        if isbn not in self.catalogue:
            return False
        # vérifier emprunts actifs bloquants
        for e in self.emprunts.values():
            if e.id_livre == isbn and e.statut:
                return False
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM livres WHERE isbn = ?", (isbn,))
        self.conn.commit()
        del self.catalogue[isbn]
        return True

    # --- Utilisateurs ---
    def inscrire_utilisateur(self, utilisateur: Utilisateur) -> bool:
        if utilisateur.numero_carte in self.utilisateurs:
            return False
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO utilisateurs (numero_carte, nom, prenom, email, statut)
            VALUES (?, ?, ?, ?, ?)
        """, (utilisateur.numero_carte, utilisateur.nom, utilisateur.prenom, utilisateur.email, utilisateur.statut))
        self.conn.commit()
        self.utilisateurs[utilisateur.numero_carte] = utilisateur
        return True

    def modifier_utilisateur(self, old_numero: str, user_modifie: Utilisateur) -> bool:
        if old_numero not in self.utilisateurs:
            return False
        if old_numero != user_modifie.numero_carte and user_modifie.numero_carte in self.utilisateurs:
            return False
        cursor = self.conn.cursor()
        if old_numero != user_modifie.numero_carte:
            cursor.execute("DELETE FROM utilisateurs WHERE numero_carte = ?", (old_numero,))
        cursor.execute("""
            INSERT OR REPLACE INTO utilisateurs (numero_carte, nom, prenom, email, statut)
            VALUES (?, ?, ?, ?, ?)
        """, (user_modifie.numero_carte, user_modifie.nom, user_modifie.prenom, user_modifie.email, user_modifie.statut))
        self.conn.commit()
        if old_numero != user_modifie.numero_carte:
            del self.utilisateurs[old_numero]
        self.utilisateurs[user_modifie.numero_carte] = user_modifie
        return True

    def supprimer_utilisateur(self, numero_carte: str) -> bool:
        # vérifier emprunts actifs
        for e in self.emprunts.values():
            if e.id_utilisateur == numero_carte and e.statut:
                return False
        if numero_carte not in self.utilisateurs:
            return False
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM utilisateurs WHERE numero_carte = ?", (numero_carte,))
        self.conn.commit()
        del self.utilisateurs[numero_carte]
        return True

    # --- Emprunts ---
    def emprunter_livre(self, numero_carte: str, isbn: str) -> Optional[int]:
        user = self.utilisateurs.get(numero_carte)
        livre = self.catalogue.get(isbn)
        if not user or not livre or not livre.est_disponible():
            return None
        emprunts_actifs = [e for e in self.emprunts.values() if e.id_utilisateur == numero_carte and e.statut]
        if len(emprunts_actifs) >= self.config["max_emprunts"]:
            return None
        if user.statut != "ACTIF":
            return None

        date_emprunt = datetime.now()
        date_retour_prevue = date_emprunt + timedelta(days=self.config["duree_emprunt"])
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO emprunts (id_utilisateur, id_livre, date_emprunt, date_retour_prevue, date_retour_effective, statut)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (numero_carte, isbn, date_emprunt.isoformat(), date_retour_prevue.isoformat(), None, 1))
        self.conn.commit()
        id_emprunt = cursor.lastrowid

        emprunt = Emprunt(
            id=id_emprunt,
            id_utilisateur=numero_carte,
            id_livre=isbn,
            date_emprunt=date_emprunt,
            date_retour_prevue=date_retour_prevue,
            statut=True
        )
        self.emprunts[id_emprunt] = emprunt

        livre.marquer_emprunte()
        user.emprunts_actifs.append(emprunt)
        return id_emprunt

    def retourner_livre(self, id_emprunt: int) -> bool:
        emprunt = self.emprunts.get(id_emprunt)
        if not emprunt or not emprunt.statut:
            return False
        emprunt.finaliser_retour()
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE emprunts SET date_retour_effective = ?, statut = ?
            WHERE id = ?
        """, (emprunt.date_retour_effective.isoformat(), 0, id_emprunt))
        self.conn.commit()

        livre = self.catalogue.get(emprunt.id_livre)
        utilisateur = self.utilisateurs.get(emprunt.id_utilisateur)
        if livre:
            livre.marquer_disponible()
        if utilisateur:
            utilisateur.emprunts_actifs = [e for e in utilisateur.emprunts_actifs if e.id != id_emprunt]
        emprunt.statut = False
        return True

    # --- Statistiques ---
    def generer_rapport(self):
        return {
            "total_livres": len(self.catalogue),
            "total_utilisateurs": len(self.utilisateurs),
            "total_emprunts": len(self.emprunts),
            "livres_disponibles": len([l for l in self.catalogue.values() if l.est_disponible()]),
        }

    def emprunts_en_retard(self):
        return [e for e in self.emprunts.values() if e.est_en_retard()]

    def calculer_amende(self, id_emprunt: int) -> float:
        emprunt = self.emprunts.get(id_emprunt)
        if emprunt is None or not emprunt.est_en_retard():
            return 0.0
        date_retour = emprunt.date_retour_effective or datetime.now()
        jours_retard = (date_retour.date() - emprunt.date_retour_prevue.date()).days
        return max(0, jours_retard) * self.config["amende_par_jour"]
