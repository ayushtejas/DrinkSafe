from rest_framework import generics, authentication, permissions
from user.serializers import (UserSerializer, AuthTokenSerializer)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied



class UserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes= [AllowAny]

    def get_queryset(self):

        user = self.request.user

        if user.is_superuser:
            return get_user_model().objects.all()

        if user.is_organisation_admin and not user.is_superuser:
            return get_user_model().objects.filter(organisation=user.organisation)
        
        return get_user_model().objects.filter(uuid=user.uuid)


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
                'phone_number':user.phone_number.as_e164 if user.phone_number else None,
                'role':user.role,
                'malik': user.is_organisation_admin,
                'organisation': user.organisation,
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

class ListUserView(generics.ListAPIView):
    serializer_class = UserSerializer
    authentication = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = get_user_model().objects.all()

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    authentication = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = get_user_model().objects.all()

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(get_user_model(), uuid=user_id)

        if not self.request.user.is_superuser:
            if self.request.user.uuid != user.uuid:
                if not (self.request.user.is_organisation_admin and
                       user.organisation == self.request.user.organisation):
                    raise PermissionDenied("You don't have permission to modify this user.")

        return user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if not request.user.is_superuser:
            restricted_fields = ['is_active', 'is_staff', 'is_superuser']
            for field in restricted_fields:
                request.data.pop(field, None)

        if request.user.is_organisation_admin and not request.user.is_superuser:
            if 'role' in request.data and request.data['role'] in ['Admin', 'SuperAdmin']:
                raise PermissionDenied("Organisation admins cannot assign admin roles.")

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if 'email' in request.data:
            email = request.data['email']
            if get_user_model().objects.exclude(id=instance.id).filter(email=email).exists():
                return Response(
                    {'email': ['This email is already in use.']},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if 'phone_number' in request.data:
            phone = request.data['phone_number']
            if get_user_model().objects.exclude(id=instance.id).filter(phone_number=phone).exists():
                return Response(
                    {'phone_number': ['This phone number is already in use.']},
                    status=status.HTTP_400_BAD_REQUEST
                )

        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.id == request.user.id:
            return Response(
                {'detail': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if instance.is_staff or instance.is_superuser:
            if not request.user.is_superuser:
                raise PermissionDenied("Only superusers can delete admin accounts.")

        instance.is_active = False
        instance.save()

        return Response(
            {'detail': 'User has been successfully deactivated.'},
            status=status.HTTP_200_OK
        )