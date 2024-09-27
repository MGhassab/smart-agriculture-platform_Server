from rest_framework import serializers
from . import models
from .models import DeviceNetworkCoverageLog
from Customer.models import Device, SubProgram, ChangeSpout
from Baghyar import utils as global_utils, serializers as global_serializers
from django.utils import timezone


class LogDeviceCheckOut(serializers.ModelSerializer):
    class Meta:
        model = models.LogDeviceCheckOut
        fields = ['id', 'time', 'land', 'device', 'message']


class SubProgramSerializer(serializers.ModelSerializer):
    pk = serializers.SerializerMethodField()
    # pk = serializers.IntegerField(source='device_id')
    start = serializers.SerializerMethodField()
    # start = global_serializers.DateTimeFieldWihTZ(formet='%Y/%m/%d %H:%M:%S')
    action = serializers.SerializerMethodField()
    interval = serializers.SerializerMethodField()
    has_interval = serializers.SerializerMethodField()

    class Meta:
        model = SubProgram
        fields = ['pk', 'start', 'interval', 'action', 'has_interval']
        # fields = ['id', 'start', 'action', 'interval', 'has_interval']

    def get_pk(self, sub_program: SubProgram):
        return f'{sub_program.device_id:02d}'

    def get_start(self, sub_program: SubProgram):
        # global_utils.update_program_group(sub_program.program_group)
        time = sub_program.start
        # time &= timezone.localtime(sub_program.start)
        return device_time_encoder(time)

    def get_action(self, sub_program: SubProgram):
        change_spouts = sub_program.spouts.all().order_by('spout__number')
        spouts = sub_program.program_group.device.spouts.all().order_by('number')
        # array = ["2" if change_spout.unchange else "1" if change_spout.is_on else "0" for change_spout in change_spouts]
        # return "".join(array)
        response = ""
        for spout in spouts:
            for change_spout in change_spouts:
                if change_spout.spout.id == spout.id:
                    response += "2" if change_spout.unchange else "1" if change_spout.is_on else "0"
                    break
            else:
                response += "2"
        return response

    def get_interval(self, sub_program: SubProgram):
        return device_interval_encoder(sub_program.program_group.interval) if sub_program.program_group else None

    def get_has_interval(self, sub_program: SubProgram):
        return sub_program.program_group.repeatable if sub_program.program_group else None

    # def get_start(self, sub_program):
    #     return sub_program['delay']
    #     # return sub_program.delay + sub_program.program_group.start if sub_program.program_group else sub_program.delay


def device_time_encoder(date_time):
    return f'{in_digits_str(date_time.year, 4)}/' \
           f'{in_digits_str(date_time.month, 2)}/' \
           f'{in_digits_str(date_time.day, 2)},' + \
           f'{in_digits_str(date_time.hour, 2)}:' \
           f'{in_digits_str(date_time.minute, 2)}:' \
           f'{in_digits_str(date_time.second, 2)}'


def in_digits_str(int_value, digits):
    value = str(int_value)
    while len(value) < digits:
        value = '0' + value
    return value


def device_interval_encoder(period):
    return f'{period.days} ' \
           f'{in_digits_str(period.seconds // 3600, 2)}:' \
           f'{in_digits_str((period.seconds % 3600) // 60, 2)}:' \
           f'{in_digits_str(period.seconds % 60, 2)}'


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'serial', 'land']


class DeviceNetworkCoverageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceNetworkCoverageLog
        fields = ['id', 'device', 'land', 'value']

