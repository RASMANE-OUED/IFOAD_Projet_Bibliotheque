class Utilisateur(Personne):
    def __init__(self, id: int, nom: str, prenom: str, email: str, telephone: int,
                 statut: str, historique: List[str], numero_carte: str):
        super().__init__(id, nom, prenom, email, telephone)
        self.statut = statut
        self.historique = historique
        self.numero_carte = numero_carte
        self.emprunts_actifs = []

    def emprunter_livre(self, livre: Livre) -> bool:
        if self.statut != "ACTIF" or len(self.emprunts_actifs) >= 5:
            return False
        if not livre.est_disponible():
            return False
        self.emprunts_actifs.append(livre)
        self.historique.append(f"Emprunt: {livre.titre}")
        livre.marquer_emprunte()
        return True

    def retourner_livre(self, livre: Livre) -> bool:
        if livre not in self.emprunts_actifs:
            return False
        self.emprunts_actifs.remove(livre)
        self.historique.append(f"Retour: {livre.titre}")
        livre.marquer_disponible()
        return True

    def consulter_emprunts(self) -> List[str]:
        return [livre.titre for livre in self.emprunts_actifs]