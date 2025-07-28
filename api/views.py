from django.db.models import Max
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from datetime import date
import math
import pandas as pd
from django.db.models import Sum

# [cite_start]Helper function to calculate credit score based on historical data [cite: 48]
def calculate_credit_score(customer_id):
    try:
        customer = Customer.objects.get(pk=customer_id)
        loans = Loan.objects.filter(customer=customer)
    except Customer.DoesNotExist:
        return 0, 0 # Return 0 for score and current loan sum

    # i. [cite_start]Past Loans paid on time [cite: 50]
    total_emis_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
    total_tenure = sum(loan.tenure for loan in loans)
    
    paid_on_time_component = (total_emis_paid_on_time / total_tenure) * 25 if total_tenure > 0 else 25

    # ii. [cite_start]No of loans taken in past [cite: 51]
    num_loans_component = min(len(loans), 10) * 5

    # iii. [cite_start]Loan activity in current year [cite: 53]
    current_year_loans = sum(1 for loan in loans if loan.start_date.year == date.today().year)
    activity_component = min(current_year_loans, 5) * 5
    
    # Sum of all current loans for the customer
    current_loans = loans.filter(end_date__gt=date.today())
    sum_of_current_loans = current_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0

    # [cite_start]v. If sum of current loans > approved limit, credit score = 0 [cite: 57]
    if sum_of_current_loans > customer.approved_limit:
        return 0, sum_of_current_loans

    # iv. [cite_start]Loan approved volume [cite: 55] (Calculated inversely: higher volume -> lower score)
    approved_volume_component = (1 - min(sum_of_current_loans / customer.approved_limit, 1)) * 40 if customer.approved_limit > 0 else 0

    credit_score = round(paid_on_time_component + num_loans_component + activity_component + approved_volume_component)
    
    return min(credit_score, 100), sum_of_current_loans


# [cite_start]Endpoint: /register [cite: 38]
class RegisterView(APIView):
    def post(self, request):
        # Calculate a new, unique customer_id
        latest_id = Customer.objects.aggregate(max_id=Max('customer_id'))['max_id'] or 0
        new_customer_id = latest_id + 1

        monthly_income = request.data.get('monthly_income')
        approved_limit = round(36 * monthly_income / 100000) * 100000

        customer_data = {
            'customer_id': new_customer_id, # Add the new customer_id
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'age': request.data.get('age'),
            'monthly_salary': monthly_income,
            'phone_number': request.data.get('phone_number'),
            'approved_limit': approved_limit,
        }

        serializer = CustomerSerializer(data=customer_data)
        if serializer.is_valid():
            customer = serializer.save()
            # The response body stays the same, as per the spec
            response_data = {
                'customer_id': customer.customer_id,
                'name': f"{customer.first_name} {customer.last_name}",
                'age': customer.age,
                'monthly_income': customer.monthly_salary,
                'approved_limit': customer.approved_limit,
                'phone_number': customer.phone_number,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# [cite_start]Endpoint: /check-eligibility [cite: 47]
class CheckEligibilityView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')
        
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        credit_score, sum_of_current_loans = calculate_credit_score(customer_id)
        
        approval = False
        corrected_interest_rate = interest_rate

        # [cite_start]If sum of all current EMIs > 50% of monthly salary, don't approve [cite: 64]
        current_emis = Loan.objects.filter(customer=customer, end_date__gt=date.today()).aggregate(Sum('monthly_repayment'))['monthly_repayment__sum'] or 0
        if current_emis > 0.5 * customer.monthly_salary:
            approval = False
        # If sum of current loans + new loan > approved limit, score is 0
        elif (sum_of_current_loans + loan_amount) > customer.approved_limit:
            credit_score = 0
            approval = False
        else:
            # Check eligibility based on credit score
            if credit_score > 50:  # credit score above 50
                approval = True
            elif 30 < credit_score <= 50:  # credit score between 31 and 50
                approval = True
                if interest_rate <= 12:
                    corrected_interest_rate = 12.0
            elif 10 < credit_score <= 30:  # credit score between 11 and 30
                approval = True
                if interest_rate <= 16:
                    corrected_interest_rate = 16.0
            else:  # credit_score <= 10
                approval = False

        monthly_installment = 0
        if approval:
            # [cite_start]Monthly installment using compound interest formula [cite: 38]
            r = (corrected_interest_rate / 100) / 12
            p = loan_amount
            n = tenure
            if r > 0:
                monthly_installment = p * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
            else:
                monthly_installment = p / n if n > 0 else 0

        # [cite_start]Response body as per specification [cite: 71]
        response_data = {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': round(monthly_installment, 2),
        }

        return Response(response_data, status=status.HTTP_200_OK)

# [cite_start]Endpoint: /create-loan [cite: 72]
class CreateLoanView(APIView):
    def post(self, request, *args, **kwargs):
        # Re-run eligibility check to get approval status and corrected values
        eligibility_view = CheckEligibilityView()
        eligibility_response = eligibility_view.post(request)
        eligibility_data = eligibility_response.data

        loan_approved = eligibility_data.get('approval', False)
        message = ''

        if loan_approved:
            customer = Customer.objects.get(pk=eligibility_data['customer_id'])
            new_loan = Loan.objects.create(
                customer=customer,
                loan_amount=request.data.get('loan_amount'),
                tenure=eligibility_data['tenure'],
                interest_rate=eligibility_data['corrected_interest_rate'],
                monthly_repayment=eligibility_data['monthly_installment'],
                emis_paid_on_time=0,
                start_date=date.today(),
                end_date=date.today() + pd.DateOffset(months=eligibility_data['tenure']),
            )
            response_data = {
                'loan_id': new_loan.loan_id,
                'customer_id': customer.customer_id,
                'loan_approved': True,
                'message': 'Loan approved and created successfully',
                'monthly_installment': new_loan.monthly_repayment,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            message = 'Loan not approved based on eligibility criteria.'
            response_data = {
                'loan_id': None,
                'customer_id': eligibility_data['customer_id'],
                'loan_approved': False,
                'message': message,
                'monthly_installment': None,
            }
            return Response(response_data, status=status.HTTP_200_OK)


# [cite_start]Endpoint: /view-loan/loan_id [cite: 79]
class ViewLoanView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(pk=loan_id)
            customer = loan.customer
            # [cite_start]Response body as per specification [cite: 82]
            customer_data = {
                'id': customer.customer_id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'phone_number': customer.phone_number,
                'age': customer.age,
            }
            response_data = {
                'loan_id': loan.loan_id,
                'customer': customer_data,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_repayment,
                'tenure': loan.tenure,
            }
            return Response(response_data)
        except Loan.DoesNotExist:
            return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)

# [cite_start]Endpoint: /view-loans/customer_id [cite: 83]
class ViewLoansByCustomerView(APIView):
    def get(self, request, customer_id):
        try:
            Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
            
        loans = Loan.objects.filter(customer_id=customer_id)
        
        response_data = []
        for loan in loans:
            # [cite_start]Response body for each loan item as per specification [cite: 85, 87]
            loan_item = {
                'loan_id': loan.loan_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_repayment,
                'repayments_left': loan.tenure - loan.emis_paid_on_time,
            }
            response_data.append(loan_item)
            
        return Response(response_data)