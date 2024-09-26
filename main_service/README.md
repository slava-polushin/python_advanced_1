## Запуск

Для запуска сервиса вне докера запустить

fastapi dev main_service/main.py

Описание интерфейсов сервиса после его старта можно получить по url:
http://127.0.0.1:8000/docs

Адмнистрирование ведомой в БД информацией можно выполнять по url:
http://127.0.0.1:8000/admin

Описание интерфейсов 'coordinates_srv' можно получить по url:
http://localhost:8001/docs

Описание интерфейсов 'price_srv' можно получить по url:
http://localhost:8002/docs

Администрирование хранилища redis (redisinsight):
http://127.0.0.1:5540/

Администрирование rabbitMQ (user / password)
http://127.0.0.1:15672/

Администрирование celery (mher/flower):
http://localhost:5555/
