from Customer import models as customer_models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Max
from django.db.models import DateTimeField, ExpressionWrapper, F


# def update_land_programs_evaluation(land: customer_models.Land, right_now: timezone = timezone.now()):
#     last_update = land.last_time_programs_evaluated
#     spouts = customer_models.Spout.objects.filter(land=land)
#     for spout in spouts:
#         change_spouts = customer_models.ChangeSpout.objects\
#             .filter(spout=spout)\
#             .filter(sub_program__program_group__passed=False)
#         last_time, last_value = last_update, spout.isOn
#         for change_spout in change_spouts:
#             change_spout_last_time = change_spout.start
#             interval = change_spout.sub_program.program_group.interval
#             if change_spout.sub_program.program_group.repeatable:
#                 while change_spout_last_time + interval <= right_now:
#                     change_spout_last_time += interval
#             if last_time is None or change_spout_last_time > last_time:
#                 last_time, last_value, unchange = change_spout_last_time, change_spout.is_on, change_spout.unchange
#         if last_value is not None and spout.isOn is not last_value and unchange is False:
#             spout.isOn = last_value
#             spout.save()
#     update_land_program_groups(land, right_now)
#     land.update_last_time_programs_evaluated(right_now)


def update_program_group(program_group: customer_models.ProgramGroup, right_now: timezone):
    if program_group.repeatable:
        while program_group.end < right_now:
            program_group.start += program_group.interval
        program_group.save()
    else:
        if program_group.end < right_now:
            program_group.delete()


def update_land_program_groups(land: customer_models.Land, right_now: timezone):
    program_groups = customer_models.ProgramGroup.objects.filter(land=land)
    for program_group in program_groups:
        update_program_group(program_group, right_now)


def is_phone_number(number):
    return True


def is_empty(query):
    return query.count() == 0