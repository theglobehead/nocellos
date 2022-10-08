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
    def check_if_user_email_taken(user_email: str) -> bool:
        """
        Checks if a username is taken
        :param user_email: the users email
        :return: True if the username is taken else False
        """
        result = True
        print("user_email", user_email)
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT user_id "
                        "FROM users WHERE user_email = %(user_email)s "
                        "LIMIT 1 ",
                        {
                            "user_email": user_email
                        }
                    )
                    result = bool(cur.fetchone())
                    print("aaaa", result)
        except Exception as e:
            logger.exception(e)
        return result

    @staticmethod
    def get_user_by_query(query_str: str, parameters: dict) -> User:
        """
        Used for getting a user with a query
        :param parameters: A dictionary of values vor the query
        :param query_str: The WHERE query
        :return: a User model
        """
        result = None

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT user_id, user_uuid, user_name, user_email, password_hash, password_salt, modified, created, is_deleted "
                        "FROM users "
                        f"{query_str}",
                        parameters
                    )
                    user_id, user_uuid, user_name, user_email, hashed_password, password_salt, modified, created, is_deleted = cur.fetchone()

            result = User(
                user_id=user_id,
                user_uuid=str(user_uuid),
                user_name=user_name,
                user_email=user_email,
                hashed_password=hashed_password,
                password_salt=password_salt,
                modified=modified,
                created=created,
                is_deleted=is_deleted,
            )
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_user_by_email(email: str) -> User:
        query_str = "WHERE user_email = %(email)s " \
                    "AND is_deleted = false "
        parameters = {"email": email}

        user = ControllerDatabase.get_user_by_query(query_str, parameters)

        return user
