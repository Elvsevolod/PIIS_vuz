# ИС ВУЗа — Информационная система управления учебным процессом

Веб-приложение для автоматизации работы деканата, кафедр и преподавателей: учебные планы, распределение нагрузки, дипломные работы, электронные ведомости.

## Стек

| Слой | Технология |
|---|---|
| Бэкенд | FastAPI + SQLAlchemy + PostgreSQL |
| Фронтенд | Flet (Python) |
| Инфраструктура | Docker Compose |
| Аутентификация | JWT (python-jose + bcrypt) |

---

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone <repo-url>
cd "10 лаба"
```

### 2. Настроить переменные окружения

```bash
cp backend/.env.example backend/.env
```

Сгенерируйте секретный ключ и замените `SECRET_KEY` в `backend/.env`:

```bash
openssl rand -hex 32
```

Готовый `.env` выглядит так:

```env
DATABASE_URL=postgresql://postgres:uis_password123@db:5432/uis_db
SECRET_KEY=<ваш-сгенерированный-ключ>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### 3. Запустить бэкенд и базу данных

```bash
docker compose up -d
```

Бэкенд будет доступен по адресу: **http://localhost:8000**

Документация API (Swagger): **http://localhost:8000/docs**

### 4. Запустить фронтенд

```bash
cd frontend
pip install -r requirements.txt
python src/main.py
```

Фронтенд откроется в браузере по адресу: **http://localhost:8500**

---

## Учётные данные по умолчанию

При первом запуске база автоматически заполняется тестовыми данными:

| Роль | Логин | Пароль |
|---|---|---|
| Администратор | `admin` | `admin123` |

Остальные роли (декан, зав. кафедрой, преподаватель) создаются через панель администратора.

---

## Структура проекта

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py              # Зависимости: аутентификация, проверка ролей
│   │   │   └── endpoints/
│   │   │       ├── auth.py          # POST /login, GET /me
│   │   │       ├── faculties.py     # CRUD факультетов
│   │   │       ├── departments.py   # CRUD кафедр
│   │   │       ├── teachers.py      # CRUD преподавателей, метаданные
│   │   │       ├── students.py      # Группы и студенты
│   │   │       ├── plans.py         # Дисциплины, учебные планы, поручения кафедрам
│   │   │       ├── load.py          # Распределение нагрузки на преподавателей
│   │   │       └── grades.py        # Дипломные работы, аттестация
│   │   ├── core/
│   │   │   ├── config.py            # Настройки (переменные окружения)
│   │   │   ├── database.py          # Подключение к БД, сессии
│   │   │   ├── security.py          # Хеширование паролей, JWT-токены
│   │   │   └── seed.py              # Начальное заполнение БД
│   │   ├── models/
│   │   │   └── models.py            # SQLAlchemy-модели (17 таблиц)
│   │   ├── schemas/
│   │   │   └── schemas.py           # Pydantic-схемы (request/response)
│   │   └── main.py                  # Точка входа FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.py                  # Точка входа Flet
│   │   ├── api_client.py            # HTTP-клиент к бэкенду
│   │   └── views/
│   │       ├── login_view.py        # Экран входа
│   │       ├── main_shell.py        # Навигация (sidebar + header)
│   │       ├── dean_plans_view.py   # Учебные планы (деканат)
│   │       ├── dean_students_view.py # Группы и студенты (деканат)
│   │       ├── dept_load_view.py    # Распределение нагрузки (кафедра)
│   │       ├── dept_diplomas_view.py # Дипломные работы (кафедра)
│   │       └── teacher_grades_view.py # Аттестация (преподаватель)
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## Роли и доступ

| Роль | Возможности |
|---|---|
| `admin` | Полный доступ ко всем разделам |
| `dean` | Учебные планы, группы, студенты |
| `department_head` | Распределение нагрузки, дипломные работы |
| `teacher` | Просмотр нагрузки, выставление оценок |

---

## API (основные эндпоинты)

| Метод | Путь | Доступ |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Все |
| `GET` | `/api/v1/auth/me` | Авторизованные |
| `GET/POST/DELETE` | `/api/v1/faculties/` | Чтение — все, запись — admin |
| `GET/POST/DELETE` | `/api/v1/departments/` | Чтение — все, запись — admin |
| `GET/POST/DELETE` | `/api/v1/teachers/` | Чтение — все, запись — admin |
| `GET/POST/PUT/DELETE` | `/api/v1/students/` | Чтение — все, запись — dean |
| `GET/POST/DELETE` | `/api/v1/plans/*` | Чтение — все, запись — dean |
| `GET/POST/DELETE` | `/api/v1/load/` | Чтение — все, запись — department_head |
| `GET/POST/DELETE` | `/api/v1/grades/*` | Зависит от эндпоинта |

Полная документация — **http://localhost:8000/docs**

---

## Команды Docker Compose

```bash
docker compose up -d          # Запустить все сервисы
docker compose down           # Остановить
docker compose down -v        # Остановить и удалить том с данными
docker compose logs -f backend # Логи бэкенда
docker compose restart backend # Перезапустить бэкенд
```
