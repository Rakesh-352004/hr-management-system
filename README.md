# HRMS - Employee / HR Management System

Python Django project implementing:
- Admin / Employee login
- Employee management
- Department management
- Attendance
- Leave management + approval/rejection
- Salary
- Performance tracking
- Dashboard
- Search
- Role-based access
- SQLite database
- Bootstrap UI

## Windows setup

```bat
cd HR_Management_Python_Django
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:
http://127.0.0.1:8000/

Admin:
http://127.0.0.1:8000/admin/

When an employee is created from the HRMS employee page, the default password is:
Employee@123

The employee should change that password from Django admin/profile functionality before production use.
