from django.db import models
from django.conf import settings

# Create your models here.

class Salary(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salaries')
    year = models.IntegerField()
    month = models.IntegerField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    meal_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    childcare_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    car_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_salary = self.base_salary + self.overtime_pay + self.meal_allowance + self.childcare_allowance + self.car_allowance
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.year}/{self.month}"
