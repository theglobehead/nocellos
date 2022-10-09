from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_babel import gettext
from flask_mail import Message
from loguru import logger

from controllers.constants import ADMIN_EMAIL, SERVER_NAME
from controllers.controller_database import ControllerDatabase
from controllers.controller_user import ControllerUser
from models.user import User
from utils.flask_utils import send_mail_message

register_view = Blueprint("register", __name__)


@register_view.route("/", methods=['GET', 'POST'])
def register():
    """
    View for the register page.
    :return: renders the register view
    """
    result = None

    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        form = request.form
        name = form.get("username").strip()
        email = form.get("email").strip()
        password1 = form.get("password1").strip()
        password2 = form.get("password2").strip()

        form_is_valid = validate_form(email=email, name=name, pass1=password1, pass2=password2)

        if form_is_valid:
            try:
                new_user = ControllerUser.create_user(email=email, name=name, password=password1)
                print("new_user:", new_user)
                send_confirmation_email(new_user)
                result = redirect(url_for("register.verify_email_page"))
            except Exception as e:
                logger.exception(e)

    if not result:
        result = render_template("register_page.html")

    return result


@register_view.route("/verify-email", methods=['GET', 'POST'])
def verify_email_page():
    """
    View for the verify email page.
    :return: renders the register view
    """
    result = render_template("email_sent_page.html")

    return result


def send_confirmation_email(user: User):
    msg = Message(gettext("strings.verify_email"), sender=ADMIN_EMAIL, recipients=[user.user_email])
    msg.html = render_template("confirm_email_email.html", user=user, server_name=SERVER_NAME)
    send_mail_message(msg)


def validate_form(email: str, name: str, pass1: str, pass2: str):
    """
    Used for validating a register form.
    If the form is invalid, it flashes a message.
    :param email: the email entered
    :param name: the username entered
    :param pass1: the first password entered
    :param pass2: the second password entered
    :return: boolean of weather or not the form is valid
    """
    result = True

    if not email:
        result = False
        flash(gettext("error_msg.enter_email"))
    elif not all((pass1, pass2)):
        result = False
        flash(gettext("error_msg.enter_both_passwords"))
    elif not name:
        result = False
        flash(gettext("error_msg.enter_name"))
    elif len(name) > 100:
        result = False
        flash(gettext("error_msg.name_is_too_long"))
    elif pass1 != pass2:
        result = False
        flash(gettext("error_msg.passwords_do_not_match"))

    return result
