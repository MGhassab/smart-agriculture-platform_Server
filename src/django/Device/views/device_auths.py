from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from Customer.models import Land, Device, Spout

from Device.device_types import device_types, get_device_type_by_code, create_device


@api_view(['Post'])
def get_land_by_serial(request):
    serial_value = request.data.get('serial')
    if not serial_value:
        msg = 'enter serial'
        raise ValidationError(msg, code='validation')
    lands = Land.objects.filter(serial=serial_value)
    if lands.count() > 0:
        land = lands.first()
        attr = {
            'land': land.id
        }
    else:
        devices = Device.objects.filter(serial=serial_value)
        if devices.count() > 0:
            device = devices.first()
            land = device.land
            attr = {
                'land': land.id,
                'device': device.id,
            }
        else:
            # l = Land.objects.all().first()
            # return Response(f'serial={l}, asked={serial_value}')
            msg = 'invalid serial'
            raise ValidationError(msg, code='validation')
    return Response(attr)


@api_view(['Post'])
def register_device_serial(request):
    serial = request.data.get('serial')
    try:
        device = create_device(serial=serial)
    # except TypeError:
    #     raise ValidationError('invalid serial string')
    except NotImplementedError:
        raise ValidationError('invalid serial')
    return Response({'device': device.id})


@api_view(['Post'])
def temp_api(request):
    return Response({"d":{"o":"01"},"c":None,"p":"0","lp":"29/07/21,18:23:56","cps":[],"ebc":"00","pbc":[{"n":1,"c":True,"t":"29/07/21,17:02:53"},{"n":2,"c":True,"t":"28/07/21,18:29:53"}],"tn":1})
