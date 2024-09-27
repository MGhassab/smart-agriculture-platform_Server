from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token


router = routers.DefaultRouter()
# router.register('customer', views.CustomerView)
# router.register('user', views.UserViewSet)
# router.register('land', views.LandView)
# router.register('spout', views.SpoutView)
# router.register('spoutSensor', views.SpoutSensorView)
# # router.register('program', view.ProgramView)
# # router.register('programLite', view.ProgramLiteView)
# router.register('programLite', views.ProgramLiteView)
# # router.register('landDailyTempRecord', view.LandDailyTempRecordView)
# router.register('sensor', views.SensorView)
# # router.register('device', view.DeviceView)
# router.register('smsReceiver', views.SmsReceiverView)
# router.register('tempSensor', views.TempSensorView)
# router.register('humiditySensor', views.HumiditySensorView)
# router.register('soilMoistureSensor', views.SoilMoistureSensorView)
# router.register('evaporationMoistureSensor', views.EvaporationSensorView)
# router.register('waterSensor', views.WaterSensorView)
# router.register('trialWaterSensor', views.TrialWaterSensorView)
# router.register('multiSensor', views.MultiSensorView, basename='multiSensor')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', obtain_auth_token, name='auth_token'),

    # path('api/sensor_set/', view.multi_sensor_set, name='multi_sensor-set')
    # path('device/reportTemp/<int:device_id>/', view.reportTemp, name="temp report"),
]
