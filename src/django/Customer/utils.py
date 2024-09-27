from kavenegar import *
import urllib.parse
from Baghyar import settings
from datetime import timedelta
from django.utils import timezone
# from .models import TempSensor
# from . import models


local_start_day_delay = timezone.timedelta(minutes=settings.MINUTES_DELAY_TO_LOCAL_TIME) # - settings.HOURS_START_DAY_DELAY)


def get_program_time(time):
    # print("Get Program Time " + str(time))
    return time + local_start_day_delay


def start_of_day(time):
    return time.replace(hour=0, minute=0, second=0, microsecond=0)


def get_server_time(program_time):
    return program_time - local_start_day_delay


def get_server_startday_based_program_time(time):
    return get_server_time(start_of_day(get_program_time(time)))


def get_max(old_value, new_value):
    if old_value is None:
        return new_value
    if old_value > new_value:
        return old_value
    return new_value


def get_min(old_value, new_value):
    if old_value is None:
        return new_value
    if old_value < new_value:
        return old_value
    return new_value


def update_avg(old_value, new_value, quantity):
    if old_value is None:
        return new_value
    return old_value + ((new_value - old_value) / quantity)


def get_current_time():
    return timezone.now() + local_start_day_delay


persian_week_days = {
    0: "دوشنبه",
    1: "سه شنبه",
    2: "چهارشنبه",
    3: "پنج شنبه",
    4: "جمعه",
    5: "شنبه",
    6: "يکشنبه",
}


def get_persian_week_day(weekday):
    return persian_week_days[weekday]


def date_to_string(date):
    return str(date.year) + (str(date.month) if date.month > 9 else ("0" + str(date.month))) \
           + (str(date.day) if date.day > 9 else ("0" + str(date.day)))

def time_to_string(time):
    return date_to_string(time) + \
           ', ' + str(time.hour) if time.hour > 9 else ('0' + time.hour) + \
           ':' + str(time.minute) if time.minute > 9 else ('0' + time.minute) + \
           ':' + str(time.second) if time.second > 9 else ('0' + time.second)

def soil_percentage(soil_value):
    return ((3.3 - soil_value) / 3.3) * 100


def dict_from_class(cls):
    return dict(
        (key, value)
        for (key, value) in cls.__dict__.items())


# SENSOR_NAME_TO_OBJECTS = {
#     'humid': .models.HumiditySensor,
#     # 'temp': TempSensor,
#     # 'temporator': models.TempSensor,
#     'humidity': models.HumiditySensor,
#     'soil': models.SoilMoistureSensor,
#     'soil_moisture': models.SoilMoistureSensor,
#     'soilMoisture': models.SoilMoistureSensor,
#     'soilmoisture': models.SoilMoistureSensor,
#     'water': models.WaterSensor,
#     'twater': models.TrialWaterSensor,
#     'trialWater': models.TrialWaterSensor,
#     'trialwater': models.TrialWaterSensor,
#     'trial_water': models.TrialWaterSensor,
#     'eva': models.EvaporationSensor,
#     'evaporation': models.EvaporationSensor,
# }
#

# def get_sensor_model(sensor_name):
#     return None
#     # return SENSOR_NAME_TO_OBJECTS['sensor_name']
