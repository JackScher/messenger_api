from datetime import datetime
from sqlalchemy import and_
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from api import log, db
from api.schema import BaseCommentRequestSchema, CommentCreateRequestSchema, CommentUpdateSchema, ResponseSchema, CommentsRequestSchema, CommentsDailyBreakdownRequestSchema, CommentsDailyBreakdownResponseSchema
from api.models import User, Post, Comment
from api.celery import schedule_auto_reply


comment_blueprint = Blueprint("comment", __name__)


@comment_blueprint.route("", methods=["GET"])
@jwt_required()
def read() -> Response:
    log(log.INFO, "Get comment starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
    
    data = request.get_json()
    try :
        validated_data = BaseCommentRequestSchema(**data).model_dump()
    except:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    comment_uuid = validated_data.get("comment_uuid")
    c: Comment = db.session.query(Comment).filter(and_(Comment.uuid==comment_uuid, Comment.is_deleted==False, Comment.is_blocked==False)).first()
    if not c:
        log(log.ERROR, "Post doesn`t exist")
        return jsonify({"status": "error", "message": "Post doesn`t exist"}), 404
    
    try:
        data = ResponseSchema(body=c.body, created_at=c.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=c.uuid).model_dump()
        log(log.INFO, "Get comment successful")
        return jsonify({"status": "success", "message": "Get comment successful", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422
 

@comment_blueprint.route("/get_all", methods=["GET"])
@jwt_required()
def read_all() -> Response:
    log(log.INFO, "Get all comments starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
    
    data = request.get_json()
    try :
        validated_data = CommentsRequestSchema(**data).model_dump()
    except:
        log(log.ERROR, "Wrong data type received")
        return jsonify({"status": "error", "message": "Wrong data type received"}), 422
    
    user_uuid = validated_data.get("user_uuid")
    post_uuid = validated_data.get("post_uuid")
    comment_uuid = validated_data.get("comment_uuid")

    if user_uuid: 
        u: User = db.session.query(User).filter(and_(User.uuid==user_uuid, User.is_deleted==False)).first()
        if not u:
            log(log.ERROR, "User doesn`t exist")
            return jsonify({"status": "error", "message": "User doesn`t exist"}), 404    
        comments: list[Comment] = [c for c in u.comments if not c.is_deleted and not c.is_blocked]
    
    elif post_uuid:
        p: Post = db.session.query(Post).filter(and_(Post.uuid==post_uuid, Post.is_deleted==False)).first()
        if not p:
            log(log.ERROR, "Post doesn`t exist")
            return jsonify({"status": "error", "message": "Post doesn`t exist"}), 404    
        comments: list[Comment] = [c for c in p.comments if not c.is_deleted and not c.is_blocked]

    elif comment_uuid:
        parent: Comment = db.session.query(Comment).filter(and_(Comment.uuid==comment_uuid, Comment.is_deleted==False, Comment.is_blocked==False)).first()
        if not parent:
            log(log.ERROR, "Comment doesn`t exist")
            return jsonify({"status": "error", "message": "Comment doesn`t exist"}), 404    
        comments: list[Comment] = [c for c in parent.answers if not c.is_deleted and not c.is_blocked]
    
    else:
        comments: list[Comment] = db.session.query(Comment).filter(Comment.is_deleted==False, Comment.is_blocked==False).all()

    try:
        data = {str(i): ResponseSchema(body=c.body, created_at=c.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=c.uuid).model_dump() for i, c in enumerate(comments)}
        log(log.INFO, "Get all comments successful")
        return jsonify({"status": "success", "message": "Get all comments successful", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422
 

@comment_blueprint.route("/create", methods=["POST"])
@jwt_required()
def create() -> Response:
    log(log.INFO, "Create comment starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415
        
    data = request.get_json()
    try:
        validated_data = CommentCreateRequestSchema(**data).model_dump()
    except Exception as e:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    u: User = db.session.query(User).filter(and_(User.email==current_user, User.is_deleted==False)).first()
    if not u:
        log(log.ERROR, "User doesn`t exist")
        return jsonify({"status": "error", "message": "User doesn`t exist"}), 404
    
    if validated_data.get("parent_uuid"):
        parent: Comment = db.session.query(Comment).filter_by(uuid=validated_data.get("parent_uuid")).first()

        if not parent:
            log(log.ERROR, "Parent comment doesn`t exist")
            return jsonify({"status": "error", "message": "Parent comment doesn`t exist"}), 404
        
        c: Comment = Comment(body=validated_data.get("body"), user_id=u.id, user=u, parent_id=parent.id, parent_comment=parent)
        c.save()
    else:
        p: Post = db.session.query(Post).filter(and_(Post.uuid==validated_data.get("post_uuid"), Post.is_deleted==False)).first()

        if not p:
            log(log.ERROR, "Post doesn`t exist")
            return jsonify({"status": "error", "message": "Post doesn`t exist"}), 404
    
        c: Comment = Comment(body=validated_data.get("body"), user_id=u.id, user=u, post_id=p.id, post=p)
        c.save()
        schedule_auto_reply(p.user, c, p)

    try:
        data = ResponseSchema(body=c.body, created_at=c.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=c.uuid).model_dump()
        log(log.INFO, "Create comment successful")
        return jsonify({"status": "success", "message": "Comment created", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422
 

@comment_blueprint.route("/update", methods=["PATCH"])
@jwt_required()
def update() -> Response:
    log(log.INFO, "Update comment starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    try:
        validated_data = CommentUpdateSchema(**data).model_dump()
    except Exception as e:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    u: User = db.session.query(User).filter(and_(User.email==current_user, User.is_deleted==False)).first()
    if not u:
        log(log.ERROR, "User doesn`t exist")
        return jsonify({"status": "error", "message": "User doesn`t exist"}), 404
    
    comment_uuid = validated_data.get("comment_uuid")
    try:
        c: Comment = [c for c in u.comments if c.uuid==comment_uuid and not c.is_deleted and not c.is_blocked][0]
    except:
        log(log.ERROR, "Comment doesn`t exist")
        return jsonify({"status": "error", "message": "Comment doesn`t exist"}), 404
    
    c.body = validated_data.get("body")
    try:
        data = ResponseSchema(body=c.body, created_at=c.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=c.uuid).model_dump()
        c.save()
        log(log.INFO, "Update comment successful")
        return jsonify({"status": "success", "message": "Comment updated", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422


@comment_blueprint.route("/delete", methods=["DELETE"])
@jwt_required()
def delete() -> Response:
    log(log.INFO, "Delete comment starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    try:
        validated_data = BaseCommentRequestSchema(**data).model_dump()
    except Exception as e:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    u: User = db.session.query(User).filter(and_(User.email==current_user, User.is_deleted==False)).first()
    if not u:
        log(log.ERROR, "User doesn`t exist")
        return jsonify({"status": "error", "message": "User doesn`t exist"}), 404
    
    comment_uuid = validated_data.get("comment_uuid")
    try:
        c: Comment = [c for c in u.comments if c.uuid==comment_uuid and not c.is_deleted][0]
    except:
        log(log.ERROR, "Comment doesn`t exist")
        return jsonify({"status": "error", "message": "Comment doesn`t exist"}), 404
    
    try:
        data = ResponseSchema(body=c.body, created_at=c.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=c.uuid).model_dump()
        c.delete()
        log(log.INFO, "Delete comment successful")
        return jsonify({"status": "success", "message": "Comment deleted", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422


@comment_blueprint.route("/restore", methods=["POST"])
@jwt_required()
def restore() -> Response:
    log(log.INFO, "Restore comment starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    try:
        validated_data = BaseCommentRequestSchema(**data).model_dump()
    except Exception as e:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422
    
    u: User = db.session.query(User).filter(and_(User.email==current_user, User.is_deleted==False)).first()
    if not u:
        log(log.ERROR, "User doesn`t exist")
        return jsonify({"status": "error", "message": "User doesn`t exist"}), 404
    
    comment_uuid = validated_data.get("comment_uuid")
    try:
        c: Comment = [c for c in u.comments if c.uuid==comment_uuid and c.is_deleted][0]
    except:
        log(log.ERROR, "Comment doesn`t exist")
        return jsonify({"status": "error", "message": "Comment doesn`t exist"}), 404
    
    try:
        data = ResponseSchema(body=c.body, created_at=c.created_at.strftime("%Y/%m/%d, %H:%M:%S"), uuid=c.uuid).model_dump()
        c.restore()
        log(log.INFO, "Restore comment successful")
        return jsonify({"status": "success", "message": "Comment restored", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422


@comment_blueprint.route("/comments_daily_breakdown", methods=["GET"])
@jwt_required()
def daily_breakdown() -> Response:
    log(log.INFO, "Restore comment starting")
    current_user = get_jwt_identity()

    if not request.is_json:
        log(log.ERROR, "Unsupported media type")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    try:
        validated_data = CommentsDailyBreakdownRequestSchema(**data).model_dump()
    except Exception as e:
        log(log.ERROR, "No needed data received")
        return jsonify({"status": "error", "message": "No needed data received"}), 422

    u: User = db.session.query(User).filter(and_(User.email==current_user, User.is_deleted==False)).first()
    if not u:
        log(log.ERROR, "User doesn`t exist")
        return jsonify({"status": "error", "message": "User doesn`t exist"}), 404
    
    date_from = datetime.strptime(validated_data.get("date_from"), "%Y-%m-%d")
    date_to = datetime.strptime(validated_data.get("date_to"), "%Y-%m-%d")

    comments: list[Comment] = [c for c in u.comments if c.created_at>=date_from and c.created_at<=date_to and not c.is_deleted]
    created = len([c for c in comments if not c.is_blocked])
    blocked = len([c for c in comments if c.is_blocked])

    try:
        data = CommentsDailyBreakdownResponseSchema(created=created, blocked=blocked).model_dump()
        log(log.INFO, "Get comments daily breakdown successful")
        return jsonify({"status": "success", "message": "Get comments daily breakdown successful", "data": data}), 200
    except:
        log(log.ERROR, "Unsupported response data type")
        return jsonify({"status": "error", "message": "Unsupported response data type"}), 422
