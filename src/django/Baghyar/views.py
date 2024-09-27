from rest_framework.exceptions import ValidationError, AuthenticationFailed
from Customer import models as customer_models
from rest_framework.authtoken.models import Token
import datetime
import json
from django.utils.dateparse import parse_duration
from datetime import timedelta
from Baghyar import settings
import re
from rest_framework import serializers
from django.db import models
from . import errors
from django.contrib.auth.models import User


def get_validated_obj(**kwargs):
    # obj_name or obj_id
    # query or request or cls
    if 'obj_name' not in kwargs:
        msg = "error 113: developer error"
        raise ValidationError(msg)
    obj_name = kwargs['obj_name']
    if 'obj_id' not in kwargs:
        if 'request' not in kwargs:
            msg = "error 112: developer error"
            raise ValidationError(msg)
        request = kwargs['request']
        obj_id_str = get_request_value(request, obj_name)
        try:
            obj_id = int(obj_id_str)
        except TypeError:
            msg = f'error 111: invalid {obj_name} format'
            raise ValidationError(msg, code='validation')
    else:
        obj_id = kwargs['obj_id']
    if 'query' not in kwargs:
        if 'cls' not in kwargs:
            msg = "error 110: developer error"
            raise ValidationError(msg)
        query = kwargs['cls'].objects
    else:
        query = kwargs['query']

    objs = query.filter(id=obj_id)
    if not objs.count():
        msg = "error 109: invalid " + obj_name
        raise ValidationError(msg, code='validation')
    return objs.first()


def get_and_validate_object_from_queryset(queryset, obj_name, obj_id):
    objs = queryset.filter(id=obj_id)
    if not objs.count():
        msg = 'error 108: invalid ' + obj_name
        raise ValidationError(msg, code='validation')
    return objs.first()


def get_and_validate_object_from_class_by_id(cls, obj_name, obj_id):
    return get_and_validate_object_from_queryset(cls.objects, obj_name, obj_id)


def get_and_validate_object_from_request_by_query(request, query, obj_name):
    obj_id = request.data.get(obj_name)
    if not isinstance(obj_id, int):
        if not isinstance(obj_id, str):
            print(type(obj_id))
            msg = f'error 107: invalid {obj_name} type {type(obj_id)}:{obj_id}'
            raise ValidationError(msg)
        try:
            return get_and_validate_object_from_queryset(query, obj_name, int(obj_id))
        except ValueError:
            msg = f'{obj_name} should be int or str and is instead: {type(obj_id)}'
            raise ValidationError('impossible')
    return get_and_validate_object_from_queryset(query, obj_name, obj_id)


def get_and_validate_object_from_request_by_class(request, cls, obj_name):
    return get_and_validate_object_from_request_by_query(request, cls.objects, obj_name)


def get_spout_and_authorize_by_request(request):
    spout = get_and_validate_object_from_request_by_class(request, customer_models.Spout, 'spout')

    user = get_user_by_request_token(request)
    customer = create_or_get_customer(user)
    if not customer_has_land(customer, spout.device.land):
        msg = 'error 106: unauthorized request'
        raise ValidationError(msg, code='authorization')
    return spout


def get_data_value(data, value_name):
    value = data.get(value_name)
    if value is None:
        msg = f'error 105: missed {value_name}'
        raise ValidationError(msg)
    return value


def get_request_value(request, value_name):
    return get_data_value(request.data, value_name)


def get_data_int_value(data, value_name):
    value = get_data_value(data, value_name)
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except ValueError:
        msg = f'error 119: {value_name} sould be int'
        raise ValidationError(msg, code='validation')


def get_data_boolean_value(data, value_name):
    value = get_data_value(data, value_name)
    if value in ['True', 'true', True, 1, '1', 'y']:
        return True
    if value in ['False', 'false', False, 0, '0', 'n']:
        return False
    msg = f'error 114: {value_name}: {value} is not boolean'
    raise ValidationError(msg, code='validation')


def get_data_datetime_value(data, value_name):
    value = get_data_value(data, value_name)
    # print(datetime.datetime.strptime(value, settings.REST_FRAMEWORK['DATETIME_FORMAT']))
    try:
        return datetime.datetime.strptime(value, settings.REST_FRAMEWORK['DATETIME_FORMAT'])
    except ValueError:
        msg = f'error 115: {value_name}: {value} is not date time format'
        raise ValidationError(msg, code='validation')
    # if isinstance(value, datetime.datetime) or type(value) is datetime.datetime:
    #     return value
    # datetime.datetime.strptime(s, "%Y-%m-%d").date()



def get_data_duration_value(data, value_name):
    value = get_data_value(data, value_name)
    duration_value = parse_duration(value)
    if duration_value:
        return duration_value
    return timedelta()
    # if isinstance(value, datetime.timedelta) or type(value) is datetime.datetime:
    # datetime.datetime.strptime(s, "%Y-%m-%d").date()
    # msg = f'error 115: {value_name}: {value} is duration time format'
    # raise ValidationError(msg, code='validation')


def get_data_json_value(data, value_name):
    value = get_data_value(data, value_name)
    # if
    # datetime.datetime.strptime(s, "%Y-%m-%d").date()
    attr = {}
    try:
        print(value)
        json_value = json.load(value)
        if type(json_value) is dict:
            return json_value
    except (json.decoder.JSONDecodeError, KeyError):
        msg = f"error 116: invalid {value_name}"
        raise ValidationError(msg, code='validation')
    msg = f"error 117: {value_name} should be in bracket fromat"
    raise ValidationError(msg, code='validation')


