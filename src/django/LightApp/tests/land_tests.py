from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory

from Customer.models import Land, Device, Spout
from LightApp.views import register_land_and_device


class UserRegisterLandTestCase(TestCase):
    testy_serial_value = '232436342435635'
    testy_username = 'testy_username'
    testy_password = 'testy_password!123'
    testy_land_name = 'testy_land_name'
    url = reverse('light_app:register-land-and-device')
    land_name = 'testy_land'
    device_name = 'testy_device'
    expected_response = {'land': {'id': 1, 'name': 'testy_land', 'location': None, 'area': 1,
                         'is_connected': False, 'is_owner': True, 'sensors': {}, 'spouts': []},
                         'device': {'id': 1, 'name': 'testy_device'}
                         }

    def setUp(self) -> None:
        user = User.objects.create_user(username=self.testy_username, password=self.testy_password)
        self.token = 'Token ' + str(Token.objects.get_or_create(user=user)[0])
        device = Device.testy_obj(land=None, serial=self.testy_serial_value)
        device.name = None
        device.save()

    def test_register_land_and_device(self):
        headers = {
            'Authorization': self.token,
            'Token': self.token,
        }
        response = self.client.post(path=self.url, data={
            'serial': self.testy_serial_value,
            'land': self.land_name,
            'device': self.device_name,
            'Authorization': self.token,
        }, **headers)
        data = response.json()
        # print(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, self.expected_response)

    # def test_register_land_and_device_2(self):
    #     headers = {
    #         'Authorization': self.token,
    #         'Token': self.token,
    #     }
    #     factory = APIRequestFactory()
    #     request = factory.post(self.url, {
    #         'serial': self.testy_serial_value,
    #         'land': self.land_name,
    #         'device': self.device_name,
    #     }, format='json', **headers)
    #     view = register_land_and_device
    #     response = view(request)
    #     print(f'response={response}')
    #     print(vars(response))
    #     print(repr(response))


class ProgramTestCase(TestCase):
    url = reverse('light_app:program-group')
    # url_id = reverse('light_app:program-group-id')

    def setUp(self) -> None:
        self.land = Land.testy_obj()
        self.device = Device.testy_obj(land=self.land)
        self.spouts = [
            Spout.testy_obj(device=self.device, number=1),
            Spout.testy_obj(device=self.device, number=2),
        ]
        # user = User.objects.create_user(username=self.testy_username, password=self.testy_password)
        # self.token = 'Token ' + str(Token.objects.get_or_create(user=user)[0])

    def test_add_program(self):
        # headers = {
        #     'Authorization':
        # }
        self.client.post(
            path=self.url,
            data={

            },

        )

    def test_get_program(self):
        pass

    def test_put_program(self):
        pass

    def test_delete_program(self):
        pass

