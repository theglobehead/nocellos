from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import session, redirect, url_for, Response, Flask
from flask_mail import Mail, Message

mail: Mail | None = None


def initialize_flask_mail(app: Flask):
    global mail
    mail = Mail(app)

    return mail


def send_mail_message(msg: Message):
    mail.send(msg)


def login_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args: list, **kwargs: dict) -> Response | dict:
        result = None
        user_id = session.get("user_id", None)
        if user_id:
            result = f(*args, **kwargs)
        else:
            result = redirect(url_for("login"))
        return result

    return decorated_function
