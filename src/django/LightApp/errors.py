from Baghyar.errors import BaseErrorHandler
from django.db import models
from Baghyar import errors as global_errors


class Error2001EmptySerial(BaseErrorHandler):
    error_number = 2001
    error_msg = "empty serial"
    error_name = "empty_serial"

    @staticmethod
    def check_serial(serial):
        if serial is None or len(serial) == 0:
            Error2001EmptySerial().raise_error()


class Error2002InvalidSerializer(BaseErrorHandler):
    error_number = 2002
    error_name = "Invalid serialize"
    serializer = None
    cls_name = ""

    def get_msg(self):
        return f'invalid {self.cls_name} serialize: {self.serializer.errors}'

    def get_validated_serializer(self, serializer, cls_name):
        if not serializer.is_valid():
            self.serializer = serializer
            self.cls_name = cls_name
            self.raise_error()
        return serializer


class Error2003DelayLessThanInterval(BaseErrorHandler):
    error_number = 2003
    error_name = "Delay less than interval"
    error_msg = "delay must be less than interval"


class Error2004ModelDataError(BaseErrorHandler):
    error_number = 2004
    error_name = "Model Data Error"
    error_msg = "error in data saving"


class Error2005InvalidPhoneNumber(BaseErrorHandler):
    error_number = 2005
    error_name = "invalid phone number"
    error_msg = "enter a valid phone number"


class Error2006MissingValues(BaseErrorHandler):
    error_number = 2006
    error_name = "missing values"
    error_msg = "missing values: "

    def send_missing_values_error(self, *args):
        for field in args:
            self.error_msg += f'{str(field)}, '
        self.raise_error()


class Error2007InvalidLandSerial(BaseErrorHandler):
    error_number = 2007
    error_name = "invalid serial"
    error_msg = "invalid serial"

class Error2008CantCreateNewSpout(BaseErrorHandler):
    error_number = 2008
    error_name = "Cant create new spout"
    error_msg = "You can't create new spout here"