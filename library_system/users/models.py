import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.contrib.gis.db import models as geomodels



class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    uid = geomodels.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = geomodels.CharField(max_length=150, blank=True)
    last_name = geomodels.CharField(max_length=150, blank=True)
    email = geomodels.EmailField(unique=True)
    location = geomodels.PointField(null=True, blank=True)
    is_staff = geomodels.BooleanField(default=False)
    is_active = geomodels.BooleanField(default=True)
    date_joined = geomodels.DateTimeField(default=timezone.now, editable=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def active_borrows(self):
        from library.models import Borrow

        return self.borrows.filter(
            status=Borrow.BorrowStatus.BORROWED
        ).count()