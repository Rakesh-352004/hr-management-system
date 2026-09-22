from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    EmployeeForm, DepartmentForm, AttendanceForm,
    LeaveForm, SalaryForm, PerformanceForm
)
from .models import (
    Employee, Department, Attendance,
    Leave, Salary, Performance
)


def is_admin(user):
    return user.is_staff or user.is_superuser


def admin_required(request):
    if not is_admin(request.user):
        messages.error(request, "Admin/HR access required.")
        return False
    return True


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    today = date.today()

    if is_admin(request.user):
        employees = Employee.objects.filter(is_active=True)

        context = {
            "is_admin": True,
            "employee_count": employees.count(),
            "department_count": Department.objects.count(),
            "pending_leaves": Leave.objects.filter(
                status="Pending"
            ).count(),
            "present_today": Attendance.objects.filter(
                date=today,
                status="Present"
            ).count(),
            "salary_total": Salary.objects.aggregate(
                total=Sum("basic")
            )["total"] or Decimal("0"),
            "average_rating": Performance.objects.aggregate(
                avg=Avg("rating")
            )["avg"] or Decimal("0"),
        }
    else:
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            employee = None

        context = {
            "is_admin": False,
            "employee": employee,
            "my_attendance": (
                Attendance.objects.filter(employee=employee).count()
                if employee else 0
            ),
            "my_pending_leaves": (
                Leave.objects.filter(
                    employee=employee,
                    status="Pending"
                ).count()
                if employee else 0
            ),
            "my_salary": (
                Salary.objects.filter(employee=employee)
                .aggregate(total=Sum("net_salary"))["total"] or 0
                if employee else 0
            ),
            "my_average_rating": (
                Performance.objects.filter(employee=employee)
                .aggregate(avg=Avg("rating"))["avg"] or 0
                if employee else 0
            ),
        }

    return render(request, "dashboard.html", context)


@login_required
def employee_list(request):
    if is_admin(request.user):
        employees = Employee.objects.select_related(
            "user", "department"
        ).all()

        query = request.GET.get("q", "").strip()

        if query:
            employees = employees.filter(
                user__first_name__icontains=query
            ) | employees.filter(
                user__last_name__icontains=query
            ) | employees.filter(
                employee_id__icontains=query
            ) | employees.filter(
                designation__icontains=query
            )

        return render(
            request,
            "employees/list.html",
            {"employees": employees, "query": query}
        )

    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        employee = None

    return render(
        request,
        "employees/list.html",
        {"employees": [employee] if employee else [], "query": ""}
    )


@login_required
def employee_create(request):
    if not admin_required(request):
        return redirect("employee_list")

    form = EmployeeForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(
            request,
            "Employee created. Default password: Employee@123"
        )
        return redirect("employee_list")

    return render(
        request,
        "form.html",
        {"form": form, "title": "Add Employee"}
    )


@login_required
def employee_update(request, pk):
    if not admin_required(request):
        return redirect("employee_list")

    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, instance=employee)

    if form.is_valid():
        form.save()
        messages.success(request, "Employee updated successfully.")
        return redirect("employee_list")

    return render(
        request,
        "form.html",
        {"form": form, "title": "Edit Employee"}
    )


@login_required
def employee_delete(request, pk):
    if not admin_required(request):
        return redirect("employee_list")

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        user = employee.user
        employee.delete()
        user.delete()
        messages.success(request, "Employee deleted successfully.")

    return redirect("employee_list")


@login_required
def department_list(request):
    departments = Department.objects.annotate(
        employee_count=Count("employee")
    )

    return render(
        request,
        "departments/list.html",
        {"departments": departments}
    )


@login_required
def department_create(request):
    if not admin_required(request):
        return redirect("department_list")

    form = DepartmentForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Department created.")
        return redirect("department_list")

    return render(
        request,
        "form.html",
        {"form": form, "title": "Add Department"}
    )


