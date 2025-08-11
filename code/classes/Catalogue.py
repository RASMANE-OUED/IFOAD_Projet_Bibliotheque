import sqlite3
from pathlib import Path
from datetime import datetime
from classes.Livre import Livre

DB_PATH = Path("data/bibliotheque.db")

class Catalogue:
    def __init__(self):
        self.livres = {}  # clé = ISBN, valeur = Livre
        self._index_recherche=None

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

        Catalogue.creer_table() 
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
               SELECT isbn, titre, auteur, editeur,
             annee_publication, categorie, nombre_pages, disponible
             FROM catalogue
                 """)

        rows = cursor.fetchall()
        conn.close()
        return [
                Livre(isbn=row[0], titre=row[1], auteur=row[2],
                       editeur=row[3], annee_publication=row[4],
                       categorie=row[5], nombre_pages=row[6], disponible=bool(row[7]))
            for row in rows
        ]
    def build_index(self):
        """Crée un index pour des recherches rapides"""
        self._index_recherche = {
            'titres': {},
            'auteurs': {},
            'categories': {}
        }
        
        for isbn, livre in self.livres.items():
            # Index par mots-clés du titre
            for mot in livre.titre.lower().split():
                if mot not in self._index_recherche['titres']:
                    self._index_recherche['titres'][mot] = []
                self._index_recherche['titres'][mot].append(isbn)
            
            # Index par auteur
            if livre.auteur not in self._index_recherche['auteurs']:
                self._index_recherche['auteurs'][livre.auteur] = []
            self._index_recherche['auteurs'][livre.auteur].append(isbn)
    
    def rechercher_avance(self, terme: str) -> list[Livre]:
        """Recherche avec index"""
        if not self._index_recherche:
            self.build_index()
        
        terme = terme.lower()
        resultats = set()
        
        # Recherche dans les titres
        for mot, isbns in self._index_recherche['titres'].items():
            if terme in mot:
                resultats.update(isbns)
        
        # Recherche dans les auteurs
        for auteur, isbns in self._index_recherche['auteurs'].items():
            if terme in auteur.lower():
                resultats.update(isbns)
        
        return [self.livres[isbn] for isbn in resultats]

    @staticmethod
    def supprimer_livre_db(isbn: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT isbn, titre, auteur, editeur,
                  annee_publication, categorie, nombre_pages, disponible
                  FROM catalogue   """)
        conn.commit()
        conn.close()
