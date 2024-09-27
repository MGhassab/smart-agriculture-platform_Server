from datetime import timedelta, datetime
from operator import itemgetter

from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from Baghyar import settings
from Customer.models import Land, TempSensor, WaterSensor, SoilMoistureSensor, TrialWaterSensor, \
    HumiditySensor, Spout, ProgramGroup, SubProgram, ChangeSpout, Device
from Device.models import ExternalButton, ExternalButtonEvent, ExternalButtonEventSpoutChange, DeviceNetworkCoverageLog, \
    ExternalButtonStatusRecord, LogDeviceCheckOut
from Device.utils import is_land_online, get_last_log_time, get_next_update_time

from LightApp.errors import Error2006MissingValues, Error2008CantCreateNewSpout
from LightApp.utils import replace_farsi_num


class ChangeSpoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeSpout
        fields = (
            'id',
            # 'sub_program',
            'spout', 'is_on',
            # 'spout_name',
            # 'spout_number'
        )


class SubProgramSerializer(serializers.ModelSerializer):
    # spouts = ChangeSpoutSerializer(many=True, read_only=True)
    change_spouts = serializers.SerializerMethodField()

    class Meta:
        model = SubProgram
        fields = (
            'id',
            'number', 'delay', 'change_spouts'
        )

    def get_change_spouts(self, device: Device):
        spouts = device.spouts.all().order_by('spout__number')
        return ChangeSpoutSerializer(spouts, many=True, context=self.context).data


class ProgramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramGroup
        fields = ('id', 'name', 'land', 'device', 'repeatable', 'interval', 'start')


class DetailedProgramGroupSerializer(serializers.ModelSerializer):
    programs = SubProgramSerializer(many=True, read_only=True)
    # land = serializers.SlugRelatedField(
    #     many=False,
    #     read_only=True,
    #     slug_field='id',
    # )
    start = serializers.DateTimeField(format=settings.REST_FRAMEWORK['DATETIME_FORMAT'])  # +', %a')

    class Meta:
        model = ProgramGroup
        fields = ('id', 'name', 'repeatable', 'interval', 'start', 'programs', 'is_ongoing',
                  # 'land',
                  'last_program_cancel',
                  )
        depth = 2


class SpoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spout
        fields = ('id', 'name', 'number', 'isOn', 'is_watering', 'is_active')


class LandSerializer(serializers.ModelSerializer):
    # sensors = serializers.SerializerMethodField()
    # spouts = SpoutSerializer(many=True, read_only=True)
    # program_groups = DetailedProgramGroupSerializer(many=True, read_only=True)
    # device_online = serializers.SerializerMethodField('is_device_online')
    # last_device_log_time = serializers.SerializerMethodField()
    # next_device_update = serializers.SerializerMethodField()
    # is_owner = serializers.SerializerMethodField()


    class Meta:
        model = Land
        fields = (
            'id', 'name', 'location', 'area',
            # 'sensors',
            # 'device_online',
            # 'is_owner',
            # 'last_device_log_time',
            # 'next_device_update',
            'longitude', 'latitude', 'city', 'has_advance_time',
        )
        depth = 3

    # def get_sensors(self, land):
    #     soils = SoilMoistureSensor.objects.filter(land=land)
    #     waters = WaterSensor.objects.filter(land=land)
    #     humiditys = HumiditySensor.objects.filter(land=land)
    #     temps = TempSensor.objects.filter(land=land)
    #     sensors = {}
    #     if soils.count():
    #         sensors['soil'] = soils.order_by('-created')[0].soil_moisture_value
    #     if waters.count():
    #         sensors['water'] = waters.order_by('-created')[0].water_value
    #     if humiditys.count():
    #         sensors['humidity'] = humiditys.order_by('-created')[0].humidity_value
    #     if temps.count():
    #         sensors['temp'] = temps.order_by('-created')[0].temp_value
    #     return sensors

    # def is_device_online(self, land):
    #     return is_land_online(land)

    # def get_last_device_log_time(self, land: Land):
    #     return get_last_log_time(land)
    #
    # def get_next_device_update(self, land: Land):
    #     return get_next_update_time(land.devices.all()[0])

    # def get_is_owner(self, land: Land):
    #     customer = self.get_customer(land)
    #     if customer and land.owner and land.owner.id is customer.id:
    #         return True
    #     return False
    #
    # def get_customer(self, obj):
    #     return self.context.get('customer', None)


class PBSpoutChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalButtonEventSpoutChange
        fields = ('id', 'spout', 'is_on', )


class PBEventSerializer(serializers.ModelSerializer):
    spout_changes = PBSpoutChangeSerializer(many=True, read_only=True)

    class Meta:
        model = ExternalButtonEvent
        fields = ('id', 'delay', 'priority', 'spout_changes')


class ProcessButtonSerializer(serializers.ModelSerializer):
    events = PBEventSerializer(many=True, read_only=True)
    function = serializers.SerializerMethodField(read_only=True)
    # has_confirmed = serializers.SerializerMethodField()
    reached_time_to_action = serializers.SerializerMethodField()

    class Meta:
        model = ExternalButton
        fields = ('id', 'name', 'number',
                  'function',
                  'on_in_device', 'is_processing', 'is_active',
                  # 'has_confirmed',
                  'reached_time_to_action',
                  'events')
        extra_kwargs = {
            'on_in_device': {'read_only': True}
        }

    def get_reached_time_to_action(self, button: ExternalButton):
        try:
            device = button.device
            last_record = button.records.exclude(status=ExternalButtonStatusRecord.STATUS.no_change).order_by('-time')[0]
            log_after_record = device.device_logs.filter(time__gt=last_record.time, get_updates=True).\
                order_by('time')[0]
            action_time = log_after_record.time + device.delay_to_action
            return timezone.now() > action_time
        except IndexError:
            return False

    def get_function(self, button: ExternalButton):
        return button.is_on

    # def get_has_confirmed(self, button: ExternalButton):
    #     is_confirmed = (button.device)
    #     return button.is_processing and is_confirmed


