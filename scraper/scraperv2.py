from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
import time
import re
import json
import os
import sys
from itertools import groupby

options=Options()
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get('https://www.oddsportal.com/matches/tennis/')
base_window = driver.current_window_handle
assert len(driver.window_handles) == 1
cookies = driver.find_element(By.ID, "onetrust-reject-all-handler")
cookies.click()

my_selector = 'td.name.table-participant'
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,ElementNotInteractableException)
wait = WebDriverWait(driver,20,ignored_exceptions=ignored_exceptions)
#matches98=dict()
matches98 = []
# with open('static\File.json', 'w', buffering=1) as f:
#     f.write("[]")
#matches98=[]
#lastHeight = driver.execute_script("return document.documentElement.scrollHeight")

## Main scraping script
def collect():
    def scroll():
        lastHeight = driver.execute_script("return document.documentElement.scrollHeight")
        while True:

            driver.execute_script(f"window.scrollTo(0, {lastHeight});")
            time.sleep(3)    
            newHeight = driver.execute_script("return document.documentElement.scrollHeight")
            print('newHeight', newHeight)
            
            if newHeight == lastHeight:
                break
            lastHeight = newHeight
    scroll()
    try:
        #my_elements = WebDriverWait(driver, 20,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, my_selector)))
        my_elements = wait.until(expected_conditions.presence_of_all_elements_located((By.XPATH, '//*[@id="table-matches"]/table/tbody/tr/td/a[contains(@href,"/tennis/")and not(contains(@href,"javascript"))and not(contains(@href,"/inplay-odds/"))]')))
        #my_elements = wait.until(expected_conditions.presence_of_all_elements_located((By.XPATH, '//*[@id="table-matches"]/table/tbody/tr/td/a[starts-with(@href,"/tennis/")]')))
        element = wait.until(expected_conditions.element_to_be_clickable)
        for element in my_elements:
            #link = element.find_element(By.TAG_NAME, 'a')
            #link = element.find_element(By.XPATH, '//*[@id="table-matches"]/table/tbody/tr/td/a[not(contains(@javascript))][not(contains(@span,"live-odds-ico-prev"))][starts-with(@href,"/tennis/")]')
            #link = element.find_element(By.XPATH, '//*[@id="table-matches"]/table/tbody/tr/td/a[starts-with(@href,"/tennis/")]')
            #link = element.find_element(By.CLASS_NAME, 'bold')
            #element = WebDriverWait(driver,30,ignored_exceptions=ignored_exceptions).until(expected_conditions.element_to_be_clickable((By.TAG_NAME, 'a')))
            #table-matches > table > tbody > tr:nth-child(106) > td.name.table-participant > a
            #print("element :", element.text)
            #element = WebDriverWait(driver, 20,ignored_exceptions=ignored_exceptions).until(expected_conditions.element_to_be_clickable(my_elements))
            element.send_keys(Keys.CONTROL + Keys.ENTER)

            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(1)
            #cookies = driver.find_element(By.ID, "onetrust-reject-all-handler")
            #cookies.click()

            #switching to prematch odds:
            #event-detail-menu > ul > li:nth-child(1) > span > strong > a
            #//*[@id="event-detail-menu"]/ul/li[1]/span/strong/a
            # try:
            #     driver.find_element(By.PARTIAL_LINK_TEXT, "PRE-MATCH ODDS").click()
            #     time.sleep(5)
            # except:
            #     pass

            #get_highest = driver.find_element(By.CLASS_NAME, 'highest')
            #get_highest = wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'highest')))
            
            ## Getting "1" column odds for a match:         
            #first_odds1 = get_highest.find_element(By.XPATH, "//*[@class='highest']/td[2]")
            first_odds1 = wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//*[@class='highest']/td[2]")))
            #print(first_odds1.text)
            if "-" in first_odds1.text:
                first_odds = 0.0
            else:
                first_odds = float(first_odds1.text)
            print("1st odds: ", first_odds)

            ## Getting "2" column odds for a match:
            #second_odds1 = get_highest.find_element(By.XPATH, "//*[@class='highest']/td[3]")
            second_odds1 = wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//*[@class='highest']/td[3]")))
            #print(second_odds1.text)
            if "-" in second_odds1.text:
                second_odds = 0.0
            else:
                second_odds = float(second_odds1.text)
            print("2nd odds: ", second_odds)

            ## Getting "payout" column for a match:
            #payout1 = get_highest.find_element(By.XPATH, "//*[@class='highest']/td[4]")
            payout1 = wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//*[@class='highest']/td[4]")))
            #print(payout1.text)
            if "-" in payout1.text:
                payout = 0.0
            else:
                payout = float(re.search("\d+\.\d+", payout1.text).group())
            print("payout: ", payout)        

            ## Getting match name and time:
            match_details_name = driver.find_element(By.XPATH, '//*[@id="col-content"]/h1')
            print("name:", match_details_name.text)
            match_details_time = driver.find_element(By.XPATH, '//*[@id="col-content"]/p[1]')
            print("time: ", match_details_time.text)

            def WriteJson(matches98, f):
                j = json.dumps(matches98, separators = [',', ':'])
                #f.write('{')
                f.write(j)
                #f.write('}')
                f.write(',')
                f.write('\n')
            def load_json():
                with open('static\File.json', "r") as json_file:
                    data = json.load(json_file)
                    data.split("\n")
                    return data

            if first_odds + payout >= 98 and first_odds + payout >second_odds + payout:
                #matches98[match_details_name.text] = match_details_time.text, first_odds+payout
                # matches98['players'] =  match_details_name.text
                # matches98['time'] =  match_details_time.text
                # matches98['payout+odds'] =  first_odds+payout
                matches98.append(f"players: {match_details_name.text}, time: {match_details_time.text}, payout+odds: {first_odds+payout}")
                with open('static\File.json', 'a', buffering=1) as f:
                    WriteJson(matches98, f)
                    #f.split("\n")
                #load_json()
                # f = json.load('static\File.json')    
                # f.split("\n")
                # with open('static\File.json', 'r') as f:      
                #     data = f.read()
                #     f = data.split("\n")
            if second_odds + payout >= 98 and second_odds + payout > first_odds + payout:
                #matches98[match_details_name.text] = match_details_time.text, second_odds+payout
                # matches98['players'] =  match_details_name.text
                # matches98['time'] =  match_details_time.text
                # matches98['payout+odds'] =  second_odds+payout
                matches98.append(f"players: {match_details_name.text}, time: {match_details_time.text}, payout+odds: {second_odds+payout}")
                with open('static\File.json', 'w', buffering=1) as f:
                    WriteJson(matches98, f)
                #load_json()
                # f = json.load('static\File.json')    
                # f.split("\n")
                # with open('static\File.json', 'r') as f:    
                #     data = f.read()
                #     f = data.split("\n")
            else:   
                pass
            # matches98_unique = [{'players': key, 'payout+odds': max(item['payout+odds'] for item in values)}
            #      for key, values in groupby(matches98, lambda dct: dct['players'])]
            
            # def WriteJson(matches98, f):
            #     j = json.dumps(matches98)
            #     f.write(j)
            #     f.write(',')
            #     f.write('\n')

            # with open('File.json', 'a', buffering=1) as f:
            #     WriteJson(matches98, f)

            

            driver.close()
            driver.switch_to.window(base_window)
            time.sleep(1)
    
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