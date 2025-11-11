from django import forms
from .models import Employee
from django.contrib.auth.models import User

class EmployeeProfileForm(forms.ModelForm):
    password = forms.CharField(
        label='Yangi parol',
        widget=forms.PasswordInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
        required=False
    )

    class Meta:
        model = Employee
        fields = ['phone', 'password']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
        }

    def save(self, commit=True):
        employee = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            # Parolni user modelida yangilaymiz
            user = employee.user
            user.set_password(password)
            user.save()
        if commit:
            employee.save()
        return employee