from django.db import models

from model_utils.models import StatusModel, TimeStampedModel
from model_utils import Choices

# from Customer.models import Spout
from Device import models as device_models


class SpoutChangeRecord(StatusModel, TimeStampedModel):
    STATUS = Choices('turn_off', 'turn_on')
    spout = models.ForeignKey('Customer.Spout', on_delete=models.CASCADE, related_name='change_records', verbose_name='شیر آب')
    time = models.DateTimeField('زمان')


class CustomerSpoutChangeRecord(SpoutChangeRecord):
    customer = models.ForeignKey(
        'Customer.Customer',
        on_delete=models.DO_NOTHING,
        related_name='spout_change_records',
        blank=True,
        null=True,
        verbose_name='مشتری',
    )


class ProgramSpoutChangeRecord(SpoutChangeRecord):
    program_group = models.ForeignKey('Customer.ProgramGroup', on_delete=models.CASCADE, blank=True, null=True)
    start = models.DateTimeField('زمان شروع برنامه', null=True, blank=True)
    finish = models.DateTimeField('زمان پایان برنامه', null=True)
    canceled = models.BooleanField('لغو شده', default=False)
    execute_before_cancel = models.BooleanField('اجرا شدن رکورد قبل از کنسلی', default=False)

    def __str__(self):
        return f'{self.id}.status={self.status},canceled={self.canceled},exe_before_cancel=' \
               f'{self.execute_before_cancel},time={self.time},spout={self.spout.id}.{self.spout.name},' \
               f'PG={self.program_group_id}.{self.program_group.name}'


class ProcessSpoutChangeRecord(SpoutChangeRecord):
    # button = models.ForeignKey(device_models.ExternalButton, on_delete=models.DO_NOTHING, related_name='spout_records',
    #                            null=True, blank=True)
    button_record = models.ForeignKey(device_models.ExternalButtonStatusRecord, on_delete=models.CASCADE,
                                      related_name='spout_records', null=True)
    change_spout = models.ForeignKey(device_models.ExternalButtonEventSpoutChange, on_delete=models.CASCADE,
                                     related_name='process_spout_records', null=True, blank=True)
    start = models.DateTimeField('زمان شروع پروسه', null=True, blank=True)
    finish = models.DateTimeField('زمان پایان پروسه')
    execute_before_cancel = models.BooleanField('اجرا قبل از کنسلی', default=False)

    def __str__(self):
        return f'{self.id}.status={self.status},time={self.time},spout={self.spout.id}.{self.spout.name},' \
               f'PR={self.button_record.process_button_id}.{self.button_record.process_button.name}'

#
# class SpoutLastIrrigation(TimeStampedModel):
#     time = models.DateTimeField('time')
#     spout = models.OneToOneField(
#         Spout,
#         on_delete=models.DO_NOTHING,
#         related_name='last_irrigation_update'
#     )
