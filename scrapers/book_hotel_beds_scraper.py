#encoding: utf8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from processors import spider, sql_write
import pyodbc, time, os, traceback
from datetime import datetime, timedelta

cities = [
    'Guatemala City, Guatemala',
    'Antigua Guatemala, Guatemala',   
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
        scrape_city(url, city, date)

def scrape_city(url, city, date):
    driver = spider(url)

    ##### city
    city_el_1 = './/div[@class="hcsb_citySearchWrapper"]/input'
    city_element_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, city_el_1)))
    city_element_1.send_keys(city)

    city_el_2 = './/ul[@id="ui-id-1"]/li' 
    city_element_2 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, city_el_2)))
    city_element_2.click()
    
    ##### checkin
    checkin = datetime.now() + timedelta(date)
    checkin_year_month = '%s-%s' % (checkin.year, checkin.month)

    checkin_el_1 = '//select[@class="hcsb_checkinMonth"]/option[@value="{}"]'.format(checkin_year_month)
    checkin_element_1 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, checkin_el_1)))
    checkin_element_1.click()
    
    checkin_el_2 = '//select[@class="hcsb_checkinDay"]/option[@value="{}"]'.format(checkin.day)
    checkin_element_2 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, checkin_el_2)))
    checkin_element_2.click()

    checkin_el_3 = './/div[contains(@class, "hcsb_checkinDateWrapper")]'
    checkin_element_3 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, checkin_el_3)))
    checkin_element_3.click()

    ##### checkout
    checkout = datetime.now() + timedelta(date + 3)
    checkout_year_month = '%s-%s' % (checkout.year, checkout.month)

    checkout_el_1 = '//select[@class="hcsb_checkoutMonth"]/option[@value="{}"]'.format(checkout_year_month)
    checkout_element_1 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, checkout_el_1)))
    checkout_element_1.click()
    
    checkout_el_2 = '//select[@class="hcsb_checkoutDay"]/option[@value="{}"]'.format(checkout.day)
    checkout_element_2 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, checkout_el_2)))
    checkout_element_2.click()

    checkout_el_3 = './/div[contains(@class, "hcsb_checkinDateWrapper")]'
    checkout_element_3 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, checkout_el_3)))
    checkout_element_3.click()

    ##### occupancy
    occupancy_el = './/select[@class="hcsb_guests"]/option[@value="1-1"]'
    occupancy_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, occupancy_el)))
    occupancy_element.click()

    ##### submit
    submit_el = '//a[@class="hcsb_searchButton"]'
    submit_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, submit_el)))
    submit_element.click()

    WebDriverWait(driver, 10).until(lambda driver: len(driver.window_handles) > 1)
    driver.switch_to_window(driver.window_handles[1])

    scrape_hotels(driver, city, checkin.strftime('%m/%d/%Y'), checkout.strftime('%m/%d/%Y'), date)

def scrape_hotels(driver, city, checkin, checkout, date):
    _next = './/a[contains(text(), "Next")]'
    hotels_el = './/div[@class="hc_sr_summary"]/div[@class="hc_sri hc_m_v4"]'
    count = 0
    while True:
        time.sleep(20)
        hotels = driver.find_elements_by_xpath(hotels_el)

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
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            page_next = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, _next)))
            page_next.click()
        except Exception, e:
            print '%s, %s, %s hotels, checkin %s, checkout %s, range %s' % (source, city, count, checkin, checkout, date)
            driver.quit()
            break


if __name__ == '__main__':
    global conn
    global cur

    conn = pyodbc.connect(r'DRIVER={SQL Server};SERVER=(local);DATABASE=hotels;Trusted_Connection=Yes;')
    cur = conn.cursor()

    url = 'http://www.book-hotel-beds.com/'
    scrape_dates()

    conn.close()


