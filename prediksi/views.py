from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib import messages

from .models import DataLatih

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
from .forms import DynamicDataUjiForm
from .models import DataUji, NilaiKriteriaUji, PilihanKriteria, DataLatih


from xhtml2pdf import pisa
import io
import csv
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login')
    else:
        form = RegisterForm()

    # Tambah class Bootstrap
    for field in form.fields:
        form.fields[field].widget.attrs.update({'class': 'form-control'})

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = LoginForm()

    # Tambah class Bootstrap
    form.fields['username'].widget.attrs.update({'class': 'form-control'})
    form.fields['password'].widget.attrs.update({'class': 'form-control'})

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')



from django.db.models import Count
from .models import DataLatih
@login_required
def dashboard_view(request):
    total_uji = DataUji.objects.count()
    total_bisa = DataUji.objects.filter(hasil_prediksi="Bisa").count()
    total_tidak_bisa = DataUji.objects.filter(hasil_prediksi="Tidak Bisa").count()
    total_latih = DataLatih.objects.count()

    context = {
        'total_uji': total_uji,
        'total_bisa': total_bisa,
        'total_tidak_bisa': total_tidak_bisa,
        'total_latih': total_latih
    }
    return render(request, 'prediksi/dashboard.html', context)


# ===== VIEW PREDIKSI =====

from sklearn.metrics import precision_score, recall_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import DataLatih

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import DataLatih


from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

# views.py
import csv
from io import TextIOWrapper
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score


from .models import (
    DataLatih, NilaiKriteriaLatih,
    Kriteria, PilihanKriteria
)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages

from .models import PilihanKriteria, DataLatih
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DynamicDataUjiForm
from .models import DataUji, NilaiKriteriaUji, PilihanKriteria, DataLatih
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DynamicDataUjiForm
from .models import DataUji, NilaiKriteriaUji, PilihanKriteria, DataLatih
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import numpy as np

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DataUji, NilaiKriteriaUji, DataLatih
from .forms import DynamicDataUjiForm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

@login_required
def tambah_data_uji(request):
    hasil_prediksi = akurasi = precision = recall = alasan = None
    tetangga_terdekat = []
    uji = None

    if request.method == 'POST':
        form = DynamicDataUjiForm(request.POST)
        if form.is_valid():
            try:
                uji = DataUji.objects.create(nama=form.cleaned_data.get('nama'))
                input_vector = []

                for field_name, value in form.cleaned_data.items():
                    if field_name.startswith('kriteria_'):
                        try:
                            kriteria_id = int(field_name.split('_')[1])

                            if not hasattr(value, 'nilai'):
                                messages.error(request, f"Input untuk kriteria {kriteria_id} belum dipilih dengan benar.")
                                uji.delete()
                                return redirect('tambah_data_uji')

                            input_vector.append(float(value.nilai))
                            NilaiKriteriaUji.objects.create(
                                data_uji=uji,
                                kriteria_id=kriteria_id,
                                pilihan=value
                            )
                        except Exception as e:
                            messages.error(request, f"Terjadi kesalahan saat menyimpan nilai kriteria: {e}")
                            uji.delete()
                            return redirect('tambah_data_uji')

                # Ambil nilai k
                try:
                    k = int(form.cleaned_data.get('k', 3))
                    if k <= 0:
                        raise ValueError("Nilai k harus lebih dari 0.")
                except Exception as e:
                    messages.error(request, f"Nilai k tidak valid: {e}")
                    uji.delete()
                    return redirect('tambah_data_uji')

                # Ambil data latih
                data_latih_all = DataLatih.objects.prefetch_related('nilai_kriteria__pilihan')
                X, y = [], []

                for d in data_latih_all:
                    try:
                        vector = [float(n.pilihan.nilai) for n in d.nilai_kriteria.order_by('kriteria__id')]
                        if vector:
                            X.append(vector)
                            y.append(d.status)
                    except Exception as e:
                        continue  # Abaikan jika data latih tidak valid

                if len(X) < k:
                    messages.warning(request, f"Jumlah data latih ({len(X)}) lebih sedikit dari nilai k ({k}). Sistem tetap akan memproses prediksi.")
                
                if len(X) == 0:
                    messages.error(request, "Tidak ada data latih yang valid untuk digunakan dalam prediksi.")
                    uji.delete()
                    return redirect('tambah_data_uji')

                model = KNeighborsClassifier(n_neighbors=min(k, len(X)))

                if len(X) >= 5:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
                    model.fit(X_train, y_train)
                    pred = model.predict([input_vector])[0]
                    y_pred = model.predict(X_test)
                    akurasi = round(accuracy_score(y_test, y_pred) * 100, 2)
                    precision = round(precision_score(y_test, y_pred, average='macro', zero_division=0) * 100, 2)
                    recall = round(recall_score(y_test, y_pred, average='macro', zero_division=0) * 100, 2)

                    distances, indices = model.kneighbors([input_vector])
                    for idx, dist in zip(indices[0], distances[0]):
                        d = data_latih_all[int(idx)]
                        tetangga_terdekat.append({
                            'nama': d.nama,
                            'status': d.status,
                            'jarak': round(dist, 4)
                        })

                    status_count = {}
                    for t in tetangga_terdekat:
                        status_count[t['status']] = status_count.get(t['status'], 0) + 1

                    if status_count:
                        mayoritas = max(status_count, key=status_count.get)
                        jumlah = status_count[mayoritas]
                        alasan = f"Hasil prediksi '{pred}' karena mayoritas dari {len(tetangga_terdekat)} tetangga memiliki status '{mayoritas}' sebanyak {jumlah} data."
                else:
                    # Tidak cukup data untuk split
                    model.fit(X, y)
                    pred = model.predict([input_vector])[0]
                    akurasi = precision = recall = 0
                    alasan = "Data latih kurang dari 5, prediksi dilakukan tanpa validasi silang."

                uji.hasil_prediksi = pred
                uji.save()
                hasil_prediksi = pred
                messages.success(request, f"Prediksi berhasil dilakukan. Hasil: {pred}")

            except Exception as e:
                if uji:
                    uji.delete()
                messages.error(request, f"Terjadi kesalahan tak terduga: {e}")
                return redirect('tambah_data_uji')
        else:
            messages.error(request, "Form tidak valid. Pastikan semua kolom telah diisi dengan benar.")
    else:
        form = DynamicDataUjiForm()

    return render(request, 'prediksi/tambah_data_uji.html', {
        'form': form,
        'hasil_prediksi': hasil_prediksi,
        'akurasi': akurasi,
        'precision': precision,
        'recall': recall,
        'tetangga_terdekat': tetangga_terdekat,
        'alasan': alasan,
        'uji': uji
    })



