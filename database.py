import sqlite3
from benevol import Benevol


class Database:

    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect("db/db.db")
        return self.connection

    def deconnection(self):
        if self.connection is not None:
            self.connection.close()

    def save_benevol_api(self, benevol):
        connection = self.get_connection()
        connection.execute(
            "INSERT INTO "
            "benevol(nom, prenom, sexe, email, adresse, motivation) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                benevol.nom,
                benevol.prenom,
                benevol.sexe,
                benevol.email,
                benevol.adresse,
                benevol.motivation,
            ),
        )
        connection.commit()
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        benevol_id = cursor.fetchone()
        benevol.id = benevol_id[0]
        return benevol

    def get_benevols_api(self):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT id, nom,prenom,sexe,email,adresse, motivation FROM benevol"
        )
        benevols = cursor.fetchall()
        return [
            Benevol(
                benevol[0],
                benevol[1],
                benevol[2],
                benevol[3],
                benevol[4],
                benevol[5],
                benevol[6],
            )
            for benevol in benevols
        ]

    def get_benevol_byId(self, id):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT id, nom, prenom, sexe, email, adresse, "
            "motivation from benevol where id = ?",
            (id,),
        )
        benevol = cursor.fetchone()
        return Benevol(
            benevol[0],
            benevol[1],
            benevol[2],
            benevol[3],
            benevol[4],
            benevol[5],
            benevol[6],
        )

    def search_benevol(self, nom, prenom, page, per_page):

        connection = self.get_connection()
        cursor = connection.cursor()

        conditions = []
        valeurs = []

        if nom:
            conditions.append("LOWER(nom) LIKE ?")
            valeurs.append(f"%{nom.lower()}%")

        if prenom:
            conditions.append("LOWER(prenom) LIKE ?")
            valeurs.append(f"%{prenom.lower()}%")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        offset = (page - 1) * per_page
        sql = (
            "SELECT id, nom, prenom, sexe, email, adresse, motivation "
            "FROM benevol "
            f"{where_clause} "
            "ORDER BY id "
            "LIMIT ? OFFSET ?"
        )
        valeurs.extend([per_page, offset])

        cursor.execute(sql, valeurs)
        rows = cursor.fetchall()
        cursor.close()
        volontaires = []
        for row in rows:
            volontaires.append(
                {
                    "id": row[0],
                    "nom": row[1],
                    "prenom": row[2],
                    "sexe": row[3],
                    "email": row[4],
                    "adresse": row[5],
                    "motivation": row[6],
                }
            )

        return volontaires

    def get_total_volunteers_api(self, nom, prenom):
        """Retourne le total des volontaires inscrits."""

        connection = self.get_connection()
        cursor = connection.cursor()

        per_page = 5
        # Requête pour le total
        count_query = "SELECT COUNT(*) FROM benevol WHERE 1=1"
        count_params = []

        if nom:
            count_query += " AND nom LIKE ?"
            count_params.append(f"%{nom}%")

        if prenom:
            count_query += " AND prenom LIKE ?"
            count_params.append(f"%{prenom}%")

        cursor.execute(count_query, count_params)
        rows = cursor.fetchone()
        print(rows)

        total_count = rows[0]
        total_pages = (total_count + per_page - 1) // per_page
        return total_pages, total_count

    def update_benevol(self, benevol):
        connection = self.get_connection()
        connection.execute(
            "UPDATE benevol set nom = ?, prenom = ?, sexe=?, "
            "email=?, adresse=?, "
            "motivation = ? where id = ?",
            (
                benevol.nom,
                benevol.prenom,
                benevol.sexe,
                benevol.email,
                benevol.adresse,
                benevol.motivation,
                benevol.id,
            ),
        )
        connection.commit()
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        benevol_id = cursor.fetchone()
        benevol.id = benevol_id[0]
        return benevol

    def delete_benevol(self, benevol):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM benevol WHERE id = ?", (benevol.id,))
        connection.commit()
        connection.close()

    def save_benevol(self, nom, prenom, sexe, email, adresse, motivation):
        connection = self.get_connection()
        connection.execute(
            "INSERT INTO "
            "benevol(nom, prenom, sexe, email, adresse, motivation) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (nom, prenom, sexe, email, adresse, motivation),
        )
        connection.commit()
        connection.close()

    def get_benevols(self):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT nom,prenom,sexe,email,adresse, motivation FROM benevol"
        )
        rows = cursor.fetchall()
        return rows

    def get_benevol_info(self, email):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT email FROM benevol where email=?", (email,))
        rows = cursor.fetchone()
        return rows

    def get_admin_info(self, email):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT id, nom, prenom, mot_de_passe_salt, mot_de_passe_hash, "
            "statut, email FROM admin where email=?",
            (email,),
        )
        rows = cursor.fetchone()
        return rows

    def get_admin_info_by_email(self, email, id):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT id, nom, prenom, mot_de_passe_salt, mot_de_passe_hash, "
            "statut, email FROM admin where email=? AND id != ?",
            (email, id),
        )
        rows = cursor.fetchone()
        return rows

    def get_admin_info_by_id(self, id):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT id, nom, prenom, mot_de_passe_salt,"
            " mot_de_passe_hash, statut, email FROM admin where id=?",
            (id,),
        )
        rows = cursor.fetchone()
        return rows

    def get_admin_by_token(self, token):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT id, nom, prenom, mot_de_passe_salt,"
            " mot_de_passe_hash, statut, email FROM admin where token=?",
            (token,),
        )
        rows = cursor.fetchone()
        return rows

    def save_admin(
        self, nom, prenom, email, mot_de_passe_salt, mot_de_passe_hash
    ):
        connection = self.get_connection()
        connection.execute(
            "INSERT INTO "
            "admin(nom, prenom, email, mot_de_passe_salt, mot_de_passe_hash) "
            "VALUES (?, ?, ?, ?, ?)",
            (nom, prenom, email, mot_de_passe_salt, mot_de_passe_hash),
        )
        connection.commit()
        connection.close()

    def get_admins(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT id,nom,prenom,email,statut FROM admin")
        rows = cursor.fetchall()
        return rows

    def suspend_admin(self, statut, email):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE admin SET statut = ? WHERE email = ?", (statut, email)
        )
        connection.commit()
        connection.close()

    def update_admin_info(self, nom, prenom, email, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE admin SET nom = ?, prenom=?, email=? WHERE id = ?",
            (nom, prenom, email, id),
        )
        connection.commit()
        connection.close()

    def update_pass_admin(self, mot_de_passe_salt, mot_de_passe_hash, email):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE admin "
            "SET mot_de_passe_salt = ?, mot_de_passe_hash=? WHERE email = ?",
            (
                mot_de_passe_salt,
                mot_de_passe_hash,
                email,
            ),
        )
        connection.commit()
        connection.close()

    def update_admin(self, token, email):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE admin SET token=? WHERE email = ?",
            (
                token,
                email,
            ),
        )
        connection.commit()
        connection.close()

    def delete_admin(self, email):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM admin WHERE email = ?", (email,))
        connection.commit()
        connection.close()
