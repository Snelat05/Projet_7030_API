import math
import smtplib
from email.mime.text import MIMEText
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    g,
    url_for,
    redirect,
    session,
    jsonify,
)
from flask_json_schema import JsonValidationError, JsonSchema
from schema import (
    inserer_benevol_schema,
    modifier_benevol_schema,
)
from database import Database
from benevol import Benevol
import re
import hashlib
import uuid
import secrets

# Configuration de l'application
app = Flask(__name__, static_url_path="", static_folder="static")
schema = JsonSchema(app)
app.config["SECRET_KEY"] = secrets.token_hex(16)

# Expressions régulières
PASSWORD_REGEX = r"[A-Za-z0-9#$%&'*+/=?@]{8,}"
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# Gestion de la base de données


def get_db():
    if not hasattr(g, "_database"):
        g._database = Database()
    return g._database


def deconnection():
    database = getattr(g, "_database", None)
    if database is not None:
        database.deconnection()


def connection_requise(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "courriel" not in session:
            return redirect(url_for("admin")), 302
        return f(*args, **kwargs)

    return decorated_function


def get_benevols():
    return get_db().get_benevols()


def verifier_email_benevol(email):
    return get_db().get_benevol_info(email)


def get_admins():
    return get_db().get_admins()


def suspend_admin(statut, email):
    if statut:
        statut = 0
    else:
        statut = 1

    return get_db().suspend_admin(statut, email)


def verifier_email_admin(email):
    return get_db().get_admin_info(email)


def get_admin_info_by_id(id_admin):
    return get_db().get_admin_info_by_id(id_admin)


def get_admin_info_by_email(email, id_admin):
    return get_db().get_admin_info_by_email(email, id_admin)


def update_info_admin(nom, prenom, email, id_admin):
    return get_db().update_admin_info(nom, prenom, email, id_admin)


def verifier_password(mot_de_passe_salt, mot_de_passe_hash, password):
    mot_de_passe_salt_password = hashlib.sha256(
        str(password + mot_de_passe_salt).encode("utf-8")
    ).hexdigest()
    return mot_de_passe_salt_password == mot_de_passe_hash


def update_pass_admin(mot_de_passe_salt, mot_de_passe_hash, email):
    return get_db().update_pass_admin(
        mot_de_passe_salt, mot_de_passe_hash, email
    )


def update_admin(token, email):
    return get_db().update_admin(token, email)


def get_admin_by_token(token):
    return get_db().get_admin_by_token(token)


def delete_admin(mail):
    return get_db().delete_admin(mail)


@app.errorhandler(JsonValidationError)
def validation_error(e):
    errors = [validation_error.message for validation_error in e.errors]
    return jsonify({"error": e.message, "errors": errors}), 400


@app.errorhandler(404)
def page_not_found():
    return render_template("html/pages/Error 404.html"), 404


@app.route("/documentation")
def documentation():
    return render_template("document.html")


@app.route("/")
def index():
    return render_template("html/pages/index.html")


@app.route("/ananda")
def ananda():
    return render_template("html/pages/ananda.html")


@app.route("/ideologie")
def ideologie():
    return render_template("html/pages/ideologie.html")


@app.route("/evenements")
def evenements():
    return render_template("html/pages/evenements.html")


@app.route("/responsable")
def responsable():
    return render_template("html/pages/responsable.html")


@app.route("/api/ajout_benevol", methods=["POST"])
@schema.validate(inserer_benevol_schema)
def benevol():
    try:
        data = request.get_json()
        nouveau_benevol = Benevol(
            None,
            data["nom"],
            data["prenom"],
            data["sexe"],
            data["email"],
            data["adresse"],
            data["motivation"],
        )
        new_bene = get_db().save_benevol_api(nouveau_benevol)
        return (
            jsonify(
                "L'utilisateur "
                + data["nom"]
                + " "
                + data["prenom"]
                + " a été ajouté avec succès.",
                new_bene.asdictionary(),
            ),
            201,
        )

    except Exception as e:
        return (
            jsonify(
                error="Une erreur interne s'est produite. L'erreur a été "
                "signalée à l'équipe de développement."
            ),
            500,
        )


@app.route("/api/afficher_benevol", methods=["GET"])
def afficher_benevols():
    benevols = get_db().get_benevols_api()
    return jsonify([benevol.asdictionary() for benevol in benevols])


@app.route("/api/afficher_benevol/<int:id>", methods=["GET"])
def afficher_benevol(id):
    benevol = get_db().get_benevol_byId(id)
    if benevol is None:
        return "", 404
    else:
        return jsonify(benevol.asdictionary())


@app.route("/recherche/benevol")
def recherche():
    return render_template("html/pages/rechercheBenevol_REST.html")


@app.route("/api/rechercher_benevols", methods=["GET"])
def rechercher_benevols():
    nom = request.args.get("nom", "")
    prenom = request.args.get("prenom", "")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 5))
    try:
        benevol = get_db().search_benevol(nom, prenom, page, per_page)
        return (
            jsonify(
                {
                    "status": "success",
                    "data": benevol,
                    "pagination": {
                        "current_page": page,
                        "per_page": per_page,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        print("Erreur recherche :", e)
        return jsonify(error=f"Erreur côté serveur{e}"), 500


@app.route("/api/modifier_benevol/<int:id>", methods=["PUT"])
@schema.validate(modifier_benevol_schema)
def update_benevol(id):
    try:
        data = request.get_json()
        if data is None:
            return (
                jsonify({"error": "Requête invalide, aucun JSON trouvé."}),
                400,
            )

        benevol_update = Benevol(
            id,
            data.get("nom"),
            data.get("prenom"),
            data.get("sexe"),
            data.get("email"),
            data.get("adresse"),
            data.get("motivation"),
        )

        result = get_db().update_benevol(benevol_update)

        if result:
            return (
                jsonify(
                    {
                        "message": f"Le bénévole avec l'id: {id} a été modifié avec succès.",
                        "data": result.asdictionary(),
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {"error": f"Bénévole non trouvé avec l'id spécifié: {id}."}
                ),
                404,
            )

    except Exception as e:
        return (
            jsonify(
                {"error": f"Une erreur interne s'est produite : {str(e)}"}
            ),
            500,
        )


@app.route("/api/supprimer_benevol/<int:id>", methods=["DELETE"])
def supprimer_benevol(id):
    benevol = get_db().get_benevol_byId(id)
    if benevol is None:
        return (
            jsonify({"error": f"Le bénévole avec l'Id {id} n'existe pas."}),
            404,
        )

    get_db().delete_benevol(benevol)
    return (
        jsonify(
            {
                "message": f"Le bénévole avec l'Id {id} a été supprimé avec succès."
            }
        ),
        200,
    )


@app.route("/Formulaire", methods=["GET", "POST"])
def formbenevol():
    if request.method == "GET":
        return render_template("html/pages/formbenevol.html"), 200

    if request.method == "POST":
        erreurs = None
        nom = request.form.get("nom").strip()
        prenom = request.form.get("prenom").strip()
        select = request.form.get("sexe")
        email = request.form.get("email").strip()
        adresse = request.form.get("adresse").strip()
        motivation = request.form.get("motivation").strip()

        if (
            nom == ""
            or prenom == ""
            or email == " "
            or adresse == ""
            or motivation == ""
            or not select
        ):
            erreurs = "Tous les champs doivent être remplis."

        elif not re.match(EMAIL_REGEX, email):
            erreurs = (
                "Format d'email invalide ! Utilisez le format "
                ": exemple@mail.com"
            )

        elif len(nom) > 50 or len(prenom) > 50 or len(adresse) > 50:
            erreurs = "Le nombre de caractère est 50"

        elif len(motivation) > 255:
            erreurs = "Le nombre de caractère est 255"

        elif select not in ["masculin", "féminin", "autre"]:
            erreurs = "Faites le bon choix"

        elif verifier_email_benevol(email):
            erreurs = "Erreur de mail ou le mail existe déjà"

        if erreurs:
            return (
                render_template(
                    "html/pages/formbenevol.html",
                    erreur=erreurs,
                    nom=nom,
                    prenom=prenom,
                    sexe=select,
                    email=email,
                    adresse=adresse,
                    motivation=motivation,
                ),
                400,
            )

        get_db().save_benevol(nom, prenom, select, email, adresse, motivation)

        return redirect(url_for("confirm"), 302)


@app.route("/confirm")
def confirm():
    return render_template("html/pages/confirm.html")


@app.route("/administration", methods=["GET", "POST"])
def admin():
    if request.method == "GET":
        return render_template("html/pages/login.html")

    if request.method == "POST":
        erreurs = None
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        if email == "" or password == "":
            erreurs = "Tous les champs doivent être remplis."

        elif not re.match(EMAIL_REGEX, email):
            erreurs = (
                "Format d'email invalide ! Utilisez le format : "
                "exemple@mail.com"
            )

        admin_connect = verifier_email_admin(email)

        if not admin_connect:
            erreurs = "Email ou mot de passe incorrect"

        elif admin_connect:
            admin_statut = admin_connect[5]

            if not verifier_password(
                admin_connect[3], admin_connect[4], password
            ):
                erreurs = "Email ou mot de passe incorrect"

            if not admin_connect[5]:
                erreurs = "Email ou mot de passe ou compte inactif"

        if erreurs:
            return (
                render_template(
                    "html/pages/login.html",
                    erreur=erreurs,
                    email=email,
                    password=password,
                ),
                400,
            )

        session.clear()
        session["nom"] = admin_connect[1]
        session["courriel"] = admin_connect[6]

        return redirect(url_for("dashboard")), 302


@app.route("/Dashboard")
@connection_requise
def dashboard():
    return render_template("html/pages/dashboard.html")


@app.route("/Ajout", methods=["GET", "POST"])
@connection_requise
def ajout():
    if request.method == "GET":
        return render_template("html/pages/ajoutadmin.html")

    if request.method == "POST":
        erreurs = None
        nom = request.form.get("nom").strip()
        prenom = request.form.get("prenom").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        confirm = request.form.get("confirm").strip()

        if (
            nom == ""
            or prenom == ""
            or email == ""
            or password == ""
            or confirm == ""
        ):
            erreurs = "Tous les champs doivent être remplis."

        elif not re.match(EMAIL_REGEX, email):
            erreurs = (
                "Format d'email invalide ! Utilisez le format : "
                "exemple@mail.com"
            )

        elif len(nom) > 50 or len(prenom) > 50:
            erreurs = "Le nombre de caractère est 50"

        elif password != confirm:
            erreurs = "Les mots de passe ne correspondent pas."

        elif verifier_email_admin(email):
            erreurs = "Erreur de mail ou le mail existe déjà"

        if erreurs:
            return (
                render_template(
                    "html/pages/ajoutadmin.html",
                    erreur=erreurs,
                    nom=nom,
                    prenom=prenom,
                    email=email,
                ),
                400,
            )

        mot_de_passe_salt = uuid.uuid4().hex
        mot_de_passe_hash = hashlib.sha256(
            str(password + mot_de_passe_salt).encode("utf-8")
        ).hexdigest()
        get_db().save_admin(
            nom, prenom, email, mot_de_passe_salt, mot_de_passe_hash
        )

        return redirect(url_for("gestion"), 302)


@app.route("/suspend/<int:statut>/<string:email>")
@connection_requise
def suspend(statut, email):
    suspend_admin(statut, email)
    return redirect(url_for("gestion"))


@app.route("/delete/<string:email>")
@connection_requise
def delete(email):
    delete_admin(email)
    return redirect(url_for("gestion"))


@app.route("/update/<int:id>", methods=["GET", "POST"])
@connection_requise
def update(id):
    if request.method == "GET":
        info_admin = get_admin_info_by_id(id)
        id = info_admin[0]
        nom = info_admin[1]
        prenom = info_admin[2]
        email = info_admin[6]
        return render_template(
            "html/pages/modinfo.html",
            nom=nom,
            prenom=prenom,
            email=email,
            id=id,
        )

    if request.method == "POST":
        erreurs = None
        nom = request.form.get("nom").strip()
        prenom = request.form.get("prenom").strip()
        email = request.form.get("email").strip()

        if nom == "" or prenom == "" or email == "":
            erreurs = "Tous les champs doivent être remplis."

        elif not re.match(EMAIL_REGEX, email):
            erreurs = (
                "Format d'email invalide ! Utilisez le format : "
                "exemple@mail.com"
            )

        elif get_admin_info_by_email(email, id):
            erreurs = "Erreur de mail ou le mail existe déjà"

        if erreurs:
            return (
                render_template(
                    "html/pages/modinfo.html",
                    erreur=erreurs,
                    id=id,
                    nom=nom,
                    prenom=prenom,
                    email=email,
                ),
                400,
            )

        get_db().update_admin_info(nom, prenom, email, id)
        return redirect(url_for("gestion")), 302


@app.route("/Modification_Password", methods=["GET", "POST"])
@connection_requise
def modpass():
    if request.method == "GET":
        return render_template("html/pages/modpass.html")

    if request.method == "POST":
        erreurs = None
        password = request.form.get("password")
        npassword = request.form.get("npassword")
        cpassword = request.form.get("cpassword")

        if password == "" or npassword == "" or cpassword == "":
            erreurs = "Tous les champs doivent être remplis."

        elif npassword != cpassword:
            erreurs = "Les mots de passe ne correspondent pas."

        elif "courriel" in session:
            email = session["courriel"]
            admin_connect = verifier_email_admin(email)
            if admin_connect:
                if not verifier_password(
                    admin_connect[3], admin_connect[4], password
                ):
                    erreurs = "Mot de passe incorrect"

        if erreurs:
            return (
                render_template(
                    "html/pages/modpass.html",
                    erreur=erreurs,
                    password=password,
                    npassord=npassword,
                    cpassword=cpassword,
                ),
                400,
            )

        mot_de_passe_salt = uuid.uuid4().hex
        mot_de_passe_hash = hashlib.sha256(
            str(npassword + mot_de_passe_salt).encode("utf-8")
        ).hexdigest()
        get_db().update_pass_admin(mot_de_passe_salt, mot_de_passe_hash, email)
        return redirect(url_for("admin")), 302


@app.route("/Gestion_Admin")
@connection_requise
def gestion():
    ad = get_admins()
    return render_template("html/pages/gestion.html", admins=ad)


@app.route("/Liste_benevoles")
@connection_requise
def benevole():
    bene = get_benevols()
    return render_template("html/pages/benevole.html", benevols=bene)


@app.route("/Réinitialisation", methods=["GET", "POST"])
def reset():
    if request.method == "GET":
        return render_template("html/pages/password.html")

    if request.method == "POST":
        erreurs = None
        email = request.form.get("email").strip()

        if not email:
            erreurs = "Le champs doit être remplis."

        elif not re.match(EMAIL_REGEX, email):
            erreurs = (
                "Format d'email invalide ! Utilisez le format : "
                "exemple@mail.com"
            )

        if erreurs:
            return (
                render_template(
                    "html/pages/password.html", erreur=erreurs, email=email
                ),
                400,
            )

        if not verifier_email_admin(email):
            return redirect(url_for("merci")), 302

        salt = uuid.uuid4().hex
        token = hashlib.sha512(str(email + salt).encode("utf-8")).hexdigest()

        update_admin(token, email)

        try:
            msg = MIMEText(
                render_template("html/pages/mail.html", token=token), "html"
            )
            msg["Subject"] = "Réinitialisation de votre mot de passe"
            msg["From"] = "evensjacquet05@gmail.com"
            msg["To"] = email

            with smtplib.SMTP("localhost", 1025) as server:
                server.send_message(msg)
            print(f"Email envoyé à {email}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")

        return redirect(url_for("merci")), 302


@app.route("/Remerciement")
def merci():
    return render_template("html/pages/remerciement.html")


@app.route("/Reset/<string:token>", methods=["GET", "POST"])
def reset_final(token):
    admin = get_admin_by_token(token)
    if request.method == "GET":
        if admin:
            return render_template("html/pages/reset.html", token=token), 200
        return redirect(url_for("admin")), 301

    else:
        erreurs = None
        password = request.form.get("password").strip()
        npassword = request.form.get("npassword").strip()

        if password != npassword:
            erreurs = "Les mots de passe ne correspondent pas."

        if erreurs:
            return (
                render_template(
                    "html/pages/reset.html",
                    erreurs=erreurs,
                    password=password,
                    npassword=npassword,
                    token=token,
                ),
                404,
            )

        mot_de_passe_salt = uuid.uuid4().hex
        mot_de_passe_hash = hashlib.sha256(
            str(password + mot_de_passe_salt).encode("utf-8")
        ).hexdigest()
        get_db().update_pass_admin(
            mot_de_passe_salt, mot_de_passe_hash, admin[6]
        )

        return redirect(url_for("admin")), 301


@app.route("/Logout")
def logout():
    session.clear()
    return redirect(url_for("index"), 302)


if __name__ == "__main__":
    app.run(debug=True)
