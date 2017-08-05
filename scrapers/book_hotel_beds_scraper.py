#encoding: utf8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from processors import spider, sql_write
import pyodbc, time, os
from datetime import datetime, timedelta

cities = [
    'Antigua Guatemala, Guatemala',   
    'Guatemala City, Guatemala',
]

dates = [15, 30, 60, 90, 120]

def scrape_address(element):
    try:
        return element.find_element_by_xpath('.//p[contains(@class, "hc_hotel_location")]').text
    except:
        return ''

def scrape_name(element):
    return element.find_element_by_xpath('.//a[contains(@data-ceid, "searchresult_hotelname")]').get_attribute('title')

def scrape_price(element):
    try:
        new_price = element.find_element_by_xpath('.//p[contains(@class, "hc_hotel_price")]').text.strip().strip('Q').strip().replace(',', '')
        new_price = int(new_price) / 3
        try:
            old_price = element.find_element_by_xpath('.//p[contains(@class, "hc_hotel_wasPrice")]').text.strip().strip('Q').strip().replace(',', '')
            old_price = int(old_price) / 3
        except:
            old_price = 0
        return new_price, old_price
    except:
        return 0, 0

def scrape_rating(element):
    try:
        return element.find_element_by_xpath('.//p[@class="hc_hotel_userRating"]/a').text.strip()
    except:
        return 0

def scrape_review(element):
    try:
        return element.find_element_by_xpath('.//p[contains(@class, "hc_hotel_numberOfReviews")]/span').text.strip()
    except:
        return 0

def scrape_dates():
    for date in dates:
        scrape_cities(url, date)

def scrape_cities(url, date):
    for city in cities:
        c1 = 0
        while c1 != 5:
            try:
                scrape_city(url, city, date)
                break
            except:
                c1 += 1
                os.system('taskkill /f /im chromedriver.exe')
                pass

def scrape_city(url, city, date):
    driver = spider(url)
    element = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('.//div[@class="hcsb_citySearchWrapper"]/input'))
    element.send_keys(city)
    element_2 = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('.//ul[@id="ui-id-1"]/li'))
    element_2.click()

    checkin = datetime.now() + timedelta(date)
    checkin_year_month = '%s-%s' % (checkin.year, checkin.month)
    checkout = datetime.now() + timedelta(date + 3)
    checkout_year_month = '%s-%s' % (checkout.year, checkout.month)

    element_3 = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//select[@class="hcsb_checkinDay"]/option[@value="%s"]' % checkin.day))
    element_3.click()
    element_4 = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//select[@class="hcsb_checkinMonth"]/option[@value="%s"]' % checkin_year_month))
    element_4.click()

    element_5 = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//select[@class="hcsb_checkoutDay"]/option[@value="%s"]' % checkout.day))
    element_5.click()
    element_6 = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//select[@class="hcsb_checkoutMonth"]/option[@value="%s"]' % checkout_year_month))
    element_6.click()

    element_7 = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('.//button[contains(@class, "ui-datepicker-close")]'))
    element_7.click()
    element_8 = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('.//select[@class="hcsb_guests"]/option[@value="1-1"]'))
    element_8.click()
    element_9 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="hcsb_searchButton"]')))
    element_9.click()
    WebDriverWait(driver, 10).until(lambda driver: len(driver.window_handles) > 1)
    driver.switch_to_window(driver.window_handles[1])
    scrape_hotels(driver, city, checkin.strftime('%m/%d/%Y'), checkout.strftime('%m/%d/%Y'), date)
    driver.quit()

def scrape_hotels(driver, city, checkin, checkout, date):
    count = 0
    while True:
        time.sleep(20)
        hotels = driver.find_elements_by_xpath('.//div[@class="hc_sr_summary"]/div[@class="hc_sri hc_m_v4"]')
        for hotel in hotels:
            name = scrape_name(hotel)
            new_price, old_price = scrape_price(hotel)
            review = scrape_review(hotel)
            rating = scrape_rating(hotel)
            address = ''
            city = city.split(',')[0]
            currency = 'GTQ'
            source = 'book-hotel-beds.com'
            count += 1
            sql_write(conn, cur, name, rating, review, address, new_price, old_price, checkin, checkout, city, currency, source, count, date)
        time.sleep(10)
        try:
            driver.find_element_by_xpath('.//span[contains(@class, "pagination_next")]').click()
        except Exception, e:
            print '%s, %s, %s hotels, checkin %s, checkout %s, range %s' % (source, city, count, checkin, checkout, date)
            break


if __name__ == '__main__':
    global conn
    global cur
    conn = pyodbc.connect(r'DRIVER={SQL Server};SERVER=(local);DATABASE=hotels;Trusted_Connection=Yes;')
    cur = conn.cursor()
    url = 'http://www.book-hotel-beds.com/'
    scrape_dates()
    conn.close()


