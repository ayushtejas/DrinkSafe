from rest_framework import generics, authentication, permissions
from user.serializers import (UserSerializer, AuthTokenSerializer)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



class UserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(APIView):
    serializer_class = AuthTokenSerializer
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES
    authentication_classes = []
    permission_classes= [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = serializer.validated_data['tokens']

        return Response(
            {
                'name': user.name,
                'email': user.email,
                'access_token': tokens['access'],
                'refresh_token': tokens['refresh'],
                'token_type': 'Bearer',
            },
            status=status.HTTP_200_OK
        )

class UpdateUserView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    authentication = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user