def parse_list(value):
    if len(value) < 2 or value[0] != '[' or value[-1] != ']':
        msg = f'error 122_invalid list str: {value}, list_start: {value[0]}, list_end: {value[-1]}, ' \
              f'list_type: {type(value)}'
        raise ValidationError(msg)
    values = []
    start_index = 1
    end_index = 1
    [open_brackets, open_squares, open_curlies, open_quotations] = [0, 0, 0, 0]
    # print([open_brackets, open_squares, open_curlies, open_quotations])
    # open_brackets = 0
    # open_squares = 0
    # open_curlies = 0
    # open_quotations = 0
    added_values = {
        '(': [1, 0, 0, 0],
        ')': [-1, 0, 0, 0],
        '[': [0, 1, 0, 0],
        ']': [0, -1, 0, 0],
        '{': [0, 0, 1, 0],
        '}': [0, 0, -1, 0],
        '"': [0, 0, 0, 1],
    }
    while end_index < len(value) - 1:
        while value[end_index] in [' ', '\n', '\t', ','] and end_index < len(value) - 1:
            if start_index is end_index:
                start_index = start_index + 1
            end_index = end_index + 1
        end_char = value[end_index]
        [open_brackets, open_squares, open_curlies, open_quotations] = [sum(pair) for pair in zip(
            [open_brackets, open_squares, open_curlies, open_quotations],
            added_values.get(end_char, [0, 0, 0, 0])
        )]
        end_index = end_index + 1
        if open_brackets == 0 and open_squares == 0 and open_curlies == 0 and open_quotations % 2 == 0:
            values.append(value[start_index:end_index])
            start_index = end_index
    return values


def get_data_list_value(data, value_name):
    values_str = get_data_value(data, value_name)

    values = parse_list(values_str)
    # for item in re.split('},{|{|}', values_str[1:-1]):
    #     values.append('{'+item+'}')
    # print(repr(values[1:-1]))
    return values


def get_user_by_request_token(request, token=None):
    # token_string = request.headers.get('Authorization')
    #
    # msg = "invalid authentication"
    # if not isinstance(token_string, str) or len(token_string) < 6:
    #     raise ValidationError(msg, code='authorization')
    #     # return None
    # token_key = token_string[6:]
    # token = Token.objects.get(key=token_key)
    token = get_and_validate_request_token(request, token)
    msg = "error 102: invalid token authentication"
    if not token:
        raise ValidationError(msg, code='authorization')
    user = token.user
    if user is None:
        msg = 'error 101: invalid authentication'
        raise ValidationError(msg, code='user validation')
    return user


def get_and_validate_request_token(request, token_string=None):
    if not token_string:
        token_string = request.headers.get('Authorization')
    if not token_string:
        token_string = request.headers.get('Token')
    if not token_string or not isinstance(token_string, str):
        token_string = request.data.get('Authorization')
    body_token = request.data.get('Authorization')
    if not isinstance(token_string, str) or len(token_string) < 6:
        msg = f'error 103: invalid authentication, headers:{request.headers}'
        # msg = "error 103: invalid authentication " + str(type(token_string)) + ' token=' + str(token_string) + ' token_body=' + str(body_token)
        raise ValidationError(msg, code='authorization')
        # return None
    token_key = token_string[6:]
    try:
        token = Token.objects.get(key=token_key)
        return token
    except Token.DoesNotExist:
        errors.Error1005InvalidToken().raise_error()


def customer_has_land(customer, land):
    customers = land.customers.all()
    if not customers.count():
        return False
    return customer in customers


def authorize_land_by_request(request, land: customer_models.Land):
    user = get_user_by_request_token(request)
    customer = create_or_get_customer(user)
    if not customer.id in [customer.id for customer in land.customers.all()]:
        msg = 'error 225: unauthorized land'
        raise ValidationError(msg)


def get_land_and_authorize_by_request(request):
    user = get_user_by_request_token(request)
    customer = create_or_get_customer(user)
    land = get_validated_obj(request=request, query=customer.lands, obj_name='land')
    # land = get_and_validate_object_from_request_by_query(request, customer.lands, 'land')
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


def create_or_get_customer(user):
    customers = user.customers.all()
    if user.customers.count() < 1:
        customer = customer_models.Customer(user=user, phoneNumber=user.username, isBlocked=False)
        customer.save()
    else:
        customer = customers[0]
    return customer


def check_spout_for_land(spout: customer_models.Spout, land : customer_models.Land):
    if spout.device.land.id != land.id:
        msg = f'error 124: accessing another land spout from spout land {spout.device.land.id}.{spout.device.land.name} to ' \
              f'{land.id}.{land.name}'
        raise ValidationError(msg)


def validate_serializer(serializer : serializers.ModelSerializer, model_name: str = None):
    if not serializer.is_valid():
        msg = f'error 120: invalid {model_name}: {serializer.errors}' if model_name is not None \
            else f'error 120: invalid data: {serializer.errors}'
        raise ValidationError(msg, code='validation')


def get_obj_with_data_id(data: dict, cls):
    try:
        pk = data['id']
    except KeyError:
        return None
    return cls.objects.filter(id=pk).first()


def get_user_by_username(username: str):
    return User.objects.get(username=username)