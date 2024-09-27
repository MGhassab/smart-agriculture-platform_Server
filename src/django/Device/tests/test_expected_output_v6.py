from datetime import time, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from Customer.models import Land, Device, Spout, ProgramGroup, SubProgram, ChangeSpout

from Device.models import ExternalButton, ExternalButtonEvent, ExternalButtonEventSpoutChange, \
    ExternalButtonStatusRecord, DeviceNetworkCoverageLog, SpoutSensorRecord
from Device.views import ExpectedOutputV6


class EO6TestCase(TestCase):
    network_coverage = 15
    spout_ons = [False, True]
    ebc_conditions = '12'
    url = reverse('device:expected-output-V6')

    def __init(self):
        pass
        # self.network_coverage = 15

    def setUp(self) -> None:
        self.land = Land.objects.create(**Land.test_values())
        self.device = Device.objects.create(**Device.test_values(land=self.land))
        self.spouts = [
            Spout.objects.create(**Spout.test_values(number=1, device=self.device)),
            Spout.objects.create(**Spout.test_values(number=2, device=self.device)),
        ]
        self.program_groups = [
            ProgramGroup.objects.create(**ProgramGroup.test_values(land=self.land)),
        ]
        self.sub_programs = [
            SubProgram.objects.create(**SubProgram.test_values(program_group=self.program_groups[0])),
            SubProgram.objects.create(
                **SubProgram.test_values(program_group=self.program_groups[0], number=2, delay=timedelta(hours=1)),
            ),
        ]
        self.change_spouts = [
            ChangeSpout.objects.create(
                **ChangeSpout.test_values(
                    spout=self.spouts[0],
                    sub_program=self.sub_programs[0],
                    is_on=True,
                    un_change=False,)),
            ChangeSpout.objects.create(
                **ChangeSpout.test_values(
                    spout=self.spouts[1],
                    sub_program=self.sub_programs[0],
                    is_on=True,
                    un_change=True,)),
            ChangeSpout.objects.create(
                **ChangeSpout.test_values(
                    spout=self.spouts[0],
                    sub_program=self.sub_programs[1],
                    is_on=False,
                    un_change=False,)),
            ChangeSpout.objects.create(
                **ChangeSpout.test_values(
                    spout=self.spouts[1],
                    sub_program=self.sub_programs[1],
                    is_on=False,
                    un_change=True,)),
        ]
        self.process_buttons = [
            ExternalButton.objects.create(**ExternalButton.test_values(device=self.device, number=1)),
            ExternalButton.objects.create(**ExternalButton.test_values(device=self.device, number=2)),
        ]
        self.process_events = [
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                process_button=self.process_buttons[0], delay=timedelta(hours=0), priority=1)),
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                process_button=self.process_buttons[0], delay=timedelta(hours=1), priority=2)),
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                process_button=self.process_buttons[1], delay=timedelta(hours=0), priority=1)),
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                process_button=self.process_buttons[1], delay=timedelta(hours=1), priority=2)),
        ]
        self.process_spout_changes = [
            ExternalButtonEventSpoutChange.objects.create(**ExternalButtonEventSpoutChange.test_values(
                external_button_event=self.process_events[0], spout=self.spouts[0], is_on=True)),
            ExternalButtonEventSpoutChange.objects.create(**ExternalButtonEventSpoutChange.test_values(
                external_button_event=self.process_events[0], spout=self.spouts[1], is_on=True)),
            ExternalButtonEventSpoutChange.objects.create(**ExternalButtonEventSpoutChange.test_values(
                external_button_event=self.process_events[1], spout=self.spouts[0], is_on=False)),
            ExternalButtonEventSpoutChange.objects.create(**ExternalButtonEventSpoutChange.test_values(
                external_button_event=self.process_events[1], spout=self.spouts[1], is_on=False)),
            ExternalButtonEventSpoutChange.objects.create(**ExternalButtonEventSpoutChange.test_values(
                external_button_event=self.process_events[2], spout=self.spouts[0], is_on=True)),
            ExternalButtonEventSpoutChange.objects.create(**ExternalButtonEventSpoutChange.test_values(
                external_button_event=self.process_events[2], spout=self.spouts[1], is_on=False)),
            ExternalButtonEventSpoutChange.objects.create(**ExternalButtonEventSpoutChange.test_values(
                external_button_event=self.process_events[3], spout=self.spouts[0], is_on=False)),
            ExternalButtonEventSpoutChange.objects.create(**ExternalButtonEventSpoutChange.test_values(
                external_button_event=self.process_events[3], spout=self.spouts[1], is_on=True)),
        ]

        factory = APIRequestFactory()
        self.request = factory.post(self.url, {
            "land": self.land.id,
            "device": self.device.id,
            "sc": str(int(self.spout_ons[0])) + str(int(self.spout_ons[1])),
            "nc": self.network_coverage,
            "ebc": self.ebc_conditions,
            # "ebc_list": [{"n": 1, "c": 2, "lt": "12/23/12,14:12:59"}, {"n": 2, "c": 2, "lt": "12/23/12,14:12:59"}],
            "has_response": True
        }, format='json')

        view = ExpectedOutputV6.as_view()
        self.response = view(self.request)

    def test_read_data(self):
        def test_network_log():
            query = DeviceNetworkCoverageLog.objects.filter(land=self.land, device=self.device)
            self.assertEqual(query.count(), 1, 'checking single network coverage log')
            log = query[0]
            self.assertEqual(self.network_coverage, log.value, 'checking network coverage value')

        def test_spout_log():
            for [i, spout], spout_is_on in zip(enumerate(self.spouts), self.spout_ons):
                record = SpoutSensorRecord.objects.filter(spout=spout)[0]
                self.assertEqual(record.is_on, spout_is_on)

        def test_process_button_status_records():
            for i, process_button in enumerate(self.process_buttons):
                query = ExternalButtonStatusRecord.objects.filter(process_button=process_button)
                self.assertEqual(query.count(), 1, 'checking process records counts')
                status = ExternalButtonStatusRecord.input_to_status(self.ebc_conditions[i])
                self.assertEqual(status, query[0].status, 'check status_value')

        test_network_log()
        test_spout_log()
        test_process_button_status_records()
        # print(self.response)
        # print(vars(self.response))
        # print(f'response={self.response.content}')

    def test_returned_data(self):
        self.assertEqual(
            b'{"d":{"o":"11"},"c":None,"p":"1","lp":"15/07/21,16:50:28","cps":[],"ebc":"00"}'[:31] + \
            b'{"d":{"o":"11"},"c":None,"p":"1","lp":"15/07/21,16:50:28","cps":[],"ebc":"00"}'[-20:],
            self.response.content[:31] + self.response.content[-20:],
            'check with stored response part 1',
        )
