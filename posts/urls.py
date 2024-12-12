from django.urls import path, include
from rest_framework import routers

from posts.views import CommentViewSet, CreateProfile, PostViewSet, UserProfileViewSet


router = routers.DefaultRouter()


router.register("posts", PostViewSet)
router.register("profiles", UserProfileViewSet)
router.register("comments", CommentViewSet)
router.register("create-profile", CreateProfile, basename="create-profile")


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "posts"
