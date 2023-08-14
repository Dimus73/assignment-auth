import jwt as pyjwt
from decouple import config
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.security import check_password_hash

from sweater import app
from sweater.models.auth_model import User
from sweater.utils.auth_utils import email_validation, pw_validation, create_tokens, remove_refresh_token, \
    save_refresh_token, is_email_in_db, create_new_user, is_token_in_db


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    email_check = email_validation(data['email']);
    if not email_check['status']:
        return jsonify({'msg': email_check['Msg']}), 400

    password_check = pw_validation(data['password'])
    if not password_check['status']:
        return jsonify({'msg': password_check['Msg']}), 400

    if is_email_in_db(data['email']):
        return jsonify({'msg': 'A user with the same email already exists in the database'}), 409

    create_new_user(data['email'], data['password'])
    # print('**********', new_user)
    return jsonify({"message": "User created!"}), 201


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()  # Modified here

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"msg": "Invalid credentials!"}), 401

    tokens = create_tokens(user.id, user.email)
    save_refresh_token(user.id, tokens['refresh_token'])

    response = jsonify({'id': user.id, "email": user.email, "access_token": tokens['access_token']})
    response.set_cookie('refresh_token', tokens['refresh_token'], samesite='None', secure=True, httponly=True, max_age=30*24*60*60)
    return response, 200


@app.route('/signout', methods=['POST'])
def sign_out():
    refresh_token = request.cookies.get('refresh_token')

    remove_refresh_token(refresh_token)

    response = jsonify({"message": "User log out"})
    response.delete_cookie('refresh_token', samesite='None', secure=True)
    return response, 200


@app.route('/refresh', methods=['get'])
def refresh():
    refresh_token = request.cookies.get('refresh_token')
    # print('refresh_token=>',refresh_token)
    if not refresh_token:
        return jsonify({"msg": "Invalid credentials!"}), 401

    try:
        token_data = pyjwt.decode(refresh_token, config('SECRET_KEY'), algorithms=["HS256"])
    except pyjwt.ExpiredSignatureError:
        print("Token has expired!")
        return jsonify({"msg": "Invalid credentials!"}), 401
    except pyjwt.DecodeError:
        print("Token is invalid!")
        return jsonify({"msg": "Invalid credentials!"}), 401
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"msg": "Invalid credentials!"}), 401

    is_in_db = is_token_in_db(refresh_token)
    if not is_in_db:
        print("No token is DataBase!")
        return jsonify({"msg": "Invalid credentials!"}), 401
    # print('Token data in refresh', token_data)
    tokens = create_tokens(token_data['id'], token_data['sub'])
    save_refresh_token(token_data['id'], tokens['refresh_token'])

    response = jsonify({"id": token_data['id'], "email": token_data['sub'], "access_token": tokens['access_token']})
    response.set_cookie('refresh_token', tokens['refresh_token'], samesite='None', secure=True, httponly=True, max_age=30*24*60*60)
    return response, 200


@app.route('/users', methods=['get'])
@jwt_required()
def users():
    user_list = []
    all_users = User.query.all()
    # print(all_users, {'id': all_users[0].id, 'email': all_users[0].email})
    for user in all_users:
        user_list.append({'id': user.id, 'email': user.email})
    return jsonify(user_list), 200
