from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from LightApp.permissions import TokenPermission
from Baghyar import errors as global_errors, settings
from LightApp import errors
from rest_framework.response import Response
import inspect


class ErrorList(APIView):
    permission_classes = ([TokenPermission])

    def get(self, request):
        global_error_list = [cls_tuple[1] for cls_tuple in inspect.getmembers(global_errors, inspect.isclass)]
        local_errorList = [cls_tuple[1] for cls_tuple in inspect.getmembers(errors, inspect.isclass)]
        error_list = [*global_error_list, *local_errorList]
        error_list = set(error_list)
        error_list.remove(global_errors.BaseErrorHandler)
        cls_list = error_list.copy()
        error_list.clear()
        for cls in cls_list:
            if issubclass(cls, global_errors.BaseErrorHandler):
                error_list.add(cls())
        error_list = [error_cls.get_dict() for error_cls in error_list]
        # error_list = [
        #     global_errors.Error1000MissedObjectPk.get_dict(),
        #     global_errors.Error1001InvalidRelationshipError.get_dict(),
        #     global_errors.Error1002SerializerValidationError.get_dict(),
        #     global_errors.Error1003NoneObject.get_dict(),
        #     global_errors.Error1004CustomerDoesNotOwnLand.get_dict(),
        #
        #     errors.Error2001EmptySerial.get_dict(),
        #     errors.Error2002InvalidSerializer.get_dict(),
        #     errors.Error2003DelayLessThanInterval.get_dict(),
        #     errors.Error2004ModelDataError.get_dict(),
        #     errors.Error2005InvalidPhoneNumber.get_dict(),
        #     errors.Error2006MissingValues.get_dict(),
        #     errors.Error2007InvalidLandSerial.get_dict(),
        #
        # ]
        return Response(error_list)
