from kavenegar import *
import urllib.parse
from .models import SMSLog
# import asyncio


api_key = '7561424D583378446373356F6470474A363978533273515478796D4D4E76642F786B7258354663327043553D'
default_sender = '0018018949161'


def send_sms(to, template, context):
    # print(f'sms=> to:{to}, template:{template}, context:{context}')
    sender = default_sender
    receiver = to
    SMSLog(msg=context, sender=sender, receiver=receiver).save()
    api = KavenegarAPI(api_key)
    params = {
        'sender': sender,
        'receptor': receiver,
        'message': context,
    }

    def sms_send(api, params):
        try:
            api.sms_send(params)
        except APIException as e:
            pass

        except HTTPException as e:
            pass
    sms_send(api, params)
    # asyncio.create_task(sms_send(api, params))


def send_otp(to, template, context, token):
    receiver = to
    SMSLog(msg=context, receiver=receiver).save()
    api = KavenegarAPI(api_key)
    params = {
        'receptor': receiver,
        'template': 'Verify',
        'token': token,
        'type': 'sms',
    }

    def sms_otp(api, params):
        try:
            api.verify_lookup(params)
        except APIException as e:
            pass

        except HTTPException as e:
            pass
    sms_otp(api, params)
    # asyncio.create_task(sms_otp(api, params))
