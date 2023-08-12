from datetime import timedelta

import jwt as pyjwt
from decouple import config
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, decode_token
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.debug = True

resources = {r"/*": {"origins": "http://localhostt:3000"}}
CORS(app, resources=resources)

url = config('DB_URL')
port = config('DB_PORT')
username = config('DB_USERNAME')
password = config('DB_PASSWORD')
base_name = config('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@{url}:{port}/{base_name}"
app.config['JWT_SECRET_KEY'] = config('SECRET_KEY')

# Set lifetime of ACCESS and REFRESH token
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(minutes=30)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_RECORD_QUERIES'] = True

db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)  # Changed from username to email
    password = db.Column(db.String(256), nullable=False)
    token = db.relationship('Token', backref='user', lazy=True)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refresh_token = db.Column(db.String(512), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    candidate = User.query.filter_by(email=data['email']).first()
    # print('Candidate', candidate)
    if candidate:
        return jsonify({'message': 'A user with the same name already exists in the database'}), 409
    hashed_password = generate_password_hash(data['password'], method='scrypt')
    new_user = User(email=data['email'], password=hashed_password)  # Modified here
    db.session.add(new_user)
    db.session.commit()
    # print('**********', new_user)
    return jsonify({"message": "User created!"}), 201


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()  # Modified here
    # print('!!!!!!!!!!!!!!!', data, user)
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"message": "Invalid credentials!"}), 401
    tokens = create_tokens(user.id, user.email)
    # print('88888888888', tokens)
    save_refresh_token(user.id, tokens['refresh_token'])
    # access_token = create_access_token(identity=user.email)  # Use email as identity
    response = jsonify({"email": user.email, "access_token": tokens['access_token']})
    response.set_cookie('refresh_token', tokens['refresh_token'], httponly=True, max_age=30*24*60*60)
    return response, 200


@app.route('/signout', methods=['POST'])
def sign_out():
    refresh_token = request.cookies.get('refresh_token')
    response = jsonify({"message": "User log out"})
    response.delete_cookie('refresh_token')
    remove_refresh_token(refresh_token)
    return response, 200


@app.route('/refresh', methods=['get'])
def refresh():
    print('vvvvv1')
    refresh_token = request.cookies.get('refresh_token')
    print(refresh_token)
    if not refresh_token:
        return jsonify({"message": "Invalid credentials!"}), 401
    print('-------------')
    # token_data = decode_token(refresh_token)
    # try:
    #     print('vvvvv2')
    #     token_data = decode_token(refresh_token)
    #     print(token_data)
    # except Exception as e:
    #     print('********')
    #     return jsonify({"message": "Invalid credentials!"}), 401
    try:
        token_data = pyjwt.decode(refresh_token, config('SECRET_KEY'), algorithms=["HS256"])
        print('?????????????', token_data)
    except pyjwt.ExpiredSignatureError:
        print("Token has expired!")
    except pyjwt.DecodeError:
        print("Token is invalid!")
    except Exception as e:
        print(f"An error occurred: {e}")

    tokens = create_tokens(token_data['id'], token_data['email'])
    save_refresh_token(token_data['id'], tokens['refresh_token'])

    response = jsonify({"email": token_data['email'], "access_token": tokens['access_token']})
    response.set_cookie('refresh_token', tokens['refresh_token'], httponly=True, max_age=30*24*60*60)
    return response, 200


##--------------------------


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


def remove_refresh_token(token):
    db_token = Token.query.filter_by(refresh_token=token).first()
    if db_token:
        db.session.delete(db_token)
        db.session.commit()


# def refresh_tokens(refresh_token):
#     try:
#         token_data = decode_token(refresh_token)
#     except Exception as e:
#         return jsonify({"message": "Invalid credentials!"}), 401
#
#     db_token = Token.query.filter_by(refresh_token=refresh_token).first()
#
#     if db_token:
#         new_tokens = create_tokens()
#         save_refresh_token(token_data['id'], new_tokens['refresh_token'])
#         return new_tokens
#
#     return

if __name__ == '__main__':
    app.run()
