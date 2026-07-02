@echo off
echo ====================================
echo  TaskFlow AI Manager - Setup
echo ====================================
echo.
echo Installing dependencies...
pip install django==4.2.7 groq==1.2.0
echo.
echo Running database migrations...
python manage.py makemigrations tasks
python manage.py migrate
echo.
echo Creating admin user (admin / admin123)...
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@taskflow.com','admin123')"
echo.
echo ====================================
echo  Setup Complete!
echo  Run: python manage.py runserver
echo  Open: http://127.0.0.1:8000
echo  Admin: http://127.0.0.1:8000/admin
echo ====================================
pause
