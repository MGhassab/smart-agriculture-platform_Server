import random
from datetime import time, timedelta
from kavenegar import HTTPException
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Max, DateTimeField, ExpressionWrapper, F
from django.db.models.constraints import UniqueConstraint
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
# from .utils import send_sms
from rest_framework.exceptions import APIException, ValidationError

import Baghyar.settings as settings
from Irrigation.models import SpoutChangeRecord
from SMSService.views import send_sms

from Customer import utils


# class Log(models.Model):
#     type = models.CharField('type', max_length=100)
#     description = models.CharField('description', max_length=500)
#     criticalLevel = models.IntegerField()
#
#     def __str__(self):
#         return self.type + "\n " + str(self.criticalLevel)
#
#     pass


# class Contract(models.Model):
#     start_date = models.DateField()
#     due_date = models.DateField()
#     price = models.DateField()
#     brought_date = models.DateField()
#
#     def __str__(self):
#         return self.due_date
#
#     pass


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='کاربر', on_delete=models.CASCADE, related_name='customers')
    phoneNumber = models.CharField('شماره تماس', max_length=12)
    isBlocked = models.BooleanField('بلاک شده', default=False)
    isActivated = models.BooleanField('فعال شده', default=False)
    type = models.CharField('نوع', max_length=20, default='baghyar')
    is_admin = models.BooleanField('ادمین', default=False)
    is_supervisor = models.BooleanField('پشتیبان', default=False)
    has_registered_land = models.BooleanField('زمین ثبت‌شده دارد', default=False)

    @property
    def is_customer(self):
        return not self.is_admin and not self.is_admin
    #
    # def __init__(self, user: User, phoneNumber, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.user = user
    #     if isinstance(phoneNumber, int):
    #         self.phoneNumber = str(phoneNumber)
    #     if isinstance(phoneNumber, str):
    #         self.phoneNumber = phoneNumber

    def __str__(self):
        return f'{self.id}.phone={self.phoneNumber}:user={self.user.id}.{self.user.username}' \
               f'_name={self.user.first_name}_{self.user.last_name}_isAdmin:{self.is_admin}'
        # return self.user.username + "_" + self.phoneNumber

    @classmethod
    def get_or_create(cls, user: User):
        customers = Customer.objects.filter(user__id=user.id)
        if customers.count():
            return customers.first()
        customer = cls(user=user, phoneNumber=user.username)
        customer.save()
        return customer

    pass


class Land(models.Model):
    name = models.CharField('نام', max_length=500)
    location = models.CharField('مکان', max_length=100, blank=True, null=True)
    customers = models.ManyToManyField(Customer, verbose_name='مشتری‌ها', related_name='lands', blank=True)
    device = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='land', blank=True, null=True)
    serial = models.CharField('serial', default='', max_length=30, blank=True, null=True)
    area = models.IntegerField('area', default=1)
    is_active = models.BooleanField('is active', default=True)
    need_program_check = models.BooleanField('is modified', default=False)
    last_program_change = models.DateTimeField('last_program_change', blank=True, null=True)
    owner = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, related_name='owned_lands', blank=True, null=True)
    longitude = models.FloatField('longitude', null=True, default=settings.DEFAULT_LONGITUDE)
    latitude = models.FloatField('latitude', null=True, default=settings.DEFAULT_LATITUDE)
    city = models.CharField('city', max_length=20, default=settings.DEFAULT_LOCATION)
    last_time_programs_evaluated = models.DateTimeField('last time programs evaluated', null=True, blank=True)
    has_advance_time = models.BooleanField('has advance time', default=False)

    def __str__(self):
        return f'{self.id}.{self.name}_located:{self.location}_area:{self.area}_serial:{self.serial}'

    def set_to_be_checked(self):
        if not self.need_program_check:
            self.need_program_check = True
            self.save()

    def checked(self):
        if self.need_program_check:
            self.need_program_check = False
            self.save()

    def update_last_time_programs_evaluated(self, eval_time):
        self.last_time_programs_evaluated = eval_time
        self.save()

    def reset_serial(self):
        num1 = random.randint(10000000, 100000000)
        num2 = random.randint(10000000, 100000000)
        self.serial = str(num1) + str(num2)
        self.save()

    @staticmethod
    def test_values():
        return {'name': 'test_land', 'location': 'Petus_test', 'serial': '5364343646353423546', 'city': 'Tehran'}

    @classmethod
    def testy_obj(cls, **kwargs):
        return cls.objects.create(**cls.test_values(**kwargs))

    def has_name(self):
        return not(self.name is None or len(self.name) == 0 or self.name.isspace())


