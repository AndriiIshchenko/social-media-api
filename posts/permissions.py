from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
        )


class IsAuthenticatedWithProfile(BasePermission):
    """User with profile can create comments to posts"""

    message = "User must create a profile to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return bool(request.user.profile)
        except ObjectDoesNotExist:
            return False


class PostOwner(BasePermission):
    """The owner has full access to their posts"""

    def has_object_permission(self, request, view, obj):
        return bool(obj.user_profile == request.user.profile)


class OwnerOrReadOnlyProfile(BasePermission):
    """
    The owner has full access to their profile.
    Users with profile can only view the profiles of other users.
    """

    def has_object_permission(self, request, view, obj):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
                and request.user.profile
            )
            or (obj.user == request.user)
        )
