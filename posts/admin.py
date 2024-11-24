from django.contrib import admin

from .models import (
    Like,
    Post,
)

admin.site.register(Like)
admin.site.register(Post)