class Device(models.Model):
    serial = models.CharField('سریال', max_length=30)
    land = models.ForeignKey(Land, verbose_name='زمین', on_delete=models.CASCADE, related_name='devices', blank=True, null=True)
    is_active = models.BooleanField('فعال', default=True)
    name = models.CharField('نام', max_length=500, blank=True, null=True)
    update_period = models.DurationField(
        'دوره اتصال به دستگاه',
        default=timedelta(minutes=settings.DEVICE_CONNECTION_LOG_MINUTES),
    )
    delay_to_action = models.DurationField(
        'تاخیر تا اعمال',
        default=timedelta(seconds=settings.DEVICE_DELAY_TO_ACTION_DEFAULT_SECONDS)
    )
    type_number = models.IntegerField('نوع عددی مدل', 'type_number', default=1)
    last_modified_program = models.DateTimeField(null=True, blank=True)
    last_modified_button = models.DateTimeField(null=True, blank=True)

    @property
    def customers(self):
        return self.land.customers

    def __str__(self):
        name = f'land:{self.land.id}.{self.land.name}' if self.land else "landless"
        return f'{self.id}.{name}_serial:{self.serial}'

    @property
    def customer_process_buttons(self):
        return self.process_buttons.filter(is_active=True, customer_reachable=True)

    @staticmethod
    def test_values(land: Land, serial: str = '123456'):
        return {
            'name': 'testy_device_name',
            'land': land,
            'serial': serial,
        }

    @classmethod
    def testy_obj(cls, **kwargs):
        return cls.objects.create(**cls.test_values(**kwargs))

    def has_name(self):
        return not(self.name is None or len(self.name) == 0 or self.name.isspace())

    def update_last_modified_program(self):
        if self.last_modified_program is None or self.last_modified_program + timedelta(seconds=1) < timezone.now():
            self.last_modified_program = timezone.now()
            self.save()

    def update_last_modified_button(self):
        if self.last_modified_button is None or self.last_modified_button + timedelta(seconds=1) < timezone.now():
            self.last_modified_button = timezone.now()
            self.save()

    def has_user_access(self, user):
        customer = Customer.get_or_create(user)
        return self.customers.filter(id=customer.id).count() > 0

# class Sensor(models.Model):
#
#     class Meta:
#         abstract = False
#
#     type = models.CharField('sensor_type', max_length=10, default='temp', blank=True)
#     value = models.CharField('value', max_length=100, default=0)
#     land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='%(class)ss')
#     created = models.DateTimeField(editable=False)
#     modified = models.DateTimeField()
#
#     def save(self, *args, **kwargs):
#         if not self.id:
#             self.created = timezone.now()
#         self.modified = timezone.now()
#         return super(Sensor, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return "sensor" + self.type + "_" + self.value + "_" + self.land.name


