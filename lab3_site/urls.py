from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    # path('api-auth/', include('rest_framework.urls', namespace='api')),
]
