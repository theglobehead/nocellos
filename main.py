from flask import Flask, render_template
from loguru import logger
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.config["SECRET_KEY"] = "8f42a73054b1749h8f58848be5e6502c"


@app.route('/')
def home():
    """
    The home view
    :return: Renders the home page
    """
    return render_template("login_page.html")


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

    return error_code


if __name__ == "__main__":
    logger.add("./logs/{time:YYYY-MM-DD}.log", colorize=True, rotation="00:00")
    app.run(debug=True)
