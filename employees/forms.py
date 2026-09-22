from django import forms
from django.contrib.auth.models import User
from .models import (
    Employee, Department, Attendance,
    Leave, Salary, Performance
)


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "phone",
            "address",
            "department",
            "designation",
            "joining_date",
            "basic_salary",
            "is_active",
        ]
        widgets = {
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "basic_salary": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields["username"].initial = user.username
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = User.objects.filter(username=username)

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.user.pk)

        if qs.exists():
            raise forms.ValidationError("This username already exists.")

        return username

    def save(self, commit=True):
        employee = super().save(commit=False)

        if employee.pk:
            user = employee.user
            user.username = self.cleaned_data["username"]
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.email = self.cleaned_data["email"]
            user.save()
        else:
            user = User.objects.create_user(
                username=self.cleaned_data["username"],
                password="Employee@123",
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                email=self.cleaned_data["email"],
            )
            employee.user = user

        if commit:
            employee.save()

        return employee


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3})
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["employee", "date", "check_in", "check_out", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "check_in": forms.TimeInput(attrs={"type": "time"}),
            "check_out": forms.TimeInput(attrs={"type": "time"}),
        }


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = [
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")

        if start and end and end < start:
            raise forms.ValidationError(
                "End date cannot be before start date."
            )

        return cleaned


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = [
            "employee",
            "month",
            "basic",
            "allowance",
            "deduction",
            "paid",
        ]
        widgets = {
            "month": forms.DateInput(attrs={"type": "date"}),
            "basic": forms.NumberInput(attrs={"step": "0.01"}),
            "allowance": forms.NumberInput(attrs={"step": "0.01"}),
            "deduction": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def clean(self):
        cleaned = super().clean()
        basic = cleaned.get("basic") or 0
        allowance = cleaned.get("allowance") or 0
        deduction = cleaned.get("deduction") or 0

        if basic + allowance - deduction < 0:
            raise forms.ValidationError("Net salary cannot be negative.")

        return cleaned


class PerformanceForm(forms.ModelForm):
    class Meta:
        model = Performance
        fields = [
            "employee",
            "review_date",
            "rating",
            "goals",
            "feedback",
        ]
        widgets = {
            "review_date": forms.DateInput(attrs={"type": "date"}),
            "rating": forms.NumberInput(
                attrs={"step": "0.1", "min": "0", "max": "5"}
            ),
            "goals": forms.Textarea(attrs={"rows": 3}),
            "feedback": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 0 or rating > 5:
            raise forms.ValidationError("Rating must be between 0 and 5.")
        return rating
