from flask import Blueprint, render_template


dashboard_view = Blueprint("dashboard", __name__)


@dashboard_view.route("/", methods=['GET', 'POST'])
def dashboard():
    """
    View for the dashboard page.
    :return: renders the login view
    """
    result = render_template("dashboard_page.html")

    return result