class DeviceSerializer(serializers.ModelSerializer):
    weekly_ordered_program_groups_value = None
    # on_going_index = None
    # records = None

    # TODO: refactor all fields to run from device
    # sensors = serializers.SerializerMethodField()
    spouts = SpoutSerializer(many=True, read_only=True)
    # program_groups = DetailedProgramGroupSerializer(many=True, read_only=True)
    device_online = serializers.SerializerMethodField('is_device_online')
    last_device_log_time = serializers.SerializerMethodField()
    next_device_update = serializers.SerializerMethodField()
    time_to_action = serializers.SerializerMethodField()
    # is_owner = serializers.SerializerMethodField()
    land = LandSerializer()
    # process_buttons = ProcessButtonSerializer(many=True, read_only=True)
    network_coverage = serializers.SerializerMethodField()
    customer_process_buttons = serializers.SerializerMethodField()
    # program_records = serializers.SerializerMethodField()
    # # ProcessButtonSerializer(many=True, read_only=True)
    # program_record_first_index = serializers.SerializerMethodField()
    weekly_ordered_program_groups = serializers.SerializerMethodField()
    first_ongoing_program = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = (
            'id', 'name', 'last_device_log_time', 'next_device_update', 'time_to_action', 'device_online',
            'type_number',
            'network_coverage', 'spouts', 'land', 'customer_process_buttons',
            # 'program_records', 'program_record_first_index',
            'weekly_ordered_program_groups', 'first_ongoing_program',
        )
        # fields = (
        #     'id', 'name', 'location', 'area', 'sensors', 'device_online', 'is_owner', 'last_device_log_time',
        #     'next_device_update', 'longitude', 'latitude', 'city', 'has_advance_time', 'spouts', 'program_groups'
        # )
        depth = 4

    def set_weekly_ordered_program_groups(self, device: Device):
        if self.weekly_ordered_program_groups_value is None:
            self.weekly_ordered_program_groups_value = list(
                ProgramGroup.objects.filter(land=device.land).filter(
                    start__lte=timezone.now() + timedelta(days=14)
                ).order_by('start'))
        self.weekly_ordered_program_groups_value.sort(key=lambda x: x.start.replace(year=1, month=1, day=1))

    def get_weekly_ordered_program_groups(self, device: Device):
        self.set_weekly_ordered_program_groups(device)
        return DetailedProgramGroupSerializer(
            self.weekly_ordered_program_groups_value, many=True, context=self.context
        ).data

    def get_first_ongoing_program(self, device: Device):
        self.set_weekly_ordered_program_groups(device)
        for index, program_group in enumerate(self.weekly_ordered_program_groups_value):
            if program_group.is_ongoing():
                return {
                    'index': index,
                    'has_synced': program_group.has_synced
                }
        else:
            return None

    # def set_program_records(self, device: Device):
    #     programs = device.land.program_groups.filter(repeatable=True)
    #     records = []
    #     for program in programs:
    #         selected_time = program.next_run_time()
    #         if selected_time is None:
    #             continue
    #         end_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=14)
    #         while selected_time < end_time:
    #             data = DetailedProgramGroupSerializer(instance=program, many=False, read_only=False).data
    #             data['start'] = selected_time
    #             records.append(data)
    #             selected_time = selected_time + program.interval
    #         for index, record in enumerate(records):
    #             if record['is_ongoing']:
    #                 self.on_going_index = index
    #                 break
    #         else:
    #             self.on_going_index = None
    #         self.records = sorted(records, key=itemgetter('start'))
    #
    # def get_program_records(self, device: Device):
    #     if self.records is None:
    #         self.set_program_records(device)
    #     return self.records
    #
    # def get_program_record_first_index(self, device: Device):
    #     if self.records is None:
    #         self.set_program_records(device)
    #     return self.on_going_index

    def get_customer_process_buttons(self, device: Device):
        return ProcessButtonSerializer(device.process_buttons.filter(customer_reachable=True). \
                                       order_by('number'), many=True, read_only=True).data

    def get_sensors(self, device: Device):
        land = device.land
        soils = SoilMoistureSensor.objects.filter(land=land)
        waters = WaterSensor.objects.filter(land=land)
        humiditys = HumiditySensor.objects.filter(land=land)
        temps = TempSensor.objects.filter(land=land)
        sensors = {}
        if soils.count():
            sensors['soil'] = soils.order_by('-created')[0].soil_moisture_value
        if waters.count():
            sensors['water'] = waters.order_by('-created')[0].water_value
        if humiditys.count():
            sensors['humidity'] = humiditys.order_by('-created')[0].humidity_value
        if temps.count():
            sensors['temp'] = temps.order_by('-created')[0].temp_value
        return sensors

    def is_device_online(self, device: Device):
        return is_land_online(device)

    def get_last_device_log_time(self, device: Device):
        try:
            return get_last_log_time(device).strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'])
        except AttributeError:
            return None

    def get_next_device_update(self, device: Device):
        return get_next_update_time(device).strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'])

    def get_time_to_action(self, device: Device):
        return (get_next_update_time(device) + device.delay_to_action).strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'])

    # def get_is_owner(self, device: Device):
    #     customer = self.get_customer()
    #     if customer and device.land.owner and device.land.owner.id == customer.id:
    #         return True
    #     return False

    def get_customer(self, obj=None):
        return self.context.get('customer', None)

    def get_network_coverage(self, device: Device):
        try:
            log = DeviceNetworkCoverageLog.objects.filter(device=device).order_by('-time')[0]
            if timezone.now() - log.time > device.update_period:
                return 0
            value = log.value
            if value > 18:
                return 4
            if value > 14:
                return 3
            if value > 7:
                return 2
            return 1
        except TypeError:
            return 0
        except IndexError:
            return 6
        except DeviceNetworkCoverageLog.DoesNotExist:
            return 7


class SpoutInfoSerializer(serializers.Serializer):
    class Meta:
        model = Spout
        fields = ['name', 'is_activate', 'number']


