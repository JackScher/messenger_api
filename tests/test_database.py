from flask.testing import FlaskClient
from api.models import User, Post, Comment
from .conftest import db


def test_user(client: FlaskClient) -> None:
    User(username="test_username", email="test_email@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name").save()
    
    r: User = db.session.query(User).filter_by(id=1).first()
    assert r
    assert r.username == "test_username"
    assert r.email == "test_email@gmail.com"
    assert r.comments == []
    assert r.posts == []


def test_post(client: FlaskClient) -> None:
    u: User = User(username="test_username", email="test_email@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name")
    u.save()

    Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u).save()

    p: Post = db.session.query(Post).filter_by(id=1).first()
    assert p
    assert p.body == "test post body..."
    assert p in u.posts

    Post(body="test post body banword1...", title="test_title", description="test_description", user_id=u.id, user=u).save()
    p: Post = db.session.query(Post).filter_by(id=2).first()
    assert p
    assert p.is_deleted == True

    Post(body="test post body...", title="test_title BANword2", description="test_description", user_id=u.id, user=u).save()
    p: Post = db.session.query(Post).filter_by(id=3).first()
    assert p
    assert p.is_deleted == True
    
    Post(body="test post body...", title="test_title", description="test_descriptionBANWORD3", user_id=u.id, user=u).save()
    p: Post = db.session.query(Post).filter_by(id=4).first()
    assert p
    assert p.is_deleted == True
    

def test_comment(client: FlaskClient) -> None:
    u1: User = User(username="test_username1", email="test_email1@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name")
    u1.save()

    u2: User = User(username="test_username2", email="test_email2@gmail.com", password="test_password")
    u2.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u1.id, user=u1)
    p.save()

    c1: Comment = Comment(body="test comment body 1", post_id=p.id, post=p, user_id=u1.id, user=u1)
    c1.save()

    c2: Comment = Comment(body="test comment body 2", parent_id=c1.id, parent_comment=c1, user_id=u2.id, user=u2)
    c2.save()

    c3: Comment = Comment(body="test comment body with BANWORD5", parent_id=c1.id, parent_comment=c1, user_id=u2.id, user=u2)
    c3.save()

    result1: Comment = db.session.query(Comment).filter_by(id=1).first()
    result2: Comment = db.session.query(Comment).filter_by(id=2).first()
    result3: Comment = db.session.query(Comment).filter_by(id=3).first()

    assert result1
    assert result1.body == "test comment body 1"
    assert result1 in p.comments
    assert result1 in u1.comments

    assert result2
    assert result2.body == "test comment body 2"
    assert result2 in result1.answers
    assert result2 in u2.comments

    assert result3
    assert result3.is_blocked == True
