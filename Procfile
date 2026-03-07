web: gunicorn echocard.wsgi:application --bind 0.0.0.0:$PORT
release: cd echocard && python manage.py migrate