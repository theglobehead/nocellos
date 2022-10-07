from flask import Blueprint, render_template

register_view = Blueprint("register", __name__)


@register_view.route("/", methods=['GET', 'POST'])
def register():
    """
    View for the register page.
    :return: renders the register view
    """
    result = render_template("register_page.html")

    return result
