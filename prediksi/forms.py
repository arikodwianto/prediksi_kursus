from django import forms
from .models import DataLatih
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Password dan konfirmasi tidak sama.")
        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


from django import forms
from .models import DataLatih, Kriteria, PilihanKriteria

# Form tambah data latih otomatis berdasarkan kriteria
class DynamicDataLatihForm(forms.ModelForm):
    class Meta:
        model = DataLatih
        fields = ['nama', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for kriteria in Kriteria.objects.all():
            pilihan = PilihanKriteria.objects.filter(kriteria=kriteria)
            self.fields[f'kriteria_{kriteria.id}'] = forms.ChoiceField(
                label=kriteria.nama,
                choices=[(p.id, p.label) for p in pilihan],
                widget=forms.Select(attrs={'class': 'form-control'}),
                required=True
            )




# Tambah kriteria baru
class KriteriaForm(forms.ModelForm):
    class Meta:
        model = Kriteria
        fields = ['nama']


# Tambah pilihan kriteria
class PilihanKriteriaForm(forms.ModelForm):
    class Meta:
        model = PilihanKriteria
        fields = ['kriteria', 'nilai', 'label']

from django import forms
from .models import DataUji, Kriteria, PilihanKriteria

from django import forms
from .models import DataUji, Kriteria, PilihanKriteria

class DynamicDataUjiForm(forms.ModelForm):
    k = forms.IntegerField(label='Nilai K', min_value=1)

    class Meta:
        model = DataUji
        fields = ['nama']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Styling Bootstrap untuk field yang ada
        self.fields['nama'].widget.attrs.update({'class': 'form-control'})
        self.fields['k'].widget.attrs.update({'class': 'form-control'})

        # Tambahkan field dinamis untuk setiap kriteria
        for kriteria in Kriteria.objects.all():
            field_name = f'kriteria_{kriteria.id}'
            self.fields[field_name] = forms.ModelChoiceField(
                label=kriteria.nama,
                queryset=PilihanKriteria.objects.filter(kriteria=kriteria),
                required=True,
                widget=forms.Select(attrs={'class': 'form-select'})
            )

