from django.contrib import admin
from .models import (
    Department, Employee, Attendance,
    Leave, Salary, Performance
)

admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Attendance)
admin.site.register(Leave)
admin.site.register(Salary)
admin.site.register(Performance)
