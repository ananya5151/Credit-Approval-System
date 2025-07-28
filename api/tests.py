from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Customer, Loan
from datetime import date

class APITests(APITestCase):

    def setUp(self):
        """Set up initial data for tests."""
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="Customer",
            age=30,
            monthly_salary=50000,
            phone_number="1234567890",
            approved_limit=200000
        )
        # Create a past loan for eligibility checks
        Loan.objects.create(
            customer=self.customer,
            loan_amount=50000,
            tenure=12,
            interest_rate=10,
            monthly_repayment=4614,
            emis_paid_on_time=10,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )

    def test_register_customer_success(self):
        """
        Ensure we can create a new customer.
        """
        url = reverse('register')
        data = {
            "first_name": "New",
            "last_name": "User",
            "age": 25,
            "monthly_income": 60000,
            "phone_number": "9876543210"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2) # Check that a new customer was created
        # Check if approved_limit was calculated correctly (36 * 60000 rounded to nearest lakh)
        self.assertEqual(response.data['approved_limit'], 2200000)

    def test_check_eligibility_approved(self):
        """
        Test the eligibility of an existing customer who should be approved.
        """
        url = reverse('check-eligibility')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 30000,
            "interest_rate": 15,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['approval'])

    def test_check_eligibility_rejected_high_emi(self):
        """
        Test that a loan is rejected if the sum of current EMIs exceeds 50% of monthly salary.
        """
        # Add another active loan to push the customer over the EMI limit
        Loan.objects.create(
            customer=self.customer,
            loan_amount=200000,
            tenure=12,
            interest_rate=12,
            monthly_repayment=26000, # This EMI is > 50% of 50000 salary
            emis_paid_on_time=1,
            start_date=date.today(),
            end_date=date(2026, 1, 1)
        )
        
        url = reverse('check-eligibility')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 10000,
            "interest_rate": 10,
            "tenure": 6
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['approval'])