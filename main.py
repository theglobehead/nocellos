from flask import Flask, render_template, redirect, url_for
from flask_babel import Babel
from loguru import logger
from werkzeug.exceptions import HTTPException

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
    return redirect(url_for("login.login"))


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


if __name__ == "__main__":
    logger.add("./logs/{time:YYYY-MM-DD}.log", colorize=True, rotation="00:00")
    app.register_blueprint(login_view, url_prefix="/login")
    app.register_blueprint(register_view, url_prefix="/register")
    app.run(debug=True)
