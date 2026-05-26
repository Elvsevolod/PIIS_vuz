import time
from playwright.sync_api import sync_playwright

def run_chrome_live_walkthrough():
    print("🚀 Инициализация демонстрации во встроенном Google Chrome...")
    print("🖥️ Запускаем ВАШ установленный Google Chrome на вашем экране (headless=False)...")
    
    with sync_playwright() as p:
        # Запускаем системный Google Chrome с помощью channel="chrome", чтобы окно гарантированно всплыло на переднем плане!
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--start-maximized"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        print("🔗 Переход на страницу: http://localhost:8500 ...")
        page.goto("http://localhost:8500")
        
        print("⏳ Ожидание полной прорисовки интерфейса (6 секунд)...")
        time.sleep(6)
        
        # 1. ФОКУСИРОВКА И ВХОД
        print("🖱️ Активируем окно кликом...")
        page.mouse.click(200, 200)
        time.sleep(1)
        
        print("⌨️ Переходим к полю логина (Tab)...")
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
        
        # 2. ДЕМОНСТРАЦИЯ ВСЕХ РАЗДЕЛОВ МЕНЮ
        print("🧭 Начинаем последовательный обход ВСЕХ разделов меню, чтобы вы видели переключение экранов...")
        
        # Фокусируемся на боковом меню
        page.keyboard.press("Tab")
        time.sleep(1.5)
        
        # Раздел 1: 🧭 Обзор (уже открыт, перейдем на Справочники)
        print("📂 Открываем раздел 'Справочники'...")
        page.keyboard.press("ArrowDown") # На Справочники
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(3)
        
        # Раздел 2: 👥 Пользователи
        print("👥 Открываем раздел 'Пользователи'...")
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(3)
        
        # Раздел 3: 📅 Учебные планы
        print("📅 Открываем раздел 'Учебные планы'...")
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(3.5)
        
        # Раздел 4: 👨‍🎓 Группы и студенты
        print("👨‍🎓 Открываем раздел 'Группы и студенты'...")
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(3.5)
        
        # Раздел 5: 💼 Распределение нагрузки
        print("💼 Открываем раздел 'Распределение нагрузки'...")
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(3.5)
        
        # Раздел 6: 🎓 Дипломные работы
        print("🎓 Открываем раздел 'Дипломные работы'...")
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(3.5)
        
        # Раздел 7: 📊 Аттестация
        print("📊 Открываем раздел 'Аттестация'...")
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(3.5)
        
        print("⌛ Оставляем окно Google Chrome открытым на 15 секунд, чтобы вы могли его рассмотреть...")
        time.sleep(15)
        
        print("🚪 Закрытие браузера. Демонстрация успешно завершена!")
        browser.close()

if __name__ == "__main__":
    try:
        run_chrome_live_walkthrough()
    except Exception as e:
        print(f"❌ Произошла ошибка во время демонстрации в Google Chrome: {e}")
        print("Подсказка: Убедитесь, что у вас установлен стандартный браузер Google Chrome в системе.")
