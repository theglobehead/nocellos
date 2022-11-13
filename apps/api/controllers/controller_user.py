from __future__ import annotations

from hashlib import sha256
import numpy as np

from controllers.controller_database import ControllerDatabase
from models.token import Token
from models.user import User


class ControllerUser:
    @staticmethod
    def hash_password(password: str, salt: str = "") -> str:
        """
        Used for hashing a users' password.
        Uses sha256
        :param password: the users passwords
        :param salt: the users' password salt
        :return: returns the hashed password
        """
        password_utf8 = (password + salt).encode("utf-8")
        hashed_password = sha256(password_utf8)
        result = hashed_password.hexdigest()

        return result

    @staticmethod
    def generate_salt() -> str:
        """
        Generates salt for the users' hashed password
        :return: an 8 character long string
        """
        chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
        random_chars = np.random.choice(list(chars), 8)
        result = "".join(random_chars)

        return result

    @staticmethod
    def create_user(email: str, name: str, password: str, email_verified: bool = False) -> User:
        salt = ControllerUser.generate_salt()
        hashed_password = ControllerUser.hash_password(password, salt)

        user = User(
            user_name=name,
            user_email=email,
            password_salt=salt,
            hashed_password=hashed_password,
            email_verified=email_verified,
        )

        return ControllerDatabase.insert_user(user)

    @staticmethod
    def log_user_in(email: str, password: str) -> User | None:
        """
        Used for checking if the user entered valid data, when logging in
        :param email: the email entered
        :param password: the password entered
        :return: Returns the User, if the form is valid, else it returns false
        """
        result = None

        user_email_taken = ControllerDatabase.check_if_user_email_taken(email)

        if user_email_taken:
            user = ControllerDatabase.get_user_by_email(email)

            if user:
                hashed_password = ControllerUser.hash_password(password, user.password_salt)

                if user.hashed_password == hashed_password:
                    token = ControllerUser.create_token(user)
                    user.token = token
                    result = user

        return result

    @staticmethod
    def create_token(user: User) -> Token:
        if user.token.token_id:
            ControllerDatabase.delete_token(user.token)

        new_token = ControllerDatabase.insert_token(Token(user_user_id=user.user_id))

        return new_token