# views.py
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import DataUji

@login_required
def cetak_pdf_data_uji(request, uji_id):
    uji = DataUji.objects.get(id=uji_id)
    nilai_kriteria = uji.nilai_kriteria.select_related('kriteria', 'pilihan').all()

    template = get_template('prediksi/laporan_pdf.html')
    html = template.render({
        'uji': uji,
        'nilai_kriteria': nilai_kriteria,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="hasil_prediksi_{uji.nama}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Gagal membuat PDF', status=500)
    return response







from django.utils.timezone import localtime
from .models import DataLatih, Kriteria

@login_required
def data_latih_view(request):
    data = DataLatih.objects.prefetch_related('nilai_kriteria__kriteria', 'nilai_kriteria__pilihan')
    kriteria_list = Kriteria.objects.all()
    return render(request, 'prediksi/data_latih.html', {
        'data': data,
        'kriteria_list': kriteria_list
    })




# ===== CETAK PDF =====
@login_required
def cetak_prediksi_pdf(request):
    form_data = request.session.get('prediksi_data')
    if not form_data:
        return HttpResponse("Tidak ada data untuk dicetak.", content_type="text/plain")

    template = get_template('prediksi/prediksi_pdf.html')
    html = template.render(form_data)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laporan_prediksi.pdf"'

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=response)
    if pisa_status.err:
        return HttpResponse('Terjadi kesalahan saat membuat PDF', status=500)
    return response

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.utils.timezone import localtime
import io
@login_required
def cetak_riwayat_pdf(request):
    data = DataUji.objects.all().order_by('-id')
    tanggal_cetak = localtime().strftime("%d-%m-%Y %H:%M")

    template = get_template('prediksi/riwayat_prediksi_pdf.html')
    html = template.render({'data': data, 'tanggal_cetak': tanggal_cetak})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="riwayat_prediksi.pdf"'

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=response)
    if pisa_status.err:
        return HttpResponse('Terjadi kesalahan saat membuat PDF', status=500)
    return response


# ===== VIEW DATA LATIH =====
from .models import DataLatih, Kriteria

@login_required
def data_latih_view(request):
    data = DataLatih.objects.prefetch_related('nilai_kriteria__kriteria', 'nilai_kriteria__pilihan')
    kriteria_list = Kriteria.objects.all()
    return render(request, 'prediksi/data_latih.html', {
        'data': data,
        'kriteria_list': kriteria_list
    })