class Spout(models.Model):
    name = models.CharField('نام', max_length=100)
    number = models.IntegerField('شماره')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='spouts', null=True)
    isOn = models.BooleanField('روشن', default=False)
    modified = models.DateTimeField('زمان آخرین تغییر', blank=True, null=True)
    is_active = models.BooleanField('فعال', default=True)
    default_is_on_value = models.BooleanField('مقدار پیش فرض', default=False)
    # type_no = models.IntegerField('نوع', default=1)
    # TODO: check if can be removed
    last_record = models.ForeignKey(SpoutChangeRecord, on_delete=models.SET_NULL, related_name='last_record_spouts',
                                    null=True, blank=True)
    # process_records = models.ManyToManyField(to='Irrigation.ProcessSpoutChangeRecord', related_name='spouts')

    USER_CONTROL = 'user'
    PROGRAM_CONTROL = 'program'
    PROCESS_CONTROL = 'process'
    UNKNOWN_CONTROL = 'unknown'
    OFF_NO_CONTROL = 'no_control'
    CONTROLLER = (
        (USER_CONTROL, 'کنترل از کاربر'),
        (PROGRAM_CONTROL, 'کنترل از برنامه'),
        (PROCESS_CONTROL, 'کنترل از پروسه'),
        (UNKNOWN_CONTROL, 'کنترل نا مشخص'),
        (OFF_NO_CONTROL, 'کنترل نشده'),
    )
    controller = models.CharField('کنترل کننده', choices=CONTROLLER, max_length=50, default=UNKNOWN_CONTROL)

    class Meta:
        ordering = ['number']

    @property
    def is_watering(self):
        sensor = SpoutSensor.objects.filter(spout__id=self.id).first()
        try:
            return sensor.isOn
        except AttributeError:
            return self.isOn

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        if self.device and self.device.land:
            return f'{self.id}.{self.name}_number:{self.number},{"on" if self.isOn else "off"},' \
                   f'device:({self.device.id}.{self.device.name})' \
                   f'land:({self.device.land.id}.{self.device.land.name})'
        else:
            return f'{self.id}.{self.name}_number:{self.number},{"on" if self.isOn else "off"},'

    def save(self, *args, **kwargs):
        self.send_sms_to_receivers()
        self.on_save_updates()
        return super().save(*args, **kwargs)

    def send_sms_to_receivers(self):
        sms_receivers = SmsReceiver.objects.all().filter(spout__id=self.id)
        for sms_receiver in sms_receivers:
            sms_receiver.notify(self.isOn)

    def on_save_updates(self):
        right_now = timezone.now()
        # self.eval_programs_on_spout_is_on(right_now)
        self.modified = right_now

    # def eval_programs_on_spout_is_on(self, eval_time: timezone.datetime = timezone.now()):
    #     try:
    #         spout_changes = ChangeSpout.objects \
    #             .filter(spout__id=self.id) \
    #             .filter(sub_program__program_group__land=self.device.land)
    #         spout_changes_with_start = spout_changes \
    #             .annotate(start=ExpressionWrapper(
    #                 F('sub_program__program_group__start') + F('sub_program__delay'),
    #                 output_field=DateTimeField()
    #             ))
    #         spout_changes_with_start_on_update_period = spout_changes_with_start \
    #             .filter(start__lte=eval_time).filter(start__gt=F('spout__modified'))
    #         latest_spout_change_value = spout_changes_with_start_on_update_period \
    #             .latest('start')
    #         self.isOn = latest_spout_change_value.is_on
    #     except AttributeError:
    #         pass
    #     except ChangeSpout.DoesNotExist:
    #         pass

    @staticmethod
    def test_values(number: int = 1, device: Device = None):
        values = [
            {'name': 'test_spout1', 'number': 1, 'device': device},
            {'name': 'test_spout2', 'number': 2, 'device': device},
            {'name': 'test_spout3', 'number': 3, 'device': device},
            {'name': 'test_spout4', 'number': 4, 'device': device},
        ]
        return {
            'name': 'test_spout' + str(number),
            'number': number,
            'device': device,
        }

    @classmethod
    def testy_obj(cls, number, device=None):
        return cls.objects.create(**cls.test_values(number, device))


class SpoutSensor(models.Model):
    spout = models.OneToOneField(Spout, on_delete=models.CASCADE, related_name='spoutSensor')
    isOn = models.BooleanField(default=False)

    def __str__(self):
        return "spout sensor " + self.spout.name + "_" + self.spout.device.land.name


