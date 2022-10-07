from models.user import User
from utils.common_utils import CommonUtils
from loguru import logger


class ControllerDatabase:
    @staticmethod
    def insert_user(user: User) -> bool:
        """
        Used for creating a new user
        :param user: the user to insert
        :return: bool of weather or not the insert was successful
        """
        result = False
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO USERS "
                        "(user_name, password_hash, password_salt) "
                        "values (%(user_name)s, %(password_hash)s, %(password_salt)s) ",
                        user.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def check_if_username_taken(name: str) -> bool:
        """
        Checks if a username is taken
        :param name: the username
        :return: True if the username is taken else False
        """
        result = True
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT user_id "
                        "FROM users WHERE user_name = %(name)s "
                        "LIMIT 1 ",
                        {
                            "name": name
                        }
                    )
                    result = bool(cur.fetchone())
        except Exception as e:
            logger.exception(e)
        return result
