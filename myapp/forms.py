from django import forms
from .models import Student, Teacher, AdminUser


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'registration_number', 'password']


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'email', 'password']


class AdminForm(forms.ModelForm):
    class Meta:
        model = AdminUser
        fields = ['name', 'password']