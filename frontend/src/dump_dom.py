import time
from playwright.sync_api import sync_playwright

def dump_dom():
    print("Dumping DOM of the Flet page...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8500")
        time.sleep(5)
        
        # Print page HTML
        html = page.content()
        print(f"HTML Length: {len(html)}")
        
        # Print list of inputs
        inputs = page.query_selector_all("input")
        print(f"Found {len(inputs)} input elements:")
        for idx, inp in enumerate(inputs):
            print(f"Input {idx}: type={inp.get_attribute('type')}, placeholder={inp.get_attribute('placeholder')}, outerHTML={inp.evaluate('el => el.outerHTML')}")
            
        # Print all buttons
        buttons = page.query_selector_all("button")
        print(f"Found {len(buttons)} button elements:")
        for idx, btn in enumerate(buttons):
            print(f"Button {idx}: text={btn.text_content()}, outerHTML={btn.evaluate('el => el.outerHTML')}")
            
        # Let's save a screenshot to check what is displayed!
        page.screenshot(path="/Users/elvsevolod/Desktop/учеба/Учёба 3 курс /ПИИС/2 семестр/10 лаба/frontend/screenshot.png")
        print("Screenshot saved to frontend/screenshot.png")
        
        browser.close()

if __name__ == "__main__":
    dump_dom()
