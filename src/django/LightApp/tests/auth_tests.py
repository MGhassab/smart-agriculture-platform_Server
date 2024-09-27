from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from Customer.models import Customer
from LightApp.models import Verification


class SMSLoginTestCase(TestCase):
    def setUp(self) -> None:
        pass

    def test_send_failed_sms(self):
        url = reverse('light_app:get-verification')
        response = self.client.post(url, data={'username': '091964392234'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'check wrong phone number error response')

    def test_authorize_with_token(self):
        user = User.objects.create_user(username='testy_user', password='testy_user_pass12!')
        customer = Customer.get_or_create(user = user)
        verification = Verification.objects.create(customer=customer, send_sms=False)
        url = reverse('light_app:verify-user-v2')
        response = self.client.post(url, data={'username': 'testy_user', 'code': verification.code})
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'test verify code')
        response = self.client.post(url, data={'username': 'testy_user', 'code': 12345})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'test verify wrong code')
        response = self.client.post(url, data={'username': 'wrong_user_name', 'code': verification.code})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'test verify wrong username')
        verification.expire = timezone.now() - timedelta(hours=1)
        verification.save()
        response = self.client.post(url, data={'username': 'wrong_user_name', 'code': verification.code})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'test verify out dated serial')
