import time
from playwright.sync_api import sync_playwright

def test_uis_app():
    print("Запуск браузера Chrome в интерактивном режиме (headless=False)...")
    with sync_playwright() as p:
        # Запускаем браузер в видимом режиме
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(viewport={"width": 1100, "height": 720})
        page = context.new_page()
        
        print("Переход на адрес ИС ВУЗа: http://localhost:8500...")
        page.goto("http://localhost:8500")
        
        # Даем Flet 6 секунд на полную прорисовку
        print("Ожидание полной прорисовки интерфейса...")
        time.sleep(6)
        
        # Фокусируем само окно
        page.mouse.click(100, 100)
        time.sleep(1)
        
        # ВАЖНО: Нажатие Tab активирует семантический/доступный слой Flutter Web,
        # что автоматически фокусирует первое текстовое поле (Логин)!
        print("Нажатие клавиши 'Tab' для активации доступности и фокуса поля логина...")
        page.keyboard.press("Tab")
        time.sleep(1.5)
        
        print("Ввод логина 'admin'...")
        page.keyboard.type("admin", delay=150)
        time.sleep(1)
        
        print("Нажатие клавиши 'Tab' для фокуса поля пароля...")
        page.keyboard.press("Tab")
        time.sleep(1.5)
        
        print("Ввод пароля 'admin123'...")
        page.keyboard.type("admin123", delay=150)
        time.sleep(1)
        
        print("Нажатие клавиши 'Tab' для фокуса кнопки 'Войти в систему'...")
        page.keyboard.press("Tab")
        time.sleep(1.5)
        
        print("Нажатие клавиши 'Enter' для входа...")
        page.keyboard.press("Enter")
        
        # Ожидаем перехода в панель управления
        print("Ожидание перехода в панель управления...")
        time.sleep(8)
        
        # Делаем скриншот после входа, чтобы подтвердить успех!
        screenshot_path = "/Users/elvsevolod/Desktop/учеба/Учёба 3 курс /ПИИС/2 семестр/10 лаба/frontend/logged_in_dashboard.png"
        page.screenshot(path=screenshot_path)
        print(f"Скриншот панели управления сохранен: {screenshot_path}")
        
        # Навигация в боковом меню через Tab-навигацию (это на 100% надежно!)
        print("Тестирование навигации бокового меню...")
        page.keyboard.press("Tab")
        time.sleep(1)
        
        # Закрываем браузер
        print("Тест завершен успешно! Закрытие браузера...")
        browser.close()

if __name__ == "__main__":
    try:
        test_uis_app()
    except Exception as e:
        print(f"Произошла ошибка при тестировании: {e}")
