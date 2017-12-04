#encoding: utf8
from base_scraper import BaseScraper
import time, sys, re


class DespegarScraper(BaseScraper):
    def __init__(self, url, spider):
        BaseScraper.__init__(self, url, spider)
        self.currency = 'USD'
        self.source = 'us.despegar.com'
        self.banners = [
            './/i[@class="nevo-modal-close nevo-icon-close"]',
            './/span[contains(@class, "eva-close")]',
        ]
        self.base_func()
      

    def main_page(self):
        self.next_element = './/a[@data-ga-el="next"]'
        self.close_banner()
        self.city_element()
        self.checkin_element()
        self.checkout_element()
        self.occupation_element()
        self.submit_element()
        self.scrape_pages()

    def city_element(self):
        element = './/input[contains(@class, "sbox-destination")]'
        element = self.presence(self.driver, element, 10)
        element.send_keys(self.city)

        element = './/div[@class="geo-searchbox-autocomplete-holder-transition"]'
        if self.city == 'Guatemala City, Guatemala':
            element2 = './/*[contains(., "Guatemala City, Guatemala, Guatemala")]'

        if self.city == 'Antigua Guatemala, Guatemala':
            element2 = './/*[contains(., "Antigua, Sacatepequez, Guatemala")]'
        
        while True:
            try:
                _element = self.presence(self.driver, element, 10)
                _element = self.elements(_element, element2)[1]
                _element.click()
                break
            except:
                pass

    def checkin_checkout_scrape(self, date):
        elements = './/div[contains(@data-month, "{}")]/div/span[contains(text(), "{}")]'
        next_element = './/div[contains(@class, "dpmg2--controls-next")]'

        x = 0
        elements = elements.format(date.strftime('%Y-%m'), date.day)
        while True:
            _elements = self.elements(self.driver, elements)
            for _element in _elements:
                try:
                    _element.click()
                    x = 1
                    break
                except:
                    pass

            if x == 1:
                break

            _next_element = self.visibility(self.driver, next_element, 5)
            _next_element.click()

    def checkin_element(self):
        element = './/input[contains(@class, "sbox-checkin-date")]'
        element = self.visibility(self.driver, element, 10)
        element.click()
        self.checkin_checkout_scrape(self.checkin)

    def checkout_element(self):
        self.checkin_checkout_scrape(self.checkout)

    def occupation_element(self):
        element = './/div[contains(@class, "sbox-guests-container")]'
        element = self.presence(self.driver, element, 5)
        element.click()
        element2 = './/a[contains(@class, "icon-minus")]'
        element2 = self.presence(self.driver, element2, 5)
        element2.click()
        element3 = './/div[contains(@class, "full")]'
        element3 = self.presence(self.driver, element3, 5)
        element3.click()

    def submit_element(self):
        element = './/a[contains(@class, "sbox-search")]'
        element = self.visibility(self.driver, element, 5)
        element.click()

    def scrape_pages(self):
        self.close_banner()

        while True:
            x = self.scrape_hotels()    

#            self.scroll_to_bottom()
        
            try:
                _next_element = self.visibility(self.driver, next_element, 5)
                _next_element.click()
                self.close_banner()
            except:
                self.driver.quit()
                self.report()
                break

    def get_elements(self):
        elements = './/div[contains(@id, "hotels")]/div[contains(@class, "results-cluster-container")]'
        return self.elements(self.driver, elements)

    def scrape_name(self, element):
        _element = './/h3[@class="hf-hotel-name"]/a'
        return self.visibility(element, _element, 5).get_attribute('title') 

    def scrape_address(self, element):
        _element = './/li[@class="hf-cluster-distance"]/span'
        return self.visibility(element, _element, 5).text.strip()

    def scrape_new_price(self, element):
        _element = './div[contains(@class, "analytics")]'
        return self.visibility(element, _element, 5).get_attribute('data-price')

    def scrape_old_price(self, element):
        try:
            _element = './/span[contains(@class, "pricebox-price-discount")]'
            _element = self.visibility(element, _element, 5).text
            return re.findall(r'([0-9.]+)', _element)[0]
        except:
            return 0

    def scrape_rating(self, element):
        try:
            _element = './/span[contains(@class, "rating-text")]'
            return self.visibility(element, _element, 5).text.strip()
        except:
            return 0

    def scrape_review(self, element):
        _element = './/p[contains(@class, "tooltip-text")]'
        return 0
    

if __name__ == '__main__':
    spider = 'chrome'
    url = 'https://www.us.despegar.com/hotels/'
    DespegarScraper(url, spider)


