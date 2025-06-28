from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib import messages

from .models import DataLatih, DataUji
from .forms import DataUjiForm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

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

# ===== Helper untuk encoding =====
def encode_jenis_kelamin(jk):
    return 1 if jk == 'L' else 0

def encode_pekerjaan(pk):
    mapping = {
        'Mahasiswa': 0, 'Pelajar': 1, 'PNS': 2,
        'Swasta': 3, 'Wiraswasta': 4, 'Lainnya': 5
    }
    return mapping.get(pk, 5)

from django.db.models import Count
from .models import DataUji, DataLatih
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
from .models import DataLatih, DataUji
from .forms import DataUjiForm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score


@login_required
def prediksi_view(request):
    hasil_prediksi = None
    akurasi = None
    precision = None
    recall = None
    tetangga_terdekat = []
    alasan = None  # >>> Tambahan

    if request.method == 'POST':
        form = DataUjiForm(request.POST)
        if form.is_valid():
            uji = form.save(commit=False)

            input_vector = [
                uji.hari,
                uji.waktu,
                uji.durasi,
                uji.paket,
                20,
                encode_jenis_kelamin('L'),
                encode_pekerjaan('Lainnya')
            ]

            X, y = [], []
            data_latih_all = list(DataLatih.objects.all())
            for d in data_latih_all:
                X.append([
                    d.hari, d.waktu, d.durasi, d.paket, 20,
                    encode_jenis_kelamin('L'),
                    encode_pekerjaan('Lainnya')
                ])
                y.append(d.status)

            model = KNeighborsClassifier(n_neighbors=3)

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

                # >>> Tambahan: hitung alasan
                status_count = {}
                for tetangga in tetangga_terdekat:
                    status = tetangga['status']
                    status_count[status] = status_count.get(status, 0) + 1
                # cari mayoritas
                if status_count:
                    mayoritas_status = max(status_count, key=status_count.get)
                    jumlah = status_count[mayoritas_status]
                    alasan = f"Hasil prediksi '{pred}' karena mayoritas dari {len(tetangga_terdekat)} tetangga terdekat memiliki status '{mayoritas_status}' sebanyak {jumlah} data."

            else:
                model.fit(X, y)
                pred = model.predict([input_vector])[0]
                akurasi = precision = recall = 0  # Tidak dihitung karena data kurang
                alasan = "Data latih kurang dari 5, sehingga hasil prediksi didapat langsung dari model tanpa perhitungan tetangga mayoritas."

            # Konversi hasil prediksi
            if pred == "Bisa":
                hasil_prediksi = "Bisa mengikuti kursus"
            elif pred == "Tidak Bisa":
                hasil_prediksi = "Tidak bisa mengikuti kursus"
            else:
                hasil_prediksi = pred

            uji.hasil_prediksi = pred
            uji.save()

            request.session['prediksi_data'] = {
                'hasil_prediksi': hasil_prediksi,
                'akurasi': akurasi,
                'precision': precision,
                'recall': recall,
                'tetangga_terdekat': tetangga_terdekat,
                'alasan': alasan,  # >>> Tambahan
                'input': {
                    'nama': uji.nama,
                    'hari': uji.hari,
                    'waktu': uji.waktu,
                    'durasi': uji.durasi,
                    'paket': uji.paket
                }
            }
    else:
        form = DataUjiForm()

    return render(request, 'prediksi/prediksi_form.html', {
        'form': form,
        'hasil_prediksi': hasil_prediksi,
        'akurasi': akurasi,
        'precision': precision,
        'recall': recall,
        'tetangga_terdekat': tetangga_terdekat,
        'alasan': alasan  # >>> Tambahan
    })


from .models import DataUji
from django.utils.timezone import localtime
@login_required
def riwayat_prediksi_view(request):
    data = DataUji.objects.all().order_by('-id')  # urutkan dari terbaru
    return render(request, 'prediksi/riwayat_prediksi.html', {'data': data})



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
from .models import DataUji
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
@login_required
def data_latih_view(request):
    data = DataLatih.objects.all()
    return render(request, 'prediksi/data_latih.html', {'data': data})

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
