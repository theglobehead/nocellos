from flask import Blueprint, render_template, flash
from flask_babel import gettext

dashboard_view = Blueprint("dashboard", __name__)


@dashboard_view.route("/", methods=['GET', 'POST'])
def dashboard():
    """
    View for the dashboard page.
    :return: renders the login view
    """
    result = render_template("dashboard_page.html")
    flash(gettext("error_msg.incorrect_login_details"))
    flash(gettext("error_msg.incorrect_login_details"))
    flash(gettext("error_msg.incorrect_login_details"))

    return result
