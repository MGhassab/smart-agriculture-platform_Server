from django.urls import path, include
from . import views
from Customer import views as customer_views


app_name = 'device'
urlpatterns = [
    # expected output 1 - 5
    # path(
    #     '<int:land_id>/eo/',
    #     views.ExpectedOutput.as_view(),
    #     name='device expected outputs'
    # ),
    # path(
    #     '<int:land_id>/eo2/',
    #     views.expected_outputV2,
    #     name='device expected outputs V2'
    # ),
    # path(
    #     '<int:land_id>/eo3/',
    #     views.expected_outputV3,
    #     name='device expected outputs V3'
    # ),
    # path(
    #     '<int:land_id>/<int:device_id>/eo4/',
    #     views.expected_outputV3,
    #     name='device expected outputs V4'
    # ),
    # path(
    #     '<int:land_id>/<int:device_id>/eo5/',
    #     views.expected_outputV5,
    #     name='device expected outputs V5'
    # ),
    path(
        'eo6/',
        views.ExpectedOutputV6.as_view(),
        name='expected-output-V6'
    ),
    # set_condition - update conditions without replying expected output
    # path(
    #     '<int:device_id>/<int:land_id>/set_condition/',
    #     views.update_condition_view,
    #     name='update spout condition view'
    # ),
    # receive device serial, take lank id
    # path(
    #     'serial_land/'
    #     , views.get_land_by_serial,
    #     name='get device land by device serial',
    # ),
    # CheckLand - check land has new program
    # path(
    #     '<int:land_id>/check/<int:program_number>/',
    #     views.CheckLand.as_view(),
    #     name='check land program',
    # ),
    # # new-sch - get program of device
    # path(
    #     '<int:land_id>/new-sch/<int:land_program_id>/',
    #     views.ask_schedule,
    #     name='get program for device',
    # ),
    # # reset_program_id_modified
    # path(
    #     'reset_program_is_modified/',
    #     views.reset_program_is_modified,
    #     name='reset program is modified',
    # ),
    # p_list - get list of programs
    # path(
    #     'p_list/',
    #     views.get_programs,
    #     name='get-programs',
    # ),
    path(
        'pd_list/',
        views.get_device_programs,
        name='get-device-programs',
    ),
    # programs/land_id - get list of programs of land
    # path(
    #     'programs/<int:land_id>/',
    #     views.Programs.as_view(),
    #     name="get_programs",
    # ),
    # # temp_availability - check availability of temp sensor logs
    # path(
    #     'temp_availability/<int:land_id>/<int:records>/',
    #     views.get_temp_availability,
    #     name='temp_availability'),
    # # hourly_temp_availability - check hourly availability of temp sensor logs
    # path(
    #     'hourly_temp_availability/<int:land_id>/<int:hours>/',
    #     views.get_hourly_temp_availability,
    #     name='hourly_temp_availability',
    # ),
    # # hourly_availability - check device hourly availability
    # path(
    #     'hourly_availability/<int:land_id>/<int:hours>/',
    #     views.get_hourly_availability,
    #     name='hourly_availability'
    # ),
    # get_land_by_device_serial
    path(
        'get_land_by_device_serial/',
        views.get_land_by_device_serial,
        name='get land by device serial'
    ),
    # path(
    #     'get_land_by_serial/',
    #     views.get_land_by_serial,
    #     name='land-by-serial'
    # ),
    # # add_device
    # path(
    #     'add_device/',
    #     views.AddDevice.as_view(),
    #     name='add device'
    # ),
    # get_owner_phone_number
    path(
        'get_owner_phone_number/<int:land_id>/',
        views.GetOwnerPhoneNumber.as_view(),
        name='get-owner-phone'
    ),
    # external_button_programs
    # path(
    #     '<int:device_id>/external_button_programs/',
    #     views.external_button_program_view,
    #     name='external button programs list'
    # ),
    # # build device
    # path(
    #     'make_device/',
    #     views.make_device,
    #     name='add device'
    # ),
    # register device by land
    path(
        'register_device_serial/',
        views.register_device_serial,
        name='define_serial',
    ),
    path(
        'device_processes/<int:device_id>/',
        views.device_process_view,
        name='device-processes'
    ),
    path(
        'temp/',
        views.temp_api,
        name='temp'
    ),
    path(
        'test/',
        views.test_input,
        name='test'
    ),
]

