from django.contrib.auth import (get_user_model, authenticate)
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext as _

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email','password','name']
        extra_kwargs = {'password': {'write_only':True, 'min_length': 5}}

    def create(self,validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self,instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if user:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):

        email = attrs.get('email')

        password = attrs.get('password')
        print(password)
        if get_user_model().objects.filter(email=email):
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password= password,
            )
            if not user:
                msg = _('Please enter Correct details')
                raise serializers.ValidationError({'Please enter valid email or password'}, code='authorization')

            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return {
                'user': user,
                'tokens': tokens
            }

