class Catalogue:
    def __init__(self):
        self.livres = {}  # clé = ISBN, valeur = Livre

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
