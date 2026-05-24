import time
from playwright.sync_api import sync_playwright

def run_live_sprint2_demo():
    print("🚀 Инициализация живой демонстрации Спринта 2 (Учебные планы и Студенты)...")
    print("🖥️ Запускаем браузер Chrome в интерактивном режиме (headless=False) на вашем экране...")
    
    with sync_playwright() as p:
        # Запуск headful Chrome
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
        
        # 1. ФОКУСИРОВКА И ВХОД
        print("🖱️ Активируем окно кликом...")
        page.mouse.click(200, 200)
        time.sleep(1)
        
        print("⌨️ Нажатие 'Tab' для фокуса на поле ввода логина...")
        page.keyboard.press("Tab")
        time.sleep(1)
        
        print("✏️ Вводим логин 'admin'...")
        page.keyboard.type("admin", delay=100)
        time.sleep(1)
        
        print("⌨️ Нажатие 'Tab' для перехода к паролю...")
        page.keyboard.press("Tab")
        time.sleep(1)
        
        print("✏️ Вводим пароль 'admin123'...")
        page.keyboard.type("admin123", delay=100)
        time.sleep(1)
        
        print("⌨️ Нажатие 'Tab' для фокуса на кнопку 'Войти в систему'...")
        page.keyboard.press("Tab")
        time.sleep(1)
        
        print("🔘 Нажатие 'Enter' для подтверждения входа...")
        page.keyboard.press("Enter")
        
        print("⏳ Ожидание перехода в личный кабинет (8 секунд)...")
        time.sleep(8)
        
        # 2. НАВИГАЦИЯ В РАЗДЕЛ "Группы и студенты"
        print("🧭 Переходим в раздел меню 'Группы и студенты'...")
        
        # Нажимаем Tab несколько раз, чтобы пройти по пунктам бокового меню
        # 1-й Tab: 🧭 Обзор
        page.keyboard.press("Tab")
        time.sleep(0.8)
        
        # 2-й Tab: 📁 Справочники
        page.keyboard.press("Tab")
        time.sleep(0.8)
        
        # 3-й Tab: 👥 Пользователи
        page.keyboard.press("Tab")
        time.sleep(0.8)
        
        # 4-й Tab: 📅 Учебные планы
        page.keyboard.press("Tab")
        time.sleep(0.8)
        
        # 5-й Tab: 👨‍🎓 Группы и студенты
        page.keyboard.press("Tab")
        time.sleep(0.8)
        
        print("🔘 Нажимаем 'Enter' для открытия экрана управления Группами и Студентами...")
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # 3. СОЗДАНИЕ НОВОЙ ГРУППЫ "401-ПИ"
        print("➕ Нажимаем кнопку 'Создать новую группу'...")
        # Перейдем по табам до кнопки создания группы. Кнопка создания группы - первый фокус на новом экране.
        page.keyboard.press("Tab")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("✏️ Вводим название новой группы '401-ПИ'...")
        page.keyboard.type("401-ПИ", delay=100)
        time.sleep(1)
        
        # Перейдем на курс
        page.keyboard.press("Tab")
        time.sleep(0.8)
        # Выбираем 4 курс (нажатия стрелок вниз)
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # Перейдем на семестр
        page.keyboard.press("Tab")
        time.sleep(0.8)
        # Выбираем 7 семестр
        for _ in range(6):
            page.keyboard.press("ArrowDown")
            time.sleep(0.2)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # Перейдем на факультет (оставляем первый по умолчанию)
        page.keyboard.press("Tab")
        time.sleep(0.8)
        
        # Перейдем на год поступления
        page.keyboard.press("Tab")
        time.sleep(0.8)
        page.keyboard.type("2023", delay=100)
        time.sleep(1)
        
        # Перейдем на кнопку Создать и нажмем Enter
        page.keyboard.press("Tab") # Кнопка Отмена
        time.sleep(0.5)
        page.keyboard.press("Tab") # Кнопка Создать
        time.sleep(0.5)
        print("🔘 Нажимаем кнопку 'Создать'...")
        page.keyboard.press("Enter")
        time.sleep(3)
        
        # 4. ЗАЧИСЛЕНИЕ СТУДЕНТА В ГРУППУ
        print("🖱️ Выбираем созданную группу '401-ПИ'...")
        # Сфокусируемся на первой группе
        page.keyboard.press("Tab")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("➕ Нажимаем кнопку 'Зачислить нового студента'...")
        # Переходим к кнопке "Зачислить"
        page.keyboard.press("Tab")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("✏️ Вводим ФИО студента 'Елисеев Всеволод'...")
        page.keyboard.type("Елисеев Всеволод", delay=100)
        time.sleep(1)
        
        page.keyboard.press("Tab")
        time.sleep(0.8)
        
        print("✏️ Вводим номер зачетной книжки '231501'...")
        page.keyboard.type("231501", delay=100)
        time.sleep(1)
        
        page.keyboard.press("Tab") # Кнопка Отмена
        time.sleep(0.5)
        page.keyboard.press("Tab") # Кнопка Зачислить
        time.sleep(0.5)
        print("🔘 Нажимаем кнопку 'Зачислить'...")
        page.keyboard.press("Enter")
        time.sleep(3)
        
        # 5. НАВИГАЦИЯ В РАЗДЕЛ "Учебные планы"
        print("🧭 Переходим в раздел меню 'Учебные планы'...")
        # Сфокусируемся обратно на боковое меню
        # Перейдем по Shift+Tab
        for _ in range(8):
            page.keyboard.press("Shift+Tab")
            time.sleep(0.2)
            
        print("🔘 Выбираем раздел 'Учебные планы'...")
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # 6. СОЗДАНИЕ ДИСЦИПЛИНЫ В КАТАЛОГЕ
        print("➕ Нажимаем кнопку 'Новая дисциплина' для каталога...")
        page.keyboard.press("Tab")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("✏️ Вводим название дисциплины 'Системный анализ'...")
        page.keyboard.type("Системный анализ", delay=100)
        time.sleep(1)
        
        page.keyboard.press("Tab")
        time.sleep(0.8)
        page.keyboard.type("Автоматизированное проектирование систем", delay=100)
        time.sleep(1)
        
        page.keyboard.press("Tab") # Отмена
        time.sleep(0.5)
        page.keyboard.press("Tab") # Создать
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(3)
        
        # 7. ДОБАВЛЕНИЕ ЭЛЕМЕНТА УЧЕБНОГО ПЛАНА
        # Сначала выберем нашу группу 401-ПИ из списка групп слева
        print("🖱️ Выбираем группу '401-ПИ' в разделе учебных планов...")
        page.keyboard.press("Tab") # Фокус на группу
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("➕ Нажимаем 'Добавить в план'...")
        # Перейдем к кнопке "Добавить в план"
        page.keyboard.press("Tab") # Кнопка Новая дисциплина
        time.sleep(0.5)
        page.keyboard.press("Tab") # Кнопка Добавить в план
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        # Поля формы добавления
        # 1. Дисциплина - выбираем Системный анализ (она первая или можем выбрать стрелками)
        page.keyboard.press("ArrowDown") # открываем или скроллим
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # 2. Вид занятия
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.press("ArrowDown") # выбираем Лекция
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # 3. Часы
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.type("36", delay=100)
        time.sleep(1)
        
        # 4. Семестр
        page.keyboard.press("Tab")
        time.sleep(0.5)
        # Оставляем семестр 7 (он выбран по умолчанию на основе семестра группы)
        
        # 5. Форма контроля
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.press("ArrowDown") # Экзамен
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # Сохраняем
        page.keyboard.press("Tab") # Отмена
        time.sleep(0.5)
        page.keyboard.press("Tab") # Добавить
        time.sleep(0.5)
        print("🔘 Нажимаем кнопку 'Добавить в план'...")
        page.keyboard.press("Enter")
        time.sleep(3)
        
        # 8. НАПРАВЛЕНИЕ ПОРУЧЕНИЯ КАФЕДРЕ (ASSIGNMENT)
        print("💼 Поручаем выполнение дисциплины кафедре...")
        # Переходим по табам к кнопке "Поручить кафедре" в таблице
        page.keyboard.press("Tab")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        # Выбираем кафедру из списка
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        page.keyboard.press("ArrowDown") # Выберем вторую кафедру для разнообразия
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # Нажимаем Поручить
        page.keyboard.press("Tab") # Отмена
        time.sleep(0.5)
        page.keyboard.press("Tab") # Поручить
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # Завершение
        print("📸 Сохраняем финальный скриншот с учебным планом и поручением...")
        screenshot_path = "/Users/elvsevolod/Desktop/учеба/Учёба 3 курс /ПИИС/2 семестр/10 лаба/frontend/sprint2_plans_and_assignments.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Скриншот успешно сохранен: {screenshot_path}")
        
        print("⌛ Оставляем окно браузера открытым на 15 секунд для вашего визуального осмотра результатов...")
        time.sleep(15)
        
        print("🚪 Закрытие браузера. Тестирование Спринта 2 завершено!")
        browser.close()

if __name__ == "__main__":
    try:
        run_live_sprint2_demo()
    except Exception as e:
        print(f"❌ Произошла ошибка при тестировании: {e}")
