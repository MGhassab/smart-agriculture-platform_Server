import random
import string
import re

from django.contrib.auth.models import User
from django.db import models
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework import parsers, renderers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from Baghyar import views as global_views
from Baghyar.settings import PHONE_NUMBER_REGEX
from Customer.models import Customer, Device

from LightApp import errors, settings
from LightApp.models import Verification
from LightApp.permissions import TokenPermission
from LightApp.serializers import *


class VerificationCheck(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = VerificationCheckSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        customer = Customer.get_or_create(user)
        customer.isActivated = True
        customer.save()
        return login_credentials_response(customer)


class VerificationCheckV2(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = VerificationCheckSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        customer = Customer.get_or_create(user)
        return verify_user_credentials(customer)


class UserInfo(APIView):
    throttle_classes = ()
    permission_classes = ([TokenPermission, ])
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = UserInfoSerializer

    def get_user(self, request):
        return global_views.get_user_by_request_token(request)

    def get(self, request):
        user = self.get_user(request)
        serializer = self.serializer_class(instance=user)
        return Response(serializer.data)

    def put(self, request):
        user = self.get_user(request)
        serializer = self.serializer_class(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Register(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        get_verification = GetVerification.as_view()
        return get_verification(request._request, *args, **kwargs)


class GetVerification(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = VerificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except (Verification.DoesNotExist, KeyError) as e:
            raise errors.Error2006MissingValues().send_missing_values_error('username')
        except User.DoesNotExist:
            raise errors.Error2005InvalidPhoneNumber().raise_error()
        data = {
            "username": serializer.data['user'].username,
            "expire": serializer.data['expire'],
            # "code": serializers.data['code'],
            "is_active": False,
        }
        return Response(data)


class GetVerificationAndCreateUser(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = VerificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            if re.search(PHONE_NUMBER_REGEX, username) is None:
                raise ValidationError('invalid phone number')
            users = User.objects.filter(username=username)
            if users.count() == 0:
                password = ''.join(random.choice(string.ascii_lowercase) for x in range(20))
                User.objects.create_user(username=username, password=password)
            # User.objects.create_user('username', )

            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except (Verification.DoesNotExist, KeyError) as e:
            raise errors.Error2006MissingValues().send_missing_values_error('username')
        except User.DoesNotExist:
            raise errors.Error2005InvalidPhoneNumber().raise_error()
        data = {
            "username": serializer.data['user'].username,

            "expire": serializer.data['expire'],
            # "code": serializers.data['code'],
            # "is_active": False,
        }
        return Response(data)

    def valid_phone_number(phone_number):
        return True  # TODO


class Authenticate(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        customer = Customer.get_or_create(user)
        if customer.isActivated:
            return login_credentials_response(customer)
        get_verification = GetVerification.as_view()
        return get_verification(request._request, *args, **kwargs)
        # return GetVerification().post(request, *args, **kwargs)
        # verification = models.Verification(customer=customer)
        # verification.save()
        # verification.send()
        # code, expire = verification.code, verification.expire
        # return Response({'code': code, 'expire': expire, 'username': user.username})


def login_credentials_response(customer: Customer):
    user = customer.user
    token, created = Token.objects.get_or_create(user=user)
    return Response(
        {
            'token': token.key, 'first_name': user.first_name, 'last_name': user.last_name,
            'username': user.username, 'is_customer': customer.is_customer,
            'is_admin': customer.is_admin, 'is_supervisor': customer.is_supervisor,
            'is_active': customer.isActivated,
        })


def verify_user_credentials(customer: Customer):
    user = customer.user
    token, created = Token.objects.get_or_create(user=user)
    return Response(
        {
            'token': token.key,
            'username': user.username,
            'has_registered_land': customer.has_registered_land,
        })


class ChangePassword(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        TokenPermission().check_own_username(request)

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

#
# @api_view(['Post'])
# @permission_classes([TokenPermission])
# @throttle_classes([UserRateThrottle])
# def user_devices(request):
#     user = request.user
#     customer = Customer.get_or_create(user=user)
#     devices = Device.objects.filter()


class UserDevices(ListAPIView):
    serializer_class = SimpleDeviceSerializer
    permission_classes = [TokenPermission]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        return Device.objects.filter(models.Q(land__customers__user=self.request.user))
