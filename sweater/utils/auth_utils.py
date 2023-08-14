from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import create_access_token, create_refresh_token
from password_strength import PasswordPolicy
from werkzeug.security import generate_password_hash

from sweater import db
from sweater.models.auth_model import Token, User


def is_email_in_db(email):
    candidate = User.query.filter_by(email=email).first()
    return True if candidate else False

def create_new_user(email, password):
    hashed_password = generate_password_hash(password, method='scrypt')
    new_user = User(email=email, password=hashed_password)  # Modified here
    db.session.add(new_user)
    db.session.commit()

def create_tokens(user_id, email):
    # print('**********In tokens ', user_id, email)
    access_token = create_access_token(identity=email, additional_claims={'id': user_id})
    refresh_token = create_refresh_token(identity=email, additional_claims={'id': user_id})
    return {'access_token': access_token, 'refresh_token': refresh_token}


def save_refresh_token(user_id, token):
    token_in_base = Token.query.filter_by(user_id=user_id).first()
    if token_in_base:
        token_in_base.refresh_token = token
        db.session.commit()
        return

    new_token = Token(user_id=user_id, refresh_token=token)
    db.session.add(new_token)
    db.session.commit()


def is_token_in_db(token):
    # print('******** token in=>', token)
    db_token = Token.query.filter_by(refresh_token=token).first()
    # print('******** token object=>', db_token)
    return True if db_token else False


def remove_refresh_token(token):
    # print('******** Remove token in=>', token)
    db_token = Token.query.filter_by(refresh_token=token).first()
    # print('******** Remove token object=>', db_token)
    if db_token:
        db.session.delete(db_token)
        db.session.commit()


def pw_validation(pw):
    policy = PasswordPolicy.from_names(
        # For debug mode only
        length=3,

        # This is for production mode. This or something similar
        # length=8,
        # uppercase=2,
        # numbers=2,
        # nonletters=2,
    )
    res = policy.test(pw)
    if len(res) == 0:
        return {'status': True}
    message = f"Password does not meet security requirements: {', '.join(str(m) for m in res)}"
    # print('pw_validation=>', message)
    return {'status': False, 'Msg': message}


def email_validation(email):
    try:
        v = validate_email(email)
        email = v["email"]
        # print('EMAIL =>', email)
        return {'status': True, 'email': email}
    except EmailNotValidError as e:
        # print('EMAIL DDDDDDDD=>', str(e))
        return {'status': False, 'Msg': str(e)}
