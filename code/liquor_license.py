import time
import datetime
import logging
from random import randint

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# create logger
logging.basicConfig(
    level=logging.INFO,
    filename="liquor_license_scraping.log",
    filemode="a",  # append to the log file
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# put the chromium driver in the same folder as this file
# downlaod the driver here: https://chromedriver.chromium.org/downloads


search_city = "Iowa City"
url = "https://iowaabd.my.site.com/s/public-database"


options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get(url)

dt_now = datetime.datetime.now()
logging.info(f"Started scraping at {dt_now}")

#################### Search for a city ####################

# wait for the page to load, then click on "Premise Location" tab
premise_location_tab = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="tab-5__item"]'))
)
premise_location_tab.click()

# wait for "Premise Location" tab to load
city_input = WebDriverWait(driver, 10).until(
    EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="input-75"]'))
)

# if city input is present, then enter the city name
if city_input:
    city_input[0].send_keys(search_city)
    time.sleep(2)

    # click on the search button
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//*[@id="tab-5"]/slot/c-iaabd-premise-public-access/article/div[1]/lightning-layout/slot/lightning-layout-item[8]/slot/div/lightning-button/button',
            )
        )
    )

    search_button.click()

#################### End search for a city ####################


def scrape():
    # time.sleep(randint(10, 20))

    bars = WebDriverWait(driver, 30).until(
        EC.visibility_of_all_elements_located(
            (By.XPATH, "//span[@class='slds-media__body']")
        )
    )

    bars = driver.find_elements(By.XPATH, "//span[@class='slds-media__body']")

    for bar in bars:
        bar_name.append(bar.find_element(By.XPATH, "./span[1]").text)
        address.append(bar.find_element(By.XPATH, "./span[2]").text)


#################### Scrape the results ####################
bar_name = []
address = []

next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            '//*[@id="tab-5"]/slot/c-iaabd-premise-public-access/article/div[2]/lightning-layout-item/slot/div/ul/li[6]/button',
        )
    )
)
more_bars = True
while more_bars := True:
    print("scrape the results on this page")
    scrape()
    print(f"#bars: {len(bar_name)} and the last bar scraped is: {bar_name[-1]}")
    print(f"#addresses: {len(address)} and the last address scraped is: {address[-1]}")
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="tab-5"]/slot/c-iaabd-premise-public-access/article/div[2]/lightning-layout-item/slot/div/ul/li[6]/button',
                )
            )
        )
    except TimeoutException:
        more_bars = False
        break
    next_button.click()
    time.sleep(3)

# scrape the last page of results - next button will not be present
if more_bars := False:
    print("scrape the results on the last page")
    scrape()
    print(f"#bars: {len(bar_name)} and the last bar scraped is: {bar_name[-1]}")
    print(f"#addresses: {len(address)} and the last address scraped is: {address[-1]}")
    time.sleep(20)
#################### End scrape the results ####################

# create a dataframe from the scraped data
df = pd.DataFrame(
    {
        "bar": bar_name,
        "address": address,
    }
)

logging.info(f"Scraped {len(bar_name)} bars in {search_city}")

dt_now = datetime.datetime.now()
logging.info(f"Done scraping at {dt_now}")

currentMonth = dt_now.month
currentYear = dt_now.year
filename = f"../{currentYear}-{currentMonth}_{search_city}_liquor_license.csv"
df.to_csv(filename, encoding="utf-8", index=False)

driver.quit()