class LandInfoSerializer(serializers.Serializer):
    name = serializers.CharField(label=_('land_name'))
    location = serializers.CharField(label=_('location'), required=False)
    serial = serializers.CharField(label=_('serial'), required=False)
    area = serializers.IntegerField(min_value=1, required=False)
    longitude = serializers.FloatField(required=False)
    latitude = serializers.FloatField(required=False)
    city = serializers.CharField(required=False)
    spouts = SpoutInfoSerializer(many=True)
    device_update_period = serializers.DurationField(required=False)

    class Meta:
        model = Land
        # fields = ['name', 'location' 'serial', 'area', 'longitude', 'latitude', 'city', 'spouts']
        land_fields = ['id', 'name', 'location', 'serial', 'area', 'longitude', 'latitude', 'city',
                       'device_update_period']

    def create(self, validated_data):
        data = validated_data.copy()
        data.pop('spouts', None)
        instance = self.Meta.model.objects.create(**data)
        # spouts_data = validated_data['spouts']
        spouts_data = self.get_initial().get('spouts')
        # try:
        number = 1
        for spout_data in spouts_data:
            spout_name = spout_data.get('name')
            spout_is_active = spout_data.get('is_active')
            if spout_name is None or spout_is_active is None:
                Error2006MissingValues()\
                    .send_missing_values_error('spout name' if spout_name is None else 'spout is_active')
            spout = Spout.objects.create(land=instance, name=spout_name, is_active=spout_is_active, number=number)
            number = number + 1

        return instance

    def update(self, instance: Land, validated_data):
        for field in self.Meta.land_fields:
            if hasattr(instance, field):
                setattr(instance, field, validated_data.get(field, getattr(instance, field)))
        spouts_data = self.get_initial().get('spouts')
        # print(spouts_data)
        number = 1
        for spout_data in spouts_data:
            spout_id = spout_data.get('id')
            spout_name = spout_data.get('name')
            spout_is_active = spout_data.get('is_active')
            if spout_name is None or spout_is_active is None:
                Error2006MissingValues() \
                    .send_missing_values_error('spout name' if spout_name is None else 'spout is_active')
            try:
                # print(f'spout_id={spout_id}')
                spout = Spout.objects.get(id=spout_id, land=instance)
                spout.name = spout_name
                spout.is_active = spout_is_active
                spout.number = number
                spout.save()
            except Spout.DoesNotExist:
                Error2008CantCreateNewSpout().raise_error()
            # spout = Spout.objects.create(land=instance, name=spout_name, is_active=spout_is_active, number=number)
            number = number + 1

        instance.save()
        return instance

    def to_representation(self, instance: Land):
        data = {}
        for field in self.Meta.land_fields:
            if hasattr(instance, field):
                data[field] = getattr(instance, field)
        spouts_data = []
        spouts = Spout.objects.filter(land=instance)
        for spout in spouts:
            spouts_data.append({
                'id': spout.id,
                'name': spout.name,
                'is_active': spout.is_active,
                'number': spout.number
            })
        data['spouts'] = spouts_data
        return data


# TODO
class RegisterLandAndDeviceSerializer(serializers.Serializer):
    pass
#     land = serializers.CharField(max_length=500)
#     device = serializers.CharField(max_length=500)
#     serial = serializers.CharField(max_length=30)
#     def create(self, validated_data):
#         user = validated_data.get('user')
#         device =


class SerialAvailabilitySerializer(serializers.Serializer):
    serial = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            serial = replace_farsi_num(attrs['serial'])
            if Device.objects.get(serial=serial) is None:
                raise serializers.ValidationError('invalid serial')
        except():
            raise serializers.ValidationError('missing serial')
        except Device.DoesNotExist:
            raise ValidationError('invalid serial')
        return attrs

    def create(self, validated_data):
        serial = validated_data['serial']
        serial = replace_farsi_num(serial)
        try:
            device = Device.objects.get(serial=serial)
        except Device.DoesNotExist:
            raise ValidationError("invalid serial")
        return {
            'has_land': device.land is not None and device.land.has_name(),
            'has_device': device.has_name(),
        }


class SimpleDeviceSerializer(serializers.ModelSerializer):
    land = serializers.SlugRelatedField(slug_field='name', read_only=True, many=False)

    class Meta:
        model = Device
        fields = ['id', 'name', 'type_number', 'land']
