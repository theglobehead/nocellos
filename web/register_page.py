from flask import Blueprint, render_template, request, redirect, url_for, session
from loguru import logger

from controllers.controller_database import ControllerDatabase
from controllers.controller_user import ControllerUser

register_view = Blueprint("register", __name__)


@register_view.route("/", methods=['GET', 'POST'])
def register():
    """
    View for the register page.
    :return: renders the register view
    """
    result = render_template("register_page.html")

    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        form = request.form
        name = form.get("username").strip()
        email = form.get("email").strip()
        password1 = form.get("password1").strip()
        password2 = form.get("password2").strip()

        form_is_valid = validate_form(name=name, pass1=password1, pass2=password2)

        if form_is_valid:
            try:
                ControllerUser.create_user(email=email, name=name, password=password1)
                result = redirect(url_for("login.login"))
            except Exception as e:
                logger.exception(e)

    return result


def validate_form(name: str, pass1: str, pass2: str):
    """
    Used for validating a register form.
    If the form is invalid, it flashes a message.
    :param name: the username entered
    :param pass1: the first password entered
    :param pass2: the second password entered
    :return: boolean of weather or not the form is valid
    """
    result = True

    if not all((pass1, pass2)):
        result = False
    elif not name:
        result = False
    elif len(name) > 100:
        result = False
    elif pass1 != pass2:
        result = False

    return result
