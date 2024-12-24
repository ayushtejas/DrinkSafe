from django.contrib.auth import (get_user_model, authenticate)
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext as _
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = get_user_model()
        fields = ['uuid','email', 'phone_number', 'password','organisation', 'name', 'role',
                 'is_organisation_admin', 'is_active', 'is_staff', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'email': {'required': False},
            'is_active': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True}
        }

    def validate(self, attrs):
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')

        if not email and not phone_number:
            raise serializers.ValidationError({
                'non_field_errors': ['Either email or phone number must be provided.']
            })

        if email:
            if get_user_model().objects.filter(email=email).exists():
                raise serializers.ValidationError({
                    'email': ['User with this email already exists, please login.']
                })

        if phone_number:
            try:
                if get_user_model().objects.filter(phone_number=phone_number).exists():
                    raise serializers.ValidationError({
                        'phone_number': ['User with this phone number already exists, please login.']
                    })

                phone_obj = PhoneNumber.from_string(phone_number, region='IN')
                if not phone_obj.is_valid():
                    raise serializers.ValidationError({
                        'phone_number': ['Invalid phone number format.']
                    })
                attrs['phone_number'] = phone_obj

                if not email:
                    attrs['email'] = f"{phone_number.replace('+', '').replace(' ', '')}@example.com"
                    if get_user_model().objects.filter(email=attrs['email']).exists():
                        raise serializers.ValidationError({
                            'email': ['Generated email already exists. Please provide a different email.']
                        })

            except serializers.ValidationError:
                raise
            except Exception as e:
                raise serializers.ValidationError({
                    'phone_number': [f'Invalid phone number: {str(e)}']
                })

        return attrs

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):

        email_or_phone = attrs.get('email_or_phone')

        password = attrs.get('password')
        print(password)

        if not email_or_phone or not password:
            raise serializers.ValidationError({'Please enter email or phone number and password'}, code='authorization')

        user = None
        if '@'in email_or_phone:
            user = get_user_model().objects.filter(email=email_or_phone).first()
        else:
            user = get_user_model().objects.filter(phone_number=email_or_phone).first()
        if user is not None:
            print(user)
            user = authenticate(
                request=self.context.get('request'),
                username=user.email,
                password= password,
            )
            if not user:
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

        else:
            raise serializers.ValidationError({'User does not exist, please register'}, code='authorization')

