from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _
from Customer.models import Customer
from LightApp.models import Verification
from LightApp.errors import Error2006MissingValues
from Baghyar.errors import Error1006RepeatedUsername


class UserInfoSerializer(serializers.Serializer):
    class Meta:
        fields = ['username', 'first_name', 'last_name', 'email']
        editable_fields = ['first_name', 'last_name', 'email']

    username = serializers.CharField(label=_('username'), required=False)
    first_name = serializers.CharField(label=_('first_name'))
    last_name = serializers.CharField(label=_('last_name'))
    email = serializers.EmailField(label=_('email'))

    def update(self, instance: User, validated_data):
        for field in self.Meta.editable_fields:
            if hasattr(instance, field):
                setattr(instance, field, validated_data.get(field, getattr(instance, field)))
        instance.save()
        return instance

    def to_representation(self, instance: User):
        customer = Customer.get_or_create(instance)
        return {
            "username": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
            "is_admin": customer.is_admin,
            "is_supervisor": customer.is_supervisor,
            "is_customer": customer.is_customer,
        }


class ChangePasswordSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if username and password:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                msg = _('Invalid username')
                raise serializers.ValidationError(msg, code='authorization')
            user.set_password(password)
            user.save()
            tokens = Token.objects.filter(user=user)
            if tokens.count():
                tokens.delete()
            token = Token.objects.create(user=user)
            attrs['token'] = token.key
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['msg'] = 'successfully changed'
        return attrs


class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ('user', 'expire', 'code')
        extra_kwargs = {'expire': {'read_only': True}, 'code': {'read_only': True}}

    def create(self, validated_data):
        username = self.initial_data['username']
        data = validated_data.copy()
        data['username'] = username
        return self.Meta.model.create_verification(**data)


class VerificationCheckSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    code = serializers.CharField(label=_("code"))

    def validate(self, attrs):
        username = attrs.get('username')
        code = attrs.get('code')
        if username and code:
            verification = Verification.verify_user(username, code)
            if verification:
                attrs['user'] = verification.customer.user
                return attrs
            else:
                msg = _('Invalid verification code')
        else:
            msg = _('Enter username and verification code')
        raise serializers.ValidationError(msg, code='authorization')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        data = validated_data.copy()
        return self.Meta.model.objects.create_user(**data)

    def is_valid(self, raise_exception=False):
        data = self.initial_data
        username, password = None, None
        try:
            username = data['username']
            password = data['password']
        except KeyError:
            if raise_exception:
                Error2006MissingValues().send_missing_values_error('username' if not username else 'password')
        Error1006RepeatedUsername().check_unique_username(data['username'])
        super(RegisterSerializer, self).is_valid(raise_exception)


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
