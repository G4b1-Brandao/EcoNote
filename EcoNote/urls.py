from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('EconoteApp.urls')),  # conecta as URLs do app
]
