from .models import Customer, Land, Spout, SpoutSensor, \
    SmsReceiver, TempSensor, SoilMoistureSensor, HumiditySensor, EvaporationSensor, WaterSensor, \
    TrialWaterSensor
from django.contrib.auth.models import User
from rest_framework import serializers
from django.db import models
from . import models
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}


class SimpleLandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Land
        fields = ('id', 'name', 'location', 'need_program_check', 'url')


# class SensorSerializer(serializers.ModelSerializer):
#     # land = SimpleLandSerializer(many=False, read_only=False)
#
#     class Meta:
#         model = Sensor
#         fields = ('id', 'type', 'value', 'land', 'modified', 'created')
#         extra_kwargs = {'modified': {'read_only': True}}
#         # depth = 1


class TempSensorSerializer(serializers.ModelSerializer):

    class Meta:
        model = TempSensor
        fields = ('id', 'temp_value', 'land', 'modified', 'created', 'created_string')
        extra_kwargs = {'modified': {'read_only': True}, 'created': {'read_only': True}, 'created_string': {'read_only': True}}


class SoilMoistureSensorSerializer(serializers.ModelSerializer):

    class Meta:
        model = SoilMoistureSensor
        fields = ('id', 'soil_moisture_value', 'land', 'modified', 'created')
        extra_kwargs = {'modified': {'read_only': True}, 'created': {'read_only': True}}


class HumiditySensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = HumiditySensor
        fields = ('id', 'humidity_value', 'land', 'modified', 'created')
        extra_kwargs = {'modified': {'read_only': True}, 'created': {'read_only': True}}


class WaterSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterSensor
        fields = ('id', 'water_value', 'land', 'modified', 'created')
        extra_kwargs = {'modified': {'read_only': True}, 'created': {'read_only': True}}


class TrialWaterSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrialWaterSensor
        fields = ('id', 'trial_water_value', 'land', 'modified', 'created')
        extra_kwargs = {'modified': {'read_only': True}, 'created': {'read_only': True}}


class EvaporationSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaporationSensor
        fields = ('id', 'evaporation_value', 'land', 'modified', 'created')
        extra_kwargs = {'modified': {'read_only': True}, 'created': {'read_only': True}}


class SmsReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsReceiver
        fields = ('id', 'number', 'spout', 'url')


class SpoutSerializer(serializers.HyperlinkedModelSerializer):
    sms_receivers = SmsReceiverSerializer(many=True)

    class Meta:
        model = Spout
        fields = ('id', 'name', 'isOn', 'device', 'spoutSensor', 'sms_receivers', 'url')
        depth = 2


class LightSpoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spout
        fields = ('id', 'name', 'isOn')


class SpoutSensorSerializer(serializers.HyperlinkedModelSerializer):
    spout = SpoutSerializer(many=False)

    class Meta:
        model = SpoutSensor
        fields = ('id', 'spout', 'isOn', 'url')
        depth = 1


class LandSerializer(serializers.HyperlinkedModelSerializer):
    # sensors = SensorSerializer(many=True)
    # spouts = SpoutSerializer(many=True)
    # spoutSensors = SpoutSensorSerializer(many=True)

    class Meta:
        model = Land
        fields = ('id',
                  'name',
                  'location',
                  'area',
                  'device',
                  'customers',
                  # 'spouts',
                  'sensors',
                  'url')
        # 'spoutSensors'
        depth = 1


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    lands = LandSerializer(many=True)
    user = UserSerializer(many=False)

    class Meta:
        model = Customer
        fields = ('id',
                  'url',
                  'user',
                  'lands',
                  'phoneNumber',
                  'isBlocked',
                  'isActivated',
                  )
        depth = 1


# class ProgramLiteSerializer(serializers.ModelSerializer):
#     condition = serializers.CharField(source='spouts_condition_str')
#
#     class Meta:
#         model = models.Program
#         fields = ('number', 'name', 'condition', 'start', 'interval', 'has_repeat',
#                   'land', 'modified', 'is_modified')
#         extra_kwargs = {'number': {'read_only': True}, 'modified': {'read_only': True}}