class ChangeSpout(models.Model):
    spout = models.ForeignKey(Spout, on_delete=models.CASCADE, related_name='spout_changes')
    is_on = models.BooleanField('is on', default=False)
    unchange = models.BooleanField('unchange', default=False)
    sub_program = models.ForeignKey('SubProgram', on_delete=models.CASCADE, related_name='spouts', null=True)
    modified = models.DateTimeField('آخرین زمان تغییر', auto_now=True, null=True, blank=True, )

    @property
    def spout_name(self):
        return self.spout.name if self.spout else ""

    @property
    def spout_number(self):
        return self.spout.number if self.spout else ""

    @property
    def land(self):
        return self.sub_program.program_group.land

    @property
    def start(self):
        return self.sub_program.start

    class Meta:
        default_related_name = 'change_spouts'
        # unique_together = [['spout', 'sub_program']]
        constraints = [
            UniqueConstraint(fields=['spout', 'sub_program'], name='unique spout and sub program for change spout')
        ]

    def __str__(self):
        name_str = f'{self.id}.{"on" if self.is_on else "off"}'
        try:
            return f'{name_str}_{self.spout.name},' \
                   f'program:{str(self.sub_program)}'
        except AttributeError:
            pass
        return name_str

    def save(self, *args, **kwargs):
        # self.update_land_modified()
        # self.sub_program.save()
        return super(ChangeSpout, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # self.update_land_modified()
        return super(ChangeSpout, self).save(*args, **kwargs)

    # def update_land_modified(self):
    #     self.land.set_to_be_checked()

    @staticmethod
    def test_values(spout: Spout, sub_program, is_on: bool = False, un_change: bool = False):
        return {
            'spout': spout,
            'sub_program': sub_program,
            'is_on': is_on,
            'unchange': un_change,
        }

    @classmethod
    def testy_obj(cls, **kwargs):
        return cls.objects.create(**cls.test_values(**kwargs))


class ProgramGroup(models.Model):
    name = models.CharField('نام', max_length=50, default="no_name_pr", blank=True, null=True)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='program_groups')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='program_groups', null=True, blank=True)
    repeatable = models.BooleanField('قابلیت تکرار', default=True)
    interval = models.DurationField('بازه‌های تکرار', default=timedelta(days=7), null=True)
    start = models.DateTimeField('زمان شروع', default=timezone.now)
    next_start = models.DateTimeField('زمان شروع بعدی', default=timezone.now, null=True, blank=True)
    last_start = models.DateTimeField('آخرین زمان انجام', null=True, blank=True)
    passed = models.BooleanField('عبور کرده', default=False)
    has_changes = models.BooleanField('تغییر یافته', default=False)
    number1 = models.IntegerField('شماره اول', default=0)
    number2 = models.IntegerField('شماره‌ دوم', default=0)
    last_change_time = models.DateTimeField('آخرین زمان تغییر', blank=True, null=True)
    modified = models.DateTimeField('آخرین زمان تغییر', auto_now=True, null=True, blank=True, )
    has_synced = models.BooleanField(default=False)
    last_program_cancel = models.DateTimeField(null=True, blank=True)
    # spout_changes = models.ManyToManyField(ChangeSpout, related_name='program_groups')

    @property
    def max_delay(self):
        max_delay = SubProgram.objects.filter(program_group__id=self.id).aggregate(Max('delay'))['delay__max']
        return timedelta(minutes=1) if max_delay is None or max_delay < timedelta(minutes=1) else max_delay

    @property
    def end(self):
        try:
            max_delay = self.max_delay
            return self.next_start + max_delay if max_delay is not None else self.next_start
        except AttributeError:
            return self.start

    def is_ongoing(self):
        right_now = timezone.now()
        max_delay = self.max_delay
        if self.last_start is not None and self.last_start <= right_now <= self.last_start + max_delay:
            if not self.last_program_cancel or self.last_program_cancel < self.last_start:
                return True
        if self.next_start is not None and self.next_start <= right_now <= self.next_start + max_delay:
            if not self.last_program_cancel or self.last_program_cancel < self.next_start:
                return True
        if self.start <= right_now <= self.start + max_delay:
            if not self.last_program_cancel or self.last_program_cancel < self.start:
                return True
        return False

    class Meta:
        constraints = [
            models.CheckConstraint(name='valid interval', check=models.Q(interval__gte=timedelta(minutes=1)))
        ]

    def __init__(self, *args, **kwargs):
        super(ProgramGroup, self).__init__(*args, **kwargs)
        self.__original_repeatable = self.repeatable
        self.__original_interval = self.interval
        self.__original_start = self.start

    def __str__(self):
        name = f'{self.id}.{self.name},land:{self.land.id}.{self.land.name},next_start:{repr(self.next_start)}' \
               f'{",repeatable:" + repr(self.interval) + "," if self.repeatable else ""}'
        if self.land is not None:
            name += '_land:' + self.land.name
        return name

    def save(self, *args, **kwargs):
        # if self.interval < timedelta(minutes=5):
        #     raise ValueError('time delta must be greater than 5 minutes')
        # self.update_land_modified()
        if self.id is None or self.number1 < 10 or self.number2 < 10:
            self.number1 = self.find_min_available_number()
            self.number2 = self.find_min_available_number(exclude=self.number1)

        if self.id is None or self.__original_start != self.start:
            self.next_start = self.next_run_time()
            
        if self.__original_interval != self.interval or self.__original_repeatable != self.repeatable or \
                self.__original_start != self.start or self.last_change_time is None:
            self.__original_interval = self.interval
            self.__original_repeatable = self.repeatable
            self.__original_start = self.start
            self.last_change_time = timezone.now()
            if self.device:
                self.device.update_last_modified_program()

        # self.land.need_program_check = True
        # self.land.last_program_change = timezone.now()
        # self.land.save()
        if self.name is None or len(self.name) == 0:
            self.name = "no name"

        return super(ProgramGroup, self).save(*args, **kwargs)

    def next_run_time_today(self):
        if self.interval < timedelta(minutes=5):
            return None
        if self.interval.seconds != 0:
            return None
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        program_start_day = self.start.replace(hour=0, minute=0, second=0, microsecond=0)
        if program_start_day < today:
            passed_days = (today - program_start_day).days
            try:
                passed_repeats = int((passed_days - 1) / self.interval.days)
            except ZeroDivisionError:
                passed_repeats = 0
            return self.start + (self.interval * (passed_repeats + 1))
        else:
            return self.start

    def next_run_time(self):
        time = self.next_run_time_today()
        if time < timezone.now():
            return time + self.interval
        return time

    def find_min_available_number(self, exclude=0):
        p_groups = ProgramGroup.objects.filter(land=self.land).exclude(id=self.id)
        found_number = False
        min_number = 10
        while found_number is False:
            if p_groups.filter(number1=min_number).count() == 0 and p_groups.filter(number2=min_number).count() == 0 \
                    and min_number != exclude:
                found_number = True
            else:
                min_number += 1
        return min_number

    @staticmethod
    def test_values(
            land: Land, repeatable: bool = False, interval: timedelta = timedelta(days=1),
            start: timezone.datetime = timezone.now()) -> dict:
        return {
            'name': 'testy_program_group',
            'land': land,
            'repeatable': repeatable,
            'interval': interval,
            'start': start,
        }

    @classmethod
    def testy_obj(cls, **kwargs):
        return cls.objects.create(**cls.test_values(**kwargs))

    def can_edit(self, user):
        land = self.device.land
        return Customer.get_or_create(user=user).lands.filter(id=land.id).count() > 0

    def set_synced(self, value):
        if self.has_synced != value:
            self.has_synced = value
            self.save()


