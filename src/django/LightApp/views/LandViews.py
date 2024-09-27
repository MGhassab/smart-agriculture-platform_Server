from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import parsers, renderers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import UserRateThrottle

from Baghyar import settings
from Customer.models import Land, ProgramGroup, SubProgram, ChangeSpout, Spout, Customer, SoilMoistureSensor, \
    WaterSensor, TempSensor, HumiditySensor, Device
from Baghyar.errors import Error1004CustomerDoesNotOwnLand, Error1003NoneObject, Error1001InvalidRelationshipError
from Baghyar.utils import is_empty
from Baghyar.views import get_validated_obj, get_data_boolean_value, get_user_by_request_token, \
    get_land_and_authorize_by_request, get_data_duration_value, get_data_datetime_value, \
    get_data_value, validate_serializer, get_obj_with_data_id, check_spout_for_land, \
    authorize_land_by_request, customer_has_land, get_request_value
from Device.models import ExternalButton, ExternalButtonStatusRecord
from Device.utils import is_land_online, get_next_update_time
from Irrigation.models import ProgramSpoutChangeRecord
from Irrigation.services import IrrigationManager

from LightApp import permissions
from LightApp.permissions import TokenPermission
from LightApp.errors import Error2004ModelDataError, Error2002InvalidSerializer, Error2001EmptySerial, \
    Error2007InvalidLandSerial
from LightApp.serializers import *
from LightApp.utils import replace_farsi_num


@api_view(['Post'])
@permission_classes([TokenPermission])
def add_user_land(request):
    user = get_user_by_request_token(request)
    customer = Customer.get_or_create(user)
    serial = get_request_value(request, 'serial').strip()
    Error2001EmptySerial().check_serial(serial)
    land = get_land_by_serial(serial)
    land.customers.add(customer)
    land.save()
    attr = {
        land.id: get_land_infos(land, customer),
        # 'msg': 'land successfully added'
    }
    return Response(attr)


@api_view(['Post'])
@permission_classes([TokenPermission])
def register_land_and_device(request):
    # serializers = RegisterLandAndDeviceSerializer(request=request, context={'request': request})
    user = get_user_by_request_token(request)
    customer = Customer.get_or_create(user)
    serial = get_request_value(request, 'serial').strip()
    serial = replace_farsi_num(serial)
    Error2001EmptySerial().check_serial(serial)
    try:
        device = Device.objects.filter(serial=serial)[0]
    except(IndexError, TypeError) as e:
        raise ValidationError(detail="wrong serial")
    if not device.has_name():
        try:
            device_name = request.data.get('device').strip()
            if len(device_name) == 0:
                raise ValidationError()
        except():
            raise ValidationError(detail="enter device name")
        device.name = device_name

    if device.land is None or not device.land.has_name():
        try:
            land_name = request.data.get('land').strip()
            if len(land_name) == 0:
                raise ValidationError()
        except():
            raise ValidationError(detail="enter land name")
        if device.land is None:
            land = Land.objects.create(name=land_name)
            device.land = land
        else:
            land = device.land
            land.name = land_name
            land.save()
    land = device.land
    if land.customers.filter(id=customer.id).count() == 0:
        land.customers.add(customer)
        if land.owner is None:
            land.owner = customer
        land.save()

    device.save()

    if not customer.has_registered_land:
        customer.has_registered_land = True
        customer.save()

    # serializer = DeviceSerializer(instance=device)
    # return Response(serializer.data)
    return Response({"device": device.id})


@api_view(['Post'])
@permission_classes([TokenPermission])
@throttle_classes([UserRateThrottle])
def check_serial_availability(request):
    serializer = SerialAvailabilitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.save())


def get_land_by_serial(serial):
    lands = Land.objects.filter(serial=serial)
    if not lands.count():
        Error2007InvalidLandSerial().raise_error()
    return lands.first()


@api_view(['Post'])
def toggle_spout(request):
    spout = get_spout_and_authorize_by_request(request)
    is_on = get_request_value(request, 'isOn')
    spout.isOn = True if (is_on == 'True' or is_on == 'true' or is_on is True) else False
    spout.save()
    serializer = SpoutSerializer(spout)
    return Response(serializer.data)


