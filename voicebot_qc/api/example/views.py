from django.contrib.auth.models import User
from rest_framework.viewsets import ReadOnlyModelViewSet

from voicebot_qc.api.example.serializers import UserSerializer


class UserViewSet(ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing accounts.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
