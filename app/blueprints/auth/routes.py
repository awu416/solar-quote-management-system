from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from app.blueprints.auth import auth_bp
from app.extensions import db
from app.models.user import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            error = "Email and password are required."
        else:
            user = db.session.execute(
                db.select(User).where(User.email == email)
            ).scalar_one_or_none()

            if user is None or not user.check_password(password):
                error = "Invalid email or password."
            else:
                login_user(user)

                return redirect(url_for("main.home"))

    return render_template(
        "auth/login.html",
        error=error
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()

    flash("You have been logged out.")

    return redirect(url_for("auth.login"))