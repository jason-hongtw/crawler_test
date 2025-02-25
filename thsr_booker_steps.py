import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select  # 下拉式選單使用
from selenium.common.exceptions import NoSuchElementException #handle exception
from ocr_component import get_captcha_code
from pprint import pprint
from datetime import date
from booking_info_extraction_flow import (
    ask_booking_information,
    ask_missing_information,
    convert_date_to_thsr_format
)

def create_driver():
    options = webdriver.ChromeOptions()  # 創立 driver物件所需的參數物件
    options.add_argument("--disable-blink-features=AutomationControlled")
    global driver
    driver = webdriver.Chrome(options=options)
    driver.get("https://irs.thsrc.com.tw/IMINT/")

def booking_with_info(start_station, dest_station, start_time, start_date):
    '''
    Step 1: setup options for booking information
    '''


    # Click accept cookie button
    accept_cookie_button = driver.find_element(By.ID, "cookieAccpetBtn")
    accept_cookie_button.click()

    # Choose Booking parameters: startStation, destStation, time
    start_station_element = driver.find_element(By.NAME, 'selectStartStation')
    Select(start_station_element).select_by_visible_text(start_station)

    dest_station_element = driver.find_element(By.NAME, 'selectDestinationStation')
    Select(dest_station_element).select_by_visible_text(dest_station)

    start_time_element = driver.find_element(By.NAME, 'toTimeTable')
    Select(start_time_element).select_by_visible_text(start_time)

    # choose start_date parameters
    driver.find_element(
        By.XPATH, "//input[@class='uk-input' and @readonly='readonly']").click()
    time.sleep(2)

    # include today's class and other days
    driver.find_element(
        By.XPATH, f"//span[(@class='flatpickr-day' or @class='flatpickr-day today selected') and @aria-label='{start_date}']").click()

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
    for idx, train in enumerate(trains_info):
            idx += 1
            print(
                f"({idx}) - {train['train_code']}, \
                行駛時間={train['duration']} | \
                {train['depart_time']} -> \
                {train['arrival_time']}"
            )

    return trains_info


def select_train_and_submit_booking(trains_info):

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

    return

if __name__ == "__main__":

    # Booking parameters
    #start_station = '台中'
    #dest_station = '板橋'
    #start_time = '18:00'
    #start_date = '二月 25, 2025'

    # Step 1
    booking_info = ask_booking_information()

    # Step 2
    booking_info = ask_missing_information(booking_info)

    # Step 3：調整日期格式以便爬蟲使用, ex: '2025/02/25' -> '二月 25, 2025'
    booking_info = convert_date_to_thsr_format(booking_info)

    create_driver()

    # Step 4
    trains_info = booking_with_info(
        start_station=booking_info['出發站'],
        dest_station=booking_info['到達站'],
        start_time=booking_info['出發時分'],
        start_date=booking_info['出發日期'])

    # Step 5
    select_train_and_submit_booking(trains_info)

    time.sleep(10)
    driver.quit()


