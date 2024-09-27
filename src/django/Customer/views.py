from django.shortcuts import render
from rest_framework import viewsets
from .models import Customer, Land, Spout, SpoutSensor, \
    SmsReceiver, TempSensor, SoilMoistureSensor, HumiditySensor, EvaporationSensor, WaterSensor, TrialWaterSensor
from .serializers import CustomerSerializer, UserSerializer, LandSerializer,\
    SpoutSerializer, SpoutSensorSerializer,\
    SmsReceiverSerializer, \
    TempSensorSerializer, SoilMoistureSensorSerializer, HumiditySensorSerializer, EvaporationSensorSerializer, \
    WaterSensorSerializer, TrialWaterSensorSerializer
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from datetime import date
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.viewsets import ModelViewSet
from django.views import View
from rest_framework.settings import api_settings
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from . import models, serializers
from django.utils import timezone
from . import utils
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException, ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from Baghyar import views as global_views, utils as global_utils, errors as global_errors


# class CustomerView(viewsets.ModelViewSet):
#     queryset = Customer.objects.all()
#     serializer_class = CustomerSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# class LandView(viewsets.ModelViewSet):
#     queryset = Land.objects.all()
#     serializer_class = LandSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     # def perform_create(self, serializers):
#     #     serializers.save(owner=self.request.user)
#
#
# class SpoutView(viewsets.ModelViewSet):
#     queryset = Spout.objects.all()
#     serializer_class = SpoutSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# class SpoutSensorView(viewsets.ModelViewSet):
#     queryset = SpoutSensor.objects.all()
#     serializer_class = SpoutSensorSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# # class ProgramView(viewsets.ModelViewSet):
# #     queryset = Program.objects.all()
# #     serializer_class = ProgramSerializer
# # #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
# #
# #
# # class ProgramLiteView(viewsets.ModelVie   wSet):
# #     queryset = Program.objects.all()
# #     serializer_class = ProgramLiteSerializer
#
#
# class ProgramLiteView(viewsets.ModelViewSet):
#     queryset = models.Program.objects.all()
#     serializer_class = serializers.ProgramLiteSerializer
#
#
# # class LandDailyTempRecordView(viewsets.ModelViewSet):
# #     queryset = LandDailyTempRecord.objects.all()
# #     serializer_class = LandDailyTempRecordSerializer
# # #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# class TempSensorView(viewsets.ModelViewSet):
#     queryset = TempSensor.objects.all()
#     serializer_class = TempSensorSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# class HumiditySensorView(viewsets.ModelViewSet):
#     queryset = HumiditySensor.objects.all()
#     serializer_class = HumiditySensorSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# class SoilMoistureSensorView(viewsets.ModelViewSet):
#     queryset = SoilMoistureSensor.objects.all()
#     serializer_class = SoilMoistureSensorSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# class EvaporationSensorView(viewsets.ModelViewSet):
#     queryset = EvaporationSensor.objects.all()
#     serializer_class = EvaporationSensorSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# class WaterSensorView(viewsets.ModelViewSet):
#     queryset = WaterSensor.objects.all()
#     serializer_class = WaterSensorSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# class TrialWaterSensorView(viewsets.ModelViewSet):
#     queryset = TrialWaterSensor.objects.all()
#     serializer_class = TrialWaterSensorSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# class MultiSensorView(viewsets.ModelViewSet):
# class MultiSensorView(GenericViewSet, CreateModelMixin):
#     queryset = TempSensor.objects.all()
#     serializer_class = TempSensorSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def create(self, request, *args, **kwargs):
#         humidity_sensor_serializer = HumiditySensorSerializer(data=request.data)
#         lands = Land.objects.filter(id=request.data.get('land'))
#         if lands.count() < 1:
#             return Response({'message': 'invalid land id'}, status=status.HTTP_406_NOT_ACCEPTABLE)
#         land = lands.first()
#         if land.is_active is False:
#             return Response({'message': 'inactive land'}, status=status.HTTP_406_NOT_ACCEPTABLE)
#         if humidity_sensor_serializer.is_valid(raise_exception=True):
#             humidity_sensor_serializer.save()
#
#         soil_moisture_sensor_serializer = SoilMoistureSensorSerializer(data=request.data)
#         if soil_moisture_sensor_serializer.is_valid(raise_exception=False):
#             soil_moisture_sensor_serializer.save()
#
#         temp_sensor_serializer = TempSensorSerializer(data=request.data)
#         if temp_sensor_serializer.is_valid(raise_exception=False):
#             temp_sensor_serializer.save()
#
#         water_sensor_serializer = WaterSensorSerializer(data=request.data)
#         if water_sensor_serializer.is_valid(raise_exception=False):
#             water_sensor_serializer.save()
#
#         trial_water_sensor_serializer = TrialWaterSensorSerializer(data=request.data)
#         if trial_water_sensor_serializer.is_valid(raise_exception=False):
#             trial_water_sensor_serializer.save()
#
#         evaporation_sensor_serializer = EvaporationSensorSerializer(data=request.data)
#         if evaporation_sensor_serializer.is_valid(raise_exception=False):
#             evaporation_sensor_serializer.save()
#
#         # return super.create(request, args, kwargs)
#         # humidity_headers = self.get_success_headers(humidity_sensor_serializer.data)
#
#         data = {**humidity_sensor_serializer.data,
#                 **soil_moisture_sensor_serializer.data,
#                 **temp_sensor_serializer.data,
#                 **water_sensor_serializer.data,
#                 **trial_water_sensor_serializer.data,
#                 **evaporation_sensor_serializer.data, }
#         data.pop('id')
#         return Response(data, status=status.HTTP_201_CREATED, headers=None)
#
#     # def get_success_headers(self, data):
#     #     try:
#     #         return {'Location': str(data[api_settings.URL_FIELD_NAME])}
#     #     except (TypeError, KeyError):
#     #         return {}

