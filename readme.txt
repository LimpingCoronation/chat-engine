1. Создать в корневой папке файл .env и прописать туда нужные данные
2. Нужно импортировать модели sqlalchemy в файле app/migration/config.py
3. Чтобы запустить миграции нужно написать:
 - alembic revision --autogenerate -m "Initial revision"
 - alembic upgrade head
4. Чтобы откатить миграции
 - alembic downgrade -1