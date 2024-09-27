from django.http import JsonResponse
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from Baghyar.views import get_validated_obj
from Customer.models import Land, ProgramGroup, SubProgram, ChangeSpout, Spout, Device
from Device.models import ExternalButton
from Irrigation.services import IrrigationManager

from Device.serializers import SubProgramSerializer


# @api_view(['Post'])
# def read_program(request):
#     number = request.data.get('number')
#     if number is None:
#         return Response({"response": "enter program 'number'"}, status.HTTP_400_BAD_REQUEST)
#     land = get_validated_obj(request=request, cls=Land, obj_name='land')
#     programs = Program.objects.filter(number=number, land=land)
#     if programs.exists():
#         serializer = ProgramLiteSerializer(programs.first())
#         return Response(serializer.data)
#     return Response({"response": "program don't exists"}, status.HTTP_400_BAD_REQUEST)


# @api_view(['Post'])
# def get_programs(request):
#     programs = []
#     # land = get_validated_obj(request=request, obj_name='land', cls=Land)
#     try:
#         land_id = request.data.get('land')
#         if land_id:
#             land = Land.objects.get(id=land_id)
#         else:
#             device_id = request.data.get('device')
#             device = Device.objects.get(id=device_id)
#             land = device.land
#     except():
#         raise ValidationError('invalid land or device')
#
#     right_now = timezone.now()
#     manager = IrrigationManager(right_now)
#     manager.update_land_irrigation(land)
#     sub_programs = SubProgram.objects.filter(program_group__land=land)
#     for sub_program in sub_programs:
#         start = sub_program.start
#         # while sub_program.program_group.repeatable and start < right_now:
#         #     start += sub_program.program_group.interval
#         if start >= right_now:
#             serializer = SubProgramSerializer(sub_program)
#             serializer.data['start'] = start
#             programs.append(serializer.data)
#
#     land.checked()
#     return Response(programs)


@api_view(['Post'])
def get_device_programs(request):
    device = Device.objects.get(id=request.data.get('device'))
    manager = IrrigationManager()
    manager.update_device_irrigation(device)
    # TODO: set get program_groups for device
    # sub_programs = SubProgram.objects.filter(program_group__land=device.land)
    data_list = list([
        SubProgramSerializer(sub_program).data
        for sub_program in SubProgram.objects.filter(program_group__land=device.land)
    ])
    for program_group in ProgramGroup.objects.filter(land=device.land):
        program_group.set_synced(True)
    return Response(data_list)


def device_process_view(request, device_id):
    device = Device.objects.get(id=device_id)
    buttons = ExternalButton.objects.filter(device=device).order_by('number')
    spouts = Spout.objects.filter(device=device).order_by('number')
    response = []
    for button in buttons:
        events = button.events.order_by('delay')
        events_response = []
        last_delay = None
        last_spout_responses = ""
        for event in events:
            spout_conditions = ["2" for spout in spouts]
            for change_spout in event.spout_changes.order_by('spout__number'):
                spout_index = change_spout.spout.number - 1
                spout_conditions[spout_index] = '1' if change_spout.is_on else '0'
            spout_responses = ''.join(spout_conditions)
            if last_delay is not None:
                events_response.append({
                    'delay': event.delay.total_seconds(),
                    'spouts': last_spout_responses
                })
            last_delay = event.delay
            last_spout_responses = spout_responses
        response.append({
            'number': button.number,
            'events': events_response,
            'events_count': len(events_response)
        })
    return JsonResponse(response, safe=False)
