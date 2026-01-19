from uuid import uuid4

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class AccountManager(BaseUserManager):
    def create_account(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("first_name", "admin")
        return self.create_account(email, password, **extra_fields)


# Create your models here.
class Account(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    objects = AccountManager()

    class Meta:
        verbose_name = "account"
        verbose_name_plural = "accounts"
        ordering = ["-created_at"]
        db_table = "account"  # custom table name

    def __str__(self):
        return print(
            f"{self.email} - {self.first_name} - {self.created_at} - {self.updated_at} - {self.is_staff}"
        )
