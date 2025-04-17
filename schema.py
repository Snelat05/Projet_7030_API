inserer_benevol_schema = {
    "type": "object",
    "required": ["nom", "prenom", "sexe", "email", "adresse", "motivation"],
    "properties": {
        "nom": {"type": "string"},
        "prenom": {"type": "string"},
        "sexe": {"type": "string"},
        "email": {"type": "string"},
        "adresse": {"type": "string"},
        "motivation": {"type": "string"},
    },
    "additionalProperties": False,
}

modifier_benevol_schema = {
    "type": "object",
    "properties": {
        "nom": {"type": "string"},
        "prenom": {"type": "string"},
        "sexe": {"type": "string"},
        "email": {"type": "string"},
        "adresse": {"type": "string"},
        "motivation": {"type": "string"},
    },
    "additionalProperties": False,
}