# ===== IMPORT CSV DATA LATIH =====
@login_required
def import_data_latih(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File harus berformat CSV')
            return redirect('data_latih')

        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        next(reader)  # Lewati header

        for row in reader:
            try:
                DataLatih.objects.create(
                    nama=row[0],
                    hari=int(row[1]),
                    waktu=int(row[2]),
                    durasi=int(row[3]),
                    paket=int(row[4]),
                    status=row[5],
                )
            except Exception as e:
                messages.error(request, f"Error baris: {row} | {str(e)}")
                continue

        messages.success(request, 'Data CSV berhasil diimport!')
        return redirect('data_latih')

    return redirect('data_latih')

from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import DynamicDataLatihForm

from django.contrib.auth.decorators import login_required
from .forms import DynamicDataLatihForm, KriteriaForm, PilihanKriteriaForm
from .models import DataLatih, NilaiKriteriaLatih, Kriteria, PilihanKriteria
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import csv
from io import TextIOWrapper
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DataLatih, Kriteria, PilihanKriteria, NilaiKriteriaLatih
from .forms import DynamicDataLatihForm
from django.contrib.auth.decorators import login_required

from io import TextIOWrapper
import csv
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import DataLatih, NilaiKriteriaLatih, PilihanKriteria, Kriteria
from .forms import DynamicDataLatihForm
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DynamicDataLatihForm
from .models import DataLatih, NilaiKriteriaLatih, PilihanKriteria, Kriteria

import csv
from io import TextIOWrapper

@login_required
def tambah_data_latih(request):
    form = None

    if request.method == 'POST':
        # === Upload dari CSV ===
        if 'csv_file' in request.FILES:
            errors = []
            try:
                file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
                reader = csv.DictReader(file)

                baris = 1
                for row in reader:
                    baris += 1
                    nama = row.get('nama')
                    status = row.get('status')

                    if not nama or not status:
                        errors.append(f"Baris {baris}: Nama atau Status kosong.")
                        continue

                    try:
                        data_latih = DataLatih.objects.create(nama=nama.strip(), status=status.strip())
                    except Exception as e:
                        errors.append(f"Baris {baris}: Gagal membuat entri data latih: {e}")
                        continue

                    for kriteria in Kriteria.objects.all():
                        key = f'kriteria_{kriteria.nama.lower().replace(" ", "_")}'
                        label = row.get(key)

                        if not label:
                            errors.append(f"Baris {baris}: Kolom '{key}' tidak ditemukan atau kosong.")
                            continue

                        try:
                            pilihan = PilihanKriteria.objects.get(
                                kriteria=kriteria, label__iexact=label.strip()
                            )
                            NilaiKriteriaLatih.objects.create(
                                data_latih=data_latih,
                                kriteria=kriteria,
                                pilihan=pilihan
                            )
                        except PilihanKriteria.DoesNotExist:
                            errors.append(
                                f"Baris {baris}: Label '{label}' tidak cocok dengan pilihan kriteria '{kriteria.nama}'."
                            )
                        except Exception as e:
                            errors.append(f"Baris {baris}: Gagal menyimpan nilai kriteria: {e}")

                # Tampilkan hasil
                if errors:
                    for e in errors:
                        messages.warning(request, e)
                    messages.error(request, "Beberapa data gagal diimpor. Silakan periksa pesan peringatan di atas.")
                else:
                    messages.success(request, "Semua data CSV berhasil diimpor.")

                return redirect('data_latih')

            except Exception as e:
                messages.error(request, f"Gagal memproses file CSV: {e}")
                return redirect('tambah_data_latih')

        # === Tambah Manual via Form ===
        else:
            form = DynamicDataLatihForm(request.POST)
            if form.is_valid():
                try:
                    data_latih = form.save()
                    for field_name, value in form.cleaned_data.items():
                        if field_name.startswith('kriteria_'):
                            try:
                                kriteria_id = int(field_name.split('_')[1])
                                pilihan_id = int(value)
                                NilaiKriteriaLatih.objects.create(
                                    data_latih=data_latih,
                                    kriteria_id=kriteria_id,
                                    pilihan_id=pilihan_id
                                )
                            except Exception as e:
                                messages.error(request, f"Kesalahan saat menyimpan nilai kriteria: {e}")
                    messages.success(request, 'Data latih berhasil ditambahkan.')
                    return redirect('data_latih')
                except Exception as e:
                    messages.error(request, f"Terjadi kesalahan saat menyimpan data latih: {e}")
            else:
                messages.error(request, "Form tidak valid. Silakan periksa kembali input Anda.")

    # Jika GET atau form belum diinisialisasi
    if not form:
        form = DynamicDataLatihForm()

    return render(request, 'prediksi/tambah_data_latih.html', {'form': form})



@login_required
def edit_data_latih_view(request, latih_id):
    data_latih = get_object_or_404(DataLatih, id=latih_id)
    nilai_kriteria = {n.kriteria_id: n.pilihan_id for n in data_latih.nilai_kriteria.all()}

    initial_data = {
        'nama': data_latih.nama,
        'status': data_latih.status,
        **{f'kriteria_{k}': v for k, v in nilai_kriteria.items()}
    }

    form = DynamicDataLatihForm(request.POST or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        data_latih.nama = form.cleaned_data['nama']
        data_latih.status = form.cleaned_data['status']
        data_latih.save()

        data_latih.nilai_kriteria.all().delete()

        for field, val in form.cleaned_data.items():
            if field.startswith('kriteria_'):
                kriteria_id = int(field.split('_')[1])
                pilihan_id = int(val)
                NilaiKriteriaLatih.objects.create(
                    data_latih=data_latih,
                    kriteria_id=kriteria_id,
                    pilihan_id=pilihan_id
                )

        messages.success(request, "Data latih berhasil diperbarui.")
        return redirect('data_latih')

    return render(request, 'prediksi/tambah_data_latih.html', {
        'form': form,
        'edit_mode': True,
        'data_latih': data_latih,
    })


@login_required
def hapus_data_latih_view(request, latih_id):
    data_latih = get_object_or_404(DataLatih, id=latih_id)
    data_latih.delete()
    messages.success(request, "Data latih berhasil dihapus.")
    return redirect('data_latih')




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import KriteriaForm
from .models import Kriteria

@login_required
def tambah_kriteria_view(request, kriteria_id=None):
    # Jika ada ID, berarti edit
    if kriteria_id:
        kriteria = get_object_or_404(Kriteria, id=kriteria_id)
        form = KriteriaForm(request.POST or None, instance=kriteria)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, "Kriteria berhasil diperbarui.")
            return redirect('tambah_kriteria')
    else:
        # Jika tidak ada ID, maka tambah baru
        form = KriteriaForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, "Kriteria berhasil ditambahkan.")
            return redirect('tambah_kriteria')

    # Daftar semua kriteria
    kriteria_list = Kriteria.objects.all().order_by('id')

    return render(request, 'prediksi/tambah_kriteria.html', {
        'form': form,
        'kriteria_list': kriteria_list,
        'edit_mode': True if kriteria_id else False,
    })

