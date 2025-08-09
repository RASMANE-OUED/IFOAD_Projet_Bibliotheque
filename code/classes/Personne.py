from datetime import datetime

class Personne:
    def __init__(self, nom: str, prenom: str, email: str, telephone: str = ""):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self.date_creation = datetime.now()

    def get_info(self) -> str:
        return f"{self.prenom} {self.nom} ({self.email})"

    def valider_email(self) -> bool:
        return "@" in self.email and "." in self.email
