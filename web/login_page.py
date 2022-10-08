import datetime

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_babel import gettext

from controllers.controller_user import ControllerUser

login_view = Blueprint("login", __name__)


@login_view.route("/", methods=['GET', 'POST'])
def login():
    """
    View for the login page.
    :return: renders the login view
    """
    result = render_template("login_page.html")

    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        form = request.form
        email = form.get("email").strip()
        password = form.get("password").strip()
        remember_me = bool(form.get("remember_me"))

        user = ControllerUser.log_user_in(email, password, remember_me)

        if user:
            session["user_id"] = user.user_id
            result = redirect(url_for("dashboard.dashboard"))
            if user.token.token_uuid:
                result.set_cookie(
                    "token",
                    user.token.token_uuid,
                    expires=datetime.datetime.now() + datetime.timedelta(days=3)
                )
        else:
            flash(gettext("error_msg.incorrect_login_details"))

    return result
