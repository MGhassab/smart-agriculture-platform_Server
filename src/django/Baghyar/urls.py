from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerSplitView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel/', include(('Panel.urls', 'Panel'), namespace='Panel')),
    path('panel/api/', include(('Customer.urls', 'Customer'), namespace='Panel-Customer')),
    path('panel/api/d/', include(('Device.urls', 'Device'), namespace='Panel-Device')),
    path('panel/api/u/', include(('LightApp.urls', 'LightApp'), namespace='Panel-LightApp')),
    # path('api/', include(('Customer.urls', 'Customer'), namespace='Customer')),
    # path('api/d/', include(('Device.urls', 'Device'), namespace='Device')),
    # path('api/u/', include(('LightApp.urls', 'LightApp'), namespace='LightApp')),
    path('panel/api-auth/', include(('rest_framework.urls', 'djangorestframework'), namespace='rest_framework')),
    # path('api-auth/', include(('rest_framework.urls', 'djangorestframework'), namespace='api-auth')),

    path('panel/developer/swagger/', SpectacularAPIView.as_view(), name='schema'),
    path('panel/developer/api-docs/', SpectacularSwaggerSplitView.as_view(url_name='schema'), name='api-doc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
