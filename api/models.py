from django.db import models

class Customer(models.Model):
    # We will now use Django's default auto-incrementing 'id' as the primary key.
    # The 'customer_id' from the Excel file will be a separate, unique field.
    customer_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    monthly_salary = models.IntegerField()
    phone_number = models.CharField(max_length=20)
    approved_limit = models.IntegerField()
    current_debt = models.FloatField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Loan(models.Model):
    # No changes needed for the Loan model
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_repayment = models.FloatField()
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan ID: {self.loan_id} for {self.customer}"