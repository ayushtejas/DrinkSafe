from django.db import models
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from .utils import RoleTypes
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from django.conf import settings
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_field):
        if not email:
            raise ValueError('Email can not be empty')
        user = self.model(email= self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True
        user.is_organisation_admin = True
        user.role = 'SuperUser'
        user.phone_number = PhoneNumber.from_string('+919909685836', region='IN')
        user.save(using = self._db)

class User(AbstractBaseUser, PermissionsMixin):
    '''Users in the system'''

    name = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4,unique=True)
    email = models.EmailField(max_length=255, unique= True,blank=True,null=True)
    phone_number = PhoneNumberField(unique=True,blank=True,null=True, region="IN")
    role = models.CharField(choices=RoleTypes.choices(), max_length=20,default='Customer', null=True, blank=True)
    is_organisation_admin = models.BooleanField(default=False)
    organisation = models.CharField(null=True,blank=True, max_length=40)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'