def get_spout_and_authorize_by_request(request):
    spout = get_validated_obj(request=request, cls=Spout, obj_name='spout')
    # spout = global_views.get_and_validate_object_from_request_by_class(request, Spout, 'spout')

    user = get_user_by_request_token(request)
    customer = Customer.get_or_create(user)
    if not customer_has_land(customer, spout.land):
        msg = 'unauthorized request'
        raise ValidationError(msg, code='authorization')
    return spout


@api_view(['Post'])
def get_land_updates(request):
    user = get_user_by_request_token(request)

    customer = Customer.get_or_create(user)

    land = get_validated_obj(request=request, cls=Land, obj_name='land')

    Error1004CustomerDoesNotOwnLand.check_customer_owns_land(land, customer)

    attr = get_land_infos(land)
    return Response(attr)


@api_view(['Post'])
@permission_classes([permissions.TokenPermission])
def user_lands(request):
    user = get_user_by_request_token(request)
    customer = Customer.get_or_create(user)
    lands = customer.lands.all()
    lands_details = {
        land.id: get_land_infos(land, customer) for land in lands
    }
    return Response(lands_details)


@api_view(['Post'])
@permission_classes([permissions.TokenPermission])
def del_user_land(request):
    user = get_user_by_request_token(request)
    customer = Customer.get_or_create(user)
    land = get_validated_obj(request=request, cls=Land, obj_name='land')
    if customer not in land.customers.all():
        msg = "customer don't have access to land"
        raise ValidationError(msg, code='validation')
    land.customers.remove(customer)
    attr = {
        land.id: get_land_infos(land, customer),
    }
    return Response(attr)


def get_land_infos(land, customer):
    return {
        'id': land.id,
        'name': land.name,
        'location': land.location,
        'area': land.area,
        'is_connected': is_land_online(land),
        'is_owner': land.owner is not None and land.owner.id == customer.id,
        'sensors': get_land_last_sensors(land),
        'spouts': get_land_spouts(land),
    }


def get_land_spouts(land):
    land_spouts = Spout.objects.filter(device__land=land)
    return [{
            'id': spout.id,
            'number': spout.number,
            'name': spout.name,
            'isOn': spout.isOn,
    } for spout in land_spouts]


def get_land_last_sensors(land):
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


