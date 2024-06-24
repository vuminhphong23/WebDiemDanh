from django import forms
from .models import TblStudents

class TblStudentsForm(forms.ModelForm):
    class Meta:
        model = TblStudents
        fields = ['name', 'email', 'phone', 'date_birth']
