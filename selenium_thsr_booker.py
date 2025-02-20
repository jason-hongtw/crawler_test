import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select  # 下拉式選單使用
from ocr_component import get_captcha_code

options = webdriver.ChromeOptions() #創立 driver物件所需的參數物件(防止爬網頁繞圈)
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)
driver.get("https://irs.thsrc.com.tw/IMINT/")
accept_cookie_button = driver.find_element(By.ID, "cookieAccpetBtn")
accept_cookie_button.click()

# startStation, destStation, uk-select
start_station_element = driver.find_element(By.NAME, 'selectStartStation')
Select(start_station_element).select_by_visible_text('台中')

dest_station_element = driver.find_element(By.NAME, 'selectDestinationStation')
Select(dest_station_element).select_by_visible_text('板橋')

start_time_element = driver.find_element(By.NAME, 'toTimeTable')
Select(start_time_element).select_by_visible_text('18:30')

# start_date
driver.find_element(
    By.XPATH, "//input[@class='uk-input' and @readonly='readonly']").click()

start_date = '二月 21, 2025'
driver.find_element(
    By.XPATH, f"//span[@class='flatpickr-day' and @aria-label='{start_date}']").click()

# captcha
captcha_img = driver.find_element(By.ID, 'BookingS1Form_homeCaptcha_passCode')
captcha_img.screenshot('captcha.png')
captcha_code = get_captcha_code()
captcha_input = driver.find_element(By.ID, 'securityCode')
captcha_input.send_keys(captcha_code)

time.sleep(50)
# submit
driver.find_element(By.ID, 'SubmitButton').click()


# time.sleep(20)
driver.quit()
