import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.views import View
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException, ValidationError, PermissionDenied
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import parsers, renderers
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from Customer import utils as customer_utils
from Customer.models import *
from Customer.serializers import *
from Customer import views as customer_views
from Customer import serializers as customer_serializers
from Customer import utils as customer_utils
from Baghyar import views as global_views, errors as global_errors, utils as global_utils
from LightApp.serializers import AuthTokenSerializer
from Irrigation.services import IrrigationManager

from Device.models import *
from Device import serializers, models
from Device.serializers import DeviceNetworkCoverageLogSerializer
from Device.views.expected_output_v6 import ExpectedOutputV6
from Device.views.device_auths import get_land_by_serial, register_device_serial, temp_api
from Device.views.device_views import get_device_programs, device_process_view


class DeviceRequest(View):
    message = 'not implemented'

    def get(self, request, *args, **kwargs):
        self.set_message(request, *args, **kwargs)
        return HttpResponse(self.message)

    def set_message(self, request, *args, **kwargs):
        self.message = ""


class CheckLand(DeviceRequest):
    # land_id
    # program_id
    # response: {“d”:{“sch”:1,“exp”:0,“del_sch”:0},“c”:null}
    # {"d" {"sch":"0/1 edited or added", "exp": "one of outputs has changed" \
    # , "del_sch": "a program has deleted"} "c":"error code / null"}
    # TODO
    def set_message(self, request, *args, **kwargs):
        land_id = self.kwargs['land_id']
        program_number = self.kwargs['program_number']
        land = global_views.get_validated_obj(cls=Land, obj_id=land_id, obj_name='land')
        # programs = Program.objects.filter(land=land, number=program_number)
        # if not programs.count():
        #     msg = "invalid program"
        #     raise ValidationError(msg, code='validation')
        # program = programs.first()
        # TODO
        attr = {
            "d": {
                # "sch": 1 if program.modified else 0,
                # "exp": 1 if program.modified else 0,
                # "del_sch": 1 if program.modified else 0,
            },
            "c": None,
        }
        self.message = str(attr)


class ExpectedOutput(DeviceRequest):
    # land_id
    # response: {“d”:{“o”:“111”},“c”:null,"p":1,"cps":"10,11"}
    # {"d":{"o":"1/0 1/0 1/0 spouts are on/off"}, "c":"error",
    # "p":1 has modified programs, "cps":"...,..." list of modified programs}
    land = None
    device = None

    def set_message(self, request, *args, **kwargs):
        land_id = kwargs['land_id']
        self.land = global_views.get_and_validate_object_from_class_by_id(Land, 'land', land_id)
        self.check_and_execute_program_turns()
        self.message = self.create_expected_output_msg()
        self.add_log()

    def create_expected_output_msg(self):
        spouts_conditions_str = self.create_spout_condition_string_list()
        modified_programs_list, need_program_check = self.get_modified_programs_numbers()
        external_button_is_on_str =  self.get_external_button_is_on_str()

        # "c":null has errors
        error = '"c":null'

        # "p":1/0
        has_modified_program_str = '"p":' + ('1' if self.land.need_program_check else '0')

        # "d":{"o":"1/0 1/0 1/0 spouts are on/off"}
        expected_output_msg = '"d":{' + f'"o":"{spouts_conditions_str}"' + '}'

        # "cps":"10,11"
        modified_programs_str = f'"cps":{modified_programs_list}'

        # "ebc":"01" external button enabled
        external_button_msg = f'"ebc":{external_button_is_on_str}'

        return '{' + f'{expected_output_msg},{error},{has_modified_program_str},{modified_programs_str},{external_button_msg}' + '}'

    def get_external_button_is_on_str(self):
        msg = ''
        for external_button in ExternalButton.objects.filter(device__land=self.land).order_by('number'):
            msg = msg + ('1' if external_button.is_on else '0')
        return msg

    # def get_modified_programs_numbers(self):
    #     modified_programs = list(Program.objects.filter(land=self.land, is_modified=True).values('number'))
    #     modified_programs_list = []
    #     has_modified_program = False  # False
    #     for program in modified_programs:
    #         modified_programs_list.append(program['number'])
    #
    #     if len(modified_programs_list):
    #         has_modified_program = True
    #     return modified_programs_list, has_modified_program

    def check_and_execute_program_turns(self):
        manager = IrrigationManager()
        manager.update_land_irrigation(self.land)
        # global_utils.update_land_programs_evaluation(self.land)
        # programs = customer_models.Program.objects.filter(land=self.land)
        # if programs.exists():
        #     while True:
        #         program = programs.order_by('start')[0]
        #         if not program.check_is_turn():
        #             break

    def create_spout_condition_string_list(self):
        spouts = self.device.spouts
        spouts_conditions = ''
        for spout in spouts.all():  # .filter(is_active=True):
            spouts_conditions += '1' if spout.isOn is True else '0'
        return spouts_conditions

    def add_log(self):
        log = models.LogDeviceCheckOut(land=self.land, message=self.message, time=timezone.now(), device=self.device)
        log.save()

    # # @csrf_exempt
    # def post(self, request, *args, **kwargs):
    #     print(request)
    #     # print(request.Post)
    #     self.update_spout_condition(request, *args, **kwargs)
    #     return self.get(request, *args, **kwargs)
    #
    # def update_spout_condition(self, request, *args, **kwargs):
    #     land_id = self.kwargs['land_id']
    #     self.land = global_views.get_and_validate_object_from_class_by_id(Land, 'land', land_id)
    #     spout_conditions = global_views.get_data_value(request.data, 'sc')
    #     spouts = Spout.objects.filter(land=self.land)
    #     for spout in spouts:
    #         responced_spout_value = spout_conditions[spout.number - 1] == '1'
    #         spout_sensor = SpoutSensor.objects.get_or_create(spout=spout)
    #         spout_sensor.isOn = responced_spout_value
    #         spout_sensor.save()


