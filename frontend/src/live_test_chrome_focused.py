import time
import os
from playwright.sync_api import sync_playwright

def run_focused_live_walkthrough():
    print("🚀 Инициализация полного визуального тестирования ИС ВУЗа в вашем Google Chrome...")
    
    with sync_playwright() as p:
        # Запускаем системный Google Chrome
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--start-maximized"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        # --- macOS СИСТЕМНЫЙ ФОКУС: ФОРСИРУЕМ ВЫВОД ОКНА НА ЭКРАН ---
        print("🖥️ Форсируем вывод Google Chrome на передний план вашего Mac с помощью AppleScript...")
        try:
            # Этот скрипт принудительно переключает экран Mac на Chrome и поднимает его поверх всех окон!
            os.system('osascript -e "tell application \\"Google Chrome\\" to activate"')
        except Exception as es:
            print(f"Предупреждение по AppleScript: {es}")
            
        print("🔗 Открываем веб-интерфейс: http://localhost:8500 ...")
        page.goto("http://localhost:8500")
        
        print("⏳ Ожидание прорисовки окна авторизации (6 секунд)...")
        time.sleep(6)
        
        # 1. АВТОРИЗАЦИЯ
        print("🖱️ Активируем форму кликом...")
        page.mouse.click(200, 200)
        time.sleep(1)
        
        print("⌨️ Переходим к вводу логина...")
        page.keyboard.press("Tab")
        time.sleep(1)
        
        print("✏️ Вводим логин 'admin'...")
        page.keyboard.type("admin", delay=120)
        time.sleep(1)
        
        page.keyboard.press("Tab")
        time.sleep(1)
        
        print("✏️ Вводим пароль 'admin123'...")
        page.keyboard.type("admin123", delay=120)
        time.sleep(1)
        
        page.keyboard.press("Tab")
        time.sleep(1)
        
        print("🔘 Нажимаем кнопку 'Войти в систему'...")
        page.keyboard.press("Enter")
        
        print("⏳ Ожидание загрузки личного кабинета (8 секунд)...")
        time.sleep(8)
        
        # 2. УПРАВЛЕНИЕ ГРУППАМИ И СТУДЕНТАМИ
        print("🧭 Открываем раздел 'Группы и студенты'...")
        # Переходим к пункту меню по Tab
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
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # Создаем еще одну демонстрационную группу "402-ПИ"
        print("➕ Нажимаем кнопку 'Создать новую группу'...")
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("✏️ Вводим название группы '402-ПИ'...")
        page.keyboard.type("402-ПИ", delay=100)
        time.sleep(1)
        
        # Спускаемся по курсу и семестру
        page.keyboard.press("Tab") # Курс
        time.sleep(0.5)
        page.keyboard.press("ArrowDown") # 2 курс
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        page.keyboard.press("Tab") # Семестр
        time.sleep(0.5)
        page.keyboard.press("ArrowDown") # 3 семестр
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        page.keyboard.press("Tab") # Факультет
        time.sleep(0.5)
        
        page.keyboard.press("Tab") # Год поступления
        time.sleep(0.5)
        page.keyboard.type("2024", delay=100)
        time.sleep(1)
        
        page.keyboard.press("Tab") # Отмена
        time.sleep(0.3)
        page.keyboard.press("Tab") # Создать
        time.sleep(0.3)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # Выберем созданную группу 402-ПИ
        print("🖱️ Выбираем созданную группу '402-ПИ'...")
        # Сфокусируемся на списке групп (нажимаем Tab)
        page.keyboard.press("Tab")
        time.sleep(0.5)
        # Перейдем на вторую группу (нажатие стрелки вниз)
        page.keyboard.press("ArrowDown")
        time.sleep(0.8)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        # Зачислим студента
        print("➕ Зачисляем студента в группу '402-ПИ'...")
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        print("✏️ Вводим имя студента...")
        page.keyboard.type("Иванов Петр", delay=100)
        time.sleep(1)
        
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.type("241502", delay=100)
        time.sleep(1)
        
        page.keyboard.press("Tab") # Отмена
        time.sleep(0.3)
        page.keyboard.press("Tab") # Зачислить
        time.sleep(0.3)
        page.keyboard.press("Enter")
        time.sleep(3)
        
        # 3. НАВИГАЦИЯ В УЧЕБНЫЕ ПЛАНЫ
        print("🧭 Переходим в раздел 'Учебные планы'...")
        for _ in range(8):
            page.keyboard.press("Shift+Tab")
            time.sleep(0.2)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # 4. ДЕМОНСТРАЦИЯ ДИПЛОМНЫХ РАБОТ
        print("🧭 Переходим в раздел 'Дипломные работы'...")
        for _ in range(3):
            page.keyboard.press("Shift+Tab")
            time.sleep(0.2)
        # Спустимся на "Дипломные работы"
        page.keyboard.press("ArrowDown") # На Группы
        time.sleep(0.3)
        page.keyboard.press("ArrowDown") # На Нагрузку
        time.sleep(0.3)
        page.keyboard.press("ArrowDown") # На Дипломы
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # 5. ДЕМОНСТРАЦИЯ АТТЕСТАЦИИ И АВТОСОХРАНЕНИЯ ОЦЕНОК
        print("🧭 Переходим в раздел ведомости 'Аттестация'...")
        # Перейдем в боковое меню
        for _ in range(6):
            page.keyboard.press("Shift+Tab")
            time.sleep(0.2)
        page.keyboard.press("ArrowDown") # Аттестация
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        print("⌛ Обход разделов завершен! Оставляем окно Google Chrome открытым на 20 секунд...")
        time.sleep(20)
        
        print("🚪 Закрытие браузера.")
        browser.close()

if __name__ == "__main__":
    try:
        run_focused_live_walkthrough()
    except Exception as e:
        print(f"❌ Ошибка во время визуального теста: {e}")
