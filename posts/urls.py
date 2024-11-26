from django.urls import path, include
from rest_framework import routers

from posts.views import LikeViewSet, PostViewSet, UserProfileViewSet


router = routers.DefaultRouter()

router.register("likes", LikeViewSet)
router.register("posts", PostViewSet)
router.register("profiles", UserProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "posts"
