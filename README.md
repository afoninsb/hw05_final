# hw05_final

Блогоплатформа для любителей писать и читать статьи


## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:afoninsb/hw05_final.git
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Создать супераользователя:

```
python3 manage.py createsuperuser
```

Запустить проект:

```
python3 manage.py runserver
```

## Управление проектом

Управление проектом происходит в админке по адресу: http://localhost:8000/admin/


## 🚀 About Me
I'm a backend-developer...


