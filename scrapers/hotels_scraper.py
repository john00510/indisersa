#encoding: utf8
from selenium.webdriver.common.keys import Keys
from base_scraper import BaseScraper
from settings import cities
import time, re, sys


class HotelsScraper(BaseScraper):
    def __init__(self, mode):
        self.url = 'https://www.hotels.com/?pos=HCOM_US&locale=en_US'
        self.mode = mode
        self.cities = cities
        self.banners = [
            './/button[contains(@class, "close")]',
            './/div[@class="widget-query-group widget-query-occupancy"]',
            './/div/span[@class="title"][contains(text(), "Save an extra")]/following-sibling::span[@class="close-button"]',
            './/span[contains(@class, "close")]',
            './/button[contains(@class, "cta")]'
        ]
        self.currency = 'USD'
        self.source = 'hotels.com'
        BaseScraper.__init__(self)

    def scrape_pages(self):
        element_to = './/li[contains(text(), "Travelers also looked at these properties nearby")]'
        self.scroll_to_element(800, element_to)

        elements = './/ol[contains(@class, "listings")]/li[contains(@class, "hotel")][not(contains(@class, "expanded-area"))]'
        self.presence(self.driver, elements, 10)
        elements = self.elements(self.driver, elements)
        self.scrape_hotels(elements)

    def city_element(self):
        self.close_banner()
        element = './/input[@name="q-destination"]'
        self.visibility(self.driver, element, 10).send_keys(self.city)
        element = './/h1[contains(@class, "widget-query-heading")]'
        self.presence(self.driver, element, 10).click()

    def checkin_element(self):
        element = '//input[@name="q-localised-check-in"]'
        self.clickable(self.driver, element)
        self.presence(self.driver, element, 10).clear()
        self.presence(self.driver, element, 10).send_keys(self.checkin2)    

    def checkout_element(self):
        element = '//input[@name="q-localised-check-out"]'
        self.clickable(self.driver, element)
        self.presence(self.driver, element, 10).clear()
        self.presence(self.driver, element, 10).send_keys(self.checkout2)

    def occupancy_element(self):
        element = './/select[@id="qf-0q-compact-occupancy"]/option[contains(text(), "1 room, 1 adult")]'
        element = self.visibility(self.driver, element, 10)
        element.click()

    def submit_element(self):
        element = './/button[contains(@type, "submit")]'
        element = self.visibility(self.driver, element, 10)
        element.click()

    def scrape_name(self, _element):
        return _element.get_attribute('data-title')

    def scrape_address(self, _element):
        element = './/p[contains(@class, "p-adr")]/span'
        elements = self.elements(_element, element)
        elements = [x.text for x in elements]
        elements = ', '.join(elements)
        return elements

    def scrape_price(self, _element):
        element = './/*[contains(text(), "$")]'
        element = self.elements(_element, element)
        element = [e.text.strip('$') for e in element]
        return element

    def scrape_new_price(self, element):
        elements = self.scrape_price(element)
        if len(elements) > 0:
            return elements[-1]
        else:
            return 0

    def scrape_old_price(self, element):
        elements = self.scrape_price(element)
        if len(elements) == 0 or len(elements) == 1:
            return 0
        else:
            return elements[0]

    def scrape_rating(self, _element):
        try:
            element = './/div[contains(@class, "guest-rating")]'
            element = self.element(_element, element, 2).text
            element = re.findall(r'([0-9.]+)', element)[0]
            return element
        except:
            return 0

    def scrape_review(self, _element):
        try:
            element = './/span[contains(@class, "total-reviews")]'
            element = self.element(_element, element, 2).text
            element = re.findall(r'([0-9,]+)', element)[0]
            element = re.sub(r',', '', element)
            return element
        except:
            return 0


if __name__ == '__main__':
    try: mode = sys.argv[1]
    except: mode = ''

    HotelsScraper(mode)

