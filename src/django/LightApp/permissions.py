from rest_framework import permissions
from Baghyar.views import get_user_by_request_token
from Baghyar import errors as global_errors, views as global_views
from rest_framework.exceptions import ValidationError, PermissionDenied, AuthenticationFailed
from Customer.models import Customer, Land, ProgramGroup, SubProgram, Spout, ChangeSpout, Device


class TokenPermission(permissions.BasePermission):

    request = None
    user = None
    customer = None
    land = None

    def __init__(self, request=None):
        self.request = request
        if request is not None:
            self.user, self.customer = self.get_user_customer()
        if request is not None:
            self.land = self.get_land(request)

    def has_object_permission(self, request, view, obj):
        if type(obj) == Device:
            pass  # TODO
            # raise PermissionError()

    def get_user(self, request):
        if not self.user:
            self.user = get_user_by_request_token(request)
        return self.user

    def get_customer(self, request):
        if not self.customer:
            self.customer = Customer.get_or_create(self.get_user(request))
        return self.customer

    def get_land(self, request=None):
        if request is None:
            request = self.request
        self.land = self.get_from_request_if_is_None(self.land, request, 'land', Land)
        return self.land

    def get_user_customer(self, request=None):
        if request is None:
            request = self.request
        user = get_user_by_request_token(request)
        return user, Customer.get_or_create(user)

    def check_own_username(self, request, username=None):
        if not username:
            username = request.data.get('username')
        if not self.user:
            self.user = self.get_user(request)
        if self.user.username != username:
            # print(f'user:{user.username}!=username:{username}')
            global_errors.Error1007DontOwnUsername().raise_error()

    def has_permission(self, request, view):
        try:
            token = global_views.get_and_validate_request_token(request)
        except (ValidationError, ValueError) as e:
            raise AuthenticationFailed()
        if not token:
            raise AuthenticationFailed()
        return True

    def get_from_request_if_is_None(self, obj, request, obj_name, obj_class):
        if not obj:
            obj = request.data.get(obj_name)
            if isinstance(obj, int):
                obj = obj_class.objects.get(id=obj)
            assert obj, f'should enter {obj_name} value or has {obj_name} in request'
        return obj

    def check_access_land(self, request, land=None):
        if not self.customer:
            self.customer = self.get_customer(request)
        land = self.get_from_request_if_is_None(land, request, 'land', Land)
        if self.customer not in land.customers.all() and not self.customer.is_supervisor and not self.customer.is_admin:
            raise PermissionDenied()

    def check_access_program_group(self, request, program_group=None):
        program_group = self.get_from_request_if_is_None(program_group, request, 'program_group', ProgramGroup)
        return self.check_access_land(request, program_group.land)

    def check_access_sub_program(self, request, sub_program=None):
        sub_program = self.get_from_request_if_is_None(sub_program, request, 'program', SubProgram)
        return self.check_access_land(request, sub_program.land)

    def check_access_change_spout(self, request, change_spout=None):
        change_spout = self.get_from_request_if_is_None(change_spout, request, 'change_spout', ChangeSpout)
        return self.check_access_land(request, change_spout.land)

    def check_access_spout(self, request, spout=None):
        spout = self.get_from_request_if_is_None(spout, request, 'spout', Spout)
        return self.check_access_land(request, spout.device.land)

    def check_can_admin_land(self, request, land=None):
        if land:
            self.land = land
        if not self.land:
            self.land = self.get_from_request_if_is_None(self.land, request, 'land', Land)
        if not self.user or not self.customer:
            self.user, self.customer = self.get_user_customer(request)
        # print(f'{user.id}.user:{user}_type:{type(user)}\n{land.owner.user.id}.owner:{land.owner.user}_type:{type(land.owner.user)}')
        if not ((self.land.owner and self.user.id is self.land.owner.user.id) or self.user.is_staff or
                self.customer.is_admin or self.customer.is_supervisor):
            raise PermissionDenied()

    def check_can_create_land(self, request):
        if not self.user or not self.customer:
            self.user, self.customer = self.get_user_customer(request)
        if not self.user.is_staff and not self.customer.is_admin and not self.customer.is_supervisor:
            raise PermissionDenied()

