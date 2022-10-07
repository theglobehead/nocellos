from __future__ import annotations

from hashlib import sha256
import numpy as np

from controllers.controller_database import ControllerDatabase
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
        password_hash = sha256(password_utf8)
        result = password_hash.hexdigest()

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
    def create_user(name: str, password: str):
        salt = ControllerUser.generate_salt()
        hashed_password = ControllerUser.hash_password(password, salt)

        user = User(
            user_name=name,
            password_salt=salt,
            password_hash=hashed_password,
        )

        return ControllerDatabase.insert_user(user)
