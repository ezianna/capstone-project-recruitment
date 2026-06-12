from django.contrib import admin
from django.urls import path

from recruitment.views import proses_profile_matching, dashboard, pendaftaran, persiapan_ujian, ujian

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='home'),
    path('ranking/', proses_profile_matching, name='ranking'),
    path('pendaftaran/', pendaftaran, name='pendaftaran'),
    
    # Rute CBT yang baru
    path('cbt/', persiapan_ujian, name='persiapan_ujian'),
    path('ujian/', ujian, name='ujian'),
]