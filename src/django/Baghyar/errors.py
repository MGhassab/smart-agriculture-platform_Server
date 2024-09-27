from rest_framework.exceptions import APIException, ValidationError
from rest_framework import serializers
from Baghyar import settings
from django.db import models
from Customer import models as customer_models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class BaseErrorHandler:
    error_number = None
    error_name = "undefined error"
    error_msg = _("unassigned")

    def get_msg(self):
        return self.error_msg

    def raise_error(self):
        if settings.DEBUG:
            int('error here')
        msg = self.get_msg()
        msg = f'error_{self.error_number}: {self.error_name} error' \
              f'{"," + msg if msg is not "unassigned" else ""}'
        raise ValidationError(detail=f'Error_{self.error_number}.{self.error_name}:{self.get_msg()}', code='validation')

    @classmethod
    def get_dict(cls):
        return {
            'number': cls.error_number,
            'name': cls.error_name,
            'msg': cls.error_msg
        }


class Error1000MissedObjectPk(BaseErrorHandler):
    error_number = 1000
    error_name = 'missed_object_pk'
    error_msg = "enter pk(id)"

    @staticmethod
    def check_pk_get_instance(pk, cls: models.Model):
        try:
            pk = int(pk)
            if isinstance(pk, int):
                return cls.objects.get(id=pk)
        except ValueError:
            pass
        except cls.DoesNotExist:
            pass

        Error1000MissedObjectPk().raise_error()


class Error1001InvalidRelationshipError(BaseErrorHandler):

    error_number = 1001
    error_name = "Invalid Relationship"
    error_msg = "invalid relationship"
    relationship_from = "undefined"
    relationship_to = "undefined"

    def __init__(self, relationship_from=None, relationship_to=None):
        self.relationship_from = relationship_from
        self.relationship_to = relationship_to

    @staticmethod
    def check_pks_relationship(pk1: int, pk2: int, relationship_from: str, relationship_to: str):
        if pk1 is not pk2:
            Error1001InvalidRelationshipError(relationship_from, relationship_to).raise_error()


class Error1002SerializerValidationError(BaseErrorHandler):
    error_number = 1002
    error_name = 'Serializer Validation'
    serializer: serializers.ModelSerializer = None

    def get_msg(self):
        return self.serializer.errors

    def __init(self, serializer):
        self.serializer = serializer

    @staticmethod
    def validate_serializer(serializer):
        if not serializer.is_valid():
            Error1002SerializerValidationError(serializer).raise_error()


class Error1003NoneObject(BaseErrorHandler):
    error_number = 1003
    error_name = 'none object'
    error_msg = ""

    def raise_error_for_none_object(self, obj, name):
        print(f'here2 {obj} of {name} is {obj is None}')
        if not obj or not type(obj):
            self.error_msg = f'None {name} object'
            print('error')
            self.raise_error()


class Error1004CustomerDoesNotOwnLand(BaseErrorHandler):
    error_number = 1004
    error_name = 'unreachable land'
    error_msg = 'customer does not own land'

    @classmethod
    def check_customer_owns_land(cls, land: customer_models.Land, customer: customer_models.Customer):
        customers = land.customers.all()
        if not customers.count() or customer not in customers:
            cls().raise_error()


class Error1005InvalidToken(BaseErrorHandler):
    error_number = 1005
    error_name = 'Invalid Token'
    error_msg = 'Invalid Token'


class Error1006RepeatedUsername(BaseErrorHandler):
    error_number = 1006
    error_name = 'Repeated Username'
    error_msg = 'user with this username already exists'

    def check_unique_username(self, username):
        users = User.objects.filter(username=username)
        if users.count():
            self.raise_error()


class Error1007DontOwnUsername(BaseErrorHandler):
    error_number = 1007
    error_name = "dont own username"
    error_msg = "you don't own this username"
    #
    # def temp_raise(self, username, user):
    #     self.error_msg = f' username={username}_type={type(username)}_len={len(username)}_first={username[0]}_last={username[-1]}, user username={user.username}_type={type(user.username)}_len={len(user.username)}_first={user.username[0]}_last={user.username[-1]}'
    #     self.raise_error()
