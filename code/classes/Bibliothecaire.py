from classes.Personne import Personne

class Bibliothecaire(Personne):
    def __init__(self, id: int, matricule: str, nom: str, prenom: str,
                 email: str, telephone: str = "", niveau_acces: str = "standard"):
        super().__init__(nom, prenom, email, telephone)
        self.id = id
        self.matricule = matricule
        self.niveau_acces = niveau_acces

    def ajouter_livre(self, catalogue, livre) -> bool:
        return catalogue.ajouter_livre(livre)

    def supprimer_livre(self, catalogue, isbn: str) -> bool:
        return catalogue.supprimer_livre(isbn)

    def gerer_emprunt(self, emprunt) -> bool:
        return emprunt.finaliser_retour()

    def __repr__(self):
        return (f"Bibliothecaire(id={self.id}, matricule='{self.matricule}', "
                f"nom='{self.nom}', prenom='{self.prenom}', email='{self.email}', "
                f"telephone='{self.telephone}', niveau_acces='{self.niveau_acces}')")
