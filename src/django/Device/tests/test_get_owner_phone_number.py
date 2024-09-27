import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

from Customer.models import Customer, Land

from Device.views import GetOwnerPhoneNumber


class GetOwnerPhoneNumberTestCase(TestCase):
    url_name = 'device:get-owner-phone'

    def test_get_owner_phone_number(self):
        user = User.objects.create_user(username='testy_user_unique', password='testy_password_123_!')
        cusomer = Customer.get_or_create(user)
        user_owner = User.objects.create_user(username='testy_owner_phone', password='testy_password_123_!')
        customer_owner = Customer.get_or_create(user_owner)
        land = Land.objects.create(**Land.test_values())
        land.customers.add(cusomer)
        land.owner = customer_owner
        land.save()
        factory = APIRequestFactory()
        url = reverse(self.url_name, kwargs={'land_id': land.id})
        self.request = factory.post(url, format='json')
        view = GetOwnerPhoneNumber.as_view()
        response = view(self.request, land_id=land.id)
        self.assertEqual(user_owner.username, response.data['phone'], 'check valid phone number')

