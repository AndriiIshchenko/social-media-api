from django.contrib import admin

from .models import (
    Comment,
    Like,
    Post,
    UserProfile,
)

admin.site.register(Like)
admin.site.register(Post)
admin.site.register(UserProfile)
admin.site.register(Comment)
