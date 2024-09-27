from rest_framework import serializers
from django.utils import timezone


# Class to make output of a DateTime Field timezone aware
class DateTimeFieldWihTZ(serializers.DateTimeField):
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldWihTZ, self).to_representation(value)