@login_required
def hapus_kriteria_view(request, kriteria_id):
    kriteria = get_object_or_404(Kriteria, id=kriteria_id)
    kriteria.delete()
    messages.success(request, "Kriteria berhasil dihapus.")
    return redirect('tambah_kriteria')




from .models import PilihanKriteria
from .forms import PilihanKriteriaForm

@login_required
def tambah_pilihan_kriteria_view(request):
    form = PilihanKriteriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Pilihan kriteria berhasil ditambahkan.")
        return redirect('tambah_pilihan_kriteria')

    pilihan_list = PilihanKriteria.objects.select_related('kriteria').order_by('kriteria__id')
    return render(request, 'prediksi/tambah_pilihan_kriteria.html', {
        'form': form,
        'pilihan_list': pilihan_list
    })

from django.shortcuts import get_object_or_404

@login_required
def edit_pilihan_kriteria_view(request, pilihan_id):
    pilihan = get_object_or_404(PilihanKriteria, id=pilihan_id)
    form = PilihanKriteriaForm(request.POST or None, instance=pilihan)
    
    if form.is_valid():
        form.save()
        messages.success(request, "Pilihan kriteria berhasil diperbarui.")
        return redirect('tambah_pilihan_kriteria')

    pilihan_list = PilihanKriteria.objects.select_related('kriteria').order_by('kriteria__id')
    return render(request, 'prediksi/tambah_pilihan_kriteria.html', {
        'form': form,
        'pilihan_list': pilihan_list,
        'edit_mode': True,
        'edit_id': pilihan_id,
    })

@login_required
def hapus_pilihan_kriteria_view(request, pilihan_id):
    pilihan = get_object_or_404(PilihanKriteria, id=pilihan_id)
    pilihan.delete()
    messages.success(request, "Pilihan kriteria berhasil dihapus.")
    return redirect('tambah_pilihan_kriteria')

 

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def riwayat_prediksi_view(request):
    data = DataUji.objects.all().order_by('-id')  # urut dari terbaru
    return render(request, 'prediksi/riwayat_prediksi.html', {'data': data})

from django.utils.timezone import now
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import DataUji

from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from django.templatetags.static import static
from django.conf import settings
import os

from weasyprint import HTML
from django.conf import settings
import os

@login_required
def cetak_pdf_riwayat_prediksi(request):
    data = DataUji.objects.all().order_by('-id')
    template = get_template('prediksi/riwayat_pdf.html')
    html_string = template.render({'data': data, 'tanggal_cetak': now()})

    # base path ke folder static
    base_url = settings.STATIC_ROOT
    if not base_url:
        base_url = os.path.join(settings.BASE_DIR, 'static')  # fallback jika STATIC_ROOT None

    pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="riwayat_prediksi.pdf"'
    return response



