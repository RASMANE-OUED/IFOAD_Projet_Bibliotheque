from datetime import datetime, timedelta
from typing import List, Optional
from classes.Catalogue import Catalogue
from classes.Emprunt import Emprunt

class Bibliotheque:
    def __init__(self, nom: str, adresse: str):
        self.nom = nom
        self.adresse = adresse
        self.catalogue = Catalogue()
        self.utilisateurs = {}      # clé = numero_carte (str)
        self.bibliothecaires = {}   # clé = matricule (str)
        self.emprunts = {}          # clé = id emprunt (int)
        self.config = {
            "max_emprunts": 5,
            "duree_emprunt": 14,
            "periode_grace": 2
        }

    # --- CRUD Livres ---
    def ajouter_livre(self, livre) -> bool:
        return self.catalogue.ajouter_livre(livre)

    def modifier_livre(self, isbn: str, **modifications) -> bool:
        livre = self.catalogue.livres.get(isbn)
        if not livre:
            return False
        for attr, val in modifications.items():
            if hasattr(livre, attr):
                setattr(livre, attr, val)
        return True

    def supprimer_livre(self, isbn: str) -> bool:
        emprunts_actifs = [e for e in self.emprunts.values() if e.id_livre == isbn and e.statut]
        if emprunts_actifs:
            return False
        return self.catalogue.supprimer_livre(isbn)

    def lister_livres(self) -> List:
        return list(self.catalogue.livres.values())

    # --- CRUD Utilisateurs ---
    def inscrire_utilisateur(self, utilisateur) -> bool:
        if utilisateur.numero_carte in self.utilisateurs:
            return False
        self.utilisateurs[utilisateur.numero_carte] = utilisateur
        return True

    def modifier_utilisateur(self, numero_carte: str, **modifications) -> bool:
        utilisateur = self.utilisateurs.get(numero_carte)
        if not utilisateur:
            return False
        for attr, val in modifications.items():
            if hasattr(utilisateur, attr):
                setattr(utilisateur, attr, val)
        return True

    def supprimer_utilisateur(self, numero_carte: str) -> bool:
        emprunts_actifs = [e for e in self.emprunts.values() if e.id_utilisateur == numero_carte and e.statut]
        if emprunts_actifs:
            return False
        if numero_carte in self.utilisateurs:
            del self.utilisateurs[numero_carte]
            return True
        return False

    def lister_utilisateurs(self) -> List:
        return list(self.utilisateurs.values())

    # --- Emprunts / Retours ---
    def emprunter_livre(self, numero_carte: str, isbn: str) -> Optional[int]:
        utilisateur = self.utilisateurs.get(numero_carte)
        livre = self.catalogue.livres.get(isbn)
        if not utilisateur or not livre:
            return None
        if not livre.est_disponible():
            return None
        emprunts_actifs = [e for e in self.emprunts.values() if e.id_utilisateur == numero_carte and e.statut]
        if len(emprunts_actifs) >= self.config["max_emprunts"]:
            return None
        if utilisateur.statut != "ACTIF":
            return None

        id_emprunt = len(self.emprunts) + 1
        date_retour_prevue = datetime.now() + timedelta(days=self.config["duree_emprunt"])
        emprunt = Emprunt(
            id=id_emprunt,
            id_utilisateur=numero_carte,
            id_livre=isbn,
            date_retour_prevue=date_retour_prevue,
            statut=True
        )
        self.emprunts[id_emprunt] = emprunt
        livre.marquer_emprunte()

        utilisateur.emprunts_actifs.append(emprunt)
        utilisateur.historique.append(f"Emprunt: {livre.titre} ({datetime.now().strftime('%Y-%m-%d')})")

        return id_emprunt

    def retourner_livre(self, id_emprunt: int) -> bool:
        emprunt = self.emprunts.get(id_emprunt)
        if not emprunt or emprunt.statut is False:
            return False
        emprunt.finaliser_retour()

        livre = self.catalogue.livres.get(emprunt.id_livre)
        if livre:
            livre.marquer_disponible()

        utilisateur = self.utilisateurs.get(emprunt.id_utilisateur)
        if utilisateur:
            utilisateur.emprunts_actifs = [e for e in utilisateur.emprunts_actifs if e.id != id_emprunt]
            utilisateur.historique.append(f"Retour: {livre.titre} ({datetime.now().strftime('%Y-%m-%d')})")

        return True

    # --- Recherches multi-critères ---
    def rechercher_livres(self, titre: Optional[str] = None, auteur: Optional[str] = None,
                          categorie: Optional[str] = None, disponibilite: Optional[bool] = None) -> List:
        resultats = list(self.catalogue.livres.values())
        if titre:
            resultats = [l for l in resultats if titre.lower() in l.titre.lower()]
        if auteur:
            resultats = [l for l in resultats if auteur.lower() in l.auteur.lower()]
        if categorie:
            resultats = [l for l in resultats if categorie.lower() == l.categorie.lower()]
        if disponibilite is not None:
            resultats = [l for l in resultats if l.est_disponible() == disponibilite]
        return resultats

    def rechercher_utilisateurs(self, nom: Optional[str] = None, email: Optional[str] = None,
                                statut: Optional[str] = None) -> List:
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

    # --- Gestion des retards et amendes ---
    def emprunts_en_retard(self) -> List[Emprunt]:
        maintenant = datetime.now()
        return [e for e in self.emprunts.values() if e.statut and e.date_retour_prevue < maintenant]

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
        retard = any(e for e in self.emprunts.values() if e.id_utilisateur == numero_carte and e.est_en_retard() and e.statut)
        if retard:
            utilisateur.statut = "BLOQUÉ"
            return True
        else:
            utilisateur.statut = "ACTIF"
            return False

    # --- Méthode ajoutée corrigée : generer_rapport ---
    def generer_rapport(self) -> dict:
        return {
            "total_livres": len(self.catalogue.livres),
            "total_utilisateurs": len(self.utilisateurs),
            "total_emprunts": len(self.emprunts),
            "livres_disponibles": len(self.catalogue.lister_livres_disponibles())
        }
