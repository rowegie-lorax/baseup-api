from django.db import models

from jsonfield import JSONField
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)

from datetime import datetime, timedelta
from app.settings import ToUpload

import collections


class Manager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not first_name:
            raise ValueError('First name is required')
        
        if not last_name:
            raise ValueError('Last name is required')

        if not email:
            raise ValueError('Users must have an email address')

        if User.objects.filter(email=email).count() > 0:
            raise ValueError('Email address already exists')

        user = self.model(email=self.normalize_email(email))
        if password:
            user.set_password(password)
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user('','',email, password=password)
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):

    # User types Enum
    USER = 'U'
    CLIENT = 'C'
    ADMIN = 'A'

    # credentials
    email =  models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # address
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    timezone = models.CharField(max_length=30, blank=True, null=True)
    # contact
    phone = models.CharField(max_length=20, blank=True, null=True)
    alt_phone = models.CharField(max_length=20, blank=True, null=True)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    objects = Manager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Service(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=5, decimal_places=2)
    duration = models.DurationField(default = timedelta(hours=0, minutes=0, seconds=0))
    max_customers = models.IntegerField(default=1)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

PROVIDER_STATUS = (('A','Active'),('I','Inactive'))
class Provider(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    avatar = models.ImageField(upload_to=ToUpload('provider'), blank=True)
    services = models.ManyToManyField(Service, blank=True)
    status = models.CharField(max_length=1, choices=PROVIDER_STATUS, default='A')

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Account(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    metadata = JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict})
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + ' - ' + self.create_at.strftime('%Y-%m-%d %H:%M:%S')


class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)


class AccountRole(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Capabilities(models.Model):
    name = models.CharField(max_length=100)


