from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from .forms import BillForm, BillSplitForm
from .models import Bill, BillSplit, User
from django.contrib.auth.decorators import login_required

def profile(request):
  return render(request, "profile.html")

def logout_view(request):
  logout(request)
  return redirect("/")

@login_required
def bills_view(request):
    bills = Bill.objects.filter(created_by=request.user)
    return render(request, "bills.html", {'bills': bills})

@login_required
def bill_create(request):
    if request.method == 'POST':
        bill_form = BillForm(request.POST)
        num_users = int(request.POST.get('num_users', 0))  

        if bill_form.is_valid():
            bill = bill_form.save(commit=False)
            bill.created_by = request.user  
            bill.save() 

            total_spent = 0
            participants = []

            for i in range(num_users):
                participant_name = request.POST.get(f'name_{i}')
                amount_spent = Decimal(request.POST.get(f'amount_spent_{i}'))  

                total_spent += amount_spent

                participants.append((participant_name, amount_spent))

            # Calculate the total amount of the bill (including tax and tip)
            total_bill = Decimal(bill.total_amount)  
            tip_amount = (Decimal(bill.tip_percentage) / 100) * total_bill  
            tax_amount = Decimal(bill.tax_amount)  

            total_bill_with_tax_and_tip = total_bill + tip_amount + tax_amount

            # Calculate how much each participant owes based on their share
            for participant_name, amount_spent in participants:
                # Calculate each person's share of the total bill
                participant_share = (amount_spent / total_bill) * total_bill_with_tax_and_tip

                # Create an entry for each participant
                BillSplit.objects.create(
                    bill=bill,
                    participant_name=participant_name,  
                    amount_spent=amount_spent,  
                    amount_owed=participant_share  
                )

            return redirect('bills') 

    else:
        bill_form = BillForm()

    return render(request, 'bill_create.html', {'bill_form': bill_form})

@login_required
def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)

    bill_splits = BillSplit.objects.filter(bill=bill)

    # Calculate the total bill (with tip and tax)
    total_bill = Decimal(bill.total_amount)
    tip_amount = (Decimal(bill.tip_percentage) / 100) * total_bill
    tax_amount = Decimal(bill.tax_amount)
    total_bill_with_tax_and_tip = round((total_bill + tip_amount + tax_amount), 2)

    # Calculate amount owed for each participant based on their proportion of the total spent
    for split in bill_splits:
        # Calculate how much each participant owes based on their share of the total bill
        amount_owed = (split.amount_spent / total_bill) * total_bill_with_tax_and_tip
        split.amount_owed = round(amount_owed, 2)
        split.save() 

    return render(request, 'bill_detail.html', {
        'bill': bill,
        'bill_splits': bill_splits,
        'total_bill_with_tax_and_tip': total_bill_with_tax_and_tip,
    })
