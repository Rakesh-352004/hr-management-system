from django.contrib import admin
from django.urls import path
from employees import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("", views.dashboard, name="dashboard"),

    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),

    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.department_create, name="department_create"),
    path("departments/<int:pk>/delete/", views.department_delete, name="department_delete"),

    path("attendance/", views.attendance_list, name="attendance_list"),
    path("attendance/add/", views.attendance_create, name="attendance_create"),

    path("leaves/", views.leave_list, name="leave_list"),
    path("leaves/add/", views.leave_create, name="leave_create"),
    path("leaves/<int:pk>/status/<str:status>/", views.leave_status, name="leave_status"),

    path("salary/", views.salary_list, name="salary_list"),
    path("salary/add/", views.salary_create, name="salary_create"),

    path("performance/", views.performance_list, name="performance_list"),
    path("performance/add/", views.performance_create, name="performance_create"),
]
