web: python manage.py migrate && python manage.py collectstatic && gunicorn easycook.wsgi:application --bind 0.0.0.0:$PORT
