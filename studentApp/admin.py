from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from studentApp.models import CustomUser


class UsreModel(UserAdmin):
    pass

admin.site.register(CustomUser,UsreModel)