from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.db.models import Sum
from .forms import BillForm
from .models import Bill, BillSplit
from django.contrib.auth.decorators import login_required

def login_view(request):
    return render(request, "login.html")

@login_required
def profile(request):
    user = request.user  # Get the logged-in user
    # Get the number of bills created by the user
    num_bills = Bill.objects.filter(created_by=user).count()

    # Get the total amount owed by the user
    total_owed = BillSplit.objects.filter(bill__created_by=user, paid=False).aggregate(Sum('amount_owed'))['amount_owed__sum']

    # Default to 0 if no amount is owed (in case the sum is None)
    total_owed = total_owed if total_owed is not None else 0

    context = {
        'user': user,
        'num_bills': num_bills,
        'total_owed': round(total_owed, 2),
    }

    return render(request, "profile.html", context)

def logout_view(request):
  logout(request)
  return redirect("/")

@login_required
def bills_view(request):
    user = request.user  # Get the logged-in user

    # Fetch all bills created by the user
    bills = Bill.objects.filter(created_by=user)

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

        # If total_owed is 0, mark the bill as past (is_current = False)
        if total_owed == 0:
            bill.is_current = False  # Set the bill to past
        else:
            bill.is_current = True  # Otherwise, it is still current

        # Save the calculated total_owed to the bill instance in the database
        bill.total_with_tax_and_tip = total_bill_with_tax_and_tip
        bill.total_owed = total_owed  # Save the total_owed
        bill.save()

    # Fetch current bills (where is_current is True)
    current_bills = Bill.objects.filter(created_by=request.user, is_current=True)

    # Fetch past bills (where is_current is False)
    past_bills = Bill.objects.filter(created_by=request.user, is_current=False)

    # Limit the past bills to the first 3 for display
    limited_past_bills = past_bills[:3]

    # Full list of past bills (for when the user clicks "View All")
    all_past_bills = past_bills

    return render(request, "bills.html", {
        'bills': bills,
        'current_bills': current_bills,
        'limited_past_bills': limited_past_bills,
        'all_past_bills': all_past_bills,
    })

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
        'created_at': bill.created_at,
    })

@login_required
def past_bills(request):
    # Fetch all past bills created by the user where is_current is False
    past_bills = Bill.objects.filter(created_by=request.user, is_current=False).order_by('-created_at')
    past_bills_count = 0

    # Calculate after tip and tax for each bill
    for bill in past_bills:
        tip_percentage_decimal = Decimal(bill.tip_percentage) / 100
        after_tip_tax = (bill.total_amount * (1 + tip_percentage_decimal)) + bill.tax_amount
        bill.after_tip_tax = round(after_tip_tax, 2)  
        past_bills_count += 1

    return render(request, 'past_bills.html', {
        'past_bills': past_bills,
        'past_bills_count': past_bills_count
    })