def update_spout_condition(request, *args, **kwargs):
    land_id = kwargs['land_id']
    try:
        land = global_views.get_and_validate_object_from_class_by_id(Land, 'land', land_id)
        spout_conditions = global_views.get_data_value(request.data, 'sc')
        spouts = Spout.objects.filter(device__land=land)
        for spout in spouts:
            # number = spout.number - spouts.filter(number__lt=spout.number, is_active=False)
            responded_spout_value = spout_conditions[spout.number - 1] == '1'
            spout_sensor, created = SpoutSensor.objects.get_or_create(spout=spout)
            # print(spout_sensor)
            spout_sensor.isOn = responded_spout_value
            spout_sensor.save()
    except (Land.DoesNotExist, Device.DoesNotExist, Spout.DoesNotExist, SpoutSensor.DoesNotExist):
        pass


@api_view(['Post'])
def expected_outputV2(request, *args, **kwargs):
    update_spout_condition(request, *args, **kwargs)
    return ExpectedOutput(**kwargs).get(request, *args, **kwargs)


# class Programs(DeviceRequest):
#     def set_message(self, request, *args, **kwargs):
#         attr = []
#         land_id = kwargs['land_id']
#         land = global_views.get_validated_obj(obj_id=land_id, obj_name='land', cls=Land)
#         right_now = timezone.now()
#         manager = IrrigationManager(right_now)
#         manager.update_land_irrigation(land)
#         # global_utils.update_land_programs_evaluation(land, right_now)
#         sub_programs = SubProgram.objects.filter(program_group__land=land)
#         for sub_program in sub_programs:
#             start = sub_program.start
#             while sub_program.program_group.repeatable and start < right_now:
#                 start += sub_program.program_group.interval
#             if start >= right_now:
#                 serializer = serializers.SubProgramSerializer(sub_program)
#                 serializer.data['start'] = start
#                 attr.append(serializer.data)
#
#         land.checked()
#         self.message = json.dumps(attr)


