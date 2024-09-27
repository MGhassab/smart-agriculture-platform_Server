from Customer.models import Device, Land
from . import models
from Customer import models as customer_models
from datetime import timedelta
from django.utils import timezone
from Baghyar import settings
from django.db.models import Max
import copy


def is_land_online(device: Device):
    recent = timezone.now() - timedelta(minutes=settings.DEVICE_CONNECTION_LOG_MINUTES)
    recent_logs = models.LogDeviceCheckOut.objects\
        .filter(device=device)\
        .filter(time__gte=recent)
    has_recent_log = recent_logs.count() != 0
    return has_recent_log


def get_last_log(device: Device) -> models.LogDeviceCheckOut:
    return models.LogDeviceCheckOut.objects.filter(device=device, get_updates=True).order_by('-time')[0]


def get_last_log_time(device: Device):
    return models.LogDeviceCheckOut.objects.filter(device=device, get_updates=True).aggregate(Max('time'))['time__max']


def get_next_update_time(device: Device):
    right_now = timezone.now()
    last_log = get_last_log_time(device)
    period = device.update_period
    if not last_log or not period or period < timedelta(minutes=1):
        return right_now + device.update_period
    while last_log + period <= right_now:
        period_factor = copy.copy(period)
        while last_log + period_factor <= right_now:
            last_log = last_log + period_factor
            period_factor = period_factor + period_factor
    return last_log + period

