from typing import List, Dict

from models.card import Card
from models.deck import Deck
from models.friend_request import FriendRequest
from models.label import Label
from models.study_set import StudySet
from models.token import Token
from models.user import User
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
                        {"user_uuid", user_uuid}
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
                        "(deck_name, creator_user_id, is_in_set) "
                        "values (%(deck_name)s, %(creator_user_id)s, %(is_in_set)s) "
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
                        "   is_public, "
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
                        "   created, "
                        "   modified, "
                        "   is_deleted, "
                        "   creator_user_id, "
                        "   is_in_set, "
                        "   is_public "
                        "FROM decks "
                        "WHERE creator_user_id = %(user_id)s "
                        f"{ show_public_str }"
                        "AND is_deleted = false ",
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
                        decks.append(new_deck)

        except Exception as e:
            logger.exception(e)

        return decks

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
                        "   deck_deck_id, "
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
                        "   is_public "
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
                    ) = cur.fetchone()

            result = StudySet(
                study_set_id=study_set_id,
                creator_user_id=creator_user_id,
                created=created,
                modified=modified,
                is_deleted=is_deleted,
                study_set_name=study_set_name,
                is_public=is_public,
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
                        "   study_set_id, "
                        "   creator_user_id, "
                        "   created, "
                        "   modified, "
                        "   is_deleted, "
                        "   study_set_name, "
                        "   is_public "
                        "FROM study_sets "
                        "WHERE creator_user_id = %(user_id)s "
                        f"{show_public_str}"
                        "AND is_deleted = false ",
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
                    ) in cur.fetchall():
                        new_study_sets = StudySet(
                            study_set_id=study_set_id,
                            creator_user_id=creator_user_id,
                            created=created,
                            modified=modified,
                            is_deleted=is_deleted,
                            study_set_name=study_set_name,
                            is_public=is_public,
                        )
                        study_sets.append(new_study_sets)

        except Exception as e:
            logger.exception(e)

        return study_sets

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
                        "WHERE (study_set_id = %(token_id)s AND is_deleted = false) ",
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
                        "(label_id, label_name) "
                        "values (%(label_id)s, %(label_name)s) "
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
