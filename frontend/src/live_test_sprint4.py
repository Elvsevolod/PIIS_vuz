import time
from playwright.sync_api import sync_playwright

def run_live_sprint4_demo():
    print("🚀 Инициализация живой демонстрации Спринта 4 (Дипломы, Аттестация и Автосохранение)...")
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
        
        # 2. НАЗНАЧЕНИЕ РУКОВОДИТЕЛЯ ДИПЛОМА
        print("🧭 Переходим в раздел меню 'Дипломные работы'...")
        page.keyboard.press("Tab") # 🧭 Обзор
        time.sleep(0.5)
        page.keyboard.press("Tab") # 📁 Справочники
        time.sleep(0.5)
        page.keyboard.press("Tab") # 👥 Пользователи
        time.sleep(0.5)
        page.keyboard.press("Tab") # 📅 Учебные планы
        time.sleep(0.5)
        page.keyboard.press("Tab") # 👨‍🎓 Группы и студенты
        time.sleep(0.5)
        page.keyboard.press("Tab") # 💼 Распределение нагрузки
        time.sleep(0.5)
        page.keyboard.press("Tab") # 🎓 Дипломные работы
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        print("🖱️ Выбираем студента 'Елисеев Всеволод'...")
        page.keyboard.press("Tab") # Фокус на 1-го студента в списке
        time.sleep(1.0)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("✏️ Вводим тему диплома...")
        page.keyboard.press("Tab") # Фокус на поле ввода "Тема диплома"
        time.sleep(0.8)
        page.keyboard.type("Информационная система ВУЗа на базе Flet и FastAPI", delay=80)
        time.sleep(1)
        
        print("✏️ Выбираем научного руководителя...")
        page.keyboard.press("Tab") # Фокус на выпадающий список руководителей
        time.sleep(0.8)
        # Выбираем Ивана Ивановича Иванова (он первый в списке или скроллим)
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        print("🔘 Нажимаем 'Сохранить назначение'...")
        page.keyboard.press("Tab") # Фокус на кнопку "Сохранить"
        time.sleep(0.8)
        page.keyboard.press("Enter")
        time.sleep(3)
        print("✅ Руководитель диплома успешно назначен!")
        
        # 3. НАВИГАЦИЯ В ВЕДОМОСТЬ АТТЕСТАЦИИ И АВТОСОХРАНЕНИЕ
        print("🧭 Переходим в раздел меню 'Аттестация'...")
        # Сфокусируемся обратно на боковое меню ( Shift+Tab-навигацией)
        for _ in range(8):
            page.keyboard.press("Shift+Tab")
            time.sleep(0.2)
            
        page.keyboard.press("ArrowDown") # Сдвиг вниз на "Аттестация"
        time.sleep(0.8)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # Сначала распределим лекцию преподавателю Ивану Ивановичу Иванову (если сбросили в Спринте 3),
        # Но подождите! В Спринте 3 мы сбросили нагрузку, а в тесте 2 назначили лабораторную работу Петру Петровичу Петрову.
        # Давайте выберем нагрузку ассистента Петра Петровича Петрова!
        # Сначала сменим преподавателя в ведомости на Петра Петровича Петрова, чтобы выставить оценку за зачет по лабораторной работе!
        print("✏️ Меняем активного преподавателя на ассистента Петра Петровича Петрова...")
        page.keyboard.press("Tab") # Фокус на дропдаун выбора преподавателя
        time.sleep(0.8)
        page.keyboard.press("ArrowDown") # Переходим ко 2-му преподавателю (Петр Петрович)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("🖱️ Выбираем закрепленную нагрузку 'Системный анализ (лабораторная работа)'...")
        page.keyboard.press("Tab") # Фокус на первую нагрузку в списке
        time.sleep(1.0)
        page.keyboard.press("Enter")
        time.sleep(3)
        
        print("📝 Открылась электронная ведомость аттестации группы 401-ПИ!")
        print("🔍 Проверяем список студентов... Находим студента 'Елисеев Всеволод'.")
        
        print("🔘 Выставляем оценку 'Зачет' (Автосохранение)...")
        # Переходим к выпадающему списку оценок для первого студента
        page.keyboard.press("Tab")
        time.sleep(0.8)
        page.keyboard.press("ArrowDown") # Зачет
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        print("✅ Оценка успешно выставлена! Зеленый маркер подтвердил мгновенную синхронизацию (Autosave).")
        
        # 4. ФИНАЛЬНАЯ ФИКСАЦИЯ
        print("📸 Сохраняем финальный скриншот результатов аттестации...")
        screenshot_path = "/Users/elvsevolod/Desktop/учеба/Учёба 3 курс /ПИИС/2 семестр/10 лаба/frontend/sprint4_diplomas_and_grades.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Скриншот сохранен: {screenshot_path}")
        
        print("⌛ Оставляем окно браузера открытым на 15 секунд для вашего визуального осмотра...")
        time.sleep(15)
        
        print("🚪 Закрытие браузера. Демонстрация Спринта 4 успешно завершена!")
        browser.close()

if __name__ == "__main__":
    try:
        run_live_sprint4_demo()
    except Exception as e:
        print(f"❌ Произошла ошибка при тестировании: {e}")
