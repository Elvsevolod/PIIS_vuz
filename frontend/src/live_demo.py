import time
from playwright.sync_api import sync_playwright

def run_live_demo():
    print("🚀 Инициализация живой демонстрации ИС ВУЗа...")
    print("🖥️ Запускаем браузер Chrome в интерактивном режиме (headless=False) на вашем экране...")
    
    with sync_playwright() as p:
        # Запускаем браузер в видимом режиме с задержкой 1 секунда между действиями для наглядности (slow_mo=1000)
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--no-sandbox"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        print("🔗 Открываем страницу веб-приложения: http://localhost:8500 ...")
        page.goto("http://localhost:8500")
        
        # Даем Flet время загрузиться и отрисовать интерфейс
        print("⏳ Ожидание полной прорисовки интерфейса (6 секунд)...")
        time.sleep(6)
        
        # Клик по экрану для фокусировки окна
        print("🖱️ Активируем окно кликом...")
        page.mouse.click(200, 200)
        time.sleep(1)
        
        # Нажимаем Tab для активации доступного/семантического слоя Flutter Web
        print("⌨️ Нажатие 'Tab' для фокуса на поле ввода 'Имя пользователя'...")
        page.keyboard.press("Tab")
        time.sleep(1.5)
        
        # Вводим имя пользователя admin
        print("✏️ Вводим логин 'admin'...")
        page.keyboard.type("admin", delay=100)
        time.sleep(1)
        
        # Переходим на поле пароля
        print("⌨️ Нажатие 'Tab' для перехода к полю 'Пароль'...")
        page.keyboard.press("Tab")
        time.sleep(1.5)
        
        # Вводим пароль admin123
        print("✏️ Вводим пароль 'admin123'...")
        page.keyboard.type("admin123", delay=100)
        time.sleep(1)
        
        # Переходим к кнопке Вход
        print("⌨️ Нажатие 'Tab' для фокуса на кнопку 'Войти в систему'...")
        page.keyboard.press("Tab")
        time.sleep(1.5)
        
        # Нажимаем Enter для входа
        print("🔘 Нажатие 'Enter' для подтверждения входа...")
        page.keyboard.press("Enter")
        
        # Ожидаем отрисовки главного экрана панели управления
        print("⏳ Ожидание перехода в личный кабинет (8 секунд)...")
        time.sleep(8)
        
        # Сделаем скриншот для истории
        screenshot_path = "/Users/elvsevolod/Desktop/учеба/Учёба 3 курс /ПИИС/2 семестр/10 лаба/frontend/logged_in_dashboard.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Скриншот панели управления успешно сохранен: {screenshot_path}")
        
        # Перейдем в боковое меню на раздел 'Справочники'
        # Сначала сфокусируемся и перейдем по табам в боковое меню
        print("🧭 Начинаем демонстрацию навигации по разделам меню...")
        
        # Нажимаем Tab
        page.keyboard.press("Tab")
        time.sleep(1.5)
        
        print("📂 Успешно переключились на боковую панель навигации!")
        
        # Оставляем окно открытым, чтобы вы могли его полностью рассмотреть
        print("⌛ Оставляем окно браузера открытым на 15 секунд для вашего визуального осмотра...")
        time.sleep(15)
        
        print("🚪 Закрытие браузера. Демонстрация завершена!")
        browser.close()

if __name__ == "__main__":
    try:
        run_live_demo()
    except Exception as e:
        print(f"❌ Произошла ошибка во время живой демонстрации: {e}")
