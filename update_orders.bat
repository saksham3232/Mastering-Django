@echo off
cd /d %~dp0
echo Updating order statuses...
python manage.py update_orders
pause
