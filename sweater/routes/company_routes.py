from flask import request, jsonify
from flask_jwt_extended import jwt_required

from sweater import app, db
from sweater.models.auth_model import User
from sweater.models.company_model import Company
from sweater.utils.base_utils import is_id_in_model
from sweater.utils.company_utils import is_company_in_db, create_company, is_user_in_company, add_user_to_company, \
    get_owner_org_list, get_users_in_org


@app.route('/create-org', methods=['POST'])
@jwt_required()
def create_org():
    if not request.get_data():
        return jsonify({'message': "Server did not receive expected data"}), 400

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
        return jsonify({'msg': "Server received invalid data"}), 400

    if not is_id_in_model(user_id, User):
        return jsonify({'msg': "User with this id is not registered"}), 400

    if len(company.replace(" ", "")) == 0:
        return jsonify({'msg': "Company name cannot be an empty string"}), 400

    if is_company_in_db(user_id, company):
        return jsonify({'msg': "This user has already registered a company with that name. All company names for "
                                   "one user must be unique."}), 400
    org_list = create_company(user_id, company)

    response = jsonify(org_list)
    return response, 200


@app.route('/owner-org-list', methods=['POST'])
@jwt_required()
def owner_org_list():
    if not request.get_data():
        return jsonify({'msg': "Server did not receive expected data"}), 400
    data = request.get_json()
    print (f"This is data ____ {data} ___")

    user_id = data.get('user_id', False)
    if not user_id:
        return jsonify({'msg': "Server received invalid data"}), 400

    if not is_id_in_model(user_id, User):
        return jsonify({'msg': "User with this ID is not registered"}), 400

    org_list = get_owner_org_list(user_id)

    response = jsonify(org_list)
    return response, 200


@app.route('/add-user-to-org', methods=['POST'])
@jwt_required()
def add_user_to_org():
    if not request.get_data():
        return jsonify({'msg': "Server did not receive expected data"}), 400

    data = request.get_json()

    user_id = data.get('user_id', False)
    company_id = data.get('company_id', False)

    if not user_id or not company_id:
        return jsonify({'msg': "Server received invalid data"}), 400

    if not is_id_in_model(user_id, User):
        return jsonify({'msg': "User with this ID is not registered"}), 400

    if not is_id_in_model(company_id, Company):
        return jsonify({'msg': "Company with this ID is not registered"}), 400

    if is_user_in_company(user_id, company_id):
        return jsonify({'msg': "The user has already been added to this company. Re-adding is not possible"}), 400

    add_user_to_company(user_id, company_id)

    user_list = get_users_in_org(company_id)

    response = jsonify(user_list)
    return response, 200


@app.route('/users-in-org', methods=['POST'])
@jwt_required()
def users_in_org():
    if not request.get_data():
        return jsonify({'msg': "Server did not receive expected data"}), 400

    data = request.get_json()

    company_id = data.get('company_id', False)
    if not company_id:
        return jsonify({'msg': "Server received invalid data"}), 400

    if not is_id_in_model(company_id, Company):
        return jsonify({'msg': "Company with this ID is not registered"}), 400

    user_list = get_users_in_org(company_id)

    response = jsonify(user_list)
    return response, 200



