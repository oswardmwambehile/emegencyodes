from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from .models import NewVisit, VisitProductionLine, Customer, CustomerContact


class NewVisitForm(forms.ModelForm):
    # Read-only auto-fill fields (will be filled via JS or view)
    contact_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'id': 'id_contact_number',
        })
    )

    designation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'id': 'id_designation',
        })
    )

    class Meta:
        model = NewVisit
        exclude = ['added_by', 'created_at', 'updated_at', 'status', 'tag']  # ✅ status and tag excluded
        widgets = {
            'company_name': forms.Select(attrs={'class': 'form-select', 'id': 'id_company_name'}),
            'contact_person': forms.Select(attrs={'class': 'form-select', 'id': 'id_contact_person'}),
            'meeting_stage': forms.Select(attrs={'class': 'form-select'}),
            'item_discussed': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitude': forms.HiddenInput(attrs={'id': 'id_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'id_longitude'}),
            'client_budget': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate company dropdown
        self.fields['company_name'].queryset = Customer.objects.all().order_by('company_name')

        # Contact person dropdown defaults to empty
        self.fields['contact_person'].queryset = CustomerContact.objects.none()
        self.fields['contact_person'].empty_label = "Select company first"

        # Preload contact_person if company is selected
        company_id = None
        if self.data.get('company_name'):
            try:
                company_id = int(self.data.get('company_name'))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and getattr(self.instance, 'company_name_id', None):
            company_id = self.instance.company_name_id

        if company_id:
            self.fields['contact_person'].queryset = CustomerContact.objects.filter(
                customer_id=company_id
            ).order_by('contact_name')
            self.fields['contact_person'].empty_label = "Select contact"

    def clean(self):
        cleaned = super().clean()

        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')

        if not lat or not lon:
            raise ValidationError("Location not detected yet. Please allow location access and wait for the map.")

        try:
            cleaned['latitude'] = str(Decimal(str(lat)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP))
            cleaned['longitude'] = str(Decimal(str(lon)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP))
        except Exception:
            raise ValidationError("Invalid coordinates received. Please refresh and try again.")

        return cleaned



from django import forms
from django.forms import modelformset_factory
from .models import VisitProductionLine


class VisitProductionLineForm(forms.ModelForm):
    class Meta:
        model = VisitProductionLine
        exclude = ['visit']
        widgets = {
            'productionline': forms.Select(attrs={'class': 'form-select'}),
        }


VisitProductionLineFormSet = modelformset_factory(
    VisitProductionLine,
    form=VisitProductionLineForm,
    extra=1,
    can_delete=True
)

