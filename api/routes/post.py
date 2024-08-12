from sqlalchemy import and_
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from api import log, db
from api.schema import PostRequestSchema, PostCreateRequestSchema, PostUpdateRequestSchema, ResponseSchema, AllPostsRequestSchema
from api.models import User, Post


post_blueprint = Blueprint("post", __name__)


@post_blueprint.route("", methods=["GET"])
@jwt_required()
def read() -> Response:
    log(log.INFO, "Get post starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
    
    data = request.get_json()
    try :
        validated_data = PostRequestSchema(**data).model_dump()
    except:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    post_uuid = validated_data.get("post_uuid")
    p: Post = db.session.query(Post).filter(and_(Post.uuid==post_uuid, Post.is_deleted==False)).first()
    if not p:
        log(log.ERROR, "Post doesn`t exist")
        return jsonify({"status": "error", "message": "Post doesn`t exist"}), 404
    
    try:
        data = ResponseSchema(title=p.title, description=p.description, body=p.body, created_at=p.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=p.uuid).model_dump()
        log(log.INFO, "Get post successful")
        return jsonify({"status": "success", "message": "Get post successful", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422
   

@post_blueprint.route("/get_all", methods=["GET"]) # + all posts
@jwt_required()
def read_all() -> Response:
    log(log.INFO, "Get all posts starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
        
    data = request.get_json()
    try:
        validated_data = AllPostsRequestSchema(**data).model_dump()
    except Exception as e:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    user_uuid = validated_data.get("user_uuid")
    if user_uuid: 
        u: User = db.session.query(User).filter(and_(User.uuid==user_uuid, User.is_deleted==False)).first()
        if not u:
            log(log.ERROR, "User doesn`t exist")
            return jsonify({"status": "error", "message": "User doesn`t exist"}), 404    
        posts: list[Post] = [p for p in u.posts if not p.is_deleted]
    else:
        posts: list[Post] = db.session.query(Post).filter(Post.is_deleted==False).all()

    try:
        data = {str(i): ResponseSchema(title=p.title, description=p.description, body=p.body, created_at=p.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=p.uuid).model_dump() for i, p in enumerate(posts)}
        log(log.INFO, "Get all posts successful")
        return jsonify({"status": "success", "message": "Get all posts successful", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422
 

@post_blueprint.route("/create", methods=["POST"])
@jwt_required()
def create() -> Response:
    log(log.INFO, "Create posts starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
        
    data = request.get_json()
    try:
        validated_data = PostCreateRequestSchema(**data).model_dump()
    except Exception as e:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    u: User = db.session.query(User).filter(and_(User.email==current_user, User.is_deleted==False)).first()
    if not u:
        log(log.ERROR, "User doesn`t exist")
        return jsonify({"status": "error", "message": "User doesn`t exist"}), 404
    
    data = {key: item for key, item in validated_data.items() if key!="user_uuid"}    
    p: Post = Post(**data, user_id=u.id, user=u)
    p.save()

    try:
        data = ResponseSchema(title=p.title, description=p.description, body=p.body, created_at=p.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=p.uuid).model_dump()
        log(log.INFO, "Create post successful")
        return jsonify({"status": "success", "message": "Post created", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422


@post_blueprint.route("/update", methods=["PATCH"])
@jwt_required()
def update() -> Response:
    log(log.INFO, "Update post starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
    
    data = request.get_json()
    try :
        validated_data = PostUpdateRequestSchema(**data).model_dump()
    except:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
   
    u: User = db.session.query(User).filter(and_(User.email==current_user, User.is_deleted==False)).first()
    if not u:
        log(log.ERROR, "User doesn`t exist")
        return jsonify({"status": "error", "message": "User doesn`t exist"}), 404
    
    post_uuid = validated_data.get("post_uuid")
    try:
        p: Post = [p for p in u.posts if p.uuid==post_uuid and not p.is_deleted][0]
    except:
        log(log.ERROR, "Post doesn`t exist")
        return jsonify({"status": "error", "message": "Post doesn`t exist"}), 404
    
    new_body = validated_data.get("body", None)
    if new_body:
        p.body = new_body

    new_title = validated_data.get("title", None)
    if new_body:
        p.title = new_title

    new_description = validated_data.get("description", None)
    if new_description:
        p.description = new_description
    p.save()

    try:
        data = ResponseSchema(title=p.title, description=p.description, body=p.body, created_at=p.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=p.uuid).model_dump()
        log(log.INFO, "Update post successful")
        return jsonify({"status": "success", "message": "Post updated", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422


@post_blueprint.route("/delete", methods=["DELETE"])
@jwt_required()
def delete() -> Response:
    log(log.INFO, "Delete post starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
    
    data = request.get_json()
    try :
        validated_data = PostRequestSchema(**data).model_dump()
    except:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
  
    u: User = db.session.query(User).filter(and_(User.email==current_user, User.is_deleted==False)).first()
    if not u:
        log(log.ERROR, "User doesn`t exist")
        return jsonify({"status": "error", "message": "User doesn`t exist"}), 404
    
    post_uuid = validated_data.get("post_uuid")
    try:
        p: Post = [p for p in u.posts if p.uuid==post_uuid and not p.is_deleted][0]
    except:
        log(log.ERROR, "Post doesn`t exist")
        return jsonify({"status": "error", "message": "Post doesn`t exist"}), 404 
   
    try:
        data = ResponseSchema(title=p.title, description=p.description, body=p.body, created_at=p.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=p.uuid).model_dump()
        p.delete()
        log(log.INFO, "Delete post successful")
        return jsonify({"status": "success", "message": "Post deleted", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422
   

@post_blueprint.route("/restore", methods=["POST"])
@jwt_required()
def restore() -> Response:
    log(log.INFO, "Restore post starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
    
    data = request.get_json()
    try :
        validated_data = PostRequestSchema(**data).model_dump()
    except:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
  
    u: User = db.session.query(User).filter(and_(User.email==current_user, User.is_deleted==False)).first()
    if not u:
        log(log.ERROR, "User doesn`t exist")
        return jsonify({"status": "error", "message": "User doesn`t exist"}), 404
    
    post_uuid = validated_data.get("post_uuid")
    try:
        p: Post = [p for p in u.posts if p.uuid==post_uuid and p.is_deleted][0]
    except:
        log(log.ERROR, "Post doesn`t exist")
        return jsonify({"status": "error", "message": "Post doesn`t exist"}), 404 
    
    try:
        data = ResponseSchema(title=p.title, description=p.description, body=p.body, created_at=p.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=p.uuid).model_dump()
        p.restore()
        log(log.INFO, "Restore post successful")
        return jsonify({"status": "success", "message": "Post restored", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422
