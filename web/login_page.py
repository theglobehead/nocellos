import datetime

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_babel import gettext

from controllers.controller_database import ControllerDatabase
from controllers.controller_user import ControllerUser

login_view = Blueprint("login", __name__)


@login_view.route("/", methods=['GET', 'POST'])
def login():
    """
    View for the login page.
    :return: renders the login view
    """
    result = None

    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        form = request.form
        email = form.get("email").strip()
        password = form.get("password").strip()
        remember_me = bool(form.get("remember_me"))

        user = ControllerUser.log_user_in(email, password, remember_me)

        if user and user.email_verified:
            session["user_id"] = user.user_id
            result = redirect(url_for("dashboard.dashboard"))
            if user.token.token_uuid:
                result.set_cookie(
                    "token",
                    user.token.token_uuid,
                    expires=datetime.datetime.now() + datetime.timedelta(days=3)
                )
        elif user:
            flash(gettext("error_msg.email_not_verified"))
        else:
            flash(gettext("error_msg.incorrect_login_details"))

    if not result:
        result = render_template("login_page.html")

    return result


@login_view.route("/verify-email/<user_uuid>", methods=['GET'])
def verify_user_email(user_uuid: str):
    """
    Used for verifying a users email
    :user_uuid: the uuid of the user
    :return: renders the login view
    """
    result = redirect(url_for("login.login"))

    user = ControllerDatabase.get_user_by_uuid(user_uuid)
    ControllerDatabase.set_user_email_verified(user)

    return result
