import datetime
import http
import os

from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_babel import Babel, gettext
from loguru import logger
from werkzeug.exceptions import HTTPException

from controllers.constants import ADMIN_EMAIL
from controllers.controller_database import ControllerDatabase
from controllers.controller_user import ControllerUser
from models.friend_request import FriendRequest
from utils.flask_utils import initialize_flask_mail, login_required
from web.register_page import validate_form, send_confirmation_email

app = Flask(__name__)
app.config["SECRET_KEY"] = "8f42a73054b1749h8f58848be5e6502c"
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ADMIN_EMAIL
app.config['MAIL_PASSWORD'] = os.environ["EMAIL_PASSWORD"]
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

babel = Babel(app)
initialize_flask_mail(app)


@app.route('/')
def home():
    """
    The home view
    :return: Renders the home page
    """
    result = redirect(url_for("login"))

    if "user_id" in session:
        result = redirect(url_for("dashboard"))

    return result


@babel.localeselector
def get_locale() -> str:
    """
    Used for determining the language of the website
    :return: string of "en"
    """
    return "en"


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


@app.route("/logout", methods=['GET'])
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

    result = redirect(url_for("login"))
    result.delete_cookie("token")

    return result


@app.route("/email-sent", methods=['GET'])
def email_sent():
    """
    View for the verify email page.
    :return: renders the register view
    """
    result = render_template("email_sent_page.html")

    return result


@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    View for the register page.
    :return: renders the register view
    """
    result = None

    if "user_id" in session:
        return redirect(url_for("dashboard"))

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
                send_confirmation_email(new_user)
                result = redirect(url_for("email_sent"))
            except Exception as e:
                logger.exception(e)

    if not result:
        result = render_template("register_page.html")

    return result


@app.route("/verify-email/<user_uuid>", methods=['GET'])
def verify_user_email(user_uuid: str):
    """
    Used for verifying a users email
    :user_uuid: the uuid of the user
    :return: Sends the user to the login view
    """
    result = redirect(url_for("login"))

    user = ControllerDatabase.get_user_by_uuid(user_uuid)
    ControllerDatabase.set_user_email_verified(user)

    return result


@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    View for the login page.
    :return: renders the login view
    """
    result = None

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        form = request.form
        email = form.get("email").strip()
        password = form.get("password").strip()
        remember_me = bool(form.get("remember_me"))

        user = ControllerUser.log_user_in(email, password, remember_me)

        if user and user.email_verified:
            session["user_id"] = user.user_id
            result = redirect(url_for("dashboard"))
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


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    View for the dashboard page.
    :return: renders the dashboard view
    """
    result = render_template("dashboard_page.html")

    return result


@app.route("/send-friend-request", methods=['GET', 'POST'])
@login_required
def send_friend_request():
    """
    Ajax endpoint for sending a friend request
    :return: "", http.HTTPStatus.NO_CONTENT
    """
    sender_user_id = session.get("user_id")
    receiver_user_uuid = request.form.get("receiver_user_uuid")
    receiver_user_id = ControllerDatabase.get_user_id_by_uuid(receiver_user_uuid)

    friend_request = FriendRequest(
        sender_user_id=sender_user_id,
        receiver_user_id=receiver_user_id,
    )

    ControllerDatabase.insert_friend_request(friend_request)

    return "", http.HTTPStatus.NO_CONTENT


@app.route("/accept-friend-request", methods=['GET', 'POST'])
@login_required
def accept_friend_request():
    """
    Ajax endpoint for accepting a friend request
    :return: "", http.HTTPStatus.NO_CONTENT
    """
    friend_request_uuid = request.form.get("receiver_user_uuid")
    friend_request_id = ControllerDatabase.get_friend_request_id_by_uuid(friend_request_uuid)

    ControllerDatabase.accept_friend_request(
        FriendRequest(friend_request_id=friend_request_id)
    )

    return "", http.HTTPStatus.NO_CONTENT


@app.route("/remove-friend-request", methods=['GET', 'POST'])
@login_required
def remove_friend_request():
    """
    Ajax endpoint for removing a friend request
    :return: "", http.HTTPStatus.NO_CONTENT
    """
    friend_request_uuid = request.form.get("receiver_user_uuid")
    friend_request_id = ControllerDatabase.get_friend_request_id_by_uuid(friend_request_uuid)

    ControllerDatabase.delete_friend_request(
        FriendRequest(friend_request_id=friend_request_id)
    )

    return "", http.HTTPStatus.NO_CONTENT


@app.route("/load-searched-users", methods=['GET', 'POST'])
@login_required
def load_searched_users():
    """
    Ajax endpoint for getting searched users
    :return: A list of dictionaries containing the user_uuid, user_name and random_id
    """
    search_phrase = request.form.get("search_phrase", type=str)
    search_page = request.form.get("search_phrase", type=int)

    result = ControllerDatabase.load_searched_users(
        search_phrase=search_phrase,
        search_page=search_page
    )

    return result


if __name__ == "__main__":
    logger.add("./logs/{time:YYYY-MM-DD}.log", colorize=True, rotation="00:00")
    app.run(debug=True, port=os.getenv("PORT", default=5000))
