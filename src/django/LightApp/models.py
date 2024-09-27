from django.db import models
from model_utils.models import TimeStampedModel

from Customer import models as customer_models, utils as customer_utils
from random import randint
from django.utils import timezone
from datetime import timedelta
import urllib.parse
from LightApp import messages
from Baghyar import views as global_views
from Customer import models as customer_models
from django.contrib.auth.models import User
from SMSService.views import send_sms, send_otp


class Verification(models.Model):
    customer = models.ForeignKey(customer_models.Customer, on_delete=models.CASCADE, related_name='tokens')
    code = models.IntegerField('کد تایید', blank=True, null=True)
    expire = models.DateTimeField('زمان انقضا')
    # success = models.BooleanField('success', default=False)
    send_sms = models.BooleanField('پیغام ارسال شده', default=True)

    @property
    def user(self):
        return self.customer.user

    def save(self, *args, **kwargs):
        self.expire = timezone.now() + timezone.timedelta(minutes=120)
        code_digits = 5
        self.code = randint(10**(code_digits-1), 10**code_digits-1)
        verifications = Verification.objects \
            .filter(customer=self.customer) \
            .exclude(id=self.id) \
            .exclude(expire__gte=timezone.now())
        if verifications.count() > 0:
            verifications.delete()
        
        # super(Verification, self).save(*args, **kwargs)
        if self.send_sms:
            self.send()
        # self.success = True
        return super(Verification, self).save(*args, **kwargs)

    def send(self):
        try:
            msg = messages.verification_code_message(self.code)
            print('sending sms')
            send_otp(
                self.customer.user.username,
                'verification_code',
                msg,
                self.code,
            )
            print('sms sent')
        except Exception as e:
            print(e)
            pass

    @classmethod
    def create_verification(cls, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs["user"]
            customer = customer_models.Customer.get_or_create(user)
        elif 'customer' in kwargs:
            customer = kwargs["customer"]
        elif 'username' in kwargs:
            user = User.objects.get(username=kwargs["username"])
            customer = customer_models.Customer.get_or_create(user)
        else:
            raise ValueError("need to define user or customer or username")
        verification = cls(customer=customer)
        verification.save()
        return verification

    @classmethod
    def verify_user(cls, username, code):
        right_now = timezone.now()
        verifications = cls.objects.filter(customer__user__username=username, code=code, expire__gte=right_now)
        if verifications.count():
            return verifications.first()
        return None


class DebugLog(TimeStampedModel):
    title = models.CharField('title', max_length=500)
    description = models.CharField('description', max_length=2000, null=True, blank=True)

    @classmethod
    def log(cls, title, description=None):
        return cls.objects.create(title=title, description=description)
