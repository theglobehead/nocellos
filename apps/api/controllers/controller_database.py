import datetime
from typing import List, Dict

from models.card import Card
from models.deck import Deck
from models.friend_request import FriendRequest
from models.label import Label
from models.study_set import StudySet
from models.token import Token
from models.user import User
from models.xp import Xp
from utils.common_utils import CommonUtils
from loguru import logger


class ControllerDatabase:
    #  Functions for users table
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
                        "(user_name, user_email, hashed_password, password_salt, email_verified) "
                        "values "
                        "   (%(user_name)s, "
                        "   %(user_email)s, "
                        "   %(hashed_password)s, "
                        "   %(password_salt)s, "
                        "   %(email_verified)s"
                        ") "
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
                        "   random_id, "
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
                        random_id,
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
                random_id=random_id,
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
                        {"user_uuid": user_uuid}
                    )

                    if cur.rowcount:
                        (result, ) = cur.fetchone()

        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def load_searched_users(search_phrase: str, search_page: int = 1) -> List[Dict]:
        page_size = 10
        search_page -= 1
        page_offset = page_size*search_page
        result = []

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT DISTINCT user_uuid, user_name, random_id "
                        "FROM users "
                        "WHERE (user_name = %(search_phrase)s "
                        "OR user_email = %(search_phrase)s) "
                        "AND is_deleted = false "
                        "OFFSET %(page_offset)s "
                        "LIMIT %(page_size)s ",
                        {
                            "search_phrase": search_phrase,
                            "page_size": page_size,
                            "page_offset": page_offset,
                        }
                    )

                    for user_uuid, user_name, random_id in cur.fetchall():
                        result.append({
                            "user_uuid": user_uuid,
                            "user_name": user_name,
                            "random_id": random_id,
                        })

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

    #  Functions for tokens table
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
        token_uuid = token_uuid.replace("Bearer ", "")
        
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
    def get_user_id_by_token_uuid(token_uuid: str) -> int:
        """
        Used for deleting a playlist
        :param token_uuid: the uuid of the token
        :return: bool of weather or not the deletion was successful
        """
        result = 0
        token_uuid = token_uuid.replace("Bearer ", "")

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT u.user_id "
                        "FROM users as u "
                        "INNER JOIN tokens as t "
                        "ON t.user_user_id = u.user_id "
                        "WHERE t.token_uuid = %(token_uuid)s "
                        "AND u.is_deleted = false "
                        "AND t.is_deleted = false ",
                        {"token_uuid": token_uuid}
                    )

                    if cur.rowcount:
                        (result, ) = cur.fetchone()
        except Exception as e:
            logger.exception(e)

        return result

    #  Functions for friend_requests table
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
                        sender_user_id,
                        friend_request_uuid,
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
    def get_user_friend_requests(user_id, is_accepted: bool) -> List[FriendRequest]:
        """
        Used for getting friend_requests of a user.
        :param user_id: The id of the user
        :param is_accepted: If true, it gets the users friends
        :return: A list of FriendRequest objects
        """
        friend_requests = []

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT "
                        "   friend_request_id, "
                        "   sender_user_id, "
                        "   receiver_user_id, "
                        "   is_accepted, "
                        "   modified, "
                        "   created, "
                        "   is_deleted, "
                        "   friend_request_uuid "
                        "FROM friend_requests "
                        "WHERE (sender_user_id = %(user_id)s "
                        "OR receiver_user_id = %(user_id)s) "
                        "AND is_deleted = false "
                        "AND is_accepted = %(is_accepted)s ",
                        {
                            "user_id": user_id,
                            "is_accepted": is_accepted,
                        }
                    )
                    for (
                        friend_request_id,
                        sender_user_id,
                        receiver_user_id,
                        is_accepted,
                        modified,
                        created,
                        is_deleted,
                        friend_request_uuid,
                    ) in cur.fetchall():
                        friend_requests.append(FriendRequest(
                            friend_request_id,
                            sender_user_id=sender_user_id,
                            receiver_user_id=receiver_user_id,
                            is_accepted=is_accepted,
                            modified=modified,
                            created=created,
                            is_deleted=is_deleted,
                            friend_request_uuid=friend_request_uuid,
                        ))
        except Exception as e:
            logger.exception(e)

        return friend_requests

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
                        {"friend_request_uuid": friend_request_uuid}
                    )

                    if cur.rowcount:
                        (result,) = cur.fetchone()

        except Exception as e:
            logger.exception(e)

        return result

    #  Functions for decks table
    @staticmethod
    def insert_deck(deck: Deck) -> Deck:
        """
        Used for creating a new deck
        :param deck: the deck to insert
        :return: The inserted deck as a Deck model
        """
        result = None
        result_deck_id = 0
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO decks "
                        "(deck_name, creator_user_id, is_in_set, is_public) "
                        "values (%(deck_name)s, %(creator_user_id)s, %(is_in_set)s, %(is_public)s) "
                        "RETURNING deck_id ",
                        deck.to_dict()
                    )

                    if cur.rowcount:
                        result_deck_id = cur.fetchone()[0]

        except Exception as e:
            logger.exception(e)

        if result_deck_id:
            result = ControllerDatabase.get_deck(result_deck_id)

        return result

    @staticmethod
    def get_deck_by_query(query_str: str, parameters: dict) -> Deck:
        """
        Used for getting a deck with a query
        :param parameters: A dictionary of values vor the query
        :param query_str: The WHERE query
        :return: a Deck model
        """
        result = None

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT "
                        "   deck_id, "
                        "   deck_name, "
                        "   deck_uuid, "
                        "   created, "
                        "   modified, "
                        "   is_deleted, "
                        "   creator_user_id, "
                        "   is_in_set, "
                        "   is_public "
                        "FROM decks "
                        f"{query_str}",
                        parameters
                    )
                    (
                        deck_id,
                        deck_name,
                        deck_uuid,
                        created,
                        modified,
                        is_deleted,
                        creator_user_id,
                        is_in_set,
                        is_public,
                    ) = cur.fetchone()

            result = Deck(
                deck_id=deck_id,
                deck_name=deck_name,
                deck_uuid=deck_uuid,
                created=created,
                modified=modified,
                is_deleted=is_deleted,
                creator_user_id=creator_user_id,
                is_in_set=is_in_set,
                is_public=is_public,
            )

        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_deck(deck_id: int) -> Deck:
        query_str = "WHERE deck_id = %(deck_id)s " \
                    "AND is_deleted = false "
        parameters = {"deck_id": deck_id}

        deck = ControllerDatabase.get_deck_by_query(query_str, parameters)

        return deck

    @staticmethod
    def get_deck_by_uuid(deck_uuid: str) -> Deck:
        query_str = "WHERE deck_uuid = %(deck_uuid)s " \
                    "AND is_deleted = false "
        parameters = {"deck_uuid": deck_uuid}

        deck = ControllerDatabase.get_deck_by_query(query_str, parameters)

        return deck

    @staticmethod
    def get_user_decks(user_id: int, is_owner: bool = False) -> List[Deck]:
        """
        Used for getting a users decks
        :param user_id: The id of the deck
        :param is_owner: Boolean of weather or not to show non-public cards
        :return: a lists of Deck models
        """
        decks = []
        show_public_str = "AND is_public = true "
        if is_owner:
            show_public_str = ""

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT "
                        "   deck_id, "
                        "   deck_name, "
                        "   deck_uuid, "
                        "   d.created, "
                        "   d.modified, "
                        "   d.is_deleted, "
                        "   creator_user_id, "
                        "   is_in_set, "
                        "   is_public, "
                        "   study_set_study_set_id "
                        "FROM decks as d "
                        "LEFT JOIN decks_in_users as d_in_u "
                        "ON d_in_u.deck_deck_id = d.deck_id "
                        "WHERE ((d_in_u.user_user_id = %(user_id)s "
                        "AND d_in_u.is_deleted = false)"
                        "OR (d.creator_user_id = %(user_id)s))"
                        "AND d.is_deleted = false "
                        f"{ show_public_str }",
                        {"user_id": user_id}
                    )
                    for (
                        deck_id,
                        deck_name,
                        deck_uuid,
                        created,
                        modified,
                        is_deleted,
                        creator_user_id,
                        is_in_set,
                        is_public,
                        study_set_study_set_id
                    ) in cur.fetchall():
                        new_deck = Deck(
                            deck_id=deck_id,
                            deck_name=deck_name,
                            deck_uuid=deck_uuid,
                            created=created,
                            modified=modified,
                            is_deleted=is_deleted,
                            creator_user_id=creator_user_id,
                            is_in_set=is_in_set,
                            is_public=is_public,
                        )
                        new_deck.card_count = ControllerDatabase.get_deck_card_count_w_cur(
                            cur, deck_id
                        )
                        new_deck.labels = ControllerDatabase.get_deck_labels_w_cur(
                            cur, deck_id
                        )
                        decks.append(new_deck)

        except Exception as e:
            logger.exception(e)

        return decks

    @staticmethod
    def get_deck_card_count_w_cur(cur, deck_id: int) -> int:
        """
        Used for counting cards in a deck
        :param cur: psycopg2 cursor
        :param deck_id: id of the deck
        :return: count of non deleted cards in the deck
        """
        count = 0
        cur.execute(
            "SELECT COUNT(*) "
            "FROM cards "
            "WHERE deck_deck_id = %(deck_id)s "
            "AND is_deleted = false ",
            {"deck_id": deck_id}
        )

        if cur.rowcount:
            (count, ) = cur.fetchone()

        return count

    @staticmethod
    def delete_deck(deck: Deck) -> bool:
        """
        Used for deleting a deck
        :param deck: the deck to be deleted
        :return: bool of weather or not the deletion was successful
        """
        result = False

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE decks "
                        "SET is_deleted = true "
                        "WHERE (deck_id = %(deck_id)s AND is_deleted = false) ",
                        deck.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    #  Functions for cards table
    @staticmethod
    def insert_card(card: Card) -> Card:
        """
        Used for creating a new card
        :param card: the card to insert
        :return: bool of weather or not the insert was successful
        """
        result = None
        result_card_id = 0
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO cards "
                        "(front_text, back_text, deck_deck_id) "
                        "values (%(front_text)s, %(back_text)s, %(deck_deck_id)s) "
                        "RETURNING card_id ",
                        card.to_dict()
                    )

                    if cur.rowcount:
                        result_card_id = cur.fetchone()[0]

        except Exception as e:
            logger.exception(e)

        if result_card_id:
            result = ControllerDatabase.get_card(result_card_id)

        return result

    @staticmethod
    def get_card_by_query(query_str: str, parameters: dict) -> Card:
        """
        Used for getting a card with a query
        :param parameters: A dictionary of values vor the query
        :param query_str: The WHERE query
        :return: a Card model
        """
        result = None

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT "
                        "   card_id, "
                        "   front_text, "
                        "   back_text, "
                        "   card_uuid, "
                        "   created, "
                        "   modified, "
                        "   is_deleted, "
                        "   deck_deck_id "
                        "FROM cards "
                        f"{query_str}",
                        parameters
                    )
                    (
                        card_id,
                        front_text,
                        back_text,
                        card_uuid,
                        created,
                        modified,
                        is_deleted,
                        deck_deck_id,
                    ) = cur.fetchone()

            result = Card(
                card_id=card_id,
                front_text=front_text,
                back_text=back_text,
                card_uuid=card_uuid,
                created=created,
                modified=modified,
                is_deleted=is_deleted,
                deck_deck_id=deck_deck_id,
            )
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_card(card_id: int) -> Card:
        query_str = "WHERE card_id = %(card_id)s " \
                    "AND is_deleted = false "
        parameters = {"card_id": card_id}

        card = ControllerDatabase.get_card_by_query(query_str, parameters)

        return card

    @staticmethod
    def get_card_by_uuid(card_uuid: str) -> Card:
        query_str = "WHERE card_uuid = %(card_uuid)s " \
                    "AND is_deleted = false "
        parameters = {"card_uuid": card_uuid}

        card = ControllerDatabase.get_card_by_query(query_str, parameters)

        return card

    @staticmethod
    def get_deck_cards(deck_id: int) -> List[Card]:
        """
        Used for getting a cards from a certain deck
        :param deck_id: The id of the deck
        :return: a lists of Card models
        """
        cards = []
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT "
                        "   card_id, "
                        "   front_text, "
                        "   back_text, "
                        "   card_uuid, "
                        "   created, "
                        "   modified, "
                        "   is_deleted, "
                        "   deck_deck_id "
                        "FROM cards "
                        "WHERE deck_deck_id = %(deck_deck_id)s "
                        "AND is_deleted = false ",
                        {"deck_deck_id": deck_id}
                    )
                    for (
                        card_id,
                        front_text,
                        back_text,
                        card_uuid,
                        created,
                        modified,
                        is_deleted,
                        deck_deck_id,
                    ) in cur.fetchall():
                        new_card = Card(
                            card_id=card_id,
                            front_text=front_text,
                            back_text=back_text,
                            card_uuid=card_uuid,
                            created=created,
                            modified=modified,
                            is_deleted=is_deleted,
                            deck_deck_id=deck_deck_id,
                        )
                        cards.append(new_card)

        except Exception as e:
            logger.exception(e)

        return cards

    @staticmethod
    def delete_card(card: Card) -> bool:
        """
        Used for deleting a card
        :param card: the card to be deleted
        :return: bool of weather or not the deletion was successful
        """
        result = False

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE cards "
                        "SET is_deleted = true "
                        "WHERE (card_id = %(card_id)s AND is_deleted = false) ",
                        card.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def edit_card(card: Card) -> Card:
        """
        Used for getting a card with a query
        :param card: Card model. Used for getting the card_uuid, front_text, back_text
        :return: a Card model
        """
        result = Card()
        card_id = 0

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE cards "
                        "SET front_text = %(front_text)s, back_text = %(back_text)s "
                        "WHERE card_uuid = %(card_uuid)s "
                        "OR card_id = %(card_id)s "
                        "RETURNING card_id ",
                        card.to_dict()
                    )

                    (card_id, ) = cur.fetchone()
            result = ControllerDatabase.get_card(card_id)
        except Exception as e:
            logger.exception(e)

        return result

    #  Functions for study_sets table
    @staticmethod
    def insert_study_set(study_set: StudySet) -> StudySet:
        """
        Used for creating a new study_set
        :param study_set: the study_set to insert
        :return: bool of weather or not the insert was successful
        """
        result = None
        result_study_set_id = 0
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO study_sets "
                        "(creator_user_id, study_set_name, is_public) "
                        "values (%(creator_user_id)s, %(study_set_name)s, %(is_public)s) "
                        "RETURNING study_set_id ",
                        study_set.to_dict()
                    )

                    if cur.rowcount:
                        result_study_set_id = cur.fetchone()[0]

        except Exception as e:
            logger.exception(e)

        if result_study_set_id:
            result = ControllerDatabase.get_study_set(result_study_set_id)

        return result

    @staticmethod
    def get_study_set_by_query(query_str: str, parameters: dict) -> StudySet:
        """
        Used for getting a study_set with a query
        :param parameters: A dictionary of values vor the query
        :param query_str: The WHERE query
        :return: a StudySet model
        """
        result = None

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT "
                        "   study_set_id, "
                        "   creator_user_id, "
                        "   created, "
                        "   modified, "
                        "   is_deleted, "
                        "   study_set_name, "
                        "   is_public,"
                        "   study_set_uuid "
                        "FROM study_sets "
                        f"{query_str}",
                        parameters
                    )
                    (
                        study_set_id,
                        creator_user_id,
                        created,
                        modified,
                        is_deleted,
                        study_set_name,
                        is_public,
                        study_set_uuid,
                    ) = cur.fetchone()

            result = StudySet(
                study_set_id=study_set_id,
                creator_user_id=creator_user_id,
                created=created,
                modified=modified,
                is_deleted=is_deleted,
                study_set_name=study_set_name,
                is_public=is_public,
                study_set_uuid=study_set_uuid,
            )
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_study_set(study_set_id: int) -> StudySet:
        query_str = "WHERE study_set_id = %(study_set_id)s " \
                    "AND is_deleted = false "
        parameters = {"study_set_id": study_set_id}

        study_set = ControllerDatabase.get_study_set_by_query(query_str, parameters)

        return study_set

    @staticmethod
    def get_study_set_by_uuid(study_set_uuid: str) -> StudySet:
        query_str = "WHERE study_set_uuid = %(study_set_uuid)s " \
                    "AND is_deleted = false "
        parameters = {"study_set_uuid": study_set_uuid}

        study_set = ControllerDatabase.get_study_set_by_query(query_str, parameters)

        return study_set
    
    @staticmethod
    def invite_user_to_study_set(study_set_id: int, user_id: int, can_edit: bool) -> bool:
        """
        Used for creating a new study_set
        :param study_set_id: the id of the study set
        :param user_id: the id of the invited user
        :return: bool of weather or not the insert was successful
        """
        result = False
        
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO study_sets_in_users "
                        "(study_set_study_set_id, user_user_id, can_edit) "
                        "VALUES (%(study_set_id)s, %(user_id)s, %(can_edit)s) "
                        "RETURNING study_set_study_set_id ",
                        {
                            "study_set_id": study_set_id,
                            "user_id": user_id,
                            "can_edit": can_edit,
                        }
                    )
            
                    if cur.rowcount:
                        result = True

        except Exception as e:
            logger.exception(e)
            
        return result
    
    @staticmethod
    def remove_user_from_study_set(study_set_id: int, user_id: int) -> bool:
        """
        Used for creating a new study_set
        :param study_set_id: the id of the study set
        :param user_id: the id of the invited user
        :return: bool of weather or not the insert was successful
        """
        result = False
        
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE study_sets_in_users "
                        "SET modified = now(), "
                        "is_deleted = true "
                        "WHERE user_user_id = %(user_id)s "
                        "AND study_set_study_set_id = %(study_set_id)s ",
                        {
                            "study_set_id": study_set_id,
                            "user_id": user_id,
                        }
                    )
                
                    if cur.rowcount:
                        result = True
    
        except Exception as e:
            logger.exception(e)
            
        return result

    @staticmethod
    def get_user_study_sets(user_id: int, is_owner: bool = False) -> List[StudySet]:
        """
        Used for getting a users study_sets
        :param user_id: The id of the user
        :param is_owner: Boolean of weather or not to show non-public cards
        :return: a lists of StudySet models
        """
        study_sets = []
        show_public_str = "AND is_public = true "
        if is_owner:
            show_public_str = ""

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT "
                        "   s.study_set_id, "
                        "   s.creator_user_id, "
                        "   s.created, "
                        "   s.modified, "
                        "   s.is_deleted, "
                        "   s.study_set_name, "
                        "   s.is_public, "
                        "   s.study_set_uuid "
                        "FROM study_sets as s "
                        "LEFT JOIN study_sets_in_users as s_in_u "
                        "ON s_in_u.study_set_study_set_id = s.study_set_id "
                        "WHERE ((s_in_u.user_user_id = %(user_id)s "
                        "AND s_in_u.is_deleted = false)"
                        "OR (s.creator_user_id = %(user_id)s))"
                        "AND s.is_deleted = false "
                        f"{ show_public_str }",
                        {"user_id": user_id}
                    )
                    for (
                        study_set_id,
                        creator_user_id,
                        created,
                        modified,
                        is_deleted,
                        study_set_name,
                        is_public,
                        study_set_uuid,
                    ) in cur.fetchall():
                        new_study_sets = StudySet(
                            study_set_id=study_set_id,
                            creator_user_id=creator_user_id,
                            created=created,
                            modified=modified,
                            is_deleted=is_deleted,
                            study_set_name=study_set_name,
                            is_public=is_public,
                            study_set_uuid=study_set_uuid,
                        )
                        new_study_sets.labels = ControllerDatabase.get_study_set_labels_w_cur(
                            cur, study_set_id
                        )
                        new_study_sets.deck_count = ControllerDatabase.get_study_set_deck_count(
                            cur, study_set_id
                        )
                        study_sets.append(new_study_sets)
        except Exception as e:
            logger.exception(e)

        return study_sets

    @staticmethod
    def get_study_set_deck_count(cur, study_set_id: int) -> int:
        """
        Used for counting deck in a study set
        :param cur: psycopg2 cursor
        :param study_set_id: id of the study_set
        :return: count of non deleted decks in the study set
        """
        count = 0

        cur.execute(
            "SELECT COUNT(*) "
            "FROM decks "
            "WHERE study_set_study_set_id = %(study_set_id)s "
            "AND is_deleted = false ",
            {"study_set_id": study_set_id}
        )

        if cur.rowcount:
            (count, ) = cur.fetchone()

        return count

    @staticmethod
    def delete_study_set(study_set: StudySet) -> bool:
        """
        Used for deleting a study_set
        :param study_set: the study_set to be deleted
        :return: bool of weather or not the deletion was successful
        """
        result = False

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE study_sets "
                        "SET is_deleted = true "
                        "WHERE (study_set_id = %(study_set_id)s AND is_deleted = false) ",
                        study_set.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    #  Functions for labels table
    @staticmethod
    def insert_label(label: Label) -> Label:
        """
        Used for creating a new label
        :param label: the label to insert
        :return: bool of weather or not the insert was successful
        """
        result = None
        result_label_id = 0

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO labels "
                        "(label_name) "
                        "values (%(label_name)s) "
                        "RETURNING label_id ",
                        label.to_dict()
                    )

                    if cur.rowcount:
                        result_label_id = cur.fetchone()[0]

        except Exception as e:
            logger.exception(e)

        if result_label_id:
            result = ControllerDatabase.get_label(result_label_id)

        return result

    @staticmethod
    def get_label_by_query(query_str: str, parameters: dict) -> Label:
        """
        Used for getting a label with a query
        :param parameters: A dictionary of values vor the query
        :param query_str: The WHERE query
        :return: a Label model
        """
        result = None

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT "
                        "   label_id, "
                        "   label_name, "
                        "   modified, "
                        "   created, "
                        "   is_deleted "
                        "FROM labels "
                        f"{query_str}",
                        parameters
                    )

                    if cur.rowcount:
                        (
                            label_id,
                            label_name,
                            modified,
                            created,
                            is_deleted,
                        ) = cur.fetchone()

                        result = Label(
                            label_id=label_id,
                            label_name=label_name,
                            modified=modified,
                            created=created,
                            is_deleted=is_deleted,
                        )
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_label(label_id: int) -> Label:
        query_str = "WHERE label_id = %(label_id)s " \
                    "AND is_deleted = false "
        parameters = {"label_id": label_id}

        user = ControllerDatabase.get_label_by_query(query_str, parameters)

        return user

    @staticmethod
    def get_label_by_name(label_name: str) -> Label:
        query_str = "WHERE label_name = %(label_name)s " \
                    "AND is_deleted = false "
        parameters = {"label_name": label_name}

        user = ControllerDatabase.get_label_by_query(query_str, parameters)

        return user

    @staticmethod
    def delete_label(label: Label) -> bool:
        """
        Used for deleting a label
        :param label: the label to be deleted
        :return: bool of weather or not the deletion was successful
        """
        result = False

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE labels "
                        "SET is_deleted = true "
                        "WHERE (label_id = %(label_id)s AND is_deleted = false) ",
                        label.to_dict()
                    )
                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def get_deck_labels_w_cur(cur, deck_id: int) -> List[Label]:
        """
        Used for getting the labels in a deck
        :param cur: psycopg2 cursor
        :param deck_id: the id of the deck
        :return: A list of label objects belonging to the deck
        """
        labels = []

        cur.execute(
            "SELECT DISTINCT label_id, label_name, l.modified, l.created, l.is_deleted "
            "FROM labels AS l "
            "INNER JOIN labels_in_decks AS l_in_d "
            "ON l.label_id = l_in_d.label_label_id "
            "WHERE deck_deck_id = %(deck_id)s "
            "AND l_in_d.is_deleted = false ",
            {"deck_id": deck_id}
        )

        for label_id, label_name, modified, created, is_deleted in cur.fetchall():
            new_label = Label(
                label_id=label_id,
                label_name=label_name,
                modified=modified,
                created=created,
                is_deleted=is_deleted,
            )
            labels.append(new_label)

        return labels

    @staticmethod
    def get_study_set_labels_w_cur(cur, study_set_id: int) -> List[Label]:
        """
        Used for getting the labels in a study_set
        :param cur: psycopg2 cursor
        :param study_set_id: the id of the study_set
        :return: A list of label objects belonging to the study_set
        """
        labels = []

        cur.execute(
            "SELECT DISTINCT label_id, label_name, l.modified, l.created, l.is_deleted "
            "FROM labels AS l "
            "INNER JOIN labels_in_study_sets AS l_in_s "
            "ON l.label_id = l_in_s.label_label_id "
            "WHERE study_set_study_set_id = %(study_set_id)s "
            "AND l_in_s.is_deleted = false ",
            {"study_set_id": study_set_id}
        )

        for label_id, label_name, modified, created, is_deleted in cur.fetchall():
            new_label = Label(
                label_id=label_id,
                label_name=label_name,
                modified=modified,
                created=created,
                is_deleted=is_deleted,
            )
            labels.append(new_label)

        return labels

    @staticmethod
    def add_label_to_deck(deck_id: int, label_name: str) -> bool:
        result = False

        label = ControllerDatabase.get_label_by_name(label_name)

        if not label or (label and not label.label_id):
            label = ControllerDatabase.insert_label(Label(label_name=label_name))

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT label_in_deck_id "
                        "FROM labels_in_decks as l_in_d "
                        "INNER JOIN labels as l "
                        "ON l.label_id = l_in_d.label_label_id "
                        "WHERE label_name = %(label_name)s "
                        "AND l_in_d.is_deleted = false",
                        {"label_name": label_name}
                    )

                    if not cur.rowcount:
                        cur.execute(
                            "INSERT INTO labels_in_decks "
                            "(label_label_id, deck_deck_id) "
                            "values (%(label_id)s, %(deck_id)s) ",
                            {
                                "label_id": label.label_id,
                                "deck_id": deck_id,
                            }
                        )

                    result = True
        except Exception as e:
            logger.exception(e)

        return result

    @staticmethod
    def add_label_to_study_set(study_set_id: int, label_name: str) -> bool:
        result = False

        label = ControllerDatabase.get_label_by_name(label_name)

        if not label or (label and not label.label_id):
            label = ControllerDatabase.insert_label(Label(label_name=label_name))

        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT label_in_study_set_id "
                        "FROM labels_in_study_sets as l_in_s "
                        "INNER JOIN labels as l "
                        "ON l.label_id = l_in_s.label_label_id "
                        "WHERE label_name = %(label_name)s "
                        "AND l_in_s.is_deleted = false",
                        {"label_name": label_name}
                    )

                    if not cur.rowcount:
                        cur.execute(
                            "INSERT INTO labels_in_study_sets "
                            "(label_label_id, study_set_study_set_id) "
                            "values (%(label_id)s, %(study_set_id)s) ",
                            {
                                "label_id": label.label_id,
                                "study_set_id": study_set_id,
                            }
                        )

                    result = True
        except Exception as e:
            logger.exception(e)

        return result
    
    # Functions for the xp table
    @staticmethod
    def update_user_xp(user_id: int, xp_count: int) -> bool:
        """
        Used for updating a users xp.
        If no xp earned today it creates a new xp row
        If already exists, it simply updates today's row
        :param user_id: the id of the user
        :param xp_count: the amount of xp earned
        :return: bool of weather or not everything was successful
        """
        result = False

        start_date = datetime.datetime.now().date()
        start_date = datetime.datetime.combine(start_date, datetime.time())
        
        todays_xp = ControllerDatabase.get_user_xp_in_timeframe(
            user_id, start_date, datetime.datetime.now()
        )
        
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    if todays_xp and len(todays_xp):
                        xp_id = todays_xp[0].xp_id
                        
                        cur.execute(
                            "UPDATE xp "
                            "SET xp_count = xp_count + %(xp_count)s "
                            "WHERE xp_id = %(xp_id)s ",
                            {
                                "xp_count": xp_count,
                                "xp_id": xp_id,
                            }
                        )
                    else:
                        cur.execute(
                            "INSERT INTO xp "
                            "(user_user_id, xp_count) "
                            "VALUES (%(user_id)s, %(xp_count)s) ",
                            {
                                "xp_count": xp_count,
                                "user_id": user_id,
                            }
                        )
                        
                    result = True
        except Exception as e:
            logger.exception(e)
            
        return result

    @staticmethod
    def get_user_xp_in_timeframe(
            user_id: int,
            start_date: datetime.datetime,
            end_date: datetime.datetime
    ) -> List[Xp]:
        """
        Used for updating a users xp.
        If no xp earned today it creates a new xp row
        If already exists, it simply updates today's row
        :param user_id: the id of the user
        :param start_date: the earliest date that can be fetched
        :param end_date: the latest date that can be fetched
        :return: the amount of xp earned
        """
        result = []
        
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT xp_id, created, xp_count "
                        "FROM xp "
                        "WHERE user_user_id = %(user_id)s "
                        "AND created > %(start_date)s "
                        "AND created < %(end_date)s "
                        "AND is_deleted = false ",
                        {
                            "user_id": user_id,
                            "start_date": start_date,
                            "end_date": end_date,
                        }
                    )
                    
                    for xp_id, created, xp_count in cur.fetchall():
                        result.append(Xp(
                            xp_id=xp_id,
                            created=created,
                            xp_count=xp_count,
                        ))
        except Exception as e:
            logger.exception(e)
    
        return result

    @staticmethod
    def get_user_xp_sum_in_timeframe(
            user_id: int,
            start_date: datetime.datetime = None,
            end_date: datetime.datetime = None
    ) -> int:
        """
        Used for getting the amount of xp a user has earned
        :param user_id: the id of the user
        :param start_date: the earliest date that can be fetched
        :param end_date: the latest date that can be fetched
        :return: the amount of xp earned
        """
        result = 0
        
        start_date_str = "AND created > %(start_date)s " if start_date else ""
        end_date_str = "AND created < %(end_date)s " if end_date else ""
    
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT SUM(xp_count) as xp_count "
                        "FROM xp "
                        "WHERE user_user_id = %(user_id)s "
                        f"{ start_date_str } "
                        f"{ end_date_str } "
                        "AND is_deleted = false ",
                        {
                            "user_id": user_id,
                            "start_date": start_date,
                            "end_date": end_date,
                        }
                    )
                    
                    if cur.rowcount:
                        (result, ) = cur.fetchone()
                        
                    if not result:
                        result = 0
            
        except Exception as e:
            logger.exception(e)
    
        return result

    @staticmethod
    def get_user_leader_board(
            user: User,
    ) -> List[User]:
        """
        Used for getting leaderboard data for a user
        :param user: the user
        :return: the amount of xp earned
        """
        result = [user]
    
        try:
            with CommonUtils.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT DISTINCT "
                        "   users.user_id,"
                        "   users.user_name,"
                        "   users.user_uuid, "
                        "   users.random_id "
                        "FROM users "
                        "FULL JOIN friend_requests sender_fr on users.user_id = sender_fr.sender_user_id "
                        "FULL JOIN friend_requests receiver_fr on users.user_id = receiver_fr.receiver_user_id "
                        "WHERE sender_fr.receiver_user_id = %(user_id)s "
                        "OR receiver_fr.sender_user_id = %(user_id)s ",
                        {
                            "user_id": user.user_id,
                        }
                    )

                    now = datetime.datetime.now()
                    week_start = now.date() - datetime.timedelta(days=now.weekday())
                    week_end = week_start + datetime.timedelta(days=6)
                    
                    result[0].xp_count = ControllerDatabase.get_user_xp_sum_in_timeframe(
                        user_id=result[0].user_id,
                        start_date=datetime.datetime.combine(week_start, datetime.time()),
                        end_date=datetime.datetime.combine(week_end, datetime.time()),
                    )
                    
                    for (user_id, user_name, user_uuid, random_id) in cur.fetchall():
                        xp_count = ControllerDatabase.get_user_xp_sum_in_timeframe(
                            user_id=user_id,
                            start_date=datetime.datetime.combine(week_start, datetime.time()),
                            end_date=datetime.datetime.combine(week_end, datetime.time()),
                        )

                        result.append(User(
                            user_id=user_id,
                            user_name=user_name,
                            user_uuid=user_uuid,
                            random_id=random_id,
                            xp_count=xp_count,
                        ))
                        
        except Exception as e:
            logger.exception(e)
    
        return result