# @api_view(['Post'])
# def ask_schedule(request, land_id, land_program_id):
#     # TODO
#     # land_id
#     # program_id
#     # {“d”:{“e”: 1,“l”:“TIMESTAMP”,“s”:[{“id”:7,”st”:”2:6:19:50:02:30”,”o”:”001”}]},“c”:null}
#     # {"d":{"e": "has continue", "l":"next_ip", "s":[{"id":"program_id","st": \
#     # "per_weeK[2,1,0]:day_of_week[1-7]:hour:minute:hourly_duration:minute_duration" \
#     # ,"o":"1/0 1/0 1/0 spouts are on/off"}, "c":"error"}
#     land = global_views.get_validated_obj(cls=Land, obj_id=land_id, obj_name='land')
#     programs = Program.objects.filter(land=land, id__gte=land_program_id)
#     if programs.count():
#         program = programs.first()
#         serializer = customer_serializers.ProgramLiteSerializer(program)
#         return Response(serializer.data)
#     else:
#         msg = 'error'
#         return Response({'msg': msg})


# {"serial":""}
@api_view(['Post'])
def get_land_by_device_serial(request):
    serial_value = request.data.get('serial')
    if not serial_value:
        msg = 'enter serial'
        raise ValidationError(msg, code='validation')
    # print(serial_value)
    devices = Device.objects.filter(serial=serial_value)
    if not devices.count():
        msg = 'invalid serial'
        raise ValidationError(msg, code='validation')
    device = devices.first()
    land = device.land
    if not land:
        msg = 'unregistered device'
        raise ValidationError(msg, code='validation')
    attr = {
        'land': land.id,
        'device': device.id,
    }
    return Response(attr)


def get_hourly_temp_availability(request, land_id, hours):
    right_now = timezone.now()
    end_time = right_now
    period = timezone.timedelta(hours=hours)
    start_time = end_time - period
    count = TempSensor.objects.filter(
        land__id=land_id,
        created__gte=start_time,
        created__lt=end_time
    ).count()
    total = hours * 60 / 5
    percentage = count / total * 100

    return HttpResponse(str(percentage) + '%')


def get_hourly_availability(request, land_id, hours):
    end_time = timezone.now()
    start_time = end_time - timezone.timedelta(hours=hours)
    # print(f'start:{start_time}_end:{end_time}')
    count = models.LogDeviceCheckOut.objects.filter(
        land__id=land_id,
        time__gte=start_time,
        time__lt=end_time
    ).count()
    # print(count)
    total = hours * 60 / 5
    percentage = count / total * 100

    return HttpResponse(str(percentage) + '%')


def get_temp_availability(request, land_id, records):
    right_now = timezone.now()
    daily_end_time = right_now
    daily_period = timezone.timedelta(days=1)
    daily_start_time = daily_end_time - daily_period
    hourly_end_time = right_now
    hourly_period = timezone.timedelta(hours=1)
    hourly_start_time = hourly_end_time - hourly_period
    daily_response = {}
    hourly_response = {}
    for i in range(0, records):
        daily_count = TempSensor.objects.filter(
            land__id=land_id,
            created__gte=daily_start_time,
            created__lt=daily_end_time
        ).count()
        daily_total = 24 * 60 / 5
        daily_response[f'{i}_days_from_now:'] = {
            "recieved": daily_count,
            "total": daily_total,
            "percentage": (daily_count/daily_total) * 100,
        }
        daily_end_time = daily_end_time - daily_period
        daily_start_time = daily_start_time - daily_period

        hourly_count = TempSensor.objects.filter(
            land__id=land_id,
            created__gte=hourly_start_time,
            created__lt=hourly_end_time
        ).count()
        hourly_total = 60 / 5
        hourly_response[f'{i}_hours_from_now:'] = {
            "recieved": hourly_count,
            "total": hourly_total,
            "percentage": (hourly_count / hourly_total) * 100,
        }
        hourly_end_time = hourly_end_time - hourly_period
        hourly_start_time = hourly_start_time - hourly_period

    return JsonResponse({'hourly': hourly_response, 'daily': daily_response}, safe=False)


