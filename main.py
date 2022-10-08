from flask import Flask, render_template, redirect, url_for, session, request
from flask_babel import Babel
from loguru import logger
from werkzeug.exceptions import HTTPException

from controllers.controller_database import ControllerDatabase
from web.site import site
from web.dashboard_page import dashboard_view
from web.login_page import login_view
from web.register_page import register_view

app = Flask(__name__)
app.config["SECRET_KEY"] = "8f42a73054b1749h8f58848be5e6502c"
app.config["BABEL_DEFAULT_LOCALE"] = "en"

babel = Babel(app)


@app.route('/')
def home():
    """
    The home view
    :return: Renders the home page
    """
    result = redirect(url_for("login.login"))

    if "user_id" in session:
        result = redirect(url_for("dashboard.dashboard"))

    return result


@app.errorhandler(Exception)
def error_page(error):
    """
    This function is called any time a fatal error occurs
    :param error: The Exception that caused the error
    :return: Renders the error page with the appropriate error code
    """
    logger.exception(error)
    error_code = 500

    if isinstance(error, HTTPException):
        error_code = error.code

    return render_template("error_page.html", error_code=error_code), error_code


@app.before_request
def check_user_in():
    """
    Before each request, it checks if the user is logged in.
    If it isn't and the user has a session token, the user gets logged in.
    :return: None
    """
    if "user_id" in session:
        return

    token_uuid = request.cookies.get("token")
    if token_uuid:
        token = ControllerDatabase.get_token_by_uuid(token_uuid)
        user = ControllerDatabase.get_user(token.user_user_id)

        if user:
            session["user_id"] = user.user_id


if __name__ == "__main__":
    logger.add("./logs/{time:YYYY-MM-DD}.log", colorize=True, rotation="00:00")
    app.register_blueprint(login_view, url_prefix="/login")
    app.register_blueprint(register_view, url_prefix="/register")
    app.register_blueprint(dashboard_view, url_prefix="/dashboard")
    app.register_blueprint(site, url_prefix="/site")
    app.run(debug=True)
