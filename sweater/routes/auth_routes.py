import jwt as pyjwt
from decouple import config
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash, check_password_hash


from sweater import app, db
from sweater.models.auth_model import User
from sweater.utils.auth_utils import email_validation, pw_validation, create_tokens, remove_refresh_token, \
    save_refresh_token


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    email_check = email_validation(data['email']);
    if not email_check['status']:
        return jsonify({'message': email_check['Msg']}), 400

    password_check = pw_validation(data['password'])
    if not password_check['status']:
        return jsonify({'message': password_check['Msg']}), 400

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
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return jsonify({"message": "Invalid credentials!"}), 401
    try:
        token_data = pyjwt.decode(refresh_token, config('SECRET_KEY'), algorithms=["HS256"])
    except pyjwt.ExpiredSignatureError:
        print("Token has expired!")
        return jsonify({"message": "Invalid credentials!"}), 401
    except pyjwt.DecodeError:
        print("Token is invalid!")
        return jsonify({"message": "Invalid credentials!"}), 401
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"message": "Invalid credentials!"}), 401

    tokens = create_tokens(token_data['id'], token_data['sub'])
    save_refresh_token(token_data['id'], tokens['refresh_token'])

    response = jsonify({"email": token_data['sub'], "access_token": tokens['access_token']})
    response.set_cookie('refresh_token', tokens['refresh_token'], httponly=True, max_age=30*24*60*60)
    return response, 200


@app.route('/users', methods=['get'])
@jwt_required()
def users():
    user_list = [];
    all_users = User.query.all()
    print(all_users, {'id':all_users[0].id, 'email':all_users[0].email})
    for user in all_users:
        user_list.append( {'id': user.id, 'email': user.email} )
    return jsonify(user_list), 200