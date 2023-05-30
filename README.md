# ЯП - Спринт 16 - CI и CD проекта api_yamdb

![example workflow](https://github.com/brideshead/yamb_final/actions/workflows/main.yml/badge.svg)

Проект развернут по адресу: http://51.250.80.17/admin/
## Описание 
 
Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории:«Книги», «Фильмы», «Музыка».

### Как запустить проект:

### Клонируем репозиторий и и переходим в него:

```bash
git clone git@github.com:brideshead/yamdb_final.git
```
```bash
cd yamdb_final
```

### Создаем и активируем виртуальное окружение:
```bash
python3 -m venv venv
```
- Windows:
```bash
source venv/Scripts/activate
```
- Linux:
```bash
source venv/bin/activate
```
### Обновим pip:
```bash
python -m pip install --upgrade pip 
```

### Ставим зависимости из requirements.txt:
```bash
pip install -r api_yamdb/requirements.txt 
```

### Переходим в папку с файлом docker-compose.yaml:
```bash
cd infra
```

### Устанавливаем Docker:
```bash
sudo apt install docker.io
```

### Активируем Docker в системе, что бы при перезагрузке запускался автоматом:
```bash
sudo systemctl enable docker
```
### Запускаем Docker:
```bash
sudo systemctl start docker
```

### В папке infra создаем файл .env с следующим содержимом:
```bash
DB_ENGINE=django.db.backends.postgresql 
DB_NAME=postgres 
POSTGRES_USER=postgres 
POSTGRES_PASSWORD=postgres 
DB_HOST=db 
DB_PORT=5432
```

### В settings.py добавляем следующее:
```python
from dotenv import load_dotenv

load_dotenv()

...

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
    }
}
```
### Далее в папке где у нас находится файл settings.py создаем файл .env:
```bash
touch .env
```
```bash
nano .env
```
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=test_base
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_pass
DB_HOST=127.0.0.1
DB_PORT=5432
```
### Делаем миграции:
```bash
python manage.py migrate
```

### 
Поднимаем контейнеры:
    infra_db - база,
    infra_web - веб,
    nfra_nginx - nginx сервер
   
```bash
sudo docker-compose up -d --build 
```

### Выполняем миграции в контейнере infra_web:
```bash
sudo docker-compose exec web python manage.py makemigrations reviews 
```
```bash
sudo docker-compose exec web python manage.py migrate --run-syncdb
```
### Создаем суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser 
```

### Собираем статику:
```bash
docker-compose exec web python manage.py collectstatic --no-input 
```

### Создаем дамп базы данных (нет в текущем репозитории):
```bash
docker-compose exec web python manage.py dumpdata > dumpPostrgeSQL.json 
```

### Останавливаем контейнеры:
```bash
docker-compose down -v 
```
### Шаблон наполнения .env (не включен в текущий репозиторий) расположенный по пути infra/.env
```
DB_ENGINE=django.db.backends.postgresql 
DB_NAME=postgres 
POSTGRES_USER=postgres 
POSTGRES_PASSWORD=postgres 
DB_HOST=db 
DB_PORT=5432 
```
### Документация API YaMDb 
Документация доступна по эндпойнту: http://51.250.80.17/redoc/
