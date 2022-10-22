import uvicorn
from fastapi import FastAPI, Form, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from jinja2 import Environment, PackageLoader, select_autoescape

from loguru import logger

from controllers.constants import ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD, SERVER_NAME, ADMIN_EMAIL_USERNAME
from controllers.controller_database import ControllerDatabase
from controllers.controller_user import ControllerUser
from models.friend_request import FriendRequest
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


@app.post("/register_user", status_code=status.HTTP_201_CREATED)
async def register_user(
        email: str = Form(""),
        name: str = Form(""),
        password1: str = Form(""),
        password2: str = Form(""),
):
    form_is_valid = validate_form(
        email=email,
        name=name,
        pass1=password1,
        pass2=password2
    )

    if form_is_valid:
        try:
            new_user = ControllerUser.create_user(email=email, name=name, password=password1)

            template = jinja_env.get_template("confirm_email_email.html")

            message = MessageSchema(
                subject="Verify your email",
                recipients=[email],
                body=template.render(user=new_user, server_name=SERVER_NAME),
                subtype=MessageType.html
            )

            fm = FastMail(email_conf)
            await fm.send_message(message)
        except Exception as e:
            logger.exception(e)


@app.get("/verify_email/{user_uuid}")
async def verify_email(user_uuid: str):
    """
    Used for verifying a users email
    :user_uuid: the uuid of the user
    :return: Sends the user to the login view
    """

    user = ControllerDatabase.get_user_by_uuid(user_uuid)
    ControllerDatabase.set_user_email_verified(user)


@app.post("/login", status_code=status.HTTP_401_UNAUTHORIZED)
def login(
        response: Response,
        email: str = Form(...),
        password: str = Form(...),
        remember_me: bool = Form(...)
):
    result = {}
    user = ControllerUser.log_user_in(email, password, remember_me)

    if user and user.email_verified:
        result = {
            "user_uuid": user.user_uuid,
            "token_uuid": user.token.token_uuid,
        }
        response.status_code = status.HTTP_200_OK

    return result


@app.post("/send_friend_request", status_code=status.HTTP_200_OK)
def send_friend_request(
        user_uuid: str = Form(...),
        receiver_user_uuid: str = Form(...),
):
    """
    Used for verifying a users email
    :user_uuid: the uuid of the user
    :return: Sends the user to the login view
    """
    sender_user_id = ControllerDatabase.get_user_id_by_uuid(user_uuid)
    receiver_user_id = ControllerDatabase.get_user_id_by_uuid(receiver_user_uuid)

    friend_request = FriendRequest(
        sender_user_id=sender_user_id,
        receiver_user_id=receiver_user_id,
    )

    ControllerDatabase.insert_friend_request(friend_request)


@app.post("/accept_friend_request", status_code=status.HTTP_200_OK)
def accept_friend_request(
        friend_request_uuid: str = Form(...),
):
    """
    Ajax endpoint for accepting a friend request
    :return: "", http.HTTPStatus.NO_CONTENT
    """
    friend_request_id = ControllerDatabase.get_friend_request_id_by_uuid(friend_request_uuid)

    ControllerDatabase.accept_friend_request(
        FriendRequest(friend_request_id=friend_request_id)
    )


@app.post("/remove_friend_request", status_code=status.HTTP_200_OK)
def remove_friend_request(
        friend_request_uuid: str = Form(...),
):
    """
    Ajax endpoint for removing a friend request
    :return: "", http.HTTPStatus.NO_CONTENT
    """
    friend_request_id = ControllerDatabase.get_friend_request_id_by_uuid(friend_request_uuid)

    ControllerDatabase.delete_friend_request(
        FriendRequest(friend_request_id=friend_request_id)
    )


@app.post("/load_searched_users", status_code=status.HTTP_200_OK)
def load_searched_users(
        search_phrase: str = Form(...),
        search_page: int = Form(...),
):
    """
    Ajax endpoint for getting searched users
    :return: A list of dictionaries containing the user_uuid, user_name and random_id
    """

    result = ControllerDatabase.load_searched_users(
        search_phrase=search_phrase,
        search_page=search_page
    )

    return result


if __name__ == "__main__":
    logger.add("./logs/{time:YYYY-MM-DD}.log", colorize=True, rotation="00:00")
    uvicorn.run(app='main:app', reload=True)
