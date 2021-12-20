import json
from datetime import datetime
from setup import ether_url
import sys
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.webdriver.common.by import By

from selenium.common.exceptions import (
    NoSuchElementException,
    JavascriptException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException,
    TimeoutException,
    NoSuchWindowException,
    MoveTargetOutOfBoundsException
)
from selenium.webdriver.common.action_chains import ActionChains
from multiprocessing import Pool
from setup import exec_path
from scrap.collecting_v2 import find, find_td

NOT_AVAILABLE = "N/A"
ALL_TRANSACTIONS = []
BASE_URL = "https://cn.etherscan.com"
dates = sys.argv[1:]
try:
    start = datetime.strptime(f"{dates[0]} 00:00:00", "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(f"{dates[1]} 00:00:00", "%Y-%m-%d %H:%M:%S")
except ValueError:
    sys.exit('Error! Enter valid dates. Enter dates in format "year-month-day"')


def scroll_to_bottom(driver):

    old_position = 0
    new_position = None

    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
            (
                "return (window.pageYOffset !== undefined) ?"
                " window.pageYOffset : (document.documentElement ||"
                " document.body.parentNode || document.body);"
            )
        )
        # Sleep and Scroll
        sleep(1)
        driver.execute_script(
            (
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"
            )
        )
        # Get new position
        new_position = driver.execute_script(
            (
                "return (window.pageYOffset !== undefined) ?"
                " window.pageYOffset : (document.documentElement ||"
                " document.body.parentNode || document.body);"
            )
        )


def find_link(driver):
    element = driver.find_elements_by_tag_name("a")
    if element:
        return element
    else:
        return False


def find_pagination_stopper(driver):
    elem = driver.find_element_by_xpath(
        "/html/body/div[3]/form/div[3]/ul/li[3]/span/strong[1]"
    )
    if elem:
        return elem
    else:
        return False


def find_tds(driver):
    elem = driver.find_elements_by_tag_name("td")
    if elem:
        return elem
    else:
        return False


def get_links():
    option = webdriver.FirefoxOptions()
    option.add_argument("headless")
    driver = webdriver.Firefox(
        executable_path=exec_path, keep_alive=False, options=option
    )

    driver.get(ether_url)
    sleep(6)
    date_format_switcher = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lnkAgeDateTime2"]')))
    date_format_switcher.click()
    # driver.find_element_by_xpath('//*[@id="lnkAgeDateTime2"]').click()
    html = driver.execute_script("return document.documentElement.outerHTML")
    last_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.find_element_by_xpath(
        '//*[@id="mytable_tradingpairs_length"]/label/select'
    ).click()
    driver.find_element_by_xpath(
        '//*[@id="mytable_tradingpairs_length"]/label/select/option[4]'
    ).click()
    print("switched to 100 rows mode")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    result = []
    sleep(10)
    while True:
        pagination = WebDriverWait(driver, 3).until(find)
        print(f"----page {pagination.text}----")
        if pagination.text == "25":
            print("collecting links is completed")
            break
        sleep(3)
        trading_pairs_rows = driver.find_element_by_xpath(
            "/html/body/div[1]/main/div[3]/div/div[2]/div/div[2]/div[2]/div/div[3]/div[2]/table/tbody"
        ).find_elements_by_tag_name("tr")
        for row in trading_pairs_rows:
            try:
                fields = WebDriverWait(row, 5).until(find_td)
            except StaleElementReferenceException:
                fields = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "td"))
                )
            link = ""
            try:
                link = fields[7].find_element_by_tag_name("a").get_attribute("href")
            except StaleElementReferenceException:
                pass
            print(len(result), link)
            result.append(link)
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)
            print("switching to next page...")
            next_page = driver.find_element_by_xpath(
                "/html/body/div[1]/main/div[3]/div/div[2]/div/div[2]/div[2]/div/div[4]/div[2]/div/ul/li[4]/a"
            )
            try:
                ActionChains(driver).move_to_element(next_page).click().perform()
            except MoveTargetOutOfBoundsException:
                driver.execute_script("arguments[0].scrollIntoView();", next_page)
                next_page = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div[3]/div/div[2]/div/div[2]/div[2]/div/div[4]/div[2]/div/ul/li[4]/a")))
                ActionChains(driver).move_to_element(next_page).click().perform()
            print("Collecting...")
        except NoSuchElementException:
            print("warning")
            break
        except JavascriptException:
            print("js warning")
            break
    driver.close()
    driver.quit()
    return result


