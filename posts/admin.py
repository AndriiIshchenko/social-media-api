from django.contrib import admin

from .models import Comment, Like, Post, UserProfile, Tag

admin.site.register(Like)
admin.site.register(Post)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Tag)
