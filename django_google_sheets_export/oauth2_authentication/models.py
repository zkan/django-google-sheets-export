from django.conf import settings
from django.db import models

from oauth2client.contrib.django_util.models import CredentialsField


class CredentialsModel(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    credential = CredentialsField()
