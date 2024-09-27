from datetime import timedelta

from django.utils import timezone
import datetime
from django.db.models import Max

from Baghyar.conf.common import LOG_DEBUGS
from Baghyar.settings import IRRIGATION_UPDATE_DELAY
from Customer.models import Spout, ChangeSpout, ProgramGroup, Land, SubProgram, Device
from Device.models import ExternalButton, ExternalButtonEventSpoutChange, ExternalButtonStatusRecord, LogDeviceCheckOut

from Irrigation.models import CustomerSpoutChangeRecord, ProcessSpoutChangeRecord, \
    ProgramSpoutChangeRecord, SpoutChangeRecord
from LightApp.models import DebugLog


class IrrigationManager:
    def __init__(self, time=timezone.now()):
        self.time = time
        self.spouts = None

    """ 
    TODO:
    
    cancel program:
    add canceled program records
    add canceled to program records
    add runned_and_canceled in program records
    check for not canceled in spout condition program records
     
    """

    ###
    def record_process(self, process_button: ExternalButton, time=None, user=None,
                       status=ExternalButtonStatusRecord.STATUS.on, actor=ExternalButtonStatusRecord.UNKNOWN_ACTOR):
        if time is not None:
            self.time = time
        else:
            time = self.time = timezone.now()
        # start = self.time

        process_record = ExternalButtonStatusRecord.objects.create(
            status=status,
            process_button=process_button,
            time=time,
            actor=actor,
            user=user,
        )
        self.remove_older_records(process_record)

        self.create_process_spout_change_records(process_record)

        self.check_if_process_record_should_be_canceled(process_record)

    @staticmethod
    def check_if_process_record_should_be_canceled(process_record: ExternalButtonStatusRecord):
        common_spout_buttons = process_record.process_button.button_with_shared_spouts()
        for button in common_spout_buttons:
            future_records = ExternalButtonStatusRecord.objects.filter(
                process_button=button, canceled=False, time__gt=process_record.time
            ).exclude(id=process_record.id, status=ExternalButtonStatusRecord.STATUS.no_change)
            if future_records.count() > 0:
                if LOG_DEBUGS:
                    DebugLog.log('service: cancel process for future records', f'recordtime={process_record.time}, future_record_time:{future_records[0].time}')
                process_record.canceled = True
                process_record.finished = True
                process_record.canceled_by = future_records[0]
                process_record.save()
                return

    def create_process_spout_change_records(self, process_record):
        # if process_record.status != ExternalButtonStatusRecord.STATUS.no_change:
        if process_record.status is ExternalButtonStatusRecord.STATUS.on:
            # max_delay = process_record.process_button.events.aggregate(Max('duration'))['duration__max']
            # duration = process_record.process_button.duration
            # finish = start + duration
            spout_changes = ExternalButtonEventSpoutChange.objects.filter(
                external_button_event__external_button=process_record.process_button)
            if LOG_DEBUGS:
                DebugLog.log('service: recording spout record', f'')
            for process_spout_change in spout_changes:
                spout = process_spout_change.spout
                time = self.time + process_spout_change.external_button_event.delay

                record = ProcessSpoutChangeRecord.objects.create(
                    button_record=process_record,
                    spout=spout,
                    time=time,
                    start=self.time,
                    finish=process_record.end,
                    status=SpoutChangeRecord.STATUS.turn_on if process_spout_change.is_on else
                    SpoutChangeRecord.STATUS.turn_off,
                    change_spout = process_spout_change,
                )

    def remove_older_records(self, process_record: ExternalButtonStatusRecord):
        if process_record.status is not ExternalButtonStatusRecord.STATUS.no_change:
            buttons = process_record.process_button.button_with_shared_spouts()
            for button in buttons:
                to_terminate_process_records = ExternalButtonStatusRecord.objects.filter(
                    process_button=button, canceled=False, finished=False
                ).exclude(id=process_record.id)
                for record in to_terminate_process_records:
                    self.__cancel_record_with_newer(old_record=record, new_record=process_record)

    def __cancel_record_with_newer(self, old_record, new_record):
        if old_record.end > new_record.time >= old_record.time:
            old_record.canceled = True
            old_record.finished = True
            old_record.canceled_by = new_record
            old_record.save()
            if old_record.time > new_record.time:
                for spout_record in old_record.spout_records.filter(time__lte=new_record.time):
                    spout_record.execute_before_cancel = True
                    spout_record.save()
        else:
            old_record.finish = True
            old_record.save()

    def update_process(self, initial_record: ExternalButtonStatusRecord, time=None):
        if initial_record.canceled:
            return

        if time is not None:
            self.time = time
        start = self.time

        initial_record.time = self.time
        initial_record.save()

        self.update_process_change_spout_records(initial_record)

    def update_process_change_spout_records(self, initial_record: ExternalButtonStatusRecord):
        for record in initial_record.spout_records.all():
            record.start = self.time
            record.finish = initial_record.end
            try:
                record.time = record.change_spout.external_button_event.delay + self.time
            except AttributeError:
                pass
            record.save()

    def cancel_program_execute(self, program: ProgramGroup, time=None):
        if time is not None:
            self.time = time
        for record in ProgramSpoutChangeRecord.objects.filter(program_group=program, finish__gt=self.time):
            if record.canceled is False:
                record.canceled = True
                if record.time <= self.time:
                    record.execute_before_cancel = True
                record.save()

    def update_device_irrigation(self, device: Device, time=None) -> None:
        spouts = device.spouts.all()
        self.update_spouts_irrigation(spouts, time)

    def update_land_irrigation(self, land: Land, time=None) -> None:
        for device in land.devices.all():
            self.update_device_irrigation(device, time)

    def update_spouts_irrigation(self, spouts, time=None):
        if time is not None:
            self.time = time
        self.spouts = spouts
        self.__update_programs()
        self.__check_spouts_irrigation()

    def record_customer_spout_change(self, spout: Spout, is_on, unchanged=False, customer=None, time=None):
        if time is not None:
            self.time = time
        if not unchanged:
            customer_spout_change_record = CustomerSpoutChangeRecord.objects.create(
                spout=spout, time=self.time,
                status=SpoutChangeRecord.STATUS.turn_on if is_on else SpoutChangeRecord.STATUS.turn_off)
            if customer is not None:
                customer_spout_change_record.customer = customer
                customer_spout_change_record.save()

    def __update_programs(self):
        def update_program(program: ProgramGroup):
            time = timezone.now()
            while program.next_start <= time:
                record_program(program)
                has_repeat = program.repeatable
                program.next_start = program_next_cycle(program)
                if not has_repeat or program.passed:
                    break

        def record_program(program: ProgramGroup):
            change_spouts = ChangeSpout.objects.filter(sub_program__program_group=program)
            program_finish = program.next_start + SubProgram.objects.filter(program_group=program). \
                aggregate(Max('delay'))['delay__max']
            for change_spout in change_spouts:
                if change_spout.unchange:
                    continue
                change_spout_time = change_spout.sub_program.delay + program.next_start
                ProgramSpoutChangeRecord.objects.create(
                    program_group=program,
                    spout=change_spout.spout,
                    time=change_spout_time,
                    status=ProgramSpoutChangeRecord.STATUS.turn_on if change_spout.is_on else
                    ProgramSpoutChangeRecord.STATUS.turn_off,
                    start=program.next_start,
                    finish=program_finish
                )

        def program_next_cycle(program: ProgramGroup):
            if program.repeatable:
                program.last_start = program.next_start
                program.next_start += program.interval
            else:
                program.passed = True
            program.save()
            return program.next_start

        def get_spout_programs(spouts):
            array = []
            for spout in self.spouts:
                change_spouts = ChangeSpout.objects.filter(spout=spout)
                for change_spout in change_spouts:
                    if not change_spout.sub_program.program_group.passed:
                        array.append(change_spout.sub_program.program_group)
            return set(array)

        programs = get_spout_programs(self.spouts)
        for program in programs:
            update_program(program)

    def __check_spouts_irrigation(self):
        for spout in self.spouts:
            self.__check_spout_irrigation(spout)

    def __check_spout_irrigation(self, spout: Spout):
        # try:
        #     self.last_irrigation = SpoutLastIrrigation.objects.filter(spout=spout).order_by('-time')[0]
        # except (IndexError, SpoutLastIrrigation.DoesNotExist) as e:
        #     self.last_irrigation = SpoutLastIrrigation(spout=spout)
        # if self.last_irrigation.time is None or self.last_irrigation.time + IRRIGATION_UPDATE_DELAY <= self.time:
        #     self.__update_spout_irrigation(spout)
        #     self.last_irrigation.time = self.time
        #     self.last_irrigation.save()
        self.__update_spout_irrigation(spout)

    def __update_spout_irrigation(self, spout: Spout):

        def filter_queryset_to_spout_and_time(queryset):
            return queryset.filter(spout=spout, time__lte=timezone.now() + timedelta(seconds=1)) \
                .order_by('-time')

        def get_last_customer_spout_change():
            records = filter_queryset_to_spout_and_time(CustomerSpoutChangeRecord.objects.all())
            try:
                return records[0]
                # return {'status': records[0].status, 'time': records[0].time}
            except IndexError:
                return None

        def get_last_program_spout_change():
            records = filter_queryset_to_spout_and_time(ProgramSpoutChangeRecord.objects.filter(canceled=False))
            try:
                record = records[0]
                return record
                # return {
                #     'status': record.status,
                #     'time': record.time,
                #     'start': record.start
                # }
            except IndexError:
                return None

        def get_last_process_spout_change():
            records = filter_queryset_to_spout_and_time(ProcessSpoutChangeRecord.objects.filter(
                button_record__canceled=False, button_record__finished=False))
            # spout.process_records.set(records.all())
            try:
                record = records[0]
                return record
                # return {
                #     'status': record.status,
                #     'time': record.time,
                #     'start': record.start,
                #     'finish': record.finish,
                # }
            except IndexError:
                return None

        customer_record = get_last_customer_spout_change()
        program_record = get_last_program_spout_change()
        process_record = get_last_process_spout_change()
        
        # controller = spout.UNKNOWN_CONTROL
        if process_record is not None and (program_record is None or process_record.finish > program_record.start):
            if customer_record is None or process_record.time > customer_record.time:
                controller = Spout.PROCESS_CONTROL
                last_record = process_record
            else:
                controller = spout.USER_CONTROL
                last_record = customer_record
        else:
            if program_record is not None and (customer_record is None or program_record.time > customer_record.time):
                controller = spout.PROGRAM_CONTROL
                last_record = program_record
            else:
                if customer_record is not None:
                    controller = spout.USER_CONTROL
                    last_record = customer_record
                else:
                    controller = spout.OFF_NO_CONTROL
                    last_record = None

        spout_change = False
        if last_record is None or last_record.status != spout.isOn:
            if last_record is None or last_record.status is None:
                spout.isOn = spout.default_is_on_value
            else:
                spout.isOn = (last_record.status == SpoutChangeRecord.STATUS.turn_on)
            if spout.controller != controller:
                spout.controller = controller
            spout.last_record = last_record
            spout_change = True
        else:
            if spout.controller != controller:
                spout.controller = controller
                spout_change = True
            if last_record != spout.last_record:
                spout.last_record = last_record
                spout_change = True
        if spout_change:
            spout.save()
