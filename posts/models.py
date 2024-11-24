from django.conf import settings
from django.db import models


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Like(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes", blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    CHOICES = (
        ("like", "LIKE"), 
        ("dislike", "DISLIKE"),
        ("nothing", "NOTHING")

    )
    like_type = models.CharField(max_length=10, choices=CHOICES, default="nothing")

# class Comment(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     likes = models.ManyToManyField(Likes, related_name="comments")
#     replies = models.ManyToManyField("self", related_name="comment_replies")

