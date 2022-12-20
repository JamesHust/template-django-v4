from django.contrib.auth.models import User
from rest_framework import permissions, exceptions
from rest_framework.authentication import BaseAuthentication


class EmailAuthentication(BaseAuthentication):
    def authenticate(self, request):
        email = request.META.get("HTTP_EMAIL")
        if not email:
            raise exceptions.AuthenticationFailed("Failed to authenticate")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(email=email, username=email, is_active=True)
        return user, None


class EmailPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True
