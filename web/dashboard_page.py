from flask import Blueprint, render_template

from utils.flask_utils import login_required

dashboard_view = Blueprint("dashboard", __name__)


@dashboard_view.route("/", methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    View for the dashboard page.
    :return: renders the login view
    """
    result = render_template("dashboard_page.html")

    return result