def get_transactions_per_pair(link):
    option = webdriver.FirefoxOptions()
    option.add_argument("headless")
    driver = webdriver.Firefox(
        executable_path=exec_path, keep_alive=False, options=option
    )
    try:
        driver.get(link)
        sleep(6)
        driver.execute_script("window.scrollBy(0,800)", "")
        frame = driver.find_element_by_xpath('//*[@id="txnsiframe"]')
        driver.switch_to.frame(frame)
        switch_date_format = driver.find_element_by_xpath('//*[@id="lnkAgeDateTimeV2"]')
        switch_date_format.click()
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element_by_xpath('//*[@id="ddlRecordsPerPage"]').click()
        driver.find_element_by_xpath('//*[@id="ddlRecordsPerPage"]/option[4]').click()
        print("switched to 100 rows mode in transactions page")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        transactions = []
        sleep(10)
        stopper = 0
        while stopper < 1000:
            try:
                pagination = driver.find_element_by_xpath(
                    "/html/body/div[3]/form/div[3]/ul/li[3]/span/strong[1]"
                )
            except NoSuchElementException:
                pagination = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[3]/form/div[3]/ul/li[3]/span/strong[1]",
                        )
                    )
                )
            print(f"-----page {pagination.text}-------")
            sleep(3)
            try:
                transactions_table = driver.find_element_by_xpath(
                    "/html/body/div[3]/div[2]/table/tbody"
                ).find_elements_by_tag_name("tr")
            except NoSuchElementException:
                tbody = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[3]/div[2]/table/tbody")
                    )
                )
                transactions_table = tbody.find_elements_by_tag_name("tr")
            print(len(transactions_table))
            if len(transactions_table) > 2:
                for row in transactions_table:
                    index = transactions_table.index(row) + 1
                    print("started to collect transactions")
                    try:
                        txn_hash = row.find_element_by_xpath(
                            f"/html/body/div[3]/div[2]/table/tbody/tr[{index}]/td[2]/span"
                        ).text
                        date_time = row.find_element_by_xpath(
                            f"/html/body/div[3]/div[2]/table/tbody/tr[{index}]/td[3]/span"
                        ).text
                        action = row.find_element_by_xpath(
                            f"/html/body/div[3]/div[2]/table/tbody/tr[{index}]/td[5]/span"
                        ).text
                        price = row.find_element_by_xpath(
                            f"/html/body/div[3]/div[2]/table/tbody/tr[{index}]/td[6]/span[1]"
                        ).text
                        amount = row.find_element_by_xpath(
                            f"/html/body/div[3]/div[2]/table/tbody/tr[{index}]/td[7]"
                        ).text
                        value = row.find_element_by_xpath(
                            f"/html/body/div[3]/div[2]/table/tbody/tr[{index}]/td[8]/span[1]"
                        ).text
                    except (NoSuchElementException, StaleElementReferenceException):
                        try:
                            ind = transactions_table.index(row) + 1
                            txn_span = WebDriverWait(driver, 12).until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        f"/html/body/div[3]/div[2]/table/tbody/tr[{ind}]/td[2]/span",
                                    )
                                )
                            )
                            txn_hash = txn_span.text
                            date_time_span = WebDriverWait(driver, 12).until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        f"/html/body/div[3]/div[2]/table/tbody/tr[{ind}]/td[3]/span",
                                    )
                                )
                            )
                            date_time = date_time_span.text
                            action_span = WebDriverWait(driver, 12).until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        f"/html/body/div[3]/div[2]/table/tbody/tr[{ind}]td[5]/span",
                                    )
                                )
                            )
                            action = action_span.text
                            price_span = WebDriverWait(driver, 12).until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        f"/html/body/div[3]/div[2]/table/tbody/tr[{ind}]/ts[6]/span[1]",
                                    )
                                )
                            )
                            price = price_span.text
                            amount_td = WebDriverWait(driver, 12).until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        f"/html/body/div[3]/div[2]/table/tbody/tr[{ind}]/td[7]",
                                    )
                                )
                            )
                            amount = amount_td.text
                            value_span = WebDriverWait(driver, 12).until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        f"/html/body/div[3]/div[2]/table/tbody/tr[{ind}]/td[8]/span[1]",
                                    )
                                )
                            )
                            value = value_span.text
                        except TimeoutException:
                            print("time is out")
                            return []

                    transaction = {
                        "txn_hash": txn_hash,
                        "date_time": date_time,
                        "action": action,
                        "price_usd": price,
                        "token_amount": amount,
                        "total_value": value,
                    }
                    transactions.append(transaction)
                    print(transaction)
                    print(f'Added transaction {transaction["txn_hash"]}')
            else:
                print("No txn matching your filter.")
            sleep(3)
            pagination = WebDriverWait(driver, 3).until(find_pagination_stopper)
            if pagination.text == "3" or pagination.text == 3 or stopper == 3:
                print("___________________________________________")
                break
            next_page = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[3]/form/div[3]/ul/li[4]")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView();", next_page)
            try:
                next_page.click()
            except ElementClickInterceptedException:
                webdriver.ActionChains(driver).move_to_element(next_page).click(
                    next_page
                ).perform()
            try:
                ActionChains(driver).move_to_element(next_page).click().perform()
            except StaleElementReferenceException:
                next_page = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[3]/form/div[3]/ul/li[4]")
                    )
                )
                ActionChains(driver).move_to_element(next_page).click().perform()
            stopper += 1
        driver.close()
        driver.quit()
        return transactions
    except (WebDriverException, NoSuchWindowException):
        driver.close()
        driver.quit()
        print("connection error")
        return []


if __name__ == "__main__":
    trading_pairs_links = get_links()
    if trading_pairs_links or len(trading_pairs_links) >= 1:
        print("pairs links collected successfully")
    while len(trading_pairs_links) > 0:
        links = trading_pairs_links[:7]
        pool = Pool(processes=len(links))
        results = []

        print("processes are started")
        res = pool.map(func=get_transactions_per_pair, iterable=links)
        pool.close()
        pool.join()
        for i in enumerate(res):
            result = []
            for txn in i[1]:
                try:
                    if (
                        start
                        <= datetime.strptime(txn["date_time"], "%Y-%m-%d %H:%M:%S")
                        <= end
                    ):
                        result.append(txn)
                except ValueError:
                    sys.exit("invalid date")
                # try:
                #     result = list(filter((lambda d: start <= datetime.strptime(d['date_time'], '%Y-%m-%d %H:%M:%S') <= end), i[1]))
                # except ValueError:
                result = i[1]
            transactions_json = json.dumps(result)
            df_json = pd.read_json(transactions_json)
            df_json.to_excel(
                f'transactions/pair_{links[i[0]].strip("https://cn.etherscan.com/dex/uniswapv3/")}_txns.xlsx'
            )
            print("writing excel files...")
        del trading_pairs_links[:7]
