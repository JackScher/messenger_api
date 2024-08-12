import os 
import openai
from celery import Celery
from dotenv import load_dotenv
from .models import Comment, User, Post


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
celery = Celery(broker=os.environ.get("CELERY_BROKER_URL"), backend=os.environ.get("CELERY_RESULT_BACKEND"))


@celery.task
def send_auto_reply(comment: Comment, user: User, reply_text: str) -> None:
    Comment(body=reply_text, user_id=user.id, user=user, parent_id=comment.id, parent_comment=comment).save()


def schedule_auto_reply(user: User, comment: Comment, post: Post) -> None:
    if user.auto_reply_enabled:
        delay = user.auto_reply_delay
        reply_text = generate_reply(post.body, comment.body)
        send_auto_reply.apply_async((comment, user, reply_text), countdown=delay * 60)


def generate_reply(post_content: str, comment_content: str) -> str:
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Post: {post_content}\nComment: {comment_content}\nGenerate a relevant and polite reply:",
        max_tokens=50
    )
    reply_text = response.choices[0].text.strip()
    return reply_text