def get_availability(request, sensor_type, land_id, records):
    # sensor = utils.get_sensor_model(sensor_type)
    # if sensor is None:
    #     return HttpResponse('unknown sensor')
    sensor = models.SoilMoistureSensor
    right_now = timezone.now()
    daily_end_time = right_now
    daily_period = timezone.timedelta(days=1)
    daily_start_time = daily_end_time - daily_period
    hourly_end_time = right_now
    hourly_period = timezone.timedelta(hours=1)
    hourly_start_time = hourly_end_time - hourly_period
    daily_response = {}
    hourly_response = {}
    for i in range(0, records):
        daily_count = sensor.objects.filter(
            land__id=land_id,
            created__gte=daily_start_time,
            created__lt=daily_end_time
        ).count()
        daily_total = 24 * 60 / 5
        daily_response[f'{i}_days_from_now:'] = {
            "recieved": daily_count,
            "total": daily_total,
            "percentage": (daily_count/daily_total) * 100,
        }
        daily_end_time = daily_end_time - daily_period
        daily_start_time = daily_start_time - daily_period

        hourly_count = sensor.objects.filter(
            land__id=land_id,
            created__gte=hourly_start_time,
            created__lt=hourly_end_time
        ).count()
        hourly_total = 60 / 5
        hourly_response[f'{i}_hours_from_now:'] = {
            "recieved": hourly_count,
            "total": hourly_total,
            "percentage": (hourly_count / hourly_total) * 100,
        }
        hourly_end_time = hourly_end_time - hourly_period
        hourly_start_time = hourly_start_time - hourly_period

    return JsonResponse({'hourly': hourly_response, 'daily': daily_response}, safe=False)


# @api_view(['Post'])
# def reset_program_is_modified(request):
#     number = request.data.get('number')
#     modified = request.data.get('modified')
#     if not number or not modified:
#         msg = 'enter number and modified time'
#         raise ValidationError(msg)
#     land = global_views.get_validated_obj(request=request, cls=Land, obj_name='land')
#     programs = Program.objects.filter(land=land, number=number, modified=modified)
#
#     modified_programs = [program for program in programs.filter(is_modified=True)]
#     for program in programs:
#         program.is_modified = False
#         program.save()
#
#     return Response({"response": "Success", "modified_programs": modified_programs})


class AddDevice(APIView):
    throttle_classes = ()
    # permission_classes = (IsAuthenticated, )
    # authentication_classes = (BasicAuthentication, )
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    model = Device
    serializer_class = serializers.DeviceSerializer

    def post(self, request):
        # user = request.user
        # customer = Customer.get_or_create(user)
        # if not customer.is_supervisor or not customer.is_admin:
        #     raise PermissionDenied()
        serial = request.data.get('serial')
        devices = Device.objects.filter(serial=serial)
        if devices.count():
            serializer = self.serializer_class(instance=devices[0])
            return Response(serializer.data)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        device = serializer.save()
        return Response(serializer.data)


class GetOwnerPhoneNumber(APIView):
    throttle_classes = ()
    # permission_classes = (IsAuthenticated, )
    # authentication_classes = (BasicAuthentication, )
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    model = Device
    serializer_class = serializers.DeviceSerializer

    def post(self, request, land_id):
        # TODO: check for device user owning land
        land = Land.objects.get(id=land_id)
        owner = land.owner
        return Response({'phone': owner.user.username if owner is not None else ''})
        # if owner is not None:
        #     user = owner.user
        #     # TODO: check if username is phone number
        #     return Response({"phone": user.username})
        # return Response({})


