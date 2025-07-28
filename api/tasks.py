from celery import shared_task
import pandas as pd
from .models import Customer, Loan

@shared_task
def ingest_data():
    # Ingest Customer Data
    customer_df = pd.read_excel('customer_data.xlsx')
    for _, row in customer_df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['Customer ID'],
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'phone_number': row['Phone Number'],
                'monthly_salary': row['Monthly Salary'],
                'approved_limit': row['Approved Limit'],
                # Age is not in the excel, will be added via /register
                # Current Debt will be calculated later
            }
        )

    # Ingest Loan Data
    loan_df = pd.read_excel('loan_data.xlsx')
    for _, row in loan_df.iterrows():
        Loan.objects.update_or_create(
            loan_id=row['Loan ID'],
            customer_id=row['Customer ID'],
            defaults={
                'loan_amount': row['Loan Amount'],
                'tenure': row['Tenure'],
                'interest_rate': row['Interest Rate'],
                'monthly_repayment': row['Monthly payment'],
                'emis_paid_on_time': row['EMIs paid on Time'],
                'start_date': row['Date of Approval'],
                'end_date': row['End Date'],
            }
        )
    return "Data ingestion complete."