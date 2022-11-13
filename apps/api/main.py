import datetime

import uvicorn
from fastapi import FastAPI, Form, status, Response, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from jinja2 import Environment, PackageLoader, select_autoescape

from loguru import logger

from controllers.constants import ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD, SERVER_NAME, ADMIN_EMAIL_USERNAME
from controllers.controller_database import ControllerDatabase
from controllers.controller_labels import ControllerLabels
from controllers.controller_user import ControllerUser
from models.card import Card
from models.deck import Deck
from models.friend_request import FriendRequest
from models.study_set import StudySet
from models.user import User
from web.register_page import validate_form

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


email_conf = ConnectionConfig(
    MAIL_USERNAME=ADMIN_EMAIL_USERNAME,
    MAIL_PASSWORD=ADMIN_EMAIL_PASSWORD,
    MAIL_FROM=ADMIN_EMAIL,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

jinja_env = Environment(
    loader=PackageLoader("main"),
    autoescape=select_autoescape()
)


@app.get("/verify_email/{user_uuid}", response_class=RedirectResponse, status_code=302)
async def verify_email(response: Response, user_uuid: str):
    """
    CURRENTLY NOT USED. TEMPORARILY REMOVED
    Used for verifying a users email.
    Sets is_email_verified in the bd to true.
    :param response: The fastapi response
    :param user_uuid: the uuid of the user
    :return: Sends the user to the login view
    """
    user = ControllerDatabase.get_user_by_uuid(user_uuid)
    is_successful = ControllerDatabase.set_user_email_verified(user)
    
    if is_successful:
        response.headers["token"] = user.token.token_uuid
        
    return "/"


# These post methods act as get methods, but they have forms
@app.post("/get_searched_users", status_code=status.HTTP_200_OK)
def get_searched_users(
        search_phrase: str = Form(...),
        search_page: int = Form(...),
):
    """
    Ajax endpoint for getting searched users
    :return: A list of dictionaries {
        "user_uuid": Str of the users uuid,
        "user_name": Str of the users name,
        "random_id": Int of the 4 random numbers "username #1234",
    }
    """

    result = ControllerDatabase.load_searched_users(
        search_phrase=search_phrase,
        search_page=search_page
    )

    return result


@app.post("/get_user_study_sets", status_code=status.HTTP_200_OK)
def get_user_study_sets(
        request: Request,
        user_uuid: str = Form(...),
):
    """
    Ajax endpoint for getting a users study sets
    :param user_uuid: the uuid of the user whose sets to get
    :param token_uuid: the token_uuid of the user who requested it
    :return: A list of dictionaries. Check below
    """
    token_uuid = request.headers.get("Authorization", default="").replace("Bearer ", "")
    study_sets = []
    user_id = ControllerDatabase.get_user_id_by_uuid(user_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    is_owner = requester_user_id == user_id and user_id

    for study_set in ControllerDatabase.get_user_study_sets(user_id, is_owner=is_owner):
        study_sets.append({
            "study_set_name": study_set.study_set_name,
            "study_set_uuid": study_set.study_set_uuid,
            "deck_count": study_set.deck_count,
            "is_public": study_set.is_public,
            "labels": ControllerLabels.labels_to_dict(labels=study_set.labels),
        })

    return {"study_sets": study_sets}


@app.post("/get_user_decks", status_code=status.HTTP_200_OK)
def get_user_decks(
        user_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for getting a users decks
    :param user_uuid: the uuid of the user whose sets to get
    :param token_uuid: the token_uuid of the user who requested it
    :return: A list of dictionaries. Check below
    """
    decks = []
    user_id = ControllerDatabase.get_user_id_by_uuid(user_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    is_owner = requester_user_id == user_id and user_id

    for deck in ControllerDatabase.get_user_decks(user_id, is_owner=is_owner):
        decks.append({
            "deck_name": deck.deck_name,
            "deck_uuid": deck.deck_uuid,
            "card_count": deck.card_count,
            "is_public": deck.is_public,
            "labels": ControllerLabels.labels_to_dict(labels=deck.labels),
        })

    return {"decks": decks}


@app.post("/get_deck_details", status_code=status.HTTP_200_OK)
def get_deck_details(
        response: Response,
        deck_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for getting the details of a deck
    :param response: The fastapi response
    :param deck_uuid: uuid of the deck
    :param token_uuid: the token_uuid of the user who requested it
    :return: A dictionary. Check below
    
    }
    """
    deck_dict = {}

    deck = ControllerDatabase.get_deck_by_uuid(deck_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    
    # Check if user has permission
    if requester_user_id != deck.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return

    cards = []
    for card in ControllerDatabase.get_deck_cards(deck.deck_id):
        cards.append({
            "card_uuid": card.card_uuid,
            "front_text": card.front_text,
            "back_text": card.back_text,
        })
        
    deck_dict = {
        "deck_name": deck.deck_name,
        "deck_uuid": deck.deck_uuid,
        "card_count": deck.card_count,
        "is_public": deck.is_public,
        "labels": ControllerLabels.labels_to_dict(labels=deck.labels),
        "cards": cards,
    }

    return {"deck": deck_dict}


@app.post("/get_user_friend_requests", status_code=status.HTTP_200_OK)
def get_user_friend_requests(
        is_accepted: bool = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for getting a users friend_requests.
    It gets them from the friend_requests table.
    Can also be used to get a users friends, if is_accepted is true
    :param response: The fastapi response
    :param is_accepted: Are the friend requests accepted
    :param token_uuid: the token_uuid of the user who requested it
    :return: A list of dictionaries. Check below
    """
    friend_requests = []
    user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    for friend_request in ControllerDatabase.get_user_friend_requests(user_id=user_id, is_accepted=is_accepted):
        sender_user = ControllerDatabase.get_user(friend_request.sender_user_id)
        receiver_user = ControllerDatabase.get_user(friend_request.receiver_user_id)

        friend_requests.append({
            "friend_request_uuid": friend_request.friend_request_uuid,
            "sender_user_uuid": sender_user.user_uuid,
            "receiver_user_uuid": receiver_user.user_uuid,
        })

    return {"friend_requests": friend_requests}


@app.post("/get_user_info", status_code=status.HTTP_200_OK)
def get_user_friend_requests(
        user_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Used for getting basic info on the user
    Can also be used to get a users friends, if is_accepted is true
    :param user_uuid: The uuid of the user
    :param token_uuid: The uuid of the users token
    :return: A dictionary
    """
    user = ControllerDatabase.get_user_by_uuid(user_uuid)
    token_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid=token_uuid)
    
    email_str = ""
    if token_user_id == user.user_id:
        email_str = user.user_email

    user_dict = {
        "user_uuid": user.user_uuid,
        "user_name": user.user_name,
        "user_email": email_str,
        "random_id": user.random_id,
        "created": user.created.strftime("%Y/%m/%m"),
        "total_xp": ControllerDatabase.get_user_xp_sum_in_timeframe(user_id=user.user_id),
    }

    return {"user": user_dict}


@app.post("/get_user_xp", status_code=status.HTTP_200_OK)
def get_user_xp(
        user_uuid: str = Form(...),
        only_sum: bool = Form(...),
):
    """
    Used for getting a users xp in the last 7 days
    :param user_uuid: the user_uuid of the user
    :param only_sum: bool weather to send an integer or a list of integers
    :return: {"xp_count": int}
    """
    user_id = ControllerDatabase.get_user_id_by_uuid(user_uuid)
    xp_count = 0
    days = []
    
    start_date = datetime.datetime.now().date() - datetime.timedelta(days=6)
    start_date = datetime.datetime.combine(start_date, datetime.time())
    
    user_xp = ControllerDatabase.get_user_xp_in_timeframe(
        user_id=user_id,
        start_date=start_date,
        end_date=datetime.datetime.now(),
    )
    
    xp_int_list = list(map(lambda xp: xp.xp_count, user_xp))
    xp_count = sum(xp_int_list)
    
    if not only_sum:
        date_delta = datetime.datetime.now() - start_date
        for i in range(date_delta.days + 1):
            day_date = (start_date + datetime.timedelta(days=i)).date()
            day_xp = [xp.xp_count for xp in user_xp if xp.created.date() == day_date]
            
            day_xp_count = 0
            if len(day_xp):
                day_xp_count = day_xp[0]
            
            days.append({
                "date": day_date.strftime("%Y/%m/%d"),
                "xp_count": day_xp_count,
            })
    
    return {
        "xp_count": xp_count,
        "days": days,
    }


@app.post("/get_user_leaderboard", status_code=status.HTTP_200_OK)
def get_user_leaderboard(
        response: Response,
        user_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Used for getting a users xp in the last 7 days
    :param response: the fastapi response
    :param user_uuid: the user_uuid of the user
    :param token_uuid: the uuid of the users token
    :return: {
    "leader_board": [
            {
                "user_name": str,
                "user_uuid": str,
                "random_id": str,
                "xp_count": int,
            }
        ]
    }
    """
    leader_board = []
    user = ControllerDatabase.get_user_by_uuid(user_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    # Check if user has permission
    if requester_user_id != user.user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return
    
    user_friends = ControllerDatabase.get_user_leader_board(user)
    user_friends.append(user)
    
    for user_friend in user_friends:
        leader_board.append({
            "user_name": user_friend.user_name,
            "user_uuid": user_friend.user_uuid,
            "random_id": user_friend.random_id,
            "xp_count": user_friend.xp_count,
        })
    
    return {
        "leader_board": leader_board
    }


# Methods used for posting
@app.post("/register_user", status_code=status.HTTP_201_CREATED)
async def register_user(
        response: Response,
        email: str = Form(""),
        name: str = Form(""),
        password1: str = Form(""),
        password2: str = Form(""),
):
    """
    Used for registering a new user.
    Creates a new user with unverified email.
    Sends confirmation message to the provided email
    :param response: The fastapi response
    :param email: The email
    :param name: The name
    :param password1: The first password
    :param password2: The second password (must be the same as the first)
    :return: HTTP_201_CREATED
    """
    new_user = User()
    form_is_valid = validate_form(
        email=email,
        name=name,
        pass1=password1,
        pass2=password2
    )

    if form_is_valid:
        try:
            new_user = ControllerUser.create_user(email=email, name=name, password=password1, email_verified=True)

            #  Currently removed
            # template = jinja_env.get_template("confirm_email_email.html")

            # message = MessageSchema(
            #     subject="Verify your email",
            #     recipients=[email],
            #     body=template.render(user=new_user, server_name=SERVER_NAME),
            #     subtype=MessageType.html
            # )

            # fm = FastMail(email_conf)
            # await fm.send_message(message)
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            logger.exception(e)

    if new_user.user_uuid:
        return {"user_uuid": new_user.user_uuid}


@app.post("/login", status_code=status.HTTP_401_UNAUTHORIZED)
def login(
        response: Response,
        email: str = Form(...),
        password: str = Form(...),
):
    """
    Used for logging a user in.
    :param response: the fastapi response
    :param email: user email
    :param password: user password
    :return: dict of user_uuid and token_uuid. Token_uuid is "" if remember_me = false
    """
    result = {}
    user = ControllerUser.log_user_in(email, password)

    if user and user.email_verified:
        result = {
            "user_uuid": user.user_uuid,
            "token_uuid": user.token.token_uuid,
        }
        response.headers["token"] = user.token.token_uuid
        response.status_code = status.HTTP_200_OK

    return result


@app.post("/send_friend_request", status_code=status.HTTP_200_OK)
def send_friend_request(
        response: Response,
        user_uuid: str = Form(...),
        receiver_user_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Used for verifying a users email
    :param response: The fastapi response
    :param user_uuid: the uuid of the user
    :param receiver_user_uuid: the uuid of the request receiver user
    :param token_uuid: the token_uuid of the user who requested it
    :return: Sends the user to the login view
    """
    sender_user_id = ControllerDatabase.get_user_id_by_uuid(user_uuid)
    receiver_user_id = ControllerDatabase.get_user_id_by_uuid(receiver_user_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    # Check if user has permission
    if requester_user_id != sender_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return

    friend_request = FriendRequest(
        sender_user_id=sender_user_id,
        receiver_user_id=receiver_user_id,
    )

    is_successful = ControllerDatabase.insert_friend_request(friend_request)

    return {"is_successful": is_successful}


@app.post("/accept_friend_request", status_code=status.HTTP_200_OK)
def accept_friend_request(
        response: Response,
        friend_request_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for accepting a friend request
    :param response: The fastapi response
    :param friend_request_uuid: the uuid of the friend request
    :param token_uuid: the token_uuid of the user who requested it
    :return: "", http.HTTPStatus.NO_CONTENT
    """
    friend_request_id = ControllerDatabase.get_friend_request_id_by_uuid(friend_request_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    
    friend_request = ControllerDatabase.get_friend_request(friend_request_id)

    # Check if user has permission
    if requester_user_id != friend_request.receiver_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return

    is_successful = ControllerDatabase.accept_friend_request(
        friend_request
    )

    return {"is_successful": is_successful}


@app.post("/create_study_set", status_code=status.HTTP_200_OK)
def create_study_set(
        response: Response,
        study_set_name: str = Form(...),
        is_public: bool = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for creating a new study set
    :param response: the fastapi response
    :param study_set_name: the name of the study set to be created
    :param is_public: bool of weather or not the study set is publicly available
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK ot HTTP_500
    """
    user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    study_set = StudySet(
        creator_user_id=user_id,
        is_public=is_public,
        study_set_name=study_set_name,
    )

    study_set = ControllerDatabase.insert_study_set(study_set)

    if not study_set:
        response.status_code = status.HTTP_500

    return {"study_set_uuid": study_set.study_set_uuid}


@app.post("/create_deck", status_code=status.HTTP_200_OK)
def create_deck(
        response: Response,
        deck_name: str = Form(...),
        is_public: bool = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for creating a deck
    :param response: the fastapi response
    :param deck_name: the name of the deck
    :param is_public: bool of weather or not the deck is public
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    deck = Deck(
        creator_user_id=user_id,
        is_public=is_public,
        deck_name=deck_name,
    )

    deck = ControllerDatabase.insert_deck(deck)

    if not deck:
        response.status_code = status.HTTP_500

    return {"deck_uuid": deck.deck_uuid}


@app.post("/create_card", status_code=status.HTTP_200_OK)
def create_card(
        response: Response,
        front_text: str = Form(...),
        back_text: str = Form(...),
        deck_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for creating a card in a deck
    :param response: a fastapi response
    :param front_text: the card prompt
    :param back_text: the card answer
    :param deck_uuid: the uuid of the deck where the card will be in
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    deck = ControllerDatabase.get_deck_by_uuid(deck_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    # Check if user has permission
    if requester_user_id != deck.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return

    card = Card(
        front_text=front_text,
        back_text=back_text,
        deck_deck_id=deck.deck_id,
    )

    card = ControllerDatabase.insert_card(card)

    if not card:
        response.status_code = status.HTTP_500

    return {"card_uuid": card.card_uuid}


@app.post("/add_label_to_deck", status_code=status.HTTP_200_OK)
def add_label_to_deck(
        response: Response,
        deck_uuid: str = Form(...),
        label_name: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for adding a label to a deck.
    If the label doesn't yet exist, it is created.
    :param response: a fastapi response
    :param deck_uuid: the uuid of the deck
    :param label_name: the name of the label
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    deck = ControllerDatabase.get_deck_by_uuid(deck_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    # Check if user has permission
    if requester_user_id != deck.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return

    is_successful = ControllerDatabase.add_label_to_deck(deck.deck_id, label_name)
    return {"is_successful": is_successful}


@app.post("/add_label_to_study_set", status_code=status.HTTP_200_OK)
def add_label_to_study_set(
        response: Response,
        study_set_uuid: str = Form(...),
        label_name: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for adding a label to a study set
    :param response: a fastapi response
    :param study_set_uuid: the uuid of the study_set
    :param label_name: the name of the label
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    study_set = ControllerDatabase.get_study_set_by_uuid(study_set_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    # Check if user has permission
    if requester_user_id != study_set.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return

    is_successful = ControllerDatabase.add_label_to_study_set(study_set.study_set_id, label_name)
    return {"is_successful": is_successful}


@app.post("/edit_card", status_code=status.HTTP_200_OK)
def edit_card(
        response: Response,
        front_text: str = Form(...),
        back_text: str = Form(...),
        card_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for editing a card
    :param response: a fastapi response
    :param front_text: the card prompt
    :param back_text: the card answer
    :param card_uuid: the uuid of the card
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    card = ControllerDatabase.get_card_by_uuid(card_uuid)
    card_parent_deck = ControllerDatabase.get_deck(card.deck_deck_id)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    # Check if user has permission
    if requester_user_id != card_parent_deck.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return

    card.front_text = front_text
    card.back_text = back_text

    card = ControllerDatabase.edit_card(card)

    return {"card_uuid": card.card_uuid}


@app.post("/invite_user_to_study_set", status_code=status.HTTP_200_OK)
def invite_user_to_study_set(
        response: Response,
        study_set_uuid: str = Form(...),
        user_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
        can_edit: bool = Form(...),
):
    """
    Ajax endpoint for adding a label to a study set
    :param response: a fastapi response
    :param study_set_uuid: the uuid of the study_set
    :param user_uuid: the uuid of the user
    :param token_uuid: the token_uuid of the user who requested it
    :param can_edit: bool of can the user edit the study set
    :return: HTTP_200_OK or HTTP_500
    """
    study_set = ControllerDatabase.get_study_set_by_uuid(study_set_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    user_id = ControllerDatabase.get_user_id_by_uuid(user_uuid)
    
    if requester_user_id != study_set.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN

    is_successful = ControllerDatabase.invite_user_to_study_set(
        study_set.study_set_id, user_id, can_edit
    )

    return {"is_successful": is_successful}


@app.post("/update_user_xp", status_code=status.HTTP_200_OK)
def update_user_xp(
        response: Response,
        token_uuid: str = Header(alias="token"),
        xp_count: int = Form(...),
):
    """
    Ajax endpoint for adding a label to a study set
    :param response: a fastapi response
    :param token_uuid: the token_uuid of the user who requested it
    :param xp_count: the amount of xp uploaded
    :return: HTTP_200_OK or HTTP_500
    """
    user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    
    is_successful = ControllerDatabase.update_user_xp(user_id, xp_count)
    
    return {"is_successful": is_successful}
   

# Methods used for deleting something
@app.delete("/remove_friend_request", status_code=status.HTTP_200_OK)
def remove_friend_request(
        response: Response,
        friend_request_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for removing a friend request
    :param response: The fastapi response
    :param friend_request_uuid: uuid of the friend_request
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    friend_request = ControllerDatabase.get_friend_request_by_uuid(friend_request_uuid)
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)

    # Check if user has permission
    if requester_user_id not in (friend_request.receiver_user_id, friend_request.sender_user_id):
        response.status_code = status.HTTP_403_FORBIDDEN
        return

    is_successful = ControllerDatabase.delete_friend_request(
        FriendRequest(friend_request_id=friend_request.friend_request_id)
    )

    return {"is_successful": is_successful}


@app.delete("/remove_card", status_code=status.HTTP_200_OK)
def remove_card(
        response: Response,
        card_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for removing a card
    :param response: The fastapi response
    :param card_uuid: uuid of the card
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    card = ControllerDatabase.get_card_by_uuid(card_uuid)
    card_parent_deck = ControllerDatabase.get_deck(card.deck_deck_id)

    # Check if user has permission
    if requester_user_id != card_parent_deck.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return
    
    is_successful = ControllerDatabase.delete_card(card)

    return {"is_successful": is_successful}


@app.delete("/remove_deck", status_code=status.HTTP_200_OK)
def remove_deck(
        response: Response,
        deck_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for removing a deck
    :param response: The fastapi response
    :param deck_uuid: uuid of the deck
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    deck = ControllerDatabase.get_deck_by_uuid(deck_uuid)

    # Check if user has permission
    if requester_user_id != deck.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return
    
    is_successful = ControllerDatabase.delete_deck(deck)

    return {"is_successful": is_successful}


@app.delete("/remove_study_set", status_code=status.HTTP_200_OK)
def remove_study_set(
        response: Response,
        study_set_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for removing a study_set
    :param response: The fastapi response
    :param study_set_uuid: uuid of the study_set
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    study_set = ControllerDatabase.get_study_set_by_uuid(study_set_uuid)

    # Check if user has permission
    if requester_user_id != study_set.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return
    
    is_successful = ControllerDatabase.delete_study_set(study_set)

    return {"is_successful": is_successful}


@app.delete("/remove_user_from_study_set", status_code=status.HTTP_200_OK)
def remove_user_from_study_set(
        response: Response,
        study_set_uuid: str = Form(...),
        user_uuid: str = Form(...),
        token_uuid: str = Header(alias="token"),
):
    """
    Ajax endpoint for removing a study_set
    :param response: The fastapi response
    :param study_set_uuid: uuid of the study_set
    :param user_uuid: the uuid of the user to be removed
    :param token_uuid: the token_uuid of the user who requested it
    :return: HTTP_200_OK or HTTP_500
    """
    requester_user_id = ControllerDatabase.get_user_id_by_token_uuid(token_uuid)
    study_set = ControllerDatabase.get_study_set_by_uuid(study_set_uuid)
    user_id = ControllerDatabase.get_user_id_by_uuid(user_uuid)
    
    # Check if user has permission
    if requester_user_id != study_set.creator_user_id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return
    
    is_successful = ControllerDatabase.remove_user_from_study_set(
        study_set.study_set_id, user_id
    )
    
    return {"is_successful": is_successful}


if __name__ == "__main__":
    logger.add("./logs/{time:YYYY-MM-DD}.log", colorize=True, rotation="00:00")
    uvicorn.run(app='main:app', reload=True)
