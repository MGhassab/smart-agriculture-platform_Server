from django.test import TestCase
from django.urls import reverse

from Customer.models import Land, Spout, Device

from Device.models import ExternalButton, ExternalButtonEventSpoutChange, ExternalButtonEvent
from Device.device_types import get_device_type_by_code, device_types


class CreateDeviceSerialDefinerTestCase(TestCase):
    serial_begin = '12335351343535'

    def setUp(self) -> None:
        self.land = Land.testy_obj()
        # self.device = Device.testy_obj(land=self.land)
        # self.spouts = [
        #     Spout.testy_obj(number=1, device=self.device),
        #     Spout.testy_obj(number=2, device=self.device),
        # ]
        self.url = reverse('device:define_serial')

    def test_define_device_by_serial(self):
        for typeo in device_types:
            serial = self.serial_begin + typeo['code']
            response = self.client.post(path=self.url, data={'serial': serial}, )
            data = response.json()
            self.assertEqual(data, 'success', 'success reply')
            devices = Device.objects.filter(serial=serial)
            self.assertEqual(devices.count(), 1, 'check number of added devices')
            device = devices[0]
            spouts = Spout.objects.filter(device=device)
            self.assertEqual(spouts.count(), typeo['spouts'])