# class MultiSensorView(FlatMultipleModelMixin):
#     pagination_class = None
#     querylist = (
#         (
#             TempSensor.objects.all(),
#             TempSensorSerializer
#         ),
#         (
#             HumiditySensor.objects.all(),
#             HumiditySensorSerializer
#         ),
#         (
#             SoilMoistureSensor.objects.all(),
#             SoilMoistureSensorSerializer
#         ),
#     )
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#
#     def get_queryset(self):
#         return None


# class SensorView(viewsets.ModelViewSet):
#
#     queryset = Sensor.objects.all()
#     serializer_class = SensorSerializer
# #    authentication_classes = [TokenAuthentication]
#     # permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
# #    permission_classes = [permissions.IsAuthenticated]
#
#     def create(self, request, *args, **kwargs):
#         print(request)
#         print(json.dumps(request.data))
#         # body = json.loads(request.body.decode('utf-8'))
#         return super().create(request, *args, **kwargs)
#
#     # def create(self, request, *args, **kwargs):
#     #     query_dict = request.data.copy()
#     #     #print(query_dict)
#     #     land_id = query_dict.get('land', None)
#     #     del query_dict['land']
#     #     #print(land_id)
#     #     land = Land.objects.get(id=land_id)
#     #     #print("###" + str(land_serializer))
#     #     print(str(land_id))
#     #     query_dict['land'] = land
#     #     print(query_dict)
#     #     serializers = SensorSerializer(data=query_dict)
#     #     #print(serializers)
#     #     if serializers.is_valid():
#     #         serializers.save()
#     #         return Response(serializers.data)
#     #     return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     # return super().create(request, *args, **kwargs)
#
#
# # class DeviceView(viewsets.ModelViewSet):
# #     queryset = Device.objects.all()
# #     serializer_class = DeviceSerializer
# #     permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# class SmsReceiverView(viewsets.ModelViewSet):
#     queryset = SmsReceiver.objects.all()
#     serializer_class = SmsReceiverSerializer
# #    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
# @api_view(['Get'])
# def reset_program_is_modified(request):
#     number = request.data.get('number')
#     land_id = request.data.get('land')
#     modified = request.data.get('modified')
#     programs = models.Program.objects\
#         .filter(land__id=land_id)\
#         .filter(number=number)\
#         .filter(modified=modified)
#
#     modified_programs = []
#     for program in programs:
#         program.is_modified = False
#         program.save()
#         modified_programs.append(program.number)
#
#     return Response({"response": "Success", "modified_programs": modified_programs})


@api_view(['Post'])
def user_lands(request):
    user = get_user_by_request_token(request)
    customer = create_or_get_customer(user)
    lands = customer.lands.all()
    lands_details = {
        land.id: {
            "id": land.id,
            "name": land.name,
            "location": land.location,
            "area": land.area,
        } for land in lands
    }
    return Response(lands_details)


def create_or_get_customer(user):
    customers = user.customers.all()
    if user.customers.count() < 1:
        customer = Customer(user=user, phoneNumber=user.username, isBlocked=False)
        customer.save()
    else:
        customer = customers[0]
    return customer


