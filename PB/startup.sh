python -m venv venv

venv/Scripts/activate

pip install django
pip install pillow
pip install djangorestframework
pip install geopy

python manage.py makemigrations
python manage.py migrate
