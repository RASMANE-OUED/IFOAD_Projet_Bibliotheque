from datetime import datetime, timedelta

class Emprunt:
    DUREE_STANDARD = 14  # jours

    def __init__(self, id: int, id_utilisateur: str, id_livre: str,
                 date_retour_prevue: datetime = None,
                 date_retour_effective: datetime = None,
                 statut: bool = True):
        self.id = id
        self.id_utilisateur = id_utilisateur
        self.id_livre = id_livre
        self.date_emprunt = datetime.now()
        self.date_retour_prevue = date_retour_prevue or self.date_emprunt.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=self.DUREE_STANDARD)
        self.date_retour_effective = date_retour_effective
        self.statut = statut  # True = EN COURS, False = TERMINÉ

    def finaliser_retour(self):
        self.date_retour_effective = datetime.now()
        self.statut = False

    def est_en_retard(self) -> bool:
        if not self.date_retour_effective:
            return datetime.now() > self.date_retour_prevue
        return self.date_retour_effective > self.date_retour_prevue

    def __repr__(self):
        return (f"Emprunt(id={self.id}, id_utilisateur={self.id_utilisateur}, id_livre={self.id_livre}, "
                f"date_emprunt={self.date_emprunt.strftime('%Y-%m-%d')}, "
                f"date_retour_prevue={self.date_retour_prevue.strftime('%Y-%m-%d')}, "
                f"date_retour_effective={self.date_retour_effective.strftime('%Y-%m-%d') if self.date_retour_effective else 'Non retourné'}, "
                f"statut={'EN COURS' if self.statut else 'TERMINÉ'})")
