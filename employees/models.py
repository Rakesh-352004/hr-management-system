from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )
    employee_id = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    designation = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["employee_id"]

    def __str__(self):
        name = self.user.get_full_name() or self.user.username
        return f"{self.employee_id} - {name}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Leave", "Leave"),
        ("Half Day", "Half Day"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                name="unique_employee_attendance"
            )
        ]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date}"


class Leave(models.Model):
    LEAVE_TYPES = [
        ("Casual", "Casual"),
        ("Sick", "Sick"),
        ("Earned", "Earned"),
        ("Unpaid", "Unpaid"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leaves"
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_on"]

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type}"


class Salary(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="salary_records"
    )
    month = models.DateField(help_text="Use the first day of the salary month")
    basic = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-month"]

    @property
    def net_salary(self):
        return self.basic + self.allowance - self.deduction

    def __str__(self):
        return f"{self.employee.employee_id} - {self.month:%Y-%m}"


class Performance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="performance_records"
    )
    review_date = models.DateField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    goals = models.TextField(blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        ordering = ["-review_date"]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.rating}/5"
