web: python manage.py migrate --noinput && \
     python manage.py collectstatic --noinput && \
     python manage.py shell < customtools/create_superuser.py && \
     gunicorn easycook.wsgi:application --bind 0.0.0.0:$PORT