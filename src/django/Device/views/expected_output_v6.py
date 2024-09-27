from datetime import datetime, timedelta, date
from django import views
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from Baghyar.conf.common import LOG_DEBUGS
from Customer.models import Spout, SpoutSensor, Land, Device, ProgramGroup, SubProgram
from Device.models import SpoutSensorRecord, ExternalButtonStatusRecord, ExternalButton, LogDeviceCheckOut
from Device.serializers import DeviceNetworkCoverageLogSerializer
from Irrigation.services import IrrigationManager
from LightApp.models import DebugLog


@method_decorator(csrf_exempt, name='dispatch')
class ExpectedOutputV6(views.View):
    time_format = '%d/%m/%y,%X'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data, self.land, self.device, self.has_response, self.feedback_time = None, None, None, None, None
        self.process_button_last_change_report = None
        self.process_buttons = None

    def post(self, request):
        update_time = timezone.now()
        self.data = json.loads(request.body)
        try:
            self.land = Land.objects.get(id=self.data.get('land'))
        except Land.DoesNotExist:
            raise ValidationError('invalid land')
        try:
            self.device = Device.objects.get(id=self.data.get('device'))
        except Device.DoesNotExist:
            raise ValidationError('invalid device')
        self.process_buttons = ExternalButton.objects.filter(device_id=self.device.id).order_by('number')

        # nc - network coverage - number
        self.log_network_coverage(request)
        # sc - spout conditions - 0/1 number of spouts
        self.update_spout_condition()
        # ebc_list - process button list - [{"n":1,"c":1,"lt":"12/23/12,12:12"}]
        if not self.check_and_update_process_button_status_list():
            # ebc - process button conditions - 0/1 number of external buttons
            self.update_process_button_status()
        # ebc_lc - process button last changes ["time", ...]

        # ft = feedback time
        self.get_feedback_time()
        has_response = (self.data.get('response') or self.data.get('response') == '1')
        response_str = 'ok'
        if has_response:
            # LogDeviceCheckOut.objects.create(device=self.device)
            outputs = self.get_spout_condition_strings()
            # has_program_change = ('1' if self.land.need_program_check else '0')
            has_program_change, last_program_change = self.check_program_update()
            modified_programs = self.get_modified_programs()
            external_button_has_activated = self.external_button_has_activated()
            process_button_change = self.process_button_change()
            response = {
                'd': {'o': outputs},
                'c': None,
                'p': has_program_change,
                'lp': last_program_change.strftime(self.time_format) if last_program_change else None,
                'cps': modified_programs,
                'ebc': external_button_has_activated,
                # 'ft': update_time.strftime(self.time_format),
                'pbc': [{'n': pbc['number'], 'c': '1' if pbc['has_changed'] else '0',
                         't': pbc['change_time'].strftime(self.time_format)} for pbc in process_button_change],
                'tn': self.device.type_number,
            }
            response_str = str(response).replace(" ", "").replace("'", '"')
        LogDeviceCheckOut.objects.create(
            device=self.device, device_message=json.dumps(self.data), response_message=response_str,
            get_updates=has_response)
        return HttpResponse(response_str)

    def check_program_update(self):
        program_groups = self.land.program_groups.all()
        last_program_change = self.device.last_modified_program
        for program_group in program_groups:
            if program_group.last_change_time and (last_program_change is None or last_program_change < program_group.last_change_time):
                last_program_change = program_group.modified
            for sub_program in program_group.programs.all():
                if sub_program.modified and (last_program_change is None or last_program_change < sub_program.modified):
                    last_program_change = sub_program.modified
                for spout_change in sub_program.spouts.all():
                    if spout_change.modified and (last_program_change is None or last_program_change < spout_change.modified):
                        last_program_change = spout_change.modified
        try:
            if last_program_change > self.feedback_time + timedelta(seconds=1):
                return '1', last_program_change
            else:
                return '0', last_program_change
        except TypeError:
            return '0', date.min

    def process_button_change(self):
        try:
            process_button_last_change_report = [datetime.strptime(time, self.time_format)
                                                 for time in self.data.get('ebc_lc')]
        except ValueError:
            return [{'change_time': process_button.last_change_time(), 'has_changed': True}
                    for process_button in self.process_buttons]
        array = []
        for report, process_button in zip(process_button_last_change_report, self.process_buttons):
            change_time = process_button.last_change_time()
            array.append({
                'change_time': change_time,
                'has_changed': report < change_time - timedelta(seconds=1),  # consider missing microseconds in report
                'number': process_button.number
            })
        return array

    def read_process_buttons_update_times(self):
        self.process_button_last_change_report = [datetime.strptime(time, self.time_format)
                                                  for time in self.data.get('ebc_lc')]

    def get_feedback_time(self):
        # try:
        self.feedback_time = datetime.strptime(self.data.get('ft'), self.time_format)
        # except TypeError:
        #     pass

    def log_network_coverage(self, request):
        network_coverage = self.data.get('nc')
        serializer = DeviceNetworkCoverageLogSerializer(data={
            'value': network_coverage,
            'land': self.land.id,
            'device': self.device.id,
            }, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def update_spout_condition(self):
        spout_conditions = extract_spouts_conditions(self.data)
        for spout in Spout.objects.filter(device=self.device):
            is_on = spout_conditions[spout.number]
            try:
                spout_sensor = SpoutSensor.objects.get(spout=spout)
                spout_sensor.isOn = is_on
            except SpoutSensor.DoesNotExist:
                spout_sensor = SpoutSensor(spout=spout, isOn=is_on)
                spout_sensor.save()
            SpoutSensorRecord.objects.create(spout=spout, is_on=is_on)
      
    def update_process_button_status(self):
        external_button_str = self.data.get('ebc')
        # try:
        manager = IrrigationManager()
        for eb_number, char in enumerate(external_button_str, start=1):
            status = ExternalButtonStatusRecord.input_to_status(char)
            if status is None:
                raise ValidationError('invalid process status format:'+char)
            external_button = ExternalButton.objects.get(device__land=self.land, number=eb_number)
            # process = ExternalButtonStatusRecord.objects.create(process_button=external_button, status=status)
            manager.record_process(
                process_button=external_button, status=status,
                actor=ExternalButtonStatusRecord.DEVICE_ACTOR
            )
        # except TypeError:
        #     raise ValidationError('missing ebc or wrong format')

    def check_and_update_process_button_status_list(self) -> bool:
        process_button_status_list = self.data.get('ebc_list')
        if process_button_status_list is None or len(process_button_status_list) == 0:
            return False
        manager = IrrigationManager()
        for i, process_button_status in enumerate(process_button_status_list):
            try:
                button = ExternalButton.objects.get(device=self.device, number=process_button_status['n'])
            except ExternalButton.DoesNotExist:
                raise ValidationError('invalid process button')

            if process_button_status['c'] is None:
                raise ValidationError(f'missing c for ebc_list {str(i)}th')

            try:
                status_input = process_button_status['c']
                status = ExternalButtonStatusRecord.input_to_status(status_input)
            except IndexError:
                raise ValidationError(f'invalid condition {process_button_status["c"]}')

            try:
                time = datetime.strptime(process_button_status['lt'], self.time_format)
            except ValueError:
                raise ValidationError(f'invalid datetime value for process')

            try:
                device_actor = (process_button_status['d'] == 1)  # TODO: check if has given else raise error
            except KeyError:
                raise ValidationError(f'enter "d" for ebc_list values')

            if status is not ExternalButtonStatusRecord.STATUS.no_change:
                if device_actor:
                    if LOG_DEBUGS:
                        DebugLog.log('eo6: record process device actor', f'button:{button.id}, status:{status}, time:{time}')
                    manager.record_process(
                        process_button=button, status=status, time=time,
                        actor=ExternalButtonStatusRecord.DEVICE_ACTOR
                    )
                    if LOG_DEBUGS:
                        DebugLog.log('eo6: end of record process')
                else:
                    try:
                        last_time_record = ExternalButtonStatusRecord.objects.filter(
                            process_button=button, time__lte=timezone.now()
                        ).order_by('-time')[0]
                        if LOG_DEBUGS:
                            DebugLog.log('eo6: check for updating last record', f'record:{last_time_record.id}.{last_time_record.status}_{last_time_record.time}_now:{timezone.now()}')
                        if time > last_time_record.time and status == last_time_record.status and \
                                last_time_record.actor != ExternalButtonStatusRecord.DEVICE_ACTOR:
                            if LOG_DEBUGS:
                                DebugLog.log('eo6: updating process')
                            manager.update_process(time=time, initial_record=last_time_record)
                    except IndexError:
                        if LOG_DEBUGS:
                            DebugLog.log('eo6: record initial device log', f'button:{button.id}, status:{status}, time:{time}')
                        manager.record_process(
                            process_button=button, status=status, time=time,
                            actor=ExternalButtonStatusRecord.INITIAL_ACTOR
                        )

                if (status == ExternalButtonStatusRecord.STATUS.on and not button.on_in_device) or \
                        (status == ExternalButtonStatusRecord.STATUS.off and button.on_in_device):
                    button.on_in_device = status_input
                    button.save()
        return True

    def get_spout_condition_strings(self):
        spouts = Spout.objects.filter(device__land=self.land).order_by('number')
        spout_sensor_records = SpoutSensorRecord.objects.filter(spout__device__land=self.land)
        external_button_records = ExternalButtonStatusRecord.objects.filter(process_button__device=self.device)
        programs = ProgramGroup.objects.filter(land=self.land)
        subprograms = SubProgram.objects.filter(program_group__land=self.land)
        condition_strings = ''
        # spouts = Spout.objects.filter(device__land=self.land).order_by('number')
        IrrigationManager().update_device_irrigation(self.device)  # .update_spouts_irrigation(spouts)
        spouts = Spout.objects.filter(device__land=self.land).order_by('number')
        for spout in spouts:
            condition_strings += '1' if spout.isOn else '0'
        return condition_strings
  
    def get_modified_programs(self):
        m_program_list = []
        changed_program_groups = ProgramGroup.objects.filter(land=self.land).filter(has_changes=True)
        for p_g in changed_program_groups:
            m_program_list.append(p_g.number1)
            m_program_list.append(p_g.number2)
        return m_program_list

    def external_button_has_activated(self):
        msg = ''
        for external_button in self.device.process_buttons.all().order_by('number'):
            try:
                record = external_button.records.filter(canceled=False, time__lte=timezone.now()) \
                    .exclude(status=ExternalButtonStatusRecord.STATUS.no_change).order_by('-time')[0]
                external_button_is_on = ((record.status == ExternalButtonStatusRecord.STATUS.on) and
                                         not record.has_finished())
            except (TypeError, IndexError) as e:
                external_button_is_on = False
            msg += '1' if external_button_is_on else '0'
        return msg


def extract_spouts_conditions(data):
    spouts_str = data.get('sc')
    spout_conditions = {}
    spout_number = 1
    for c in spouts_str:
        spout_conditions[spout_number] = (c == '1')
        spout_number += 1
    return spout_conditions
