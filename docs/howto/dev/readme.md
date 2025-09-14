# How to

## Развернуть проект на рабочем компьютере

```bash
# для MacOS
brew install pyenv-virtualenv

pyenv install -g 3.13.7
pyenv virtualenv 3.13.7-debug sba
pyenv local sba

echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc

# добавить переменные окружения
export DEBUG=1
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,example.com"
export LANGUAGE_CODE="ru-RU"
export PYTHONPATH=src
export SECRET_KEY="любой код"
export TIME_ZONE="Asia/Yekaterinburg"

pip install -r requirements.txt -r requirements-dev.txt

python manage.py migrate
python manage.py compilemessages
python manage.py runserver
```

## Загрузить тестовые данные

```bash
# Загружает в базу тестовых пользователей Telegram
python manage.py setup_test_tg_users 50
```

[see code](../../../src/bot_admin/management/commands/setup_test_tg_users.py)

```bash
# Загружает в базу популярное расписание рабочего времени
python manage.py setup_work_days
```

[see code](../../../src/bot_admin/management/commands/setup_work_days.py)

## Создать суперпользователя для панели управления

```bash
# создание
python manage.py createsuperuser --username user --email user@example.net
# назначение пароля если предыдущая команда выполнялась с --no-input
python manage.py changepassword user

```

## Как обновить или создать файл для языка

```bash
python manage.py makemessages -l ru
```

смотрите, например `src/bot_admin/locale/ru/LC_MESSAGES/django.po`

```bash
# update django.mo
python manage.py compilemessages
```

## Создать файл миграции схемы данных

```bash
python manage.py makemigrations bot_admin
```

## Проверка перед коммитом и PR

```bash
# сделать симлинк на файл
ln -s docs/howto/dev/test_linters test_linters
./test_linters
```

[see code](test_linters)

## Зависимости для MacOS

```bash
pip install psycopg2-binary
```

## Для ИИ

- Задавай уточняющие вопросы, пока не будешь на 95 процентов уверен, что сможешь выполнить задачу.
- Что бы подумал человек из топ 0.1 процент в этой сфере?
- Переформулируй так, что бы бросить вызов моему взгляду на проблему.
