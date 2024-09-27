from django.db import models


class SMSLog(models.Model):
    msg = models.CharField('msg', max_length=200)
    sender = models.CharField('sender', max_length=15, null=True, default=None, blank=True)
    receiver = models.CharField('receiver', max_length=15)

    def __str__(self):
        return f'{self.id}.sender:{self.sender}_receiver:{self.receiver}_msg:{self.msg}'

