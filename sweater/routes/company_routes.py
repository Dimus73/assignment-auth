from flask import request, jsonify
from flask_jwt_extended import jwt_required

from sweater import app, db
from sweater.models.auth_model import User
from sweater.models.company_model import Company
from sweater.utils.base_utils import is_id_in_model
from sweater.utils.company_utils import is_company_in_db, create_company, is_user_in_company, add_user_to_company


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

    if not is_id_in_model(user_id, User):
        return jsonify({'message': "User with this id is not registered"}), 400

    if len(company.replace(" ", "")) == 0:
        return jsonify({'message': "Company name cannot be an empty string"}), 400

    if is_company_in_db(user_id, company):
        return jsonify({'message': "This user has already registered a company with that name. All company names for "
                                   "one user must be unique."}), 400
    create_company(user_id, company)
    return jsonify({"message": "Company created!"}), 201


@app.route('/add-user-to-org', methods=['POST'])
@jwt_required()
def add_user_to_org():
    data = request.get_json()
    user_id = data.get('user_id', False)
    company_id = data.get('company_id', False)

    if not user_id or not company_id:
        return jsonify({'message': "Server received invalid data"}), 400

    if not is_id_in_model(user_id, User):
        return jsonify({'message': "User with this id is not registered"}), 400

    if not is_id_in_model(company_id, Company):
        return jsonify({'message': "Company with this id is not registered"}), 400

    if is_user_in_company(user_id, company_id):
        return jsonify({'message': "The user has already been added to this company. Re-adding is not possible"}), 400

    add_user_to_company(user_id, company_id)
    return jsonify({"message": "User added successfully!"}), 201



