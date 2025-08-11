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
    biblio = Bibliotheque(nom="Bibliothèque Centrale", adresse="Ouagadougou")

    admin = Bibliothecaire(id=1, matricule="BIB001", nom="Kaboré", prenom="Awa", email="awa.kabore@biblio.bf")
    biblio.bibliothecaires[admin.matricule] = admin

    livre1 = Livre(
        isbn="9781234567890",
        titre="Python pour les nuls",
        auteur="John Doe",
        editeur="Eyrolles",
        annee_publication=2022,
        categorie="Informatique",
        nombre_pages=320
    )
    admin.ajouter_livre(biblio.catalogue, livre1)

    livres_data = [
        ("9780000000001", "Python pour data-scientists",      "A. Traoré",   "ENI",        2021, "Informatique", 410),
        ("9780000000002", "Apprendre Julia en 7 jours",       "B. Ouédraogo","Eyrolles",   2023, "Informatique", 180),
        # autres livres ici...
    ]

    for isbn, titre, auteur, editeur, annee, categorie, pages in livres_data:
        livre = Livre(isbn, titre, auteur, editeur, annee, categorie, pages)
        admin.ajouter_livre(biblio.catalogue, livre)

    user = Utilisateur(numero_carte="U001", nom="Sawadogo", prenom="Delwende", email="delwende@etu.bf")
    biblio.inscrire_utilisateur(user)

    utilisateurs_data = [
        ("U002", "Ilboudo",  "Mariam",  "mariam@etu.bf"),
        # autres utilisateurs ici...
    ]

    for numero_carte, nom, prenom, email in utilisateurs_data:
        u = Utilisateur(numero_carte=numero_carte, nom=nom, prenom=prenom, email=email)
        biblio.inscrire_utilisateur(u)

    id_emprunt = biblio.emprunter_livre(numero_carte="U001", isbn="9781234567890")
    print("Emprunt effectué:", biblio.emprunts.get(id_emprunt))

    if id_emprunt is not None:
        retour_ok = biblio.retourner_livre(id_emprunt=id_emprunt)
        print("Livre retourné:", retour_ok)
        print("État emprunt:", biblio.emprunts.get(id_emprunt))

    rapport = biblio.generer_rapport()
    print("Rapport:", rapport)

    print(f"Catalogue : {len(biblio.catalogue.livres)} livres")
    print(f"Utilisateurs : {len(biblio.utilisateurs)} inscrits")

if __name__ == "__main__":
    main()