@login_required
def department_delete(request, pk):
    if not admin_required(request):
        return redirect("department_list")

    if request.method == "POST":
        department = get_object_or_404(Department, pk=pk)
        department.delete()
        messages.success(request, "Department deleted.")

    return redirect("department_list")


@login_required
def attendance_list(request):
    if is_admin(request.user):
        records = Attendance.objects.select_related(
            "employee__user"
        ).all()
    else:
        try:
            employee = request.user.employee_profile
            records = Attendance.objects.filter(
                employee=employee
            ).select_related("employee__user")
        except Employee.DoesNotExist:
            records = Attendance.objects.none()

    return render(
        request,
        "attendance/list.html",
        {"records": records}
    )


@login_required
def attendance_create(request):
    if not admin_required(request):
        return redirect("attendance_list")

    form = AttendanceForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Attendance saved.")
        return redirect("attendance_list")

    return render(
        request,
        "form.html",
        {"form": form, "title": "Mark Attendance"}
    )


@login_required
def leave_list(request):
    if is_admin(request.user):
        leaves = Leave.objects.select_related(
            "employee__user"
        ).all()
    else:
        try:
            employee = request.user.employee_profile
            leaves = Leave.objects.filter(
                employee=employee
            ).select_related("employee__user")
        except Employee.DoesNotExist:
            leaves = Leave.objects.none()

    return render(
        request,
        "leaves/list.html",
        {"leaves": leaves}
    )


@login_required
def leave_create(request):
    if is_admin(request.user):
        form = LeaveForm(request.POST or None)
    else:
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            messages.error(request, "Employee profile not found.")
            return redirect("dashboard")

        form = LeaveForm(request.POST or None)
        form.fields["employee"].queryset = Employee.objects.filter(
            pk=employee.pk
        )
        form.fields["employee"].initial = employee

    if form.is_valid():
        leave = form.save(commit=False)

        if not is_admin(request.user):
            leave.employee = request.user.employee_profile

        leave.save()
        messages.success(request, "Leave request submitted.")
        return redirect("leave_list")

    return render(
        request,
        "form.html",
        {"form": form, "title": "Apply Leave"}
    )


@login_required
def leave_status(request, pk, status):
    if not admin_required(request):
        return redirect("leave_list")

    if request.method == "POST" and status in ["Approved", "Rejected"]:
        leave = get_object_or_404(Leave, pk=pk)
        leave.status = status
        leave.save()
        messages.success(request, f"Leave {status.lower()}.")

    return redirect("leave_list")


@login_required
def salary_list(request):
    if is_admin(request.user):
        salaries = Salary.objects.select_related(
            "employee__user"
        ).all()
    else:
        try:
            employee = request.user.employee_profile
            salaries = Salary.objects.filter(
                employee=employee
            ).select_related("employee__user")
        except Employee.DoesNotExist:
            salaries = Salary.objects.none()

    return render(
        request,
        "salary/list.html",
        {"salaries": salaries}
    )


@login_required
def salary_create(request):
    if not admin_required(request):
        return redirect("salary_list")

    form = SalaryForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Salary record added.")
        return redirect("salary_list")

    return render(
        request,
        "form.html",
        {"form": form, "title": "Add Salary"}
    )


@login_required
def performance_list(request):
    if is_admin(request.user):
        records = Performance.objects.select_related(
            "employee__user"
        ).all()
    else:
        try:
            employee = request.user.employee_profile
            records = Performance.objects.filter(
                employee=employee
            ).select_related("employee__user")
        except Employee.DoesNotExist:
            records = Performance.objects.none()

    return render(
        request,
        "performance/list.html",
        {"records": records}
    )


@login_required
def performance_create(request):
    if not admin_required(request):
        return redirect("performance_list")

    form = PerformanceForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Performance review saved.")
        return redirect("performance_list")

    return render(
        request,
        "form.html",
        {"form": form, "title": "Add Performance Review"}
    )
