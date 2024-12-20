from rest_framework import generics, authentication, permissions
from user.serializers import (UserSerializer, AuthTokenSerializer)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import AllowAny



class UserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES
    authentication_classes = []
    permission_classes= [AllowAny]

class UpdateUserView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    authentication = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user