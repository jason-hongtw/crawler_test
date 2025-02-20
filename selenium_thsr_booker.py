import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select  # 下拉式選單使用
from selenium.common.exceptions import NoSuchElementException #handle exception
from ocr_component import get_captcha_code
from pprint import pprint

options = webdriver.ChromeOptions() #創立 driver物件所需的參數物件(防止爬網頁繞圈)
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)
driver.get("https://irs.thsrc.com.tw/IMINT/")

'''
# Step 1: setup options for booking information
'''

#click cookie button
accept_cookie_button = driver.find_element(By.ID, "cookieAccpetBtn")
accept_cookie_button.click()

# choose booking parameters: startStation, destStation, uk-select
start_station_element = driver.find_element(By.NAME, 'selectStartStation')
Select(start_station_element).select_by_visible_text('台中')

dest_station_element = driver.find_element(By.NAME, 'selectDestinationStation')
Select(dest_station_element).select_by_visible_text('板橋')

start_time_element = driver.find_element(By.NAME, 'toTimeTable')
Select(start_time_element).select_by_visible_text('18:30')

# choose start_date parameters
driver.find_element(
    By.XPATH, "//input[@class='uk-input' and @readonly='readonly']").click()

start_date = '二月 21, 2025'
driver.find_element(
    By.XPATH, f"//span[@class='flatpickr-day' and @aria-label='{start_date}']").click()

while True:
# captcha
    captcha_img = driver.find_element(By.ID, 'BookingS1Form_homeCaptcha_passCode')
    captcha_img.screenshot('captcha.png')
    captcha_code = get_captcha_code()
    captcha_input = driver.find_element(By.ID, 'securityCode')
    captcha_input.send_keys(captcha_code)

    time.sleep(2)

    # submit
    driver.find_element(By.ID, 'SubmitButton').click()
    time.sleep(5)

    # check if captcha validation is correct or not
    # notice: if element can't be found, it will raise NoSuchElementException
    try:
        driver.find_element(By.ID,'BookingS2Form_TrainQueryDataViewPanel')
        print('Captcha validation is correct')
        break
    except NoSuchElementException: #if exception is raised, it means captcha validation is correct
        print('Captcha validation is incorrect, retrying...')


'''
# Step 2: booking right schedule
'''
trains_info = list()
trains = driver.find_element(
    By.CLASS_NAME, 'result-listing').find_elements(By.TAG_NAME, 'label')
for train in trains:
    # depart_time = train.find_element(By.ID, 'QueryDeparture').text
    # arrival_time = train.find_element(By.ID, 'QueryArrival').text
    # duration = train.find_element(
    #     By.CLASS_NAME, 'duration').find_elements(By.TAG_NAME, 'span')[1].text
    # train_code = train.find_element(By.ID, 'QueryCode').text
    # radio_box = train.find_element(By.CLASS_NAME, 'uk-radio')
    info = train.find_element(By.CLASS_NAME, 'uk-radio')

    trains_info.append(
        {
            #bs4: info.get('querydeparture')
            'depart_time': info.get_attribute('querydeparture'), 
            'arrival_time': info.get_attribute('queryarrival'),
            'duration': info.get_attribute('queryestimatedtime'),
            'train_code': info.get_attribute('querycode'),
            'radio_box': info,
        }
    )

pprint(trains_info)

time.sleep(2000)
driver.quit()