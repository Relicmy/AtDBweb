from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_element():
    driver = webdriver.Chrome()

    # Убрал пробел в URL
    driver.get("https://surfearner.com")

    buttons = driver.find_elements(By.CLASS_NAME, "button-wrapper")
    target_element = None

    for btn in buttons:
        try:
            span = btn.find_element(By.CSS_SELECTOR, "span.text.icon")
            if span.text.strip() == "Войти в кабинет":
                target_element = btn
                break
        except:
            continue
    else:
        print("Элемент не найден")

    try:
        
        # Скриншот
        driver.save_screenshot("test_images/screenshot.png")
        location = {"x": 0, "y": 0}
        size = {"width": 0, "height": 0}
        # Получение координат
        if target_element:
            location = target_element.location
            size = target_element.size
        
        with open('test_txt/screenshot.txt', "w") as file:
            file.write(f"{location['x']}, {location['y']}, {size['width']}, {size['height']}")
        
        print(f"Координаты элемента: {location}")
        print(f"Размеры элемента: {size}")
        driver.quit()
        return True
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        # Дополнительная диагностика
        print("Текущий URL:", driver.current_url)
        print("Page source:", driver.page_source[:1000])  # Первые 1000 символов HTML

    finally:
        driver.quit()
