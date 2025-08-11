from pathlib import Path
from classes.Personne import Personne
from classes.Livre import Livre
from classes.Utilisateur import Utilisateur
from classes.Bibliothecaire import Bibliothecaire
from classes.Bibliotheque import Bibliotheque
from classes.Catalogue import Catalogue
from classes.Emprunt import Emprunt

Path("data").mkdir(exist_ok=True)

Catalogue.creer_table()
Livre.creer_table()
Utilisateur.creer_table()
Emprunt.creer_table()


def main():
    # Création de la bibliothèque (connexion à SQLite et chargement des données)
    biblio = Bibliotheque(nom="Bibliothèque Centrale", adresse="Ouagadougou")

    # Création d’un bibliothécaire et ajout si inexistant
    matricule_admin = "BIB001"
    if matricule_admin not in biblio.bibliothecaires:
        admin = Bibliothecaire(id=1, matricule=matricule_admin, nom="Kaboré", prenom="Awa", email="awa.kabore@biblio.bf")
        biblio.bibliothecaires[matricule_admin] = admin
        biblio.sauvegarder_bibliothecaire(admin)

    # Ajout d’un livre d’exemple (si absent)
    isbn_exemple = "9781234567890"
    if isbn_exemple not in biblio.catalogue.livres:
        livre1 = Livre(
            isbn=isbn_exemple,
            titre="Python pour les nuls",
            auteur="John Doe",
            editeur="Eyrolles",
            annee_publication=2022,
            categorie="Informatique",
            nombre_pages=320
        )
        biblio.ajouter_livre(livre1)

    # Ajout d’un utilisateur d’exemple (si absent)
    numero_carte_user = "U001"
    if numero_carte_user not in biblio.utilisateurs:
        user = Utilisateur(numero_carte=numero_carte_user, nom="Sawadogo", prenom="Delwende", email="delwende@etu.bf")
        biblio.inscrire_utilisateur(user)

    # Faire un emprunt
    id_emprunt = biblio.emprunter_livre(numero_carte=numero_carte_user, isbn=isbn_exemple)
    print("Emprunt effectué :", biblio.emprunts.get(id_emprunt))

    # Retour du livre
    if id_emprunt is not None:
        retour_ok = biblio.retourner_livre(id_emprunt)
        print("Retour effectué :", retour_ok)
        print("État emprunt :", biblio.emprunts.get(id_emprunt))

    # Générer un rapport simple
    rapport = biblio.generer_rapport()
    print("Rapport de la bibliothèque :", rapport)

    # Fermer la connexion à la base avant de quitter
    biblio.fermer_connexion()

if __name__ == "__main__":
    main()