class ProgramGroupView(APIView):
    permission_classes = [permissions.TokenPermission]

    def post(self, request):
        # land = get_land_and_authorize_by_request(request)
        try:
            device = Device.objects.get(id=request.data.get('device'))
        except Device.DoesNotExist:
            raise ValidationError('invalid device')
        land = device.land
        token_permission = TokenPermission()
        name = request.data.get('name')
        # name = get_data_value(request.data, 'name')
        repeatable = get_data_boolean_value(request.data, 'repeatable')
        interval = get_data_duration_value(request.data, 'interval')
        start = get_data_datetime_value(request.data, 'start')
        programs_list = get_data_value(request.data, 'programs')
        program_group_serializer = ProgramGroupSerializer(
            data={
                'name': name,
                'land': land.id,
                'device': device.id,
                'repeatable': repeatable,
                'interval': interval,
                'start': start
            }
        )

        validate_serializer(program_group_serializer, 'program_group')

        sub_program_with_change_spouts_serializers = []
        for program_dict in programs_list:
            sub_program_serializer = self.sub_program_serializer(program_dict)
            change_spout_list = program_dict['spouts']
            change_spout_serializers = []
            for change_spout in change_spout_list:
                change_spout_serializers.append(self.change_spout_serializer(change_spout))

            sub_program_with_change_spouts_serializers.append({
                'sub_program_serializer': sub_program_serializer,
                'change_spout_serializers': change_spout_serializers,
            })

        for sub_serializer in sub_program_with_change_spouts_serializers:
            change_spout_serializers = sub_serializer['change_spout_serializers']
            for change_spout_serializer in change_spout_serializers:
                spout = change_spout_serializer.validated_data['spout']
                Error1003NoneObject().raise_error_for_none_object(spout, 'spout')
                token_permission.check_access_spout(request, spout)
        try:
            program_group = program_group_serializer.save()
            for sub_serializer in sub_program_with_change_spouts_serializers:
                sub_program_serializer = sub_serializer['sub_program_serializer']
                sub_program_serializer.validated_data.update({'program_group': program_group})
                sub_program = sub_program_serializer.save()
                change_spout_serializers = sub_serializer['change_spout_serializers']
                for change_spout_serializer in change_spout_serializers:
                    change_spout_serializer.validated_data.update({'sub_program': sub_program})
                    change_spout_serializer.save()
            return Response(self.get_program_group(program_group=program_group))
        except ValueError:
            raise ValidationError('saving error, maybe max number of programs exceeded')
        # except ValueError:
        #     Error2004ModelDataError().raise_error()
        # return Response(program_group_serializer.data)

    @staticmethod
    def sub_program_serializer(sub_program_dict: dict) -> SubProgramSerializer:
        sub_program_object = get_obj_with_data_id(sub_program_dict, SubProgram)
        serializer = SubProgramSerializer(instance=sub_program_object, data={**sub_program_dict})
        Error2002InvalidSerializer().get_validated_serializer(serializer, 'sub_program')
        return serializer
        # try:
        #     pk = sub_program_dict['id']
        #     sub_program = SubProgram.objects.get(id=pk)
        #     sub_program_serializer = SubProgramSerializer(sub_program, data=sub_program_dict)
        # except KeyError:
        #     sub_program_serializer = SubProgramSerializer(data=sub_program_dict)
        # except ObjectDoesNotExist:
        #     sub_program_serializer = SubProgramSerializer(data=sub_program_dict)
        # if not sub_program_serializer.is_valid():
        #     msg = f'error 121: invalid sub program: {sub_program_serializer.errors}'
        #     raise ValidationError(msg, code='Validation')
        # return sub_program_serializer

    @staticmethod
    def change_spout_serializer(change_spout_dict: dict) -> ChangeSpoutSerializer:
        change_spout_object = get_obj_with_data_id(change_spout_dict, ChangeSpout)
        # print(change_spout_object)
        # print(change_spout_dict)
        if change_spout_object:
            serializer = ChangeSpoutSerializer(instance=change_spout_object, data={**change_spout_dict})
        else:
            serializer = ChangeSpoutSerializer(data={**change_spout_dict})
        # print(serializers.initial_data)
        serializer = Error2002InvalidSerializer().get_validated_serializer(serializer, 'change_spout')
        # print(serializers.validated_data)
        # print(serializers.data)
        # print(serializers.errors)
        return serializer

    def put(self, request):
        try:
            device = Device.objects.get(id=request.data.get('device'))
        except Device.DoesNotExist:
            raise ValidationError('invalid device')
        land = device.land
        program_group = get_validated_obj(request=request, cls=ProgramGroup, obj_name='id')
        Error1001InvalidRelationshipError.check_pks_relationship(
            land.id,
            program_group.land.id,
            'land',
            'program_group'
        )
        authorize_land_by_request(request, land)
        if program_group.land.id is not land.id:
            msg = 'Error_224: unauthorized land'
            raise ValidationError(msg)
        # name = global_views.get_data_value(request.data, 'name')
        # repeatable = global_views.get_data_boolean_value(request.data, 'repeatable')
        # interval = global_views.get_data_duration_value(request.data, 'interval')
        start = get_data_datetime_value(request.data, 'start')
        programs_list = get_data_value(request.data, 'programs')
        program_group_serializer = DetailedProgramGroupSerializer(program_group, data=request.data)
        #     'name': name,
        #     'land': land.id,
        #     'repeatable': repeatable,
        #     'interval': interval,
        #     'start': start,
        # })

        validate_serializer(program_group_serializer, 'program_group')

        sub_program_with_change_spouts_serializers = []
        for program_dict in programs_list:
            # program_dict = json.loads(program_str)
            sub_program_serializer = self.sub_program_serializer(program_dict)
            change_spout_list = program_dict['spouts']
            change_spout_serializers = []
            for change_spout in change_spout_list:
                change_spout_serializers.append(self.change_spout_serializer(change_spout))
            sub_program_with_change_spouts_serializers.append({
                'sub_program_serializer': sub_program_serializer,
                'change_spout_serializers': change_spout_serializers,
            })
        for sub_serializer in sub_program_with_change_spouts_serializers:
            change_spout_serializers = sub_serializer['change_spout_serializers']
            for change_spout_serializer in change_spout_serializers:
                spout = change_spout_serializer.validated_data['spout']
                check_spout_for_land(spout, land)

        validated_sub_program_ids = []
        validated_change_spout_ids = []
        program_group = program_group_serializer.save()
        program_group.set_synced(False)
        for sub_serializer in sub_program_with_change_spouts_serializers:
            sub_program_serializer = sub_serializer['sub_program_serializer']
            sub_program_serializer.validated_data.update({'program_group': program_group})
            try:
                sub_program = sub_program_serializer.save()
                validated_sub_program_ids.append(sub_program.id)
                change_spout_serializers = sub_serializer['change_spout_serializers']
                for change_spout_serializer in change_spout_serializers:
                    change_spout_serializer.validated_data.update({'sub_program': sub_program})
                    change_spout = change_spout_serializer.save()
                    validated_change_spout_ids.append(change_spout.id)
            except ValueError:
                Error2004ModelDataError().raise_error()

        SubProgram.objects.filter(program_group__id=program_group.id)\
            .exclude(id__in=validated_sub_program_ids).delete()
        ChangeSpout.objects.filter(sub_program__program_group__id=program_group.id)\
            .exclude(id__in=validated_change_spout_ids).delete()

        return Response(program_group_serializer.data)

    def delete(self, request, program_group_id):
        program_group = self.get_and_validate_program_group(user=request.user, program_group_id=program_group_id)
        print(f'program_group:{program_group}')
        program_group.delete()
        return Response({'msg': 'successfully deleted'})

    def get(self, request, program_group_id):
        program_group = get_validated_obj(
            cls=ProgramGroup,
            obj_id=program_group_id,
            obj_name='program_group'
        )
        # program_group = global_views.get_validated_obj(request=request, cls=models.ProgramGroup, obj_name='id')
        # print(program_group)
        # print(program_group.land)
        try:
            device = Device.objects.get(id=request.data.get('device'))
        except Device.DoesNotExist:
            raise ValidationError('invalid device')
        land = device.land
        authorize_land_by_request(request, land)
        serializer = DetailedProgramGroupSerializer(program_group)
        return Response(serializer.data)

    def get_program_group(self, pk: int = None, program_group: ProgramGroup = None):
        if pk is not None:
            try:
                program_group = ProgramGroup.objects.get(pk=pk)
            except ProgramGroup.DoesNotExist:
                msg = "error 226: invalid program group"
                raise ValidationError(msg)
        serializer = DetailedProgramGroupSerializer(program_group)
        # if not serializers.is_valid():
        #     print('invalid')
        # global_errors.Error1002SerializerValidationError.validate_serializer(serializers)
        return serializer.data

    @staticmethod
    def get_and_validate_program_group(user: User, program_group_id: ProgramGroup):
        try:
            program_group = ProgramGroup.objects.get(id=program_group_id)
        except ProgramGroup.DoesNotExist:
            raise ValidationError('invalid program group')
        if not program_group.can_edit(user):
            raise PermissionDenied()
        return program_group


