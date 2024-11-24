from django.urls import path, include
from rest_framework import routers

from posts.views import LikeViewSet, PostViewSet


router = routers.DefaultRouter()

router.register("likes", LikeViewSet)
router.register("posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "posts"
