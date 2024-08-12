from sqlalchemy import and_, or_
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from api import log, db
from api.schema import LoginRequestSchema, LoginResponseSchema, RegisterRequestSchema, RegisterResponseSchema
from api.models import User


auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@auth_blueprint.route("/login", methods=["POST"])
def login() -> Response:
    log(log.INFO, "Login user starting")
    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
    
    data = request.get_json()
    try :
        validated_data = LoginRequestSchema(**data).model_dump()
    except:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    email = validated_data.get("email")
    u: User = db.session.query(User).filter(and_(User.email==email)).first()

    if not u or not check_password_hash(u.password_hash, validated_data.get("password")):
        log(log.ERROR, "Bad email or password")
        return jsonify({"status": "error", "message": "Bad email or password"}), 404
    
    access_token = create_access_token(identity=email)
    try:
        data = LoginResponseSchema(access_token=access_token).model_dump()
        log(log.INFO, "Login user successful")
        return jsonify({"status": "success", "message": "Login user successful", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422


@auth_blueprint.route("/register", methods=["POST"])
def register() -> Response:
    log(log.INFO, "Register user starting")
    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    try :
        validated_data = RegisterRequestSchema(**data).model_dump()
    except:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    u: User = db.session.query(User).filter(or_(User.username==validated_data.get("username"), User.email==validated_data.get("email"))).first()
        
    if u:
        log(log.ERROR, "Username and email should be unique")
        return jsonify({"status": "error", "message": "Username and email should be unique"}), 422
    
    u: User = User(**validated_data)
    u.save()

    try:
        data = RegisterResponseSchema(username=u.username, user_uuid=u.uuid).model_dump()
        log(log.INFO, "Register user successful")
        return jsonify({"status": "success", "message": "Register user successful", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422
