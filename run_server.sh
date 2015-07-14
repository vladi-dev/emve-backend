FLASK_UWSGI_DEBUG=true /usr/home/vagrant/.env/bin/uwsgi --http 0.0.0.0:5000 --http-websockets --master  --gevent 100 --wsgi app:app --python-autoreload 1 --catch-exceptions


