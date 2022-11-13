python3 -m venv venv

source venv/bin/activate

pip install django
pip install pillow
pip install djangorestframework
pip install geopy
pip install django-apscheduler

python3 manage.py makemigrations
python3 manage.py makemigrations # for some reason, sometimes not all the migrations are made
python3 manage.py migrate
