def validate_form(email: str, name: str, pass1: str, pass2: str):
    """
    Used for validating a register form.
    If the form is invalid, it flashes a message.
    :param email: the email entered
    :param name: the username entered
    :param pass1: the first password entered
    :param pass2: the second password entered
    :return: boolean of weather or not the form is valid
    """
    result = True

    if not email:
        result = False
    elif not all((pass1, pass2)):
        result = False
    elif not name:
        result = False
    elif len(name) > 100:
        result = False
    elif pass1 != pass2:
        result = False

    return result
