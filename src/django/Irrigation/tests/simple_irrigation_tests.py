from django.test import TestCase
from django.utils import timezone
import datetime
from datetime import timedelta

from Customer.models import Land, Spout, ProgramGroup, SubProgram, ChangeSpout, Device
from Device.models import ExternalButton, ExternalButtonEvent, ExternalButtonEventSpoutChange, \
    ExternalButtonStatusRecord

from Irrigation.services import IrrigationManager
from Irrigation.models import CustomerSpoutChangeRecord


def create_land_spout_for_test():
    land = Land.objects.create(**Land.test_values())
    device = Device.objects.create(**Device.test_values(land=land, serial='123456'))
    spout1 = Spout.objects.create(**Spout.test_values(1, device))
    spout2 = Spout.objects.create(**Spout.test_values(2, device))
    return land, device, spout1, spout2


def create_program_group_for_test(land: Land, spout1: Spout, spout2: Spout, time: datetime = timezone.now()):
    program_group = ProgramGroup.objects.create(**ProgramGroup.test_values(land=land, start=time))
    sub_program1 = SubProgram.objects.create(**SubProgram.test_values(
        program_group=program_group, delay=timedelta()))
    sub_program2 = SubProgram.objects.create(**SubProgram.test_values(
        program_group=program_group, delay=timedelta(hours=1), number=2))
    spout_change1_1 = ChangeSpout.objects.create(**ChangeSpout.test_values(spout=spout1, sub_program=sub_program1))
    spout_change1_2 = ChangeSpout.objects.create(**ChangeSpout.test_values(spout=spout2, sub_program=sub_program1,
                                                                           is_on=True))
    spout_change2_1 = ChangeSpout.objects.create(**ChangeSpout.test_values(spout=spout1, sub_program=sub_program2))
    spout_change2_2 = ChangeSpout.objects.create(**ChangeSpout.test_values(spout=spout2, sub_program=sub_program2,
                                                                           is_on=False))
    return program_group, sub_program1, sub_program2, spout_change1_1, spout_change1_2, spout_change2_1, spout_change2_2


class IrrigationTestCase(TestCase):
    def setUp(self):
        self.time = timezone.now()
        land, device, spout1, spout2 = create_land_spout_for_test()

    def test_recording_customer_spout_change(self):
        # land = Land.objects.get(name=Land.test_values()['name'])
        spout1 = Spout.objects.get(name=Spout.test_values(1)['name'])
        spout2 = Spout.objects.get(name=Spout.test_values(2)['name'])
        self.assertEqual(spout1.isOn, False, 'Initial test')
        delta = datetime.timedelta(seconds=3)
        manager = IrrigationManager(self.time)
        manager.record_customer_spout_change(spout1, is_on=True)
        manager.update_spouts_irrigation([spout1, spout2])
        spout1 = Spout.objects.get(name=Spout.test_values(1)['name'])
        self.assertEqual(spout1.isOn, True, 'test recording customer spout change to True')
        manager.record_customer_spout_change(spout1, is_on=False, time=self.time+delta)
        manager.update_spouts_irrigation([spout1, spout2])
        self.assertEqual(spout1.isOn, False, 'test recording customer spout change to False')


class IrrigationProgramTestCase(TestCase):
    def setUp(self):
        self.time = timezone.now() + timedelta(hours=1)
        land, self.device, self.spout1, self.spout2 = create_land_spout_for_test()
        self.program_group, sub_program1, sub_program2, spout_change1_1, spout_change1_2, spout_change2_1\
            , spout_change2_2 = create_program_group_for_test(land, self.spout1, self.spout2, self.time)

    def test_recording_program(self):
        spout1 = Spout.objects.get(id=self.spout1.id)
        spout2 = Spout.objects.get(id=self.spout2.id)
        manager = IrrigationManager(self.time)
        manager.update_spouts_irrigation([spout1, spout2])
        spout1 = Spout.objects.get(id=self.spout1.id)
        spout2 = Spout.objects.get(id=self.spout2.id)
        self.assertEqual(spout1.isOn, False, 'test program start spout stay to False')
        self.assertEqual(spout2.isOn, True, 'test program start spout change to True')
        manager.update_spouts_irrigation([spout1, spout2], time=self.time + timedelta(hours=2))
        self.assertEqual(spout1.isOn, False, 'test program end spout stay to False')
        self.assertEqual(spout2.isOn, False, 'test program end spout change to False')

    def test_program_repeat(self):
        program_group = ProgramGroup.objects.get(id=self.program_group.id)
        program_group.start = self.time + timedelta(days=1)
        program_group.repeatable = True
        program_group.passed = False
        program_group.save()
        spout1 = Spout.objects.get(id=self.spout1.id)
        spout2 = Spout.objects.get(id=self.spout2.id)
        manager = IrrigationManager(self.time + timedelta(days=1))
        manager.update_spouts_irrigation([spout1, spout2])
        spout1 = Spout.objects.get(id=spout1.id)
        spout2 = Spout.objects.get(id=spout2.id)
        self.assertEqual(spout1.isOn, False, 'test program repeat start spout stay to False')
        self.assertEqual(spout2.isOn, True, 'test program repeat start spout change to True')

    def test_program_not_repeat(self):
        program_group = ProgramGroup.objects.get(id=self.program_group.id)
        program_group.start = self.time + timedelta(days=2)
        program_group.repeatable = False
        program_group.passed = False
        program_group.save()
        spout2 = Spout.objects.get(id=self.spout2.id)
        manager = IrrigationManager(self.time + timedelta(days=2))
        manager.update_spouts_irrigation([
            spout2,
        ])
        spout2 = Spout.objects.get(id=self.spout2.id)
        self.assertEqual(spout2.isOn, True, 'test program not_repeat start spout not setting to True')


