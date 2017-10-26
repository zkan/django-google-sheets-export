from django.contrib import admin

from .models import CredentialsModel


@admin.register(CredentialsModel)
class CredentialsAdmin(admin.ModelAdmin):
    pass
