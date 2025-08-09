class Bibliotheque:
    def __init__(self, nom: str, adresse: str):
        self.nom = nom
        self.adresse = adresse
        self.catalogue = Catalogue()
        self.utilisateurs = {}      # clé = numéro carte
        self.bibliothecaires = {}   # clé = matricule
        self.emprunts = {}          # clé = id emprunt
        self.config = {
            "max_emprunts": 5,
            "duree_emprunt": 14,
            "periode_grace": 2
        }

    def inscrire_utilisateur(self, utilisateur) -> bool:
        if utilisateur.numero_carte in self.utilisateurs:
            return False
        self.utilisateurs[utilisateur.numero_carte] = utilisateur
        return True

    def authentifier_bibliothecaire(self, matricule: str):
        return self.bibliothecaires.get(matricule)

    def traiter_emprunt(self, user_id: str, isbn: str):
        utilisateur = self.utilisateurs.get(user_id)
        livre = self.catalogue.livres.get(isbn)
        if not utilisateur or not livre or not livre.est_disponible():
            return None
        emprunt = Emprunt(id=len(self.emprunts)+1, id_utilisateur=user_id,
                          id_livre=isbn, date_retour_prevue=datetime.now() + timedelta(days=self.config["duree_emprunt"]),
                          date_retour_effective=None, statut=True)
        self.emprunts[emprunt.id] = emprunt
        livre.marquer_emprunte()
        return emprunt

    def traiter_retour(self, emprunt_id: int) -> bool:
        emprunt = self.emprunts.get(emprunt_id)
        if not emprunt or not emprunt.statut:
            return False
        emprunt.finaliser_retour()
        return True

    def generer_rapport(self) -> dict:
        return {
            "total_livres": len(self.catalogue.livres),
            "total_utilisateurs": len(self.utilisateurs),
            "total_emprunts": len(self.emprunts),
            "livres_disponibles": len(self.catalogue.lister_livres_disponibles())
        }

    def sauvegarder_donnees(self) -> bool:
        # À implémenter : export JSON ou CSV
        return True

    def charger_donnees(self) -> bool:
        # À implémenter : import JSON ou CSV
        return True

