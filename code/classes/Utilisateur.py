from typing import List
from classes.Personne import Personne

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
        return True

    def retourner_livre(self, livre) -> bool:
        if livre not in self.emprunts_actifs:
            return False
        self.emprunts_actifs.remove(livre)
        self.historique.append(f"Retour: {livre.titre}")
        livre.marquer_disponible()
        return True

    def consulter_emprunts(self) -> List[str]:
        return [livre.titre for livre in self.emprunts_actifs]

    def __repr__(self):
        return (f"Utilisateur(numero_carte={self.numero_carte}, nom={self.nom}, "
                f"prenom={self.prenom}, email={self.email}, statut={self.statut})")
