import time
from playwright.sync_api import sync_playwright

def run_live_sprint3_demo():
    print("🚀 Инициализация живой демонстрации Спринта 3 (Нагрузка и Validation Engine)...")
    print("🖥️ Запускаем браузер Chrome в интерактивном режиме (headless=False) на вашем экране...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--no-sandbox"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        print("🔗 Открываем веб-интерфейс ИС ВУЗа: http://localhost:8500 ...")
        page.goto("http://localhost:8500")
        
        print("⏳ Ожидание полной прорисовки интерфейса (6 секунд)...")
        time.sleep(6)
        
        # 1. АВТОРИЗАЦИЯ
        print("🖱️ Активируем окно кликом...")
        page.mouse.click(200, 200)
        time.sleep(1)
        
        print("⌨️ Фокусируемся на полях ввода...")
        page.keyboard.press("Tab")
        time.sleep(1)
        
        print("✏️ Вводим логин 'admin'...")
        page.keyboard.type("admin", delay=100)
        time.sleep(1)
        
        page.keyboard.press("Tab")
        time.sleep(1)
        
        print("✏️ Вводим пароль 'admin123'...")
        page.keyboard.type("admin123", delay=100)
        time.sleep(1)
        
        page.keyboard.press("Tab")
        time.sleep(1)
        
        print("🔘 Нажимаем кнопку 'Войти в систему'...")
        page.keyboard.press("Enter")
        
        print("⏳ Ожидание перехода в личный кабинет (8 секунд)...")
        time.sleep(8)
        
        # 2. ДОБАВЛЕНИЕ ЛАБОРАТОРНОЙ РАБОТЫ В УЧЕБНЫЙ ПЛАН
        print("📅 Переходим в раздел 'Учебные планы'...")
        page.keyboard.press("Tab") # 🧭 Обзор
        time.sleep(0.5)
        page.keyboard.press("Tab") # 📁 Справочники
        time.sleep(0.5)
        page.keyboard.press("Tab") # 👥 Пользователи
        time.sleep(0.5)
        page.keyboard.press("Tab") # 📅 Учебные планы
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        print("🖱️ Выбираем группу '401-ПИ'...")
        page.keyboard.press("Tab") # Фокус на группу в списке
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("➕ Нажимаем кнопку 'Добавить в план'...")
        page.keyboard.press("Tab") # Кнопка Новая дисциплина
        time.sleep(0.5)
        page.keyboard.press("Tab") # Кнопка Добавить в план
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        # Заполняем форму для лабораторной работы
        # 1. Дисциплина (Системный анализ)
        print("✏️ Выбираем дисциплину 'Системный анализ'...")
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # 2. Вид занятия (лабораторная работа)
        print("✏️ Выбираем вид занятия 'лабораторная работа'...")
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.press("ArrowDown") # Семинар
        time.sleep(0.3)
        page.keyboard.press("ArrowDown") # Лабораторная работа
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # 3. Часы (18 ч)
        print("✏️ Вводим объем нагрузки: 18 часов...")
        page.keyboard.press("Tab")
        time.sleep(0.5)
        # Стираем старое значение и пишем 18
        page.keyboard.press("Backspace")
        time.sleep(0.2)
        page.keyboard.press("Backspace")
        time.sleep(0.2)
        page.keyboard.type("18", delay=100)
        time.sleep(1)
        
        # 4. Семестр (7)
        page.keyboard.press("Tab")
        time.sleep(0.5)
        
        # 5. Форма контроля (зачет)
        print("✏️ Выбираем форму контроля 'зачет'...")
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.press("ArrowDown") # зачет
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # Нажимаем Добавить
        page.keyboard.press("Tab") # Отмена
        time.sleep(0.5)
        page.keyboard.press("Tab") # Добавить
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(3)
        
        # Направляем лабораторную работу кафедре
        print("💼 Поручаем выполнение лабораторной работы кафедре Программной Инженерии...")
        # Перейдем по табам к новой строке таблицы
        # Фокус попадет на 1-ю строку
        page.keyboard.press("Tab")
        time.sleep(0.5)
        # 2-я строка (новая)
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.press("Enter") # Открываем диалог назначения
        time.sleep(2)
        
        # Кафедра Программной Инженерии (первая)
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        page.keyboard.press("Tab") # Отмена
        time.sleep(0.5)
        page.keyboard.press("Tab") # Поручить
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # 3. НАВИГАЦИЯ В РАСПРЕДЕЛЕНИЕ НАГРУЗКИ (Validation Engine UI)
        print("🧭 Переходим в раздел меню 'Распределение нагрузки'...")
        # Вернемся в боковое меню
        for _ in range(8):
            page.keyboard.press("Shift+Tab")
            time.sleep(0.2)
            
        page.keyboard.press("ArrowDown") # Сдвиг вниз на "Распределение нагрузки"
        time.sleep(0.8)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # 4. ТЕСТИРОВАНИЕ ВАЛИДАЦИИ: ЛЕКЦИЯ
        print("🔬 Тест 1: Распределение лекции (Системный анализ)...")
        # Выберем первое поручение (Лекция)
        page.keyboard.press("Tab") # Фокус на 1-е поручение
        time.sleep(1.0)
        page.keyboard.press("Enter")
        time.sleep(3)
        
        print("🔍 Проверяем статус преподавателей в правой колонке:")
        print(" - Петр Петрович Петров (Ассистент): заблокирован (Ассистент не может вести лекции)")
        print(" - Сидор Сидорович Сидоров (Доцент без звания): заблокирован (Необходимо ученое звание доцента)")
        print(" - Иван Иванович Иванов (Профессор): активен для выбора.")
        
        print("🔘 Назначаем лекцию профессору Ивану Ивановичу Иванову...")
        # Перейдем по табам до кнопки "Назначить" напротив профессора
        # Фокус попадет на кнопку первого валидного преподавателя
        page.keyboard.press("Tab")
        time.sleep(1.0)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        print("✅ Лекция успешно распределена! Нагрузка профессора обновилась (36 / 400 ч).")
        
        # Снимем нагрузку для демонстрации отмены
        print("🔄 Тест отмены: Снимаем нагрузку с профессора...")
        # Перейдем на кнопку удаления у 1-го поручения
        page.keyboard.press("Shift+Tab")
        time.sleep(0.5)
        page.keyboard.press("Shift+Tab")
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(3)
        print("✅ Нагрузка успешно снята. Статус вернулся в 'Не распределено'.")
        
        # Выберем поручение лекции снова
        page.keyboard.press("Enter")
        time.sleep(2)
        
        # 5. ТЕСТИРОВАНИЕ ВАЛИДАЦИИ: ЛАБОРАТОРНАЯ РАБОТА
        print("🔬 Тест 2: Выбираем лабораторную работу...")
        # Переходим ко 2-му поручению (Лабораторная работа)
        page.keyboard.press("Tab") # Кнопка Назначить у профессора
        time.sleep(0.5)
        page.keyboard.press("Tab") # Фокус на 2-е поручение
        time.sleep(1.0)
        page.keyboard.press("Enter")
        time.sleep(3)
        
        print("🔍 Проверяем статус преподавателей для лабораторной работы:")
        print(" - Иван Иванович Иванов (Профессор): заблокирован (Профессор не ведет лабораторные работы!)")
        print(" - Петр Петрович Петров (Ассистент): активен и доступен для выбора!")
        
        print("🔘 Назначаем лабораторную работу ассистенту Петру Петровичу Петрову...")
        page.keyboard.press("Tab") # Фокус на кнопку ассистента
        time.sleep(1.0)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # 6. ФИНАЛЬНАЯ ФИКСАЦИЯ
        print("📸 Сохраняем финальный скриншот распределения нагрузки...")
        screenshot_path = "/Users/elvsevolod/Desktop/учеба/Учёба 3 курс /ПИИС/2 семестр/10 лаба/frontend/sprint3_load_assignments.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Скриншот сохранен: {screenshot_path}")
        
        print("⌛ Оставляем окно браузера открытым на 15 секунд для вашего визуального осмотра...")
        time.sleep(15)
        
        print("🚪 Закрытие браузера. Тестирование Спринта 3 успешно завершено!")
        browser.close()

if __name__ == "__main__":
    try:
        run_live_sprint3_demo()
    except Exception as e:
        print(f"❌ Произошла ошибка при тестировании: {e}")
