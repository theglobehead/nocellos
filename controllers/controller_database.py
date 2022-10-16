from models.friend_request import FriendRequest
from models.token import Token
from models.user import User
from utils.common_utils import CommonUtils
from loguru import logger


class ControllerDatabase:
    @staticmethod
    def insert_user(user: User) -> User:
        """
        Used for creating a new user
        :param user: the user to insert
        :return: bool of weather or not the insert was successful
        """
        result = None
        result_user_id = 0
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO USERS "
                        "(user_name, user_email, hashed_password, password_salt) "
                        "values (%(user_name)s, %(user_email)s, %(hashed_password)s, %(password_salt)s) "
                        "RETURNING user_id ",
                        user.to_dict()
                    )

                    if cur.rowcount:
                        result_user_id = cur.fetchone()[0]

        except Exception as e:
            logger.exception(e)

        if result_user_id:
            result = ControllerDatabase.get_user(result_user_id)

        return result

    @staticmethod
    def check_if_user_email_taken(user_email: str) -> bool:
        """
        Checks if a username is taken
        :param user_email: the users email
        :return: True if the username is taken else False
        """
        result = True
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
                        "SELECT "
                        "   user_id, "
                        "   user_uuid, "
                        "   user_name, "
                        "   user_email, "
                        "   hashed_password, "
                        "   password_salt, "
                        "   email_verified, "
                        "   modified, "
                        "   created, "
                        "   is_deleted "
                        "FROM users "
                        f"{query_str}",
                        parameters
                    )
                    (
                        user_id,
                        user_uuid,
                        user_name,
                        user_email,
                        hashed_password,
                        password_salt,
                        email_verified,
                        modified,
                        created,
                        is_deleted
                    ) = cur.fetchone()

            result = User(
                user_id=user_id,
                user_uuid=str(user_uuid),
                user_name=user_name,
                user_email=user_email,
                hashed_password=hashed_password,
                password_salt=password_salt,
                email_verified=email_verified,
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

    @staticmethod
    def get_user(user_id: int) -> User:
        query_str = "WHERE user_id = %(user_id)s " \
                    "AND is_deleted = false "
        parameters = {"user_id": user_id}

        user = ControllerDatabase.get_user_by_query(query_str, parameters)

        return user

    @staticmethod
    def get_user_by_uuid(user_uuid: str) -> User:
        query_str = "WHERE user_uuid = %(user_uuid)s " \
                    "AND is_deleted = false "
        parameters = {"user_uuid": user_uuid}

        user = ControllerDatabase.get_user_by_query(query_str, parameters)

        return user

    @staticmethod
    def get_user_id_by_uuid(user_uuid: str) -> int:
        """
        Used for getting the id of a user
        :param user_uuid: the uuid of the friend request
        :return: the id of the user
        """
        result = 0

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT user_id "
                        "FROM users "
                        "WHERE user_uuid = %(user_uuid)s "
                        "AND is_deleted = false ",
                        {"user_uuid", user_uuid}
                    )

                    if cur.rowcount:
                        (result, ) = cur.fetchone()

        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_token_by_query(query_str: str, parameters: dict) -> Token:
        """
        Used for getting a session token with a query
        :param parameters: A dictionary of values vor the query
        :param query_str: The WHERE query
        :return: a Token model
        """
        result = Token()

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT token_id, token_uuid, user_user_id, created, is_deleted "
                        "FROM tokens "
                        f"{query_str}",
                        parameters
                    )

                    if cur.rowcount:
                        token_id, token_uuid, user_user_id, created, is_deleted = cur.fetchone()

                        result = Token(
                            token_id=token_id,
                            token_uuid=str(token_uuid),
                            user_user_id=user_user_id,
                            created=created,
                            is_deleted=is_deleted,
                        )
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_token(token_id: int) -> Token:
        query_str = "WHERE token_id = %(token_id)s " \
                    "AND is_deleted = false "
        parameters = {"token_id": token_id}

        token = ControllerDatabase.get_token_by_query(query_str, parameters)

        return token

    @staticmethod
    def get_token_by_uuid(token_uuid: str) -> Token:
        query_str = "WHERE token_uuid = %(token_uuid)s " \
                    "AND is_deleted = false "
        parameters = {"token_uuid": token_uuid}

        token = ControllerDatabase.get_token_by_query(query_str, parameters)

        return token

    @staticmethod
    def insert_token(token: Token) -> Token:
        """
        Used for inserting a token into the database
        :param token: the token to insert
        :return: The token
        """
        result = None

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO tokens "
                        "(user_user_id) "
                        "values (%(user_user_id)s) "
                        "RETURNING token_id",
                        token.to_dict()
                    )
                    token_id = cur.fetchone()[0]
            result = ControllerDatabase.get_token(token_id)
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def delete_token(token: Token) -> bool:
        """
        Used for deleting a playlist
        :param token: the token to be deleted
        :return: bool of weather or not the deletion was successful
        """
        result = False

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE tokens "
                        "SET is_deleted = true "
                        "WHERE (token_id = %(token_id)s AND is_deleted = false) ",
                        token.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def set_user_email_verified(user: User) -> bool:
        """
        Used for verifying a users email
        :param user: the user whose email must be verified
        :return: bool of weather or not the update was successful
        """
        result = False

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE users "
                        "SET email_verified = true "
                        "WHERE (user_id = %(user_id)s AND is_deleted = false) ",
                        user.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_friend_request_by_query(query_str: str, parameters: dict) -> FriendRequest:
        """
        Used for getting a friend request with a query
        :param parameters: A dictionary of values vor the query
        :param query_str: The WHERE query
        :return: a User model
        """
        result = None

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT "
                        "   friend_request_id, "
                        "   sender_user_id, "
                        "   friend_request_uuid, "
                        "   receiver_user_id, "
                        "   is_accepted, "
                        "   modified, "
                        "   created, "
                        "   is_deleted "
                        "FROM friend_requests "
                        f"{query_str}",
                        parameters
                    )
                    (
                        friend_request_id,
                        friend_request_uuid,
                        sender_user_id,
                        receiver_user_id,
                        is_accepted,
                        modified,
                        created,
                        is_deleted,
                    ) = cur.fetchone()

            result = FriendRequest(
                friend_request_id=friend_request_id,
                friend_request_uuid=friend_request_uuid,
                sender_user_id=sender_user_id,
                receiver_user_id=receiver_user_id,
                is_accepted=is_accepted,
                modified=modified,
                created=created,
                is_deleted=is_deleted,
            )
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_friend_request(friend_request_id: int) -> FriendRequest:
        query_str = "WHERE friend_request_id = %(friend_request_id)s " \
                    "AND is_deleted = false "
        parameters = {"friend_request_id": friend_request_id}

        user = ControllerDatabase.get_friend_request_by_query(query_str, parameters)

        return user

    @staticmethod
    def get_friend_request_by_uuid(friend_request_uuid: str) -> FriendRequest:
        query_str = "WHERE friend_request_uuid = %(friend_request_uuid)s " \
                    "AND is_deleted = false "
        parameters = {"friend_request_uuid": friend_request_uuid}

        user = ControllerDatabase.get_friend_request_by_query(query_str, parameters)

        return user

    @staticmethod
    def insert_friend_request(friend_request: FriendRequest) -> bool:
        """
        Used for inserting a friend request into the database
        :param friend_request: the friend request to insert
        :return: bool of weather or not the insertion was successful
        """
        result = False

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO friend_requests "
                        "(sender_user_id, receiver_user_id) "
                        "values (%(sender_user_id)s, %(receiver_user_id)s) ",
                        friend_request.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def delete_friend_request(friend_request: FriendRequest) -> bool:
        """
        Used for deleting a friend request
        :param friend_request: the friend request to be deleted
        :return: bool of weather or not the deletion was successful
        """
        result = False

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE friend_requests "
                        "SET is_deleted = true "
                        "WHERE (friend_request_id = %(friend_request_id)s "
                        "AND is_deleted = false) ",
                        friend_request.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def accept_friend_request(friend_request: FriendRequest) -> bool:
        """
        Used for accepting a friend request
        :param friend_request: the friend request to be deleted
        :return: bool of weather or not the deletion was successful
        """
        result = False

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE friend_requests "
                        "SET is_accepted = true "
                        "WHERE (friend_request_id = %(friend_request_id)s "
                        "AND is_deleted = false) ",
                        friend_request.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_friend_request_id_by_uuid(friend_request_uuid: str) -> int:
        """
        Used for getting the id of a friend request
        :param friend_request_uuid: the uuid of the friend request
        :return: the id of the friend request
        """
        result = 0

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT friend_request_id "
                        "FROM friend_requests "
                        "WHERE friend_request_uuid = %(friend_request_uuid)s "
                        "AND is_deleted = false ",
                        {"friend_request_uuid", friend_request_uuid}
                    )

                    if cur.rowcount:
                        (result,) = cur.fetchone()

        except Exception as e:
            logger.exception(e)

        return result
