#!/usr/bin/python
#encoding: utf8
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from processors import *
import re, pyodbc, time
from datetime import datetime, timedelta

cities = [
    'Guatemala City, Guatemala',
    'Antigua Guatemala, Guatemala',
]

banners = [
    './/span[contains(@class, "icon-close")]',
    './/div[@class="hero-banner-box cf"]',
]

dates = [15, 30, 60, 90, 120]

url = 'https://www.expedia.com/Hotels'
currency = 'USD'
source = 'expedia.com'

def get_name(element):
    return element.find_element_by_xpath('./h3').text.strip()

def get_review(element):
    review = './/li[contains(@class, "reviewCount")]/span'
    try:
        review = element.find_elements_by_xpath(review)[1].text
        review = review.strip().strip('(').strip(')')
        return review
    except:
        return 0

def get_rating(element):
    rating = './/li[@class="reviewOverall"]/span'
    try:
        rating = element.find_elements_by_xpath(rating)[1].text.strip()
        return rating
    except:
        return 0

def get_actualprice(element):
    try:
        price = './/ul[@class="hotel-price"]/li[@data-automation="actual-price"]/a'
        price = element.find_element_by_xpath(price).text.strip()
        price = re.findall(r'([0-9$]+)', price)[0].strip('$')
    except:
        try:
            price = './/ul[@class="hotel-price"]/li[@data-automation="actual-price"]'
            price = element.find_element_by_xpath(price).text.strip()
            price = re.findall(r'([0-9$]+)', price)[0].strip('$')
        except:
            price = 0
    return price

def get_strikeprice(element):
    try:
        price = './/ul[@class="hotel-price"]/li[@data-automation="strike-price"]/a'
        price = element.find_element_by_xpath(price).text.strip()
        price = re.findall(r'([0-9$]+)', price)[0].strip('$')
    except:
        price = 0
    return price

def get_address(element):
    address = './/ul[@class="hotel-info"]/li[@class="neighborhood secondary"]'
    address = element.find_element_by_xpath(address).text.strip()
    try:
        phone = './/ul[@class="hotel-info"]/li[@class="phone secondary gt-mobile"]/span'
        phone = element.find_element_by_xpath(phone).text.strip()
    except:
        phone = ''
    line = '%s, %s.' % (address, phone)
    return line, address 

def scrape_dates():
    for date in dates:
        scrape_cities(url, date)

def scrape_cities(url, date):
    for city in cities:
        scrape_city(url, city, date) 

def scrape_city(url, city, date):
    driver = spider(url)

    city_element = './/input[@id="hotel-destination-hlp"]'
    city_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, city_element)))
    city_element.send_keys(city)

    close_banner(driver, banners)

    ### checkin
    checkin = datetime.now() + timedelta(date)
    checkinn = checkin.strftime('%m/%d/%Y')
    checkin_el = './/input[@id="hotel-checkin-hlp"]' 
    checkin_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, checkin_el)))
    checkin_element.send_keys(checkinn)

    ### checkout
    checkout = datetime.now() + timedelta(date + 3)
    checkoutt = checkout.strftime('%m/%d/%Y')
    checkout_el = './/input[@id="hotel-checkout-hlp"]'
    checkout_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, checkout_el)))
    checkout_element.clear()
    checkout_element.send_keys(checkoutt)

    ### occupation
    occupation_el = './/select[contains(@class, "gcw-guests-field")]/option[contains(text(), "1 adult")]'
    occupation_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, occupation_el)))
    occupation_element.click()

    ### scroll down
    scroll_down.range(driver, 5, 0)

    ### submit
    submit_el1 = './/section[@id="section-hotel-tab-hlp"]/form'
    submit_el2 = './/button[@type="submit"]'
    submit_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, submit_el1)))
    submit_element = WebDriverWait(submit_element, 10).until(EC.visibility_of_element_located((By.XPATH, submit_el2)))
    submit_element.click()
    
    scrape_hotels(driver, city, checkin.strftime('%m/%d/%Y'), checkout.strftime('%m/%d/%Y'), date)

def scrape_hotels(driver, city, checkin, checkout, date):
    _next = './/button[@class="pagination-next"]/abbr'
    count = 0
    while True:
        hotels = './/div[@id="resultsContainer"]/section/article'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, hotels)))
        hotels = driver.find_elements_by_xpath(hotels)
        for hotel in hotels:
            count += 1
            name = get_name(hotel)
            new_price = get_actualprice(hotel)
            old_price = get_strikeprice(hotel)
            review = get_review(hotel)
            rating = get_rating(hotel)
            address, location = get_address(hotel)
            city = city.split(',')[0]
            sql_write(conn, cur, name, rating, review, address, new_price, old_price, checkin, checkout, city, currency, source, count, date)   

        try:
            scroll_down.click_element(driver, 500, _next, 0.5)
            time.sleep(15)
        except:
            time.sleep(15)
            driver.quit()
            print '{}, {}, {} hotels, checkin {}, checkout {}, range {}'.format(source, city, count, checkin, checkout, date)
            break

if __name__ == '__main__':
    global conn
    global cur

    conn = pyodbc.connect(r'DRIVER={SQL Server};SERVER=(local);DATABASE=hotels;Trusted_Connection=Yes;')
    cur = conn.cursor()
    scrape_dates()
    conn.close()


