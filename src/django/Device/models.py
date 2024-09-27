from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import CharField
from django.utils import timezone
from django.db.models import Max

from model_utils.models import TimeStampedModel
from model_utils import Choices
from model_utils.fields import StatusField
# from Customer.models import Device, Land, Spout


class LogDeviceCheckOut(models.Model):
    time = models.DateTimeField('زمان', auto_now_add=True)
    # land = models.ForeignKey(Land, on_delete=models.DO_NOTHING, null=True, blank=True)
    device = models.ForeignKey('Customer.Device', verbose_name='دستگاه', on_delete=models.DO_NOTHING, null=True,
                               blank=True, related_name='device_logs')
    device_message = models.CharField('پیغام دستگاه', max_length=500, blank=True, null=True)
    response_message = models.CharField('پاسخ', max_length=500, blank=True, null=True)
    # is_confirmed = models.BooleanField('پیغام تاییدیه', default=False)
    get_updates = models.BooleanField('دریافت آپدیت اطلاعات', default=False)

    class Meta:
        default_related_name = 'log_device_checkouts'

    def __str__(self):
        return f'{self.id}._device:{self.device_id}' \
               f'_time:{self.time}'


class DeviceNetworkCoverageLog(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey('Customer.Device', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='network_logs')
    land = models.ForeignKey('Customer.Land', on_delete=models.DO_NOTHING, null=True, blank=True)
    value = models.IntegerField('مقدار')
    time = models.DateTimeField('زمان')

    def save(self, *args, **kwargs):
        if self.time is None:
            self.time = timezone.now()
        return super(DeviceNetworkCoverageLog, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.id}.land:{self.land.id}.{self.land.name}_value:{self.value}'


class ExternalButton(models.Model):
    number = models.IntegerField(default=1)
    device = models.ForeignKey('Customer.Device', on_delete=models.CASCADE, related_name='process_buttons', blank=True, null=True)
    name = models.CharField(max_length=100)
    on_in_device = models.BooleanField(default=False)
    customer_reachable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField('modified', null=True, blank=True)

    @property
    def spouts(self) -> list:
        spouts = []
        for event in self.events.all():
            for spout_change in event.spout_changes.all():
                if spout_change.spout not in spouts:
                    spouts.append(spout_change.spout)
        return spouts


    def __init__(self, *args, **kwargs):
        super(ExternalButton, self).__init__(*args, **kwargs)
        self.__original_number = self.number
        self.__original_is_active = self.is_active

    @property
    def duration(self):
        duration = timedelta()
        try:
            duration = ExternalButtonEvent.objects.filter(external_button=self).aggregate(Max('delay'))['delay__max']
        except():
            pass
        return duration

    @property
    def last_record(self):
        try:
            return self.records.filter(process_button=self, time__gt=timezone.now()-self.duration).order_by('-time')[0]
        except IndexError:
            return None
        except TypeError:
            return None

    @property
    def is_on(self):
        record = self.last_record
        if record:
            return record.status == ExternalButtonStatusRecord.STATUS.on
        else:
            return False

    @property
    def is_processing(self):
        return self.is_on != self.on_in_device

    def button_with_shared_spouts(self):
        spouts = self.spouts
        buttons = []
        for button in ExternalButton.objects.filter(device=self.device):
            for button_spout in button.spouts:
                if button_spout in spouts:
                    break
            else:
                continue
            buttons.append(button)
        return buttons

    def save(self, *args, **kwargs):
        external_buttons = ExternalButton.objects.all()
        if not self.number:
            self.number = 1
        while external_buttons.filter(device__id=self.device.id, number=self.number).exclude(id=self.id).count():
            self.number += 1
        if self.modified is None or self.__original_is_active != self.is_active or self.__original_number != self.number:
            self.modified = timezone.now()
        return super(ExternalButton, self).save(*args, **kwargs)

    def __str__(self):
        try:
            return f'process_button:({self.id}."{self.name}" is-on:{self.is_on},' \
                   f'device:{self.device.id} land:{self.device.land.id}' \
                   f'."{self.device.land.name}")'
        except AttributeError:
            return f'process_button:({self.id}."{self.name}" is-on:{self.is_on},'

    @staticmethod
    def test_values(device, number: int = 1) -> dict:
        return {
            'number': number,
            'device': device,
            'name': 'testy_process_button' + str(number)
        }

    def last_change_time(self):
        # print(ExternalButtonEvent.objects.filter(external_button_id=self.id).aggregate(Max('modified')))
        event_change_time = ExternalButtonEvent.objects.filter(
            external_button_id=self.id).aggregate(Max('modified'))['modified__max']
        spout_change_change_time = ExternalButtonEventSpoutChange.objects.filter(
            external_button_event__external_button_id=self.id).aggregate(Max('modified'))['modified__max']

        return max([time for time in [self.modified, event_change_time, spout_change_change_time] if time is not None])


class ExternalButtonEvent(models.Model):
    external_button = models.ForeignKey(ExternalButton, on_delete=models.CASCADE, related_name='events')
    delay = models.DurationField('تاخیر')
    priority = models.IntegerField('اولویت')
    modified = models.DateTimeField('تغییر یافته')

    @property
    def string_condition(self):
        condition = ''
        for spout in self.external_button.device.spouts.all():
            for spout_change in self.spout_changes.all():
                if spout == spout_change.spout:
                    condition += '1' if spout_change.is_on else '0'
                    break
            else:
                condition += '2'
        return condition

    def __str__(self):
        return f'{self.id}.delay:"{self.delay}", button:({str(self.external_button)})'

    @staticmethod
    def test_values(process_button: ExternalButton, delay: timedelta, priority: int = 1) -> dict:
        return {
            'external_button': process_button,
            'delay': delay,
            'priority': priority,
        }

    def save(self, *args, **kwargs):
        self.modified = timezone.now()
        return super(ExternalButtonEvent, self).save(*args, **kwargs)


class ExternalButtonEventSpoutChange(models.Model):
    external_button_event = models.ForeignKey(
        ExternalButtonEvent,
        on_delete=models.CASCADE,
        related_name='spout_changes'
    )
    spout = models.ForeignKey('Customer.Spout', on_delete=models.CASCADE, related_name='external_button_event_change')
    is_on = models.BooleanField('روشن کننده', default=False)
    modified = models.DateTimeField('modified')

    def __str__(self):
        return f'{self.id}.is_on:{self.is_on}, event:({str(self.external_button_event)}), spout:({str(self.spout)})'

    @staticmethod
    def test_values(external_button_event: ExternalButtonEvent, spout, is_on: bool = False) -> dict:
        return {
            'external_button_event': external_button_event,
            'spout': spout,
            'is_on': is_on
        }

    def save(self, *args, **kwargs):
        self.modified = timezone.now()
        return super(ExternalButtonEventSpoutChange, self).save(*args, **kwargs)


class SpoutSensorRecord(TimeStampedModel):
    spout = models.ForeignKey('Customer.Spout', on_delete=models.CASCADE, related_name='spout_sensor_records')
    is_on = models.BooleanField('is_on')

    def __str__(self):
        return f'{self.id}.spout:{self.spout}'


class ExternalButtonStatusRecord(TimeStampedModel):
    # STATUS = Choices(
    #   (0, 'no_change', _('no_change'),
    #   (1, 'off', _('off'),
    #   (2, 'on', _('on'),
    # )
    STATUS = Choices(
        'no_change',
        'off',
        'on'
    )
    status = StatusField(choices=STATUS, default=STATUS.no_change)
    process_button = models.ForeignKey(ExternalButton, on_delete=models.CASCADE, related_name='records')
    time = models.DateTimeField(null=True, blank=True)
    canceled = models.BooleanField('کنسلی', default=False)
    canceled_by = models.ForeignKey('ExternalButtonStatusRecord', verbose_name='کنسل شده توسط', null=True, blank=True,
                                    on_delete=models.CASCADE, related_name='canceled_by_records')
    finished = models.BooleanField('اتمام یافته', default=False)

    APP_ACTOR = 'app_actor'
    DEVICE_ACTOR = 'device_actor'
    UNKNOWN_ACTOR = 'unknown_actor'
    INITIAL_ACTOR = 'initial_actor'
    ACTOR_CHOICES = [
        (APP_ACTOR, 'App_actor'),
        (DEVICE_ACTOR, 'Device_actor'),
        (UNKNOWN_ACTOR, 'Unknown_actor'),
        (INITIAL_ACTOR, 'Initial_actor')
    ]
    actor = models.CharField('مجری', choices=ACTOR_CHOICES, default=UNKNOWN_ACTOR, max_length=20)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='process_records',
                             null=True, blank=True)

    @property
    def end(self):
        return self.time + self.process_button.duration

    def has_finished(self):
        if self.finished:
            return True
        finished = self.end < timezone.now()
        if finished:
            self.finished = finished
            self.save()
        return finished

    def __str__(self):
        return f'process_record:{self.id}.status:{self.status},ex_button:{self.process_button}'

    @classmethod
    def input_to_status(cls, input_value):
        if type(input_value) is str:
            if input_value == '0':
                return cls.STATUS.off
            if input_value == '1':
                return cls.STATUS.on
            if input_value == '2':
                return cls.STATUS.no_change

        if type(input_value) is int:
            if input_value == 0:
                return cls.STATUS.off
            if input_value == 1:
                return cls.STATUS.on
            if input_value == 2:
                return cls.STATUS.no_change
        return None

    @classmethod
    def status_to_input(cls, status):
        if status == cls.STATUS.no_change:
            return '2'
        if status == cls.STATUS.off:
            return '0'
        if status == cls.STATUS.on:
            return '1'

    def save(self, *args, **kwargs):
        if self.time is None:
            self.time = timezone.now()
        super(ExternalButtonStatusRecord, self).save(*args, **kwargs)


class TestCall(models.Model):
    header = models.CharField(max_length=1000, null=True, blank=True)
    body = models.CharField(max_length=1000, null=True, blank=True)