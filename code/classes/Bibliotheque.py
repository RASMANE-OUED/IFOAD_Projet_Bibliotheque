import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from classes.Catalogue import Catalogue
from classes.Emprunt import Emprunt
from classes.Utilisateur import Utilisateur
from classes.Livre import Livre
from classes.Bibliothecaire import Bibliothecaire

import hashlib  # Import en haut de ton fichier

def hacher_mot_de_passe(mdp: str) -> str:
    """Retourne le hash SHA-256 du mot de passe."""
    return hashlib.sha256(mdp.encode()).hexdigest()








class Bibliotheque:
    def __init__(self, nom: str, adresse: str, db_path: str = "bibliotheque.db"):
        self.nom = nom
        self.adresse = adresse
        self.catalogue = Catalogue()
        self.utilisateurs = {}
        self.bibliothecaires = {}
        self.emprunts = {}
        self.db_path = db_path
        self.conn = None

        self.config = {
            "max_emprunts": 5,
            "duree_emprunt": 14,
            "periode_grace": 2,
        }

        self.connect_db()       # Connexion à la base SQLite
        self.creer_tables()     # Création des tables si elles n'existent pas
        self.charger_donnees()  # Chargement des données en mémoire

    def creer_tables(self):
        cursor = self.conn.cursor()





    def connect_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Accès aux colonnes par nom

    def creer_tables(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
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
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS utilisateurs (
                numero_carte TEXT PRIMARY KEY,
                nom TEXT,
                prenom TEXT,
                email TEXT,
                telephone TEXT,
                statut TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS emprunts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_carte TEXT,
                isbn TEXT,
                date_emprunt TEXT,
                date_retour_prevue TEXT,
                date_retour_effective TEXT,
                statut INTEGER,
                FOREIGN KEY(numero_carte) REFERENCES utilisateurs(numero_carte),
                FOREIGN KEY(isbn) REFERENCES livres(isbn)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bibliothecaires (
                id INTEGER PRIMARY KEY,
                matricule TEXT UNIQUE,
                nom TEXT,
                prenom TEXT,
                email TEXT,
                telephone TEXT,
                niveau_acces TEXT
            )
            """
        )

        self.conn.commit()

    def charger_donnees(self):
        cursor = self.conn.cursor()

        # Chargement livres
        cursor.execute("SELECT * FROM livres")
        for row in cursor.fetchall():
            livre = Livre(
                isbn=row["isbn"],
                titre=row["titre"],
                auteur=row["auteur"],
                editeur=row["editeur"],
                annee_publication=row["annee_publication"],
                categorie=row["categorie"],
                nombre_pages=row["nombre_pages"],
                disponibilite=bool(row["disponible"]),
            )
            self.catalogue.livres[livre.isbn] = livre

        # Chargement utilisateurs
        cursor.execute("SELECT * FROM utilisateurs")
        for row in cursor.fetchall():
            user = Utilisateur(
                numero_carte=row["numero_carte"],
                nom=row["nom"],
                prenom=row["prenom"],
                email=row["email"],
                telephone=row["telephone"],
                statut=row["statut"],
            )
            self.utilisateurs[user.numero_carte] = user

        # Chargement emprunts
        cursor.execute("SELECT * FROM emprunts")
        for row in cursor.fetchall():
            emprunt = Emprunt(
                id=row["id"],
                id_utilisateur=row["numero_carte"],
                id_livre=row["isbn"],
                date_emprunt=datetime.fromisoformat(row["date_emprunt"]) if row["date_emprunt"] else None,
                date_retour_prevue=datetime.fromisoformat(row["date_retour_prevue"]) if row["date_retour_prevue"] else None,
                date_retour_effective=datetime.fromisoformat(row["date_retour_effective"]) if row["date_retour_effective"] else None,
                statut=bool(row["statut"]),
            )
            self.emprunts[emprunt.id] = emprunt

            # Ajouter emprunt actif dans utilisateur
            if emprunt.statut and emprunt.id_utilisateur in self.utilisateurs:
                self.utilisateurs[emprunt.id_utilisateur].emprunts_actifs.append(emprunt)

        # Chargement bibliothécaires
        cursor.execute("SELECT * FROM bibliothecaires")
        for row in cursor.fetchall():
            bib = Bibliothecaire(
                id=row["id"],
                matricule=row["matricule"],
                nom=row["nom"],
                prenom=row["prenom"],
                email=row["email"],
                telephone=row["telephone"],
                niveau_acces=row["niveau_acces"],
            )
            self.bibliothecaires[bib.matricule] = bib

    # --- Méthodes de sauvegarde ---

    def sauvegarder_livre(self, livre: Livre):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO livres (isbn, titre, auteur, editeur, annee_publication,
                                          categorie, nombre_pages, disponible)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                livre.isbn,
                livre.titre,
                livre.auteur,
                livre.editeur,
                livre.annee_publication,
                livre.categorie,
                livre.nombre_pages,
                int(livre.disponible),
            ),
        )
        self.conn.commit()

    def sauvegarder_utilisateur(self, utilisateur: Utilisateur):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO utilisateurs (numero_carte, nom, prenom, email, telephone, statut)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                utilisateur.numero_carte,
                utilisateur.nom,
                utilisateur.prenom,
                utilisateur.email,
                utilisateur.telephone,
                utilisateur.statut,
            ),
        )
        self.conn.commit()

    def sauvegarder_emprunt(self, emprunt: Emprunt):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO emprunts (id, numero_carte, isbn, date_emprunt, date_retour_prevue,
                                           date_retour_effective, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                emprunt.id,
                emprunt.id_utilisateur,
                emprunt.id_livre,
                emprunt.date_emprunt.isoformat() if emprunt.date_emprunt else None,
                emprunt.date_retour_prevue.isoformat() if emprunt.date_retour_prevue else None,
                emprunt.date_retour_effective.isoformat() if emprunt.date_retour_effective else None,
                int(emprunt.statut),
            ),
        )
        self.conn.commit()

    # Table comptes pour gestion des utilisateurs applicatifs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comptes (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)

        # Insertion du compte admin par défaut si inexistant
        cursor.execute("SELECT COUNT(*) FROM comptes WHERE username = ?", ("admin",))
        if cursor.fetchone()[0] == 0:
            mdp_hash = hacher_mot_de_passe("1234")  # mot de passe par défaut admin
            cursor.execute("INSERT INTO comptes (username, password_hash) VALUES (?, ?)", ("admin", mdp_hash))

        self.conn.commit()





    def sauvegarder_bibliothecaire(self, bibliothecaire: Bibliothecaire):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO bibliothecaires (id, matricule, nom, prenom, email, telephone, niveau_acces)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                bibliothecaire.id,
                bibliothecaire.matricule,
                bibliothecaire.nom,
                bibliothecaire.prenom,
                bibliothecaire.email,
                bibliothecaire.telephone,
                bibliothecaire.niveau_acces,
            ),
        )
        self.conn.commit()

    # --- Méthodes métier et utilitaires ---

    def lister_livres(self) -> List[Livre]:
        return list(self.catalogue.livres.values())

    def lister_utilisateurs(self) -> List[Utilisateur]:
        return list(self.utilisateurs.values())

    def ajouter_livre(self, livre: Livre) -> bool:
        result = self.catalogue.ajouter_livre(livre)
        if result:
            self.sauvegarder_livre(livre)
        return result

    def inscrire_utilisateur(self, utilisateur: Utilisateur) -> bool:
        if utilisateur.numero_carte in self.utilisateurs:
            return False
        self.utilisateurs[utilisateur.numero_carte] = utilisateur
        self.sauvegarder_utilisateur(utilisateur)
        return True

    def modifier_utilisateur(self, numero_carte: str, **modifications) -> bool:
        utilisateur = self.utilisateurs.get(numero_carte)
        if not utilisateur:
            return False
        for attr, val in modifications.items():
            if hasattr(utilisateur, attr):
                setattr(utilisateur, attr, val)
        self.sauvegarder_utilisateur(utilisateur)
        return True

    def supprimer_utilisateur(self, numero_carte: str) -> bool:
        emprunts_actifs = [e for e in self.emprunts.values() if e.id_utilisateur == numero_carte and e.statut]
        if emprunts_actifs:
            return False
        if numero_carte in self.utilisateurs:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM utilisateurs WHERE numero_carte = ?", (numero_carte,))
            self.conn.commit()
            del self.utilisateurs[numero_carte]
            return True
        return False

    def emprunter_livre(self, numero_carte: str, isbn: str) -> Optional[int]:
        utilisateur = self.utilisateurs.get(numero_carte)
        livre = self.catalogue.livres.get(isbn)
        if not utilisateur or not livre or not livre.est_disponible():
            return None
        emprunts_actifs = [e for e in self.emprunts.values() if e.id_utilisateur == numero_carte and e.statut]
        if len(emprunts_actifs) >= self.config["max_emprunts"]:
            return None
        if utilisateur.statut != "ACTIF":
            return None

        id_emprunt = max(self.emprunts.keys(), default=0) + 1
        date_emprunt = datetime.now()
        date_retour_prevue = date_emprunt + timedelta(days=self.config["duree_emprunt"])
        emprunt = Emprunt(
            id=id_emprunt,
            id_utilisateur=numero_carte,
            id_livre=isbn,
            date_emprunt=date_emprunt,
            date_retour_prevue=date_retour_prevue,
            statut=True,
        )
        self.emprunts[id_emprunt] = emprunt

        livre.marquer_emprunte()
        self.sauvegarder_livre(livre)

        utilisateur.emprunts_actifs.append(emprunt)
        utilisateur.historique.append(f"Emprunt: {livre.titre} ({date_emprunt.strftime('%Y-%m-%d')})")
        self.sauvegarder_utilisateur(utilisateur)

        self.sauvegarder_emprunt(emprunt)

        return id_emprunt

    def refresh_emprunts(self):
        """Remplit le tableau des emprunts avec les données actuelles."""
    # 1. Vider le tableau
        for item in self.emprunts_tree.get_children():
            self.emprunts_tree.delete(item)

    # 2. Le remplir à nouveau
        for emprunt in self.biblio.emprunts.values():
            user  = self.biblio.utilisateurs.get(emprunt.id_utilisateur)
            livre = self.biblio.catalogue.livres.get(emprunt.id_livre)

            self.emprunts_tree.insert(
                "", tk.END,
               values=(
                emprunt.id,
                user.numero_carte  if user  else "Inconnu",
                livre.isbn         if livre else "Inconnu",
                emprunt.date_emprunt.strftime("%d/%m/%Y"),
                emprunt.date_retour_prevue.strftime("%d/%m/%Y"),
                emprunt.date_retour_effective.strftime("%d/%m/%Y") if emprunt.date_retour_effective else "",
                "En cours" if emprunt.statut else "Terminé"
            )
        )

    def retourner_livre(self, id_emprunt: int) -> bool:
        emprunt = self.emprunts.get(id_emprunt)
        if not emprunt or emprunt.statut is False:
            return False

        emprunt.finaliser_retour()
        self.sauvegarder_emprunt(emprunt)

        livre = self.catalogue.livres.get(emprunt.id_livre)
        if livre:
            livre.marquer_disponible()
            self.sauvegarder_livre(livre)

        utilisateur = self.utilisateurs.get(emprunt.id_utilisateur)
        if utilisateur:
            utilisateur.emprunts_actifs = [e for e in utilisateur.emprunts_actifs if e.id != id_emprunt]
            utilisateur.historique.append(f"Retour: {livre.titre} ({datetime.now().strftime('%Y-%m-%d')})")
            self.sauvegarder_utilisateur(utilisateur)

        return True

    def fermer_connexion(self):
        if self.conn:
            self.conn.close()

    # --- Recherche multi-critères ---

    def rechercher_livres(self, critere: str) -> List[Livre]:
        critere = critere.lower()
        return [
            livre for livre in self.catalogue.livres.values()
            if critere in livre.titre.lower() or critere in livre.auteur.lower() or critere in livre.isbn.lower()
        ]

    def rechercher_utilisateurs(self, nom: Optional[str] = None, email: Optional[str] = None,
                               statut: Optional[str] = None) -> List[Utilisateur]:
        resultats = list(self.utilisateurs.values())
        if nom:
            resultats = [u for u in resultats if nom.lower() in u.nom.lower() or nom.lower() in u.prenom.lower()]
        if email:
            resultats = [u for u in resultats if email.lower() == u.email.lower()]
        if statut:
            resultats = [u for u in resultats if u.statut == statut]
        return resultats

    # --- Historique des transactions ---

    def obtenir_historique_utilisateur(self, numero_carte: str) -> List[str]:
        utilisateur = self.utilisateurs.get(numero_carte)
        if utilisateur:
            return utilisateur.historique
        return []

    # --- Retards et amendes ---

    def emprunts_en_retard(self) -> List[Emprunt]:
        maintenant = datetime.now()
        return [
            e for e in self.emprunts.values()
            if e.statut and e.date_retour_prevue and e.date_retour_prevue < maintenant
        ]

    def calculer_amende(self, id_emprunt: int, tarif_jour: float = 0.5) -> float:
        emprunt = self.emprunts.get(id_emprunt)
        if not emprunt:
            return 0.0
        if not emprunt.est_en_retard():
            return 0.0
        date_retour = emprunt.date_retour_effective or datetime.now()
        jours_retard = (date_retour - emprunt.date_retour_prevue).days
        return max(0, jours_retard) * tarif_jour

    def bloquer_utilisateur_en_retard(self, numero_carte: str) -> bool:
        utilisateur = self.utilisateurs.get(numero_carte)
        if not utilisateur:
            return False
        retard = any(
            e for e in self.emprunts.values()
            if e.id_utilisateur == numero_carte and e.statut and e.est_en_retard()
        )
        if retard:
            utilisateur.statut = "BLOQUÉ"
            self.sauvegarder_utilisateur(utilisateur)
            return True
        else:
            utilisateur.statut = "ACTIF"
            self.sauvegarder_utilisateur(utilisateur)
            return False

    # --- Rapport simple ---

    def generer_rapport(self) -> Dict[str, int]:
        return {
            "total_livres": len(self.catalogue.livres),
            "total_utilisateurs": len(self.utilisateurs),
            "total_emprunts": len(self.emprunts),
            "livres_disponibles": len(self.catalogue.lister_livres_disponibles()),
        }
    

    # ... le reste de ta classe ...

    def verifier_identifiants(self, username: str, mot_de_passe: str) -> bool:
        mdp_hash = hacher_mot_de_passe(mot_de_passe)
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash FROM comptes WHERE username = ?", (username,))
        row = cursor.fetchone()
        return row is not None and row["password_hash"] == mdp_hash

    def changer_mot_de_passe(self, username: str, nouveau_mdp: str) -> bool:
        mdp_hash = hacher_mot_de_passe(nouveau_mdp)
        cursor = self.conn.cursor()
        cursor.execute("UPDATE comptes SET password_hash = ? WHERE username = ?", (mdp_hash, username))
        self.conn.commit()
        return cursor.rowcount > 0

