from flask import request, jsonify
from flask_jwt_extended import jwt_required

from sweater import app, db
from sweater.models.company_model import Company
from sweater.utils.base_utils import is_user_in_db


@app.route('/create-org', methods=['POST'])
@jwt_required()
def create_org():
    data = request.get_json()
    user_id = data.get('user_id', False)
    company = data.get('company', False)

    # Here we get the company owner id in the request body and
    # check it for validity.
    # Another approach, get the user id from the token:
    # auth_header = request.headers.get('Authorization')
    # token_type, token = auth_header.split(" ")
    # token_data = pyjwt.decode(token, config('SECRET_KEY'), algorithms=["HS256"])

    if not user_id or not company:
        return jsonify({'message': "Server received invalid data"}), 400

    if not is_user_in_db (user_id):
        return jsonify({'message': "User with this id is not registered"}), 400

    if len(company.replace(" ", "")) == 0:
        return jsonify({'message': "Company name cannot be an empty string"}), 400

    new_company = Company(owner_id=user_id, name=company)
    db.session.add(new_company)
    db.session.commit()
    return jsonify({"message": "Company created!"}), 201



