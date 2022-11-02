from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
import time
import re
import json
import os
import sys

options=Options()
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get('https://www.oddsportal.com/matches/tennis/')
base_window = driver.current_window_handle
assert len(driver.window_handles) == 1
cookies = driver.find_element(By.ID, "onetrust-reject-all-handler")
cookies.click()

my_selector = 'td.name.table-participant'
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
matches98={}

## Main scraping script
def collect():
    try:
        my_elements = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, my_selector)))

        for element in my_elements:
            link = element.find_element(By.TAG_NAME, 'a')
            #print("element :", element.text)

            link.send_keys(Keys.CONTROL + Keys.ENTER)

            driver.switch_to.window(driver.window_handles[-1])
            #time.sleep(3)
            #cookies = driver.find_element(By.ID, "onetrust-reject-all-handler")
            #cookies.click()

            get_highest = driver.find_element(By.CLASS_NAME, 'highest')

            ## Getting "1" column odds for a match:         
            first_odds1 = get_highest.find_element(By.XPATH, "//*[@class='highest']/td[2]")
            print(first_odds1.text)
            first_odds = float(first_odds1.text)
            print("1st odds: ", first_odds)

            ## Getting "2" column odds for a match:
            second_odds1 = get_highest.find_element(By.XPATH, "//*[@class='highest']/td[3]")
            print(second_odds1.text)
            second_odds = float(second_odds1.text)
            print("2nd odds: ", second_odds)

            ## Getting "payout" column for a match:
            payout1 = get_highest.find_element(By.XPATH, "//*[@class='highest']/td[4]")
            if payout1.text == "-":
                payout = 0.0
            else:
                payout = float(re.search("\d+\.\d+", payout1.text).group())
            print("payout: ", payout)        

            ## Getting match name and time:
            match_details_name = driver.find_element(By.XPATH, '//*[@id="col-content"]/h1')
            print("name:", match_details_name.text)
            match_details_time = driver.find_element(By.XPATH, '//*[@id="col-content"]/p[1]')
            print("time: ", match_details_time.text)


            if first_odds + payout >= 98:
                #matches98[match_details_name.text] = match_details_time.text, first_odds+payout
                matches98['players'] =  match_details_name.text
                matches98['time'] =  match_details_time.text
                matches98['payout+odds'] =  first_odds+payout
            if second_odds + payout >= 98:
                #matches98[match_details_name.text] = match_details_time.text, second_odds+payout
                matches98['players'] =  match_details_name.text
                matches98['time'] =  match_details_time.text
                matches98['payout+odds'] =  second_odds+payout
            def WriteJson(matches98, f):
                j = json.dumps(matches98)
                f.write(j)
                f.write('\n')

            with open('File.json', 'w', buffering=1) as f:
                WriteJson(matches98, f)

            

            driver.close()
            driver.switch_to.window(base_window)
            #time.sleep(3)
    
    except KeyboardInterrupt:
        print("Keyboard interrupt, closing program")
        ## Optional: deletes json file upon interrupting the script
        # if os.path.exists("File.json"):
        #     os.remove("File.json")
        # else:
        #     print("The file does not exist")
        
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    
    except Exception as e:
        print("Exception encountered:", e)

while True:
    collect()