def log_network_coverage(request, *args, **kwargs):
    data = {
        'value': global_views.get_data_value(request.data, 'nc')
    }
    try:
        device_id = kwargs['device_id']
        data['device'] = Device.objects.get(id=device_id).id
    except (Device.DoesNotExist, KeyError) as e:
        data['device'] = None
    try:
        land_id = kwargs['land_id']
        data['land'] = Land.objects.get(id=land_id).id
    except (Land.DoesNotExist, KeyError) as e:
        data['land'] = None
    serializer = DeviceNetworkCoverageLogSerializer(data=data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()


@api_view(['Post'])
def expected_outputV3(request, *args, **kwargs):

    log_network_coverage(request, *args, **kwargs)

    update_spout_condition(request, *args, **kwargs)

    return ExpectedOutput(**kwargs).get(request, *args, **kwargs)


def update_external_button_status(request, *args, **kwargs):
    try:
        device_id = kwargs['device_id']
        device = Device.objects.get(id=device_id)
        ebc = global_views.get_data_value(request.data, 'ebc')
        for button in ExternalButton.objects.filter(device=device):
            button.is_on = StringOfBitToBoolean(ebc[button.number - 1])
            button.save()

    except (Device.DoesNotExist, ValueError, ):
        pass


@api_view(['Post'])
def expected_outputV5(request, *args, **kwargs):
    # TODO: send expected button conditions

    log_network_coverage(request, *args, **kwargs)

    update_spout_condition(request, *args, **kwargs)

    update_external_button_status(request, *args, **kwargs)

    return ExpectedOutput(**kwargs).get(request, *args, **kwargs)


def booleanToStringOfBit(b: bool) -> str:
    return '1' if b is True else '0'


def StringOfBitToBoolean(s: str) -> bool:
    return s == '1'


@api_view(['Get'])
def external_button_program_view(request, *args, **kwargs):
    data = []
    try:
        device_id = kwargs['device_id']
        device = Device.objects.get(id=device_id)
        land = device.land
        spouts = Spout.objects.filter(device__land=land).order_by('number')
        for external_button in ExternalButton.objects.filter(device=device):
            external_button_data = {'number': external_button.number}
            events = []
            for event in ExternalButtonEvent.objects.filter(external_button=external_button).order_by('priority'):
                event_data = {'delay': event.delay}
                spout_changes = ""
                ebe_spout_changes = ExternalButtonEventSpoutChange.objects.filter(external_button_event=event)
                for spout in spouts:
                    filtered_spout_changes = ebe_spout_changes.filter(spout=spout)
                    try:
                        spout_change = filtered_spout_changes[0]
                        spout_changes += '1' if spout_change.is_on is True else '0'
                    except IndexError:
                        spout_changes += '2'
                # for spout_change in ExternalButtonEventSpoutChange.objects.filter(external_button_event=event).\
                #         order_by('spout__number'):
                #     spout_changes += booleanToStringOfBit(spout_change.is_on)
                event_data['spouts'] = spout_changes
                events.append(event_data)
            external_button_data['events'] = events
            external_button_data['events_count'] = len(events)
            data.append(external_button_data)
    except (ValueError, Device.DoesNotExist):
        return Response({'msg', 'invalid request'})
    return Response(data)


@api_view(['Post'])
def update_condition_view(request, *args, **kwargs):

    update_spout_condition(request, *args, **kwargs)

    update_external_button_status(request, *args, **kwargs)

    return Response({'thank you'})


@api_view(['Post'])
def test_input(request, *args, **kwargs):
    TestCall.objects.create(header = str(request.headers), body= str(request.data))
    return Response({'header': request.headers, 'body': request.body})


# @api_view(['Post'])
# def make_device(request):
#     return Response({'Not Implemented'})

# def device_time_encoder(date_time):
#     return f'{in_digits_str(date_time.year, 4)}/' \
#            f'{in_digits_str(date_time.month, 2)}/' \
#            f'{in_digits_str(date_time.day, 2)},' + \
#            f'{in_digits_str(date_time.hour, 2)}:' \
#            f'{in_digits_str(date_time.minute, 2)}:' \
#            f'{in_digits_str(date_time.second, 2)}'
#
#
# def in_digits_str(int_value, digits):
#     value = str(int_value)
#     while len(value) < digits:
#         value = '0' + value
#     return value
#
#
# def device_interval_encoder(period):
#     print(period)
#     return f'{period.days} ' \
#            f'{in_digits_str(period.seconds // 3600, 2)}:' \
#            f'{in_digits_str((period.seconds % 3600) // 60, 2)}:' \
#            f'{in_digits_str(period.seconds % 60, 2)}'
