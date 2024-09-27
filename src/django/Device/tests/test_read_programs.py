from datetime import time, timedelta
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
import pytz

from Baghyar.settings import TIME_ZONE
from Customer.models import Land, Device, Spout, ProgramGroup, SubProgram, ChangeSpout


class ReadPrograms(TestCase):
    def setUp(self) -> None:
        self.time = timezone.now() + timedelta(hours=3)
        self.land = Land.testy_obj()
        self.device = Device.testy_obj(land=self.land)
        self.spouts = [
            Spout.testy_obj(number=1, device=self.device),
            Spout.testy_obj(number=2, device=self.device),
        ]
        self.program_groups = [
            ProgramGroup.testy_obj(land=self.land, start=self.time + timedelta(hours=1))
        ]
        self.sub_programs = [
            SubProgram.testy_obj(program_group=self.program_groups[0], number=1, delay=timedelta()),
            SubProgram.testy_obj(program_group=self.program_groups[0], number=2, delay=timedelta(hours=1)),
        ]
        self.change_programs = [
            ChangeSpout.testy_obj(spout=self.spouts[0], sub_program=self.sub_programs[0], is_on=True),
            ChangeSpout.testy_obj(spout=self.spouts[1], sub_program=self.sub_programs[0], is_on=False),
            ChangeSpout.testy_obj(spout=self.spouts[0], sub_program=self.sub_programs[1], is_on=False),
            ChangeSpout.testy_obj(spout=self.spouts[1], sub_program=self.sub_programs[1], is_on=True),
        ]

    def local_time(self):
        local_timezone = pytz.timezone(TIME_ZONE)
        local_time = self.time.astimezone(local_timezone)
        local_time += timedelta(hours=1)  # don't know why :(
        return local_time

    def test_read_programs(self):
        url = reverse('device:get-programs')
        response = self.client.post(url, {'land': self.land.id})
        data = response.json()
        self.assertEqual(len(data), 2, 'test number of programs')
        self.assertEqual(data[0]['action'], '10', 'test read program output')
        self.assertEqual(data[1]['action'], '01', 'test read program output')
        self.assertEqual(data[0]['start'], self.local_time().strftime('%Y/%m/%d,%H:%M:%S'))

    def test_read_device_programs(self):
        url = reverse('device:get-device-programs')
        response = self.client.post(url, {'device': self.device.id})
        data = response.json()
        self.assertEqual(len(data), 2, 'test number of programs')
        self.assertEqual(data[0]['action'], '10', 'test read program output')
        self.assertEqual(data[1]['action'], '01', 'test read program output')
        self.assertEqual(data[0]['start'], self.local_time().strftime('%Y/%m/%d,%H:%M:%S'))
