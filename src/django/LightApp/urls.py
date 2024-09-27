from django.urls import path

from LightApp.views import *


app_name = 'light_app'
urlpatterns = [
    path(
        'user_lands/',
        user_lands,
        name="get-user-lands"
    ),
    path(
        'get_land_updates/',
        get_land_updates,
        name="get-land-updates"
    ),
    path(
        'toggle_spout/',
        toggle_spout,
        name="toggle spout"
    ),
    path(
        'add_user_land/',
        add_user_land,
        name='add land for user',
    ),
    path(
        'register_land_and_device/',
        register_land_and_device,
        name='register-land-and-device',
    ),
    path(
        'del_user_land/',
        del_user_land,
        name='delete land for user',
    ),
    path(
        'program_group/',
        ProgramGroupView.as_view(),
        name='program-group',
    ),
    path(
        'program_group/<int:program_group_id>/',
        ProgramGroupView.as_view(),
        name='program-group-id',
    ),
    path(
        'land/<int:land_id>/',
        LandView.as_view(),
        name='land view'
    ),
    path(
        'device/<int:device_id>/',
        DeviceView.as_view(),
        name="device-view"
    ),
    path(
        'device_hash/<int:device_id>/',
        DeviceHashView.as_view(),
        name="device-view"
    ),
    path(
        'error_list/',
        ErrorList.as_view(),
        name="list of errors"
    ),
    path(
        'login/',
        Authenticate.as_view(),
        name="login",
    ),
    path(
        'VerifyUser/',
        VerificationCheck.as_view(),
        name="verify user"
    ),
    path(
        'VerifyUser_v2/',
        VerificationCheckV2.as_view(),
        name="verify-user-v2"
    ),
    
    path(
        'register/',
        Register.as_view(),
        name="register"
    ),
    path(
        'setAdvanceProgramMode/',
        set_advance_program_mode,
        name="active advance time"
    ),
    path(
        'GetVerification/',
        GetVerification.as_view(),
        name="get verification"
    ),
    path(
        'GetVerification_v2/',
        GetVerificationAndCreateUser.as_view(),
        name="get-verification"
    ),
    path(
        'ChangePassword/',
        ChangePassword.as_view(),
        name="change password"
    ),
    path(
        'UserInfo/',
        UserInfo.as_view(),
        name="user info"
    ),
    path(
        'LandInfo/<int:land_id>/',
        LandInfoDetails.as_view(),
        name="land info details"
    ),
    path(
        'LandInfo/',
        LandInfoDetails.as_view(),
        name="land info"
    ),
    path(
        'ResetLandSerial/',
        reset_land_serial,
        name="reset land serial"
    ),
    path(
        'serial_available/',
        check_serial_availability,
        name="check-serial-availability"
    ),
    path(
        'user_devices/',
        UserDevices.as_view(),
        name="get-user-devices"
    ),
    path(
        'call_process/<int:device_id>/<int:process_number>/',
        call_process,
        name="call-process",
    ),
    path(
        'cancel_program_run/<int:program_id>/',
        cancel_program_run,
        name="cancel-program_run",
    )
]
