from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_babel import gettext
from flask_mail import Message

from controllers.constants import ADMIN_EMAIL, SERVER_NAME
from models.user import User
from utils.flask_utils import send_mail_message


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
