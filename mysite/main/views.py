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

    # Calculate the total amount with tax and tip for each bill
    for bill in bills:
        total_bill = Decimal(bill.total_amount)  # Make sure total_bill is a Decimal
        tip_amount = (Decimal(bill.tip_percentage) / 100) * total_bill  # Convert to Decimal for tip calculation
        tax_amount = Decimal(bill.tax_amount)  # Ensure tax_amount is a Decimal
        total_bill_with_tax_and_tip = total_bill + tip_amount + tax_amount  # Add as Decimal

        bill_splits = BillSplit.objects.filter(bill=bill)

        total_owed = Decimal('0.00')  
        for split in bill_splits:
            if split.paid:
                split.amount_owed = Decimal('0.00')  
            else:
                amount_owed = (split.amount_spent / total_bill) * total_bill_with_tax_and_tip
                split.amount_owed = round(Decimal(amount_owed), 2)  
            split.save()
            total_owed += split.amount_owed 

        bill.total_with_tax_and_tip = total_bill_with_tax_and_tip
        bill.total_owed = total_owed
        bill.save()

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
                participant_share = (amount_spent / total_bill) * total_bill_with_tax_and_tip
                BillSplit.objects.create(
                    bill=bill,
                    participant_name=participant_name,  
                    amount_spent=amount_spent,  
                    amount_owed=participant_share  
                )

            return redirect('bill_detail', bill_id=bill.id)

    else:
        bill_form = BillForm()

    return render(request, 'bill_create.html', {'bill_form': bill_form})

@login_required
def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    bill_splits = BillSplit.objects.filter(bill=bill)

    if request.method == 'POST':
        for split in bill_splits:
            paid_checkbox_name = f"paid_{split.id}"
            if paid_checkbox_name in request.POST:
                split.paid = True  
            else:
                split.paid = False 
            split.save()
        return redirect('bills')

    total_bill = Decimal(bill.total_amount)
    tip_amount = (Decimal(bill.tip_percentage) / 100) * total_bill
    tax_amount = Decimal(bill.tax_amount)
    total_bill_with_tax_and_tip = round((total_bill + tip_amount + tax_amount), 2)

    total_spent = sum([split.amount_spent for split in bill_splits])
    for split in bill_splits:
        amount_owed = (split.amount_spent / total_spent) * total_bill_with_tax_and_tip
        split.amount_owed = round(amount_owed, 2)

    return render(request, 'bill_detail.html', {
        'bill': bill,
        'bill_splits': bill_splits,
        'total_bill_with_tax_and_tip': total_bill_with_tax_and_tip,
        'tip_amount': round(tip_amount, 2),
    })