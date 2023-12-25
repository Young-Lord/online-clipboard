from flask import Blueprint
from flask_jwt_extended import JWTManager
from flask_restx import Api


api_bp = Blueprint("api", "api")
api_restx = Api(api_bp)
file_jwt = JWTManager()
