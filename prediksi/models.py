from django.db import models

# Kriteria seperti Hari, Waktu, Paket, dll
class Kriteria(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

# Pilihan untuk tiap kriteria, seperti Senin, Selasa, dst
class PilihanKriteria(models.Model):
    kriteria = models.ForeignKey(Kriteria, on_delete=models.CASCADE, related_name='pilihan')
    nilai = models.IntegerField()  # nilai numerik
    label = models.CharField(max_length=100)  # label ditampilkan ke user

    def __str__(self):
        return f"{self.kriteria.nama} - {self.label}"

# Data Latih (inputan utama)
class DataLatih(models.Model):
    STATUS_CHOICES = [
        ('Bisa', 'Bisa'),
        ('Tidak Bisa', 'Tidak Bisa'),
    ]

    nama = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.nama} - {self.status}"

# Nilai setiap kriteria untuk setiap DataLatih
class NilaiKriteriaLatih(models.Model):
    data_latih = models.ForeignKey(DataLatih, on_delete=models.CASCADE, related_name='nilai_kriteria')
    kriteria = models.ForeignKey(Kriteria, on_delete=models.CASCADE)
    pilihan = models.ForeignKey(PilihanKriteria, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.data_latih.nama} - {self.kriteria.nama} = {self.pilihan.label}"


from django.db import models
from .models import Kriteria, PilihanKriteria  # kalau dalam file sama, ini tidak perlu

class DataUji(models.Model):
    nama = models.CharField(max_length=255)
    hasil_prediksi = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nama


class NilaiKriteriaUji(models.Model):
    data_uji = models.ForeignKey(DataUji, related_name='nilai_kriteria', on_delete=models.CASCADE)
    kriteria = models.ForeignKey(Kriteria, on_delete=models.CASCADE)
    pilihan = models.ForeignKey(PilihanKriteria, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.data_uji.nama} - {self.kriteria.nama}: {self.pilihan.label}"
