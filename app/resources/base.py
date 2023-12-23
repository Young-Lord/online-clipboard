from flask import Blueprint
from flask_restx import Api, Resource


api_bp = Blueprint("api", "api")
api_restx = Api(api_bp)
