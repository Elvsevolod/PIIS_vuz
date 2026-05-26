# План реализации недостающих требований ✅

**Дата:** 2026-05-26  
**На основе:** `DOCS_COMPLIANCE_REPORT.md`

---

## Этап 1: Быстрые backend-фиксы ✅

- [x] 1.1 `students.py` — добавить query-параметры `name` (ilike) и `gradebook_number`
- [x] 1.2 Все DELETE-эндпоинты — обернуть в try/except IntegrityError → 409 Conflict (8 эндпоинтов в 7 файлах)
- [x] 1.3 `load.py` — убрать N+1 в `get_teacher_workload` через `joinedload`

## Этап 2: Административные views ✅

- [x] 2.1 `AdminDirectoriesView` — CRUD факультетов и кафедр (таблицы + диалоги создания/удаления)
- [x] 2.2 `AdminUsersView` — список пользователей, создание/удаление (+ backend эндпоинты `GET/POST/DELETE /api/v1/auth/users`)
- [x] 2.3 `main_shell.py` — подключить новые views к навигации

## Этап 3: Backend для отчётов ✅

- [x] 3.1 `reports.py` — новый endpoint-модуль:
  - `GET /api/v1/reports/teacher-workload` — нагрузка преподавателя за семестр (с фильтрами: teacher_id, department_id, semester)
  - `GET /api/v1/reports/diploma-distribution` — распределение дипломников по кафедрам (сводка + детальный список)
  - `GET /api/v1/reports/group-performance` — сводная ведомость успеваемости группы (матрица: студент × дисциплина)
- [x] 3.2 `main.py` — подключить reports router

## Этап 4: Frontend для отчётов ✅

- [x] 4.1 `ReportsView` — экран с выбором типа отчёта, фильтрами и отображением результатов
- [x] 4.2 `main_shell.py` — пункт «📊 Отчёты» в сайдбаре для всех ролей

---

**Итог:** все 4 этапа выполнены. 10 из 11 пробелов в соответствии ТЗ закрыты.
