DROP TABLE IF EXISTS benevol;
DROP TABLE IF EXISTS admin;

CREATE TABLE benevol (
    id INTEGER PRIMARY KEY,
    nom TEXT,
    prenom TEXT,
    sexe TEXT,
    email TEXT UNIQUE,
    adresse TEXT,
    motivation TEXT
);

CREATE TABLE admin (
    id INTEGER PRIMARY KEY,
    nom TEXT,
    prenom TEXT,
    email TEXT UNIQUE ,
    mot_de_passe_salt TEXT NON NULL,
    mot_de_passe_hash TEXT NON NULL,
    statut INTEGER NON NULL DEFAULT 1,
    token TEXT UNIQUE
);