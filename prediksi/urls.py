from django.urls import path
from . import views
from .views import cetak_prediksi_pdf
from .views import riwayat_prediksi_view
from .views import cetak_riwayat_pdf
from .views import cetak_pdf_data_uji
from .views import cetak_pdf_riwayat_prediksi




urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
   
    path('data-latih/', views.data_latih_view, name='data_latih'),
    path('data-latih/import/', views.import_data_latih, name='import_data_latih'),
    path('prediksi/cetak/', cetak_prediksi_pdf, name='cetak_prediksi_pdf'),
    path('riwayat/', riwayat_prediksi_view, name='riwayat_prediksi'),
    path('riwayat/cetak/', cetak_riwayat_pdf, name='cetak_riwayat_pdf'),

    path('data_latih/tambah/', views.tambah_data_latih, name='tambah_data_latih'),
    path('kriteria/tambah/', views.tambah_kriteria_view, name='tambah_kriteria'),
    path('pilihan/tambah/', views.tambah_pilihan_kriteria_view, name='tambah_pilihan_kriteria'),
    path('data-uji/', views.tambah_data_uji, name='tambah_data_uji'),
    
    path('kriteria/edit/<int:kriteria_id>/', views.tambah_kriteria_view, name='edit_kriteria'),
    path('kriteria/delete/<int:kriteria_id>/', views.hapus_kriteria_view, name='hapus_kriteria'),

    path('pilihan-kriteria/edit/<int:pilihan_id>/', views.edit_pilihan_kriteria_view, name='edit_pilihan_kriteria'),
    path('pilihan-kriteria/hapus/<int:pilihan_id>/', views.hapus_pilihan_kriteria_view, name='hapus_pilihan_kriteria'),
    
    path('data-latih/edit/<int:latih_id>/', views.edit_data_latih_view, name='edit_data_latih'),
    path('data-latih/hapus/<int:latih_id>/', views.hapus_data_latih_view, name='hapus_data_latih'),

    path('cetak-pdf/<int:uji_id>/', cetak_pdf_data_uji, name='cetak_pdf_data_uji'),

    path('cetak-riwayat/', cetak_pdf_riwayat_prediksi, name='cetak_pdf_riwayat_prediksi'),



]
