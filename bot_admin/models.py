from django.db import models
from django.utils import timezone


class TelegramUser(models.Model):
    """Telegram User
    https://core.telegram.org/bots/api#chatfullinfo
    for ChatFullInfo
    """

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    username = models.CharField(max_length=32)
    bio = models.CharField(max_length=70)
    language_code = models.CharField(max_length=2)
    is_premium = models.BooleanField()
    datetime = models.DateTimeField(default=timezone.now)


class TelegramUserProfilePhotos(models.Model):
    """Telegram User Profile Photos
    https://core.telegram.org/bots/api#userprofilephotos
    for getUserProfilePhotos
    https://core.telegram.org/bots/api#photosize
    """

    tg_user_id = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    file_id = models.CharField()
    file_unique_id = models.CharField()
    file_size = models.IntegerField()
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    # in bytes
    file_size = models.SmallIntegerField()
