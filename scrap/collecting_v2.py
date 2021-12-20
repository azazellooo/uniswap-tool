from setup import ether_url
from pprint import pprint
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from selenium.common.exceptions import NoSuchElementException, JavascriptException, StaleElementReferenceException
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from setup import exec_path

NOT_AVAILABLE = 'N/A'


def find(driver):
    element = driver.find_element_by_xpath('//*[@id="mytable_tradingpairs_wrapper"]/div[4]/div[2]/div/ul/li[3]/span/strong[1]')
    if element:
        return element
    else:
        return False


def find_td(driver):
    element = driver.find_elements_by_tag_name('td')
    if element:
        return element
    else:
        return False

def scraping():
    option = webdriver.FirefoxOptions()
    option.add_argument('headless')
    driver = webdriver.Firefox(executable_path=exec_path, keep_alive=False, options=option)

    driver.get(ether_url)
    sleep(6)
    driver.find_element_by_xpath('//*[@id="lnkAgeDateTime2"]').click()
    html = driver.execute_script('return document.documentElement.outerHTML')
    sel_soup = BeautifulSoup(html, 'html.parser')
    last_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.find_element_by_xpath('//*[@id="mytable_tradingpairs_length"]/label/select').click()
    driver.find_element_by_xpath('//*[@id="mytable_tradingpairs_length"]/label/select/option[4]').click()
    print('switched to 100 rows mode')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    result = []
    sleep(10)
    while True:
        pagination = WebDriverWait(driver, 3).until(find)
        print(pagination.text)
        if pagination.text == '25':
            break
        sleep(3)
        trading_pairs_rows = driver.find_element_by_xpath(
            '/html/body/div[1]/main/div[3]/div/div[2]/div/div[2]/div[2]/div/div[3]/div[2]/table/tbody').find_elements_by_tag_name(
            'tr')
        for row in trading_pairs_rows:
            fields = WebDriverWait(row, 5).until(find_td)
            try:
                token_price = fields[2].find_element_by_tag_name('span').text
            except NoSuchElementException:
                token_price = fields[2].text
            except StaleElementReferenceException:
                token_price = NOT_AVAILABLE
            pair_created = ''
            liquidity_pair = ''
            liquidity_usd = ''
            volume = NOT_AVAILABLE
            token = ''
            try:
                pair_created = fields[5].find_element_by_class_name('showDate').find_element_by_tag_name('span').text
                liquidity_pair = fields[1].find_element_by_tag_name('a').text
                liquidity_usd = fields[3].find_elements_by_tag_name('span')[0].text
                volume = fields[4].text
                token = fields[6].find_element_by_tag_name('a').text
            except StaleElementReferenceException:
                pass
            finally:
                pair = {
                    'liquidity_pair': liquidity_pair,
                    'token_price_usd': token_price,
                    'liquidity_usd': liquidity_usd,
                    'volume': volume,
                    'pair_created': pair_created,
                    'token': token
                }
            print(len(result))
            result.append(pair)
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            next_page = driver.find_element_by_xpath(
                '/html/body/div[1]/main/div[3]/div/div[2]/div/div[2]/div[2]/div/div[4]/div[2]/div/ul/li[4]/a')
            ActionChains(driver).move_to_element(next_page).click().perform()
            print('Collecting...')
        except NoSuchElementException:
            print('warning')
            break
        except JavascriptException:
            print('js warning')
            break
    return result
