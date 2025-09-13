from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from .models import NewVisit, ProductInterested, Customer, CustomerContact

# --------------------------
# Step 1: Add New Visit (Client Info + Discussion + Location)
# --------------------------
class NewVisitForm(forms.ModelForm):
    # Read-only auto-filled fields
    contact_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "readonly": "readonly",
            "id": "id_contact_number",
        })
    )

    designation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "readonly": "readonly",
            "id": "id_designation",
        })
    )

    class Meta:
        model = NewVisit
        fields = [
            "company_name",
            "contact_person",
            "contact_number",
            "designation",
            "latitude",
            "longitude",
            "item_discussed",
        ]
        widgets = {
            "company_name": forms.Select(attrs={"class": "form-select", "id": "id_company_name"}),
            "contact_person": forms.Select(attrs={"class": "form-select", "id": "id_contact_person"}),
            "item_discussed": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "latitude": forms.HiddenInput(attrs={"id": "id_latitude"}),
            "longitude": forms.HiddenInput(attrs={"id": "id_longitude"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Company dropdown
        self.fields["company_name"].queryset = Customer.objects.all().order_by("company_name")
        # Contact dropdown initially empty
        self.fields["contact_person"].queryset = CustomerContact.objects.none()
        self.fields["contact_person"].empty_label = "Select company first"

        # Preload contacts if company selected
        company_id = None
        if self.data.get("company_name"):
            try:
                company_id = int(self.data.get("company_name"))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and getattr(self.instance, "company_name_id", None):
            company_id = self.instance.company_name_id

        if company_id:
            self.fields["contact_person"].queryset = CustomerContact.objects.filter(
                customer_id=company_id
            ).order_by("contact_name")
            self.fields["contact_person"].empty_label = "Select contact"

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lon = cleaned.get("longitude")
        if not lat or not lon:
            raise ValidationError("Location not detected. Allow location access and wait for the map.")

        try:
            cleaned["latitude"] = str(Decimal(str(lat)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
            cleaned["longitude"] = str(Decimal(str(lon)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
        except Exception:
            raise ValidationError("Invalid coordinates received. Please refresh and try again.")
        return cleaned


# --------------------------
# Step 2: Products Interested (Add stage: only product choice)
# --------------------------
class ProductInterestedForm(forms.ModelForm):
    class Meta:
        model = ProductInterested
        fields = ["product_interested"]
        widgets = {
            "product_interested": forms.Select(attrs={"class": "form-select"}),
        }

ProductInterestedFormSet = modelformset_factory(
    ProductInterested,
    form=ProductInterestedForm,
    extra=1,
    can_delete=True,
)


# --------------------------
# Update Visit Form (All fields, stage-dependent)
# --------------------------
class UpdateVisitForm(forms.ModelForm):
    class Meta:
        model = NewVisit
        exclude = ["added_by", "created_at", "updated_at"]
        widgets = {
            "company_name": forms.Select(attrs={"class": "form-select"}),
            "contact_person": forms.Select(attrs={"class": "form-select"}),
            "contact_number": forms.TextInput(attrs={"class": "form-control"}),
            "designation": forms.TextInput(attrs={"class": "form-control"}),

            "latitude": forms.HiddenInput(attrs={"id": "id_latitude"}),
            "longitude": forms.HiddenInput(attrs={"id": "id_longitude"}),

            "meeting_stage": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "tag": forms.Select(attrs={"class": "form-select"}),

            "item_discussed": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "client_budget": forms.NumberInput(attrs={"class": "form-control"}),

            "is_order_final": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "contract_outcome": forms.Select(attrs={"class": "form-select"}),
            "contract_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "reason_lost": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "payment_collected": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# --------------------------
# Update Product Interested Form (full fields for stage)
# --------------------------
class UpdateProductInterestedForm(forms.ModelForm):
    class Meta:
        model = ProductInterested
        exclude = ["visit"]
        widgets = {
            "product_interested": forms.Select(attrs={"class": "form-select"}),
            "order_estimate": forms.NumberInput(attrs={"class": "form-control"}),
            "final_order_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "payment_collected": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, stage=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide fields depending on stage
        if stage in ["Prospecting", "Qualifying"]:
            self.fields["order_estimate"].widget = forms.HiddenInput()
            self.fields["final_order_amount"].widget = forms.HiddenInput()
            self.fields["payment_collected"].widget = forms.HiddenInput()
        elif stage == "Proposal or Negotiation":
            self.fields["final_order_amount"].widget = forms.HiddenInput()
            self.fields["payment_collected"].widget = forms.HiddenInput()
        # Closing stage shows all fields


UpdateProductInterestedFormSet = modelformset_factory(
    ProductInterested,
    form=UpdateProductInterestedForm,
    extra=1,
    can_delete=True,
)
