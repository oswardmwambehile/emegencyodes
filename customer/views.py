from django.shortcuts import render

from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import CustomerForm, CustomerContactForm
from .models import Customer, CustomerContact

# Use a plain ModelFormSet for adding contacts
ContactFormSet = modelformset_factory(
    CustomerContact,
    form=CustomerContactForm,
    extra=1,          # at least one empty row
    can_delete=True
)

def add_customer(request):
    if request.method == "POST":
        customer_form = CustomerForm(request.POST)
        # IMPORTANT: use the SAME prefix for GET and POST
        formset = ContactFormSet(request.POST, queryset=CustomerContact.objects.none(), prefix="contacts")

        if customer_form.is_valid() and formset.is_valid():
            # Save parent first
            customer = customer_form.save()

            # Save contacts and attach the customer
            contacts = formset.save(commit=False)
            for c in contacts:
                c.customer = customer
                c.save()

            # Handle deletes (if any were added then removed)
            for obj in formset.deleted_objects:
                obj.delete()

            return redirect("customer_list")

    else:
        customer_form = CustomerForm()
        # Same prefix in GET; start with no contacts from DB
        formset = ContactFormSet(queryset=CustomerContact.objects.none(), prefix="contacts")

    return render(request, "users/add_customer.html", {
        "customer_form": customer_form,
        "formset": formset,
        "is_update": False,   # just for your heading/buttons
    })


from django.shortcuts import render
from django.db.models import Q
from .models import Customer

def customer_list(request):
    query = request.GET.get("q", "")
    customers = Customer.objects.prefetch_related("contacts").all()

    if query:
        customers = customers.filter(
            Q(company_name__icontains=query) |
            Q(designation__icontains=query)
        )

    customers = customers.order_by('-created_at')  # 👈 order by latest created

    context = {
        "customers": customers,
        "query": query,
    }
    return render(request, "users/customer_list.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import Customer, CustomerContact
from .forms import CustomerForm, CustomerContactForm


def update_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    # Inline formset for contacts tied to customer
    ContactFormSet = inlineformset_factory(
        Customer,
        CustomerContact,
        form=CustomerContactForm,
        extra=0,          # no blank rows by default
        can_delete=True   # allow delete
    )

    if request.method == "POST":
        customer_form = CustomerForm(request.POST, instance=customer)
        formset = ContactFormSet(request.POST, instance=customer)

        if customer_form.is_valid() and formset.is_valid():
            customer_form.save()
            formset.save()  # updates, deletes, and adds new
            messages.success(request, "✅ Customer updated successfully!")
            return redirect("customer_list")
        else:
            print("❌ FORM ERRORS:", customer_form.errors, formset.errors)
    else:
        customer_form = CustomerForm(instance=customer)
        formset = ContactFormSet(instance=customer)

    return render(request, "users/update_customer.html", {
        "customer_form": customer_form,
        "formset": formset,
        "customer": customer,
    })

# ✅ DELETE CUSTOMER
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        customer.delete()
        messages.success(request, "🗑️ Customer deleted successfully!")
        return redirect("customer_list")

    return render(request, "users/customer_confirm_delete.html", {"customer": customer})


from django.shortcuts import render, get_object_or_404
from visits.models import CustomUser
from django.db.models import Q  # 🔍 For OR lookups

def user_list(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.all().order_by('-date_joined')  # order by newest first

    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(company_name__icontains=query)  # <-- added this
        ).order_by('-date_joined')  # maintain ordering after filtering

    return render(request, 'company/user_list.html', {
        'users': users,
        'query': query,
    })

def index(request):
    return render(request, 'company/index.html')


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from visits.models import CustomUser

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if user == request.user:
        message = "You can't change your own status."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': message}, status=403)
        messages.error(request, message)
        return redirect('user_list')

    if user.is_superuser:
        message = "You can't change status of a superuser."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': message}, status=403)
        messages.error(request, message)
        return redirect('user_list')

    user.is_active = not user.is_active
    user.save()

    status = "enabled" if user.is_active else "disabled"
    message = f"User {user.email} has been {status}."

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'is_active': user.is_active})

    messages.success(request, message)
    return redirect('user_list')

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from visits.models import CustomUser

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.company_name = request.POST.get("company_name")
        user.position = request.POST.get("position")
        user.zone = request.POST.get("zone")
        user.branch = request.POST.get("branch")
        user.contact = request.POST.get("contact")
        user.save()

        messages.success(request, "User updated successfully.")
        return redirect("user_list")

    return render(request, "company/edit_user.html", {"user_obj": user})







