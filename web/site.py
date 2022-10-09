from flask import Blueprint, session, redirect, url_for

from controllers.controller_database import ControllerDatabase

site = Blueprint("site", __name__)


@site.route("/logout", methods=['GET'])
def logout():
    """
    Used for logging a user out.
    Clears the session
    :return: Redirects to the login view
    """
    user = ControllerDatabase.get_user(user_id=session["user_id"])

    session["user"] = None
    session["user_id"] = None
    session.clear()

    if user and user.token.token_uuid:
        ControllerDatabase.delete_token(user.token)

    result = redirect(url_for("login.login"))
    result.delete_cookie("token")

    return result
