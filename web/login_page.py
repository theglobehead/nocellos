from flask import Blueprint, render_template, request

from controllers.controller_database import ControllerDatabase

login_view = Blueprint("login", __name__)


@login_view.route("/", methods=['GET', 'POST'])
def login():
    """
    View for the login page.
    :return: renders the login view
    """
    result = render_template("login_page.html")

    return result
