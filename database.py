import sqlite3


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
