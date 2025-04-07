class Benevol:
    def __init__(
        self, id, nom, prenom, sexe, email, adresse, motivation
    ):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.sexe = sexe
        self.email = email
        self.adresse = adresse
        self.motivation = motivation

    def asdictionary(self):
        return \
                {
                # "id": self.id,
                "nom": self.nom,
                "prenom": self.prenom,
                "sexe": self.sexe,
                "email": self.email,
                "adresse": self.adresse,
                "motivation": self.motivation,
                }