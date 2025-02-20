import time
import os
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
Step 1: setup options for booking information
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
        time.sleep(2)



'''
Step 2: booking right schedule
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
            # bs4: info.get('attribute')
            'depart_time': info.get_attribute('querydeparture'),
            'arrival_time': info.get_attribute('queryarrival'),
            'duration': info.get_attribute('queryestimatedtime'),
            'train_code': info.get_attribute('querycode'),
            'radio_box': info,
        }
    )

pprint(trains_info)
# Choose train
for idx, train in enumerate(trains_info): #enumerate: return index and value
    idx += 1
    print(
        f"({idx}) - {train['train_code']}, 行駛時間={train['duration']} | {train['depart_time']} -> {train['arrival_time']}")

while True:
    try:
        which_train = int(input("Choose your train. Enter from 1~10:\n"))-1
        trains_info[which_train]['radio_box'].click()
        break
    except IndexError:
        print('Index out of range, please enter again.')


# Submit booking requests
driver.find_element(By.NAME, 'SubmitButton').click()

# Check if page is redirected to passenger information page
time.sleep(2)
while True:
    try:
        driver.find_element(By.CLASS_NAME, 'ticket-summary')
        print('Redirected to passenger information page')
        break
    except NoSuchElementException:
        print('Page is not redirected to passenger information page, retrying...')
        time.sleep(2)
'''
Step 3: fill in passenger information
'''

#Check booking information for user
print("確認訂票: ")
print(
    f"車次: {trains_info[which_train]['train_code']} | \
    行駛時間: {trains_info[which_train]['duration']} | \
    {trains_info[which_train]['depart_time']} -> \
    {trains_info[which_train]['arrival_time']}"
)
print('您的車票共 ', driver.find_element(By.ID, 'TotalPrice').text, " 元")
driver.find_element(
    By.CLASS_NAME, 'ticket-summary').screenshot('thsr_summary.png')

# enter personal ID
input_personal_id = driver.find_element(By.ID, 'idNumber')
#personal_id = input('Please enter your personal ID: \n') #\n: new line
#get personal ID from environment variable, ev used to named in uppercase
personal_id = os.getenv('PERSONAL_ID')
input_personal_id.send_keys(personal_id)

# enter phone number
#input_phone = driver.find_element(By.ID, 'mobilePhone')
#phone_number = input('Please enter your phone number: \n')
#get phone number from environment variable
#phone_number = os.getenv('PERSONAL_PHONE_NUMBER')
#input_phone.send_keys(phone_number)

# enter email
#input_email = driver.find_element(By.ID, 'email')
#email = input('Please enter your email: \n')
#get email from environment variable
#email = os.getenv('PERSONAL_EMAIL')
#input_email.send_keys(email)

# check agree box
agree_box = driver.find_element(By.NAME, 'agree')
agree_box.click()

# submit
driver.find_element(By.ID, 'isSubmit').click()

# check if page is redirected to payment page
time.sleep(2)
while True:
    try:
        driver.find_element(By.CLASS_NAME, 'uk-flex uk-flex-between uk-flex-column primary-payment-v2-inner')
        print('Redirected to payment page')
        break
    except NoSuchElementException:
        print('Page is not redirected to payment page, retrying...')
        time.sleep(2)

# Save booking result
driver.find_element(
    By.CLASS_NAME, 'ticket-summary').screenshot('thsr_booking_result.png')
print("訂票完成!")

time.sleep(2000)
driver.quit()