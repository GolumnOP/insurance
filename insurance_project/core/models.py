import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Customer(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.PositiveIntegerField()

    def __str__(self):
        return self.full_name


class Car(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    vin = models.CharField(max_length=17, unique=True)
    model = models.CharField(max_length=20)
    year = models.PositiveIntegerField(validators=[
        MinValueValidator(1950),
        MaxValueValidator(datetime.datetime.now().year)
    ],
        help_text="Enter the year (e.g., YYYY)")


class InsurancePolicy(models.Model):
    STATUS = [
        ("AE", "Active"),
        ("ED", "Expired"),
        ("CD", "Canceled"),
    ]
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    policy_number = models.PositiveIntegerField(unique=True, blank=False, null=False)
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2)
    premium = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=3, choices=STATUS, default="AE")

    def one_police_validation(self):
        """
        2)
        У одной машины не может быть более одного активного полиса.
        """
        if self.status == "AE":
            existing_active_police = InsurancePolicy.objects.filter(
                car=self.car,
                status="AE"
            ).exclude(pk=self.pk).exists()
            if existing_active_police:
                raise ValidationError(f"Car {self.car} already has an active police")

    def save(self, *args, **kwargs):
        """
        1)
        если машине ≤ 3 лет → 0.05
        если машине 4–10 лет → 0.08
        если > 10 лет → 0.12
        """
        current_year = datetime.now().year

        if current_year - self.car.year <= 3:
            coefficient = 0.05
        elif 4 <= current_year - self.car.year <= 10:
            coefficient = 0.08
        elif current_year - self.car.year > 10:
            coefficient = 0.12

        self.premium = self.coverage_amount * coefficient
        super().save(*args, **kwargs)