class SubProgram(models.Model):
    program_group = models.ForeignKey(ProgramGroup, on_delete=models.CASCADE, related_name='programs', null=True)
    # spout_changes = models.ManyToManyField(ChangeSpout, related_name='sub_programs')
    number = models.IntegerField('number', default=1)
    delay = models.DurationField(default=timedelta(hours=1))
    device_id = models.IntegerField('device_id', default=10)
    modified = models.DateTimeField('آخرین زمان تغییر', auto_now=True, null=True, blank=True, )

    @property
    def start(self):
        if not self.program_group:
            return None
        return self.delay + self.program_group.start

    @property
    def land(self):
        return self.program_group.land
    #
    # @property
    # def is_out_dated(self):
    #     try:
    #         if self.program_group.repeatable:
    #             return False
    #         return self.next_start <= timezone.now()
    #     except AttributeError:
    #         return True

    class Meta:
        default_related_name = 'sub_programs'
        # unique_together = [['program_group', 'number']]
        constraints = [
            UniqueConstraint(fields=['program_group', 'number'], name='unique program_group and number for sub program')
        ]

    def __str__(self):
        try:
            return f'{self.id}.num_{str(self.number)},program_group:{self.program_group.id}.' \
                   f'"{self.program_group.name}"' \
                   f',land:{self.land.id}."{self.land.name}", start="{self.start.strftime("%x,%X")}"'
        except AttributeError:
            pass
        return 'sub' + str(self.number)

    def save(self, *args, **kwargs):
        # sub_programs = SubProgram.objects.exclude(id=self.id)\
        #     .filter(program_group=self.program_group, number=self.number)
        # if sub_programs.count():
        #     raise ValueError('repeated program group or number')
        if self.program_group is not None:
            if self.program_group.repeatable and self.delay >= self.program_group.interval:
                raise ValueError("delay must be less than program_group intervals")
        has_repeated_id = SubProgram.objects.filter(
            program_group__land=self.program_group.land, device_id=self.device_id)\
            .exclude(id=self.id).count() != 0
        if self.id is None or self.device_id is None or has_repeated_id:
            new_id = settings.PROGRAM_NEW_ID_FROM
            sub_programs_device_ids = SubProgram.objects.filter(program_group__land=self.program_group.land)\
                .values_list('device_id', flat=True)
            while new_id in sub_programs_device_ids:
                new_id += 1
            self.device_id = new_id
        if self.device_id > settings.MAX_PROGRAM_FOR_LAND + settings.PROGRAM_NEW_ID_FROM:
            raise ValueError("max number of programs for land exceeded")
        # self.update_land_modified()
        # self.program_group.save()
        return super(SubProgram, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # self.update_land_modified()
        return super(SubProgram, self).delete(*args, **kwargs)

    def update_land_modified(self):
        self.land.set_to_be_checked()

    @staticmethod
    def test_values(program_group: ProgramGroup, delay: timedelta = timedelta(seconds=0), number: int = 1) -> dict:
        return {
            'program_group': program_group,
            'delay': delay,
            'number': number,
        }

    @classmethod
    def testy_obj(cls, **kwargs):
        return cls.objects.create(**cls.test_values(**kwargs))


# class Program(models.Model):
#     name = models.CharField(max_length=50, blank=True)
#     spouts_condition_str = models.CharField('sensor_condition_str', max_length=settings.MAX_SPOUT_QUANTITY, default="")
#     spouts = models.ManyToManyField(Spout, related_name='programs')
#     land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='programs')
#     start = models.DateTimeField()
#     interval = models.DurationField(default=timedelta(days=7))
#     number = models.IntegerField('H_Number', default=10,)
#     is_modified = models.BooleanField('modified', default=False)
#     modified = models.DateTimeField(auto_now_add=True, null=True)
#     has_repeat = models.BooleanField('has repeat', default=True)
#
#     def set_spouts(self):
#         # print("set_spouts ")
#         spouts = list(self.spouts.order_by('number'))
#         # print("#" + str(len(spouts)))
#         if len(spouts) is not len(self.spouts_condition_str):
#             # set log error
#             # print ("\n error \n" + str(spouts) + "  " + str(self.spouts_condition_str))
#             return
#         else:
#             for spout in spouts:
#                 # print("spouts update")
#                 # print(self.spouts_condition_str + " _ " + str(spout.number))
#                 spout.isOn = self.spouts_condition_str[spout.number - 1]
#                 # print("spout " + str(spout.number) + " isOn=" + spout.isOn)
#                 spout.save()
#
#     def check_is_turn(self):
#         if utils.get_current_time() > self.start:
#             self.set_spouts()
#             self.start = self.start + self.interval
#             self.save()
#             return True
#         return False
#
#     def save(self, *args, **kwargs):
#         if self.interval < timedelta(minutes=1):
#             raise ValidationError("period should be greater than 1 minutes")
#         if not self.id:
#             # temp shit code
#             p_list = Program.objects.filter(land=self.land)
#             for num in range(10, 100):
#                 ok = True
#                 for program in p_list:
#                     self.number = num
#                     if num == program.number:
#                         ok = False
#                         break
#                 if ok:
#                     break
#
#         self.land.need_program_check = True
#         self.is_modified = True
#         # self.modified = timezone.now()
#         return super(Program, self).save(*args, **kwargs)
#
#     def __str__(self):
#         spout_list = [f'{spout.id}.{spout.name},' for spout in self.spouts.all()]
#
#         # return self.name
#         return f'=>{self.id}.{self.name}_Program:{self.land.id}.{self.land.name}__spouts:_{spout_list}' \
#                f'__start:{self.start}_period:{self.interval}_end:{self.start + self.interval}'
#         # return self.name \
#         #     + "_Program:_land:_" \
#         #     + str(self.land) \
#         #     + "__spouts_" + spout_list \
#         #     + "_start:" + str(self.start) \
#         #     + "_period:" + str(self.interval) \
#         #     + "_end:" + str(self.start + self.interval)
#         #     + str(self.spouts.first().land) \


class SmsReceiver(models.Model):
    number = models.CharField('شماره', max_length=20)
    spout = models.ForeignKey(Spout, verbose_name='شیر خروجی', on_delete=models.CASCADE, related_name='sms_receivers')

    def notify(self, is_on):
        # send_sms(self.number, 'notify', 'spout' + str(self.spout.number) + '_' + ('on' if is_on else 'off'))
        try:
            send_sms(self.number, 'notify', 'spout' + ('on' if is_on else 'off'))
        except APIException:
            pass
        except HTTPException:
            pass


class TempSensor(models.Model):

    temp_value = models.FloatField('temp_value', default=0)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='tempSensors')
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_string = models.CharField('created_string', max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
            self.date = timezone.now()
            # DailyInfos.set_on_temp_sensor(self)
        self.modified = timezone.now()
        self.created_string = utils.date_to_string(self.created)
        return super(TempSensor, self).save(*args, **kwargs)

    def __str__(self):
        return "Temp Sensor " + repr(self.temp_value) + "_" + self.land.name


class EvaporationSensor(models.Model):
    evaporation_value = models.FloatField('evaporation_value', default=0)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='evaporationSensors')
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_string = models.CharField('created_string', max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        self.created_string = utils.date_to_string(self.created)
        return super(EvaporationSensor, self).save(*args, **kwargs)

    def __str__(self):
        return "Evaporation Sensor " + repr(self.evaporation_value) + "_" + self.land.name


class WaterSensor(models.Model):
    water_value = models.IntegerField('water_value', default=0)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='waterSensors')
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_string = models.CharField('created_string', max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        self.created_string = utils.date_to_string(self.created)
        return super(WaterSensor, self).save(*args, **kwargs)

    def __str__(self):
        return "Water Sensor " + repr(self.water_value) + "_" + self.land.name


class TrialWaterSensor(models.Model):
    trial_water_value = models.IntegerField('trial_water_value', default=0)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='trialWaterSensors')
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_string = models.CharField('created_string', max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        self.created_string = utils.date_to_string(self.created)
        return super(TrialWaterSensor, self).save(*args, **kwargs)

    def __str__(self):
        return "Trial Water Sensor " + repr(self.trial_water_value) + "_" + self.land.name


class SoilMoistureSensor(models.Model):

    soil_moisture_value = models.FloatField('soil_moisture_value', default=0)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='soilMoistureSensors')
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_string = models.CharField('created_string', max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
            # DailyInfos.set_on_soil_moisture_sensor(self)

        self.modified = timezone.now()
        self.created_string = utils.date_to_string(self.created)
        return super(SoilMoistureSensor, self).save(*args, **kwargs)

    def __str__(self):
        return "Soil Moisture Sensor " + repr(self.soil_moisture_value) + "_" + self.land.name


class HumiditySensor(models.Model):

    humidity_value = models.FloatField('humidity_value', default=0)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='humiditySensors')
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_string = models.CharField('created_string', max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
            # DailyInfos.set_on_humidity_sensor(self)
        self.modified = timezone.now()
        self.created_string = utils.date_to_string(self.created)
        return super(HumiditySensor, self).save(*args, **kwargs)

    def __str__(self):
        return "Humidity Sensor " + repr(self.humidity_value) + "_" + self.land.name

# # TODO: to be completed
# class Program(models.Model):
#     start = models.DateTimeField('زمان شروع',)
#     duration = models.DurationField('مدت زمان',)
#     next_start = models.DateTimeField('اجرای بعدی',)
#     modified = models.DateTimeField(auto_now=True,)


@receiver([post_save, post_delete], sender=ChangeSpout)
def changed_change_spout(sender, instance: ChangeSpout, **kwargs):
    try:
        device = instance.sub_program.program_group.device
        if device:
            device.update_last_modified_program()
    except (ProgramGroup.DoesNotExist, SubProgram.DoesNotExist, TypeError, AttributeError) as e:
        pass


@receiver([post_save, post_delete], sender=SubProgram)
def changed_sub_program(sender, instance: SubProgram, **kwargs):
    try:
        device = instance.program_group.device
        if device:
            device.update_last_modified_program()
    except (ProgramGroup.DoesNotExist, TypeError, AttributeError) as e:
        pass


@receiver(post_delete, sender=ProgramGroup)
def changed_program_group(sender, instance: ProgramGroup, **kwargs):
    try:
        device = instance.device
        if device:
            device.update_last_modified_program()
    except (TypeError, AttributeError) as e:
        pass
