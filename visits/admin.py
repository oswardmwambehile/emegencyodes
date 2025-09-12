from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import *

from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import admin
from .models import CustomUser


# --- Custom User Creation Form ---
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'first_name', 'last_name', 'company_name',
            'position', 'zone', 'branch', 'contact'
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# --- Custom User Change Form ---
class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'password', 'first_name', 'last_name',
            'company_name', 'position', 'zone', 'branch', 'contact',
            'is_active', 'is_staff', 'is_superuser'
        )

    def clean_password(self):
        return self.initial["password"]


# --- Custom User Admin ---
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        'email', 'first_name', 'last_name', 'company_name',
        'position', 'zone', 'branch', 'contact', 'is_staff', 'is_superuser'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'company_name',
        'position', 'zone', 'branch'
    )
    search_fields = ('email', 'first_name', 'last_name', 'contact')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'contact')}),
        ('Company Info', {'fields': ('company_name',)}),
        ('Job Info', {'fields': ('position', 'zone', 'branch')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'company_name',
                'position', 'zone', 'branch', 'contact',
                'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'
            )}
        ),
    )


# --- Register with admin site ---
admin.site.register(CustomUser, CustomUserAdmin)