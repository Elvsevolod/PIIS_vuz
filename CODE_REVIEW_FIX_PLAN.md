# План исправлений по Code Review

**Дата:** 2026-05-26  
**Источник:** Code Review ИС ВУЗа (10 лаба)

---

## Этап 1: Критические исправления безопасности ✅

- [x] 1.1 CORS: убрать `allow_credentials=True` при `allow_origins=["*"]` — `backend/app/main.py:47-49`
- [x] 1.2 SECRET_KEY: оставить только обязательное чтение из `.env`, убрать дефолт — `backend/app/core/config.py:4`
- [x] 1.3 DATABASE_URL: убрать пароль из дефолта, только `.env` — `backend/app/core/config.py:4`
- [x] 1.4 Добавить `.env.example` с описанием переменных
- [x] 1.5 docker-compose.yml: убрать SECRET_KEY из environment → `${SECRET_KEY}`

## Этап 2: Ролевой контроль доступа ✅

- [x] 2.1 `api/deps.py`: добавить функции `check_dean`, `check_department_head`, `check_teacher_or_admin`
- [x] 2.2 `students.py`: защитить create/delete группы и студентов (admin + dean)
- [x] 2.3 `plans.py`: защитить create/delete дисциплин, элементов плана, поручений (admin + dean)
- [x] 2.4 `grades.py`: защитить assign_diploma (department_head), assign_grade (teacher/admin)
- [x] 2.5 `load.py`: защитить create/delete нагрузки (department_head)

## Этап 3: Баги и ошибки ✅

- [x] 3.1 `load.py:85`: убрать опечатку `"proffesor"` → убрать мёртвое условие
- [x] 3.2 `security.py:20-21`: `datetime.utcnow()` → `datetime.now(timezone.utc)`
- [x] 3.3 `load.py:14-19`: N+1 запросы в `get_teacher_workload` → `joinedload`

## Этап 4: Качество кода ✅ (частично)

- [ ] 4.1 Убрать магические индексы в views (сохранять ссылки на кнопки)
- [x] 4.2 `dept_load_view.py:19`, `dept_diplomas_view.py:18`: `current_dept_id` из `linked_entity_id`
- [x] 4.3 `teacher_grades_view.py:121`: убрать поиск «Ивана», брать первого преподавателя
- [x] 4.4 `api_client.py`: различать типы исключений (ConnectionError, Timeout, HTTPError)
- [x] 4.5 `seed.py`: консолидировать коммиты (flush вместо commit)
- [x] 4.6 `schemas.py:9-10`: `TokenPayload.sub` — убрать Optional

## Этап 5: Инфраструктура ✅

- [x] 5.1 `docker-compose.yml`: healthcheck для PostgreSQL + `depends_on` с `condition: service_healthy`
- [x] 5.2 `backend/Dockerfile`: убрать `--reload`
- [x] 5.3 `requirements.txt`: обновить `requests` до `>=2.31.0`
- [x] 5.4 `alembic` оставлен (полезен для будущих миграций)
- [x] 5.5 `passlib` заменён на `bcrypt==4.1.3` (используется напрямую в `security.py`)

---

## Осталось (deferred / низкий приоритет)

- [ ] 4.1 Магические индексы в views — рефакторинг, требует аккуратного переписывания UI-кода
- [ ] DELETE-эндпоинты: try/except IntegrityError → 409 Conflict
- [ ] N+1 в `get_teachers_with_validation` — требует изменения сигнатуры `validate_teacher_assignment`
- [ ] Тесты (pytest + httpx)
- [ ] Логирование (logging вместо print)

**Итог:** 17 из 18 пунктов выполнены. Остался рефакторинг магических индексов в UI (п. 4.1).