@permission_classes([permissions.TokenPermission])
class LandView(APIView):

    def get(self, request, land_id):
        user = get_user_by_request_token(request)
        customer = Customer.get_or_create(user)
        land = get_validated_obj(cls=Land, obj_name='land', obj_id=land_id)
        Error1004CustomerDoesNotOwnLand.check_customer_owns_land(land, customer)
        # update_land_programs_evaluation(land)
        IrrigationManager().update_land_irrigation(land)
        serializer = LandSerializer(land, context={'customer': customer})
        return Response(serializer.data)


@permission_classes([permissions.TokenPermission])
class DeviceView(APIView):
    @staticmethod
    def check_customer_owns_device(device: Device, customer: Customer):
        try:
            for device_customer in device.land.customers.all():
                if device_customer.id == customer.id:
                    return
        except():
            pass
        raise ValidationError('Invalid Device')

    def get(self, request, device_id):
        user = get_user_by_request_token(request)
        customer = Customer.get_or_create(user)
        device = Device.objects.get(id=device_id)
        self.check_customer_owns_device(device, customer)
        IrrigationManager().update_device_irrigation(device)
        serializer = DeviceSerializer(device, context={'customer': customer})
        return Response(serializer.data)


@permission_classes([permissions.TokenPermission])
class DeviceHashView(APIView):
    @staticmethod
    def check_customer_owns_device(device: Device, customer: Customer):
        try:
            for device_customer in device.land.customers.all():
                if device_customer.id == customer.id:
                    return
        except():
            pass
        raise ValidationError('Invalid Device')

    def get(self, request, device_id):
        user = get_user_by_request_token(request)
        customer = Customer.get_or_create(user)
        device = Device.objects.get(id=device_id)
        self.check_customer_owns_device(device, customer)
        IrrigationManager().update_device_irrigation(device)
        serializer = DeviceSerializer(device, context={'customer': customer})
        data = serializer.data
        del data['last_device_log_time']
        del data['next_device_update']
        del data['device_online']
        del data['time_to_action']
        del data['network_coverage']
        salt = Token.objects.get(user=user).key
        hash_value = PBKDF2PasswordHasher().encode(str(data), salt=salt)
        return Response({'hash': hash_value})