class IrrigationProgramCancelTestCase(TestCase):
    def setUp(self):
        self.time = timezone.now() + timedelta(hours=1)
        land, self.device, self.spout1, self.spout2 = create_land_spout_for_test()
        self.program_group, sub_program1, sub_program2, spout_change1_1, spout_change1_2, spout_change2_1\
            , spout_change2_2 = create_program_group_for_test(land, self.spout1, self.spout2, self.time)

    def test_cancel_program(self):
        spout2 = Spout.objects.get(id=self.spout2.id)
        manager = IrrigationManager(self.time)
        manager.update_spouts_irrigation([spout2])
        manager.cancel_program_execute(self.program_group)
        manager.update_spouts_irrigation([spout2])
        spout2 = Spout.objects.get(id=self.spout2.id)
        self.assertEqual(spout2.isOn, False, 'test program cancel')


class IrrigationProcessTestCase(TestCase):
    def setUp(self):
        self.time = timezone.now() + timedelta(days=2, hours=3)
        self.periods = [timedelta(), timedelta(hours=1), timedelta(hours=2)]
        land, self.device, spout1, spout2 = create_land_spout_for_test()
        self.spouts = [spout1, spout2]
        # program_group, sub_program1, sub_program2, spout_change1_1, spout_change1_2, spout_change2_1, spout_change2_2 \
        #     = create_program_group_for_test(land, spout1, spout2)
        device = Device.objects.create(**Device.test_values(land=land, serial='1234'))
        self.process_button = ExternalButton.objects.create(**ExternalButton.test_values(device, 1))
        self.process_button_events = [
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                self.process_button, self.periods[0], 1
            )),
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                self.process_button, self.periods[1], 1
            )),
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                self.process_button, self.periods[2], 1
            ))
        ]
        self.process_spout_change = []
        turn_index = 0
        self.turns = [False, True]  # +None
        for process_button_event in self.process_button_events:
            for spout in self.spouts:
                turn = self.turns[turn_index % len(self.turns)]
                turn_index += 1
                if turn is not None:
                    self.process_spout_change.append(ExternalButtonEventSpoutChange.objects.create(
                        **ExternalButtonEventSpoutChange.test_values(
                            process_button_event,
                            spout,
                            turn,
                        )))

    def test_running_process(self):
        spouts_condition = [False for spout in self.spouts]
        turn_index = 0
        manager = IrrigationManager(self.time)
        manager.record_process(self.process_button)

        updating_spouts = [Spout.objects.get(id=spout.id) for spout in self.spouts]

        for process_button_event in self.process_button_events:
            manager.update_spouts_irrigation(spouts=updating_spouts, time=self.time + process_button_event.delay)
            for i, spout in enumerate(self.spouts):
                turn = self.turns[turn_index % len(self.turns)]
                turn_index += 1
                spout_updated = Spout.objects.get(id=spout.id)
                if turn:
                    spouts_condition[i] = True
                if not turn:
                    spouts_condition[i] = False
                    spout_updated.save()
                self.assertEqual(
                    Spout.objects.get(id=spout.id).isOn,
                    spouts_condition[i],
                    'check spout change for process event'
                )


class IrrigationProcessCancelTestCase(TestCase):
    def setUp(self):
        self.time = timezone.now() + timedelta()
        self.periods = [timedelta(), timedelta(hours=1), timedelta(hours=2)]
        self.land, self.device, spout1, spout2 = create_land_spout_for_test()
        self.spouts = [spout1, spout2]
        # program_group, sub_program1, sub_program2, spout_change1_1, spout_change1_2, spout_change2_1, spout_change2_2 \
        #     = create_program_group_for_test(land, spout1, spout2)
        device = Device.objects.create(**Device.test_values(land=self.land, serial='1234'))
        self.process_button = ExternalButton.objects.create(**ExternalButton.test_values(device, 1))
        self.process_button_events = [
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                self.process_button, self.periods[0], 1
            )),
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                self.process_button, self.periods[1], 1
            )),
            ExternalButtonEvent.objects.create(**ExternalButtonEvent.test_values(
                self.process_button, self.periods[2], 1
            ))
        ]
        self.process_spout_change = []
        turn_index = 0
        self.turns = [False, True]  # +None
        for process_button_event in self.process_button_events:
            for spout in self.spouts:
                turn = self.turns[turn_index % len(self.turns)]
                turn_index += 1
                if turn is not None:
                    self.process_spout_change.append(ExternalButtonEventSpoutChange.objects.create(
                        **ExternalButtonEventSpoutChange.test_values(
                            process_button_event,
                            spout,
                            turn,
                        )))

    def test_cancel_running_process(self):
        spouts_condition = [False for spout in self.spouts]
        turn_index = 0
        manager = IrrigationManager(self.time)

        manager.record_process(self.process_button)
        updating_spouts = [Spout.objects.get(id=spout.id) for spout in self.spouts]

        manager.record_process(self.process_button, status=ExternalButtonStatusRecord.STATUS.off)

        for process_button_event in self.process_button_events:
            manager.update_land_irrigation(land=self.land, time=self.time + process_button_event.delay)
            for i, spout in enumerate(self.spouts):
                turn = self.turns[turn_index % len(self.turns)]
                turn_index += 1
                spout_updated = Spout.objects.get(id=spout.id)
                if turn:
                    spouts_condition[i] = True
                if not turn:
                    spouts_condition[i] = False
                    spout_updated.save()
                self.assertEqual(
                    Spout.objects.get(id=spout.id).isOn,
                    False,
                    'check spout unchange for process cancel'
                )

