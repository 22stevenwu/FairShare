from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import BillForm
from django.contrib.auth.decorators import login_required

def profile(request):
  return render(request, "profile.html")

def bills_view(request):
  return render(request, "bills.html")

from django.shortcuts import render, redirect
from .forms import BillForm
from django.contrib.auth.decorators import login_required

@login_required  #
def bill_create(request):
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            # Set the created_by field to the currently logged-in user
            bill = form.save(commit=False)  # Don't save yet, we need to set `created_by`
            bill.created_by = request.user  # Assign the logged-in user to created_by
            bill.save()  # Now save the bill to the database
            return redirect('bills')  # Redirect to the bill list page
    else:
        form = BillForm()

    return render(request, 'bill_create.html', {'form': form})

def logout_view(request):
  logout(request)
  return redirect("/")