@api_view(['Post'])
@permission_classes([permissions.TokenPermission])
def set_advance_program_mode(request):
    user = get_user_by_request_token(request)
    customer = Customer.get_or_create(user)
    is_advance = get_data_boolean_value(request.data, 'is_advance')
    land = get_validated_obj(request=request, cls=Land, obj_name='land')
    Error1004CustomerDoesNotOwnLand.check_customer_owns_land(land, customer)
    if not is_advance:
        ProgramGroup.objects.filter(land__id=land.id).delete()
    land.has_advance_time = is_advance
    land.save()
    return Response({"msg": "advance time activated", "land": land.id, "is_advance": is_advance})


class LandInfoDetails(APIView):
    throttle_classes = ()
    permission_classes = ([TokenPermission, ])
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = LandInfoSerializer

    def get_land(self, land_id):
        try:
            return Land.objects.get(id=land_id)
        except Land.DoesNotExist:
            raise NotFound()

    def get(self, request, land_id):
        land = self.get_land(land_id)
        TokenPermission().check_access_land(request, land)
        serializer = self.serializer_class(land)
        return Response(serializer.data)

    def put(self, request, land_id):
        land = self.get_land(land_id)
        TokenPermission().check_can_admin_land(request, land)
        serializer = self.serializer_class(land, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        TokenPermission().check_can_create_land(request)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['Post'])
@permission_classes([TokenPermission])
def reset_land_serial(request):
    permission = TokenPermission(request)
    # user, customer = permission.get_user_customer()
    permission.check_can_admin_land(request)
    land = permission.get_land(request)
    land.reset_serial()
    return Response({'serial': land.serial})


@api_view(['Post'])
@permission_classes([TokenPermission])
def call_process(request, device_id, process_number):
    try:
        device = Device.objects.get(id=device_id)
    except Device.DoesNotExist:
        raise ValidationError('invalid device')
    # TokenPermission().has_object_permission(request, device) TODO
    try:
        process_button = ExternalButton.objects.get(device=device, number=process_number)
    except ExternalButton.DoesNotExist:
        raise ValidationError('invalid process')
    status_type = False if request.data.get('function') is False else True
    process_status = ExternalButtonStatusRecord.STATUS.on if status_type else \
        ExternalButtonStatusRecord.STATUS.off
    manager = IrrigationManager()
    manager.record_process(
        process_button=process_button, status=process_status, actor=ExternalButtonStatusRecord.APP_ACTOR,
        user=request.user, time=timezone.now()
    )
    manager.update_device_irrigation(device)
    response = {'update_time': get_next_update_time(device).strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT']),
                'time_to_action': (get_next_update_time(device) + device.delay_to_action)
                .strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'])
                }
    return Response(response)


@api_view(['Post'])
@permission_classes([TokenPermission])
def cancel_program_run(request, program_id: int):
    try:
        program_group = ProgramGroup.objects.get(id=program_id)
    except ProgramGroup.DoesNotExist:
        raise ValidationError('invalid program group')
    if not program_group.device.has_user_access(request.user):
        raise PermissionDenied()
    if not program_group.is_ongoing():
        raise ValidationError('the program is not running')
    records = ProgramSpoutChangeRecord.objects.filter(program_group=program_group, start=program_group.last_start,
                                                      canceled=False)
    for record in records:
        record.canceled = True
        record.save()

    program_group.last_program_cancel = timezone.now()
    program_group.save()

    return Response(data={'msg': 'successfully canceled'})
