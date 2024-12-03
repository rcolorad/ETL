from django import forms

class AdministradorForm(forms.Form):
    nombre = forms.CharField(max_length=50, label="Nombre")
    siglas = forms.CharField(max_length=10, label="Siglas")