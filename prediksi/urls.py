from django.urls import path
from . import views
from .views import cetak_prediksi_pdf
from .views import riwayat_prediksi_view
from .views import cetak_riwayat_pdf


urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('prediksi/', views.prediksi_view, name='prediksi'),
    path('data-latih/', views.data_latih_view, name='data_latih'),
    path('data-latih/import/', views.import_data_latih, name='import_data_latih'),
    path('prediksi/cetak/', cetak_prediksi_pdf, name='cetak_prediksi_pdf'),
    path('riwayat/', riwayat_prediksi_view, name='riwayat_prediksi'),
    path('riwayat/cetak/', cetak_riwayat_pdf, name='cetak_riwayat_pdf'),
    path('tambah-data-latih/', views.tambah_data_latih, name='tambah_data_latih')

]
