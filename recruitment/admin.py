from django.contrib import admin
from .models import Pelamar, Kriteria
from .models import Pelamar, Kriteria, Penilaian

# Daftarkan model supaya muncul di halaman admin
admin.site.register(Pelamar)
admin.site.register(Kriteria)
admin.site.register(Penilaian)