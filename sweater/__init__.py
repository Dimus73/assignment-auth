from datetime import timedelta

from decouple import config
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.debug = True

# resources = {r"/*": {"origins": "http://localhostt:3000"}}
# CORS(app, resources=resources)
# CORS(app, origins=["http://localhost:3000"])
CORS(app, origins=["https://localhost:3000"], supports_credentials=True)
# CORS(app)

url = config('DB_URL')
port = config('DB_PORT')
username = config('DB_USERNAME')
password = config('DB_PASSWORD')
base_name = config('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@{url}:{port}/{base_name}"
app.config['JWT_SECRET_KEY'] = config('SECRET_KEY')

# Set lifetime of ACCESS and REFRESH token
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=60*60)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=60*60*24*30)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_RECORD_QUERIES'] = True

db = SQLAlchemy(app)
jwt = JWTManager(app)


@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(e):

    return jsonify({'msg': "Data Base conaction error"}), 500

from sweater.models import auth_model
from sweater.models import company_model

from sweater.routes import auth_routes
from sweater.routes import company_routes

from sweater.utils import auth_utils