# @api_view(['Post'])
# def get_land_updates(request):
#     user = get_user_by_request_token(request)
#
#     customer = create_or_get_customer(user)
#
#     land_id = request.data.get('land')
#     if not isinstance(land_id, int):
#         msg = 'invalid land type'
#         raise ValidationError(msg)
#         # return Response({'msg': 'invalid land type'}, status.HTTP_400_BAD_REQUEST)
#     # print(land_id_str)
#     # if type(land_id_str) is not int or land_id_str is None:
#     #     return Response({'msg': 'enter a land'}, status.HTTP_400_BAD_REQUEST)
#     # try:
#     #     land_id = int(land_id_str)
#     # except ValueError:
#     #     return Response({'msg': 'invalid land type'}, status.HTTP_400_BAD_REQUEST)
#
#     land = Land.objects.get(id=land_id)
#     if land is None:
#         msg = 'invalid land'
#         raise ValidationError(msg, code='land validation')
#         # return Response({'msg': 'invalid land'}, status.HTTP_400_BAD_REQUEST)
#     if not customer_has_land(customer, land):
#         return Response({'msg': 'invalid land access request'}, status.HTTP_400_BAD_REQUEST)
#
#     attr = {
#         'id': land.id,
#         'name': land.name,
#         'location': land.location,
#         'area': land.area,
#     }
#
#     soils = SoilMoistureSensor.objects.filter(land=land)
#     waters = WaterSensor.objects.filter(land=land)
#     humiditys = HumiditySensor.objects.filter(land=land)
#     temps = TempSensor.objects.filter(land=land)
#     land_spouts = Spout.objects.filter(device__land=land)
#
#     sensors = {}
#
#     if soils.count():
#         sensors['soil'] = soils.order_by('-created')[0].soil_moisture_value
#
#     if waters.count():
#         sensors['water'] = waters.order_by('-created')[0].water_value
#
#     if humiditys.count():
#         sensors['humidity'] = humiditys.order_by('-created')[0].humidity_value
#
#     if temps.count():
#         sensors['temp'] = temps.order_by('-created')[0].temp_value
#
#     attr['sensors'] = sensors
#
#     spouts = {}
#     for spout in land_spouts:
#         spouts[spout.name] = {
#             'id': spout.id,
#             'number': spout.number,
#             'name': spout.name,
#             'isOn': spout.isOn,
#         }
#
#     attr['spouts'] = spouts
#
#     return Response(attr)


# @api_view(['Post'])
# def set_spout_output(request):
#     spout = get_spout_and_authorize_by_request(request)
#     is_on = global_views.get_request_value(request, 'isOn')
#     # is_on = get_request_value_or_raise_error(request, 'isOn')
#     is_on_bool = True if (is_on == 'True' or is_on == 'true' or is_on is True) else False
#     spout.isOn = True if (is_on == 'True' or is_on == 'true' or is_on is True) else False
#     spout.save()
#     attr = {'isOn': str(spout.isOn)}
#     return Response(attr)


def get_user_by_request_token(request):
    # token_string = request.headers.get('Authorization')
    #
    # msg = "invalid authentication"
    # if not isinstance(token_string, str) or len(token_string) < 6:
    #     raise ValidationError(msg, code='authorization')
    #     # return None
    # token_key = token_string[6:]
    # token = Token.objects.get(key=token_key)
    token = get_and_validate_request_token(request)
    msg = "invalid token authentication"
    if not token:
        raise ValidationError(msg, code='authorization')
    user = token.user
    if user is None:
        msg = 'invalid authentication'
        raise ValidationError(msg, code='user validation')
    return user


def get_and_validate_request_token(request):
    token_string = request.headers.get('Authorization')
    msg = "invalid authentication"
    if not isinstance(token_string, str) or len(token_string) < 6:
        raise ValidationError(msg, code='authorization')
        # return None
    token_key = token_string[6:]
    token = Token.objects.get(key=token_key)
    msg = "invalid token authentication"
    if not token:
        raise ValidationError(msg, code='authorization')
    return token


def customer_has_land(customer, land):
    customers = land.customers.all()
    if not customers.count():
        return False
    return customer in customers


def get_land_and_authorize_by_request(request):
    user = get_user_by_request_token(request)
    customer = create_or_get_customer(user)
    land = get_and_validate_object_from_request_by_query(request, customer.lands, 'land')
    # land_id = request.data.get('land')
    # if land_id is None:
    #     msg = 'need land'
    #     raise ValidationError(msg, code='validation')
    # lands = customer.lands.filter(id=land_id)
    # if not lands.count():
    #     msg = 'unauthorized land'
    #     raise ValidationError(msg, code='authorization')
    # return lands.first()
    return land


def get_and_validate_object_from_queryset(queryset, obj_name, obj_id):
    objs = queryset.filter(id=obj_id)
    if not objs.count():
        msg = 'invalid ' + obj_name
        raise ValidationError(msg, code='validation')
    return objs.first()


def get_and_validate_object_from_class_by_id(cls, obj_name, obj_id):
    return get_and_validate_object_from_queryset(cls.objects, obj_name, obj_id)


def get_and_validate_object_from_request_by_class(request, cls, obj_name):
    obj_id = request.data.get(obj_name)
    return get_and_validate_object_from_class_by_id(cls, obj_name, obj_id)


def get_and_validate_object_from_request_by_query(request, query, obj_name):
    obj_id = request.data.get(obj_name)
    return get_and_validate_object_from_queryset(query, obj_name, obj_id)


def get_spout_and_authorize_by_request(request):
    spout = get_and_validate_object_from_request_by_class(request, Spout, 'spout')

    user = get_user_by_request_token(request)
    customer = create_or_get_customer(user)
    if not customer_has_land(customer, spout.device.land):
        msg = 'unauthorized request'
        raise ValidationError(msg, code='authorization')
    return spout



