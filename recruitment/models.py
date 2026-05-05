from django.db import models

class Pelamar(models.Model):
    nama = models.CharField(max_length=200)
    posisi_dilamar = models.CharField(max_length=100)
    pendidikan_terakhir = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nama

class Kriteria(models.Model):
    nama_kriteria = models.CharField(max_length=100)
    nilai_standar = models.IntegerField()
    jenis_faktor = models.CharField(max_length=20, choices=[('Core', 'Core'), ('Secondary', 'Secondary')])

    def __str__(self):
        return self.nama_kriteria
    
class Penilaian(models.Model):
    pelamar = models.ForeignKey(Pelamar, on_delete=models.CASCADE)
    kriteria = models.ForeignKey(Kriteria, on_delete=models.CASCADE)
    nilai_aktual = models.IntegerField()

    def __str__(self):
        return f"{self.pelamar.nama} - {self.kriteria.nama_kriteria}"