from django.contrib import admin
from django.urls import path
from recruitment.views import proses_profile_matching, dashboard, pendaftaran

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='home'),
    path('ranking/', proses_profile_matching, name='ranking'),
    path('pendaftaran/', pendaftaran, name='pendaftaran'), # Baris baru
]