"""Admin Bot Admin"""

from django.contrib import admin
from .models import TelegramUser, TelegramUserProfilePhotos


@admin.register(TelegramUser, TelegramUserProfilePhotos)
class PersonAdmin(admin.ModelAdmin):
    """PersonAdmin"""

    pass
