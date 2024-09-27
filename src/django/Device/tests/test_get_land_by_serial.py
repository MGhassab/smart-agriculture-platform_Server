from django.test import TestCase
from django.urls import reverse

from Customer.models import Land, Device


class GetLandBySerialTestCase(TestCase):
    voucher_serial = '2425rdg3535'
    url = reverse('device:land-by-serial')

    def setUp(self) -> None:
        self.land = Land.objects.create(**Land.test_values())
        self.land_serial = Land.test_values()['serial']
        self.device = Device.objects.create(**Device.test_values(land=self.land))
        self.land_serial = Device.test_values(land=self.land)['serial']

    def send_request(self, serial):
        return self.client.post(path=self.url, data={'serial': serial, })

    def test_get_land_by_land_serial(self):
        response = self.send_request(self.land_serial)
        self.assertEqual(self.land.id, response.json()['land'], 'check land id')

    def test_get_land_by_device_serial(self):
        response = self.send_request(self.land_serial)
        self.assertEqual(self.device.land.id, response.json()['land'])
        self.assertEqual(self.device.id, response.json()['device'])
