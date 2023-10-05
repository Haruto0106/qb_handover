import selenium
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

###注意###
#必ず使う前にすべてのchromeを閉じること！！！#

class Google_map(webdriver.Chrome):
    def __init__(self, options: Options = None, service: Service = None, keep_alive: bool = True) -> None:
        super().__init__(options, service, keep_alive)
        
    def connect_map(self, filename):
        # self.get("https://www.google.com/maps/d/edit?mid=1xKpRGqwE8uADSR4TXu0K2IAKU7_MGOw&ll=35.7967851633272%2C139.89187999999996&z=13")
        self.get("https://www.google.com/maps/d/viewer?mid=1022Apvy7vVeDwBbGWMPJXtyZIdw&hl=ja&ll=36.387674999999994%2C139.032733&z=17")

        while True:
            try:
                self.find_element(By.XPATH, "//*[@id='legendPanel']/div/div/div[1]/div[1]/div/span/span/span").click()
                break
            except:
                time.sleep(0.1)
                continue
        while True:
            try:
                self.find_element(By.XPATH, '/html/body/div[1]/div[7]/div[3]/div[1]/div[1]/div[2]').click()
                break
            except :
                time.sleep(0.1)
                continue
        while True:
            try:
                self.find_element(By.XPATH, '//*[@id="map-title-desc-bar"]/div[1]').click()
                break
            except:
                time.sleep(0.1)
                continue
        while True:
            try:
                rename = self.find_elements(By.TAG_NAME, "input")
                rename[2].send_keys(filename)
                break
            except:
                time.sleep(0.1)
                continue
        while True:
            try:
                self.find_element(By.XPATH, "//button[@name='save']").click()
                break
            except:
                time.sleep(0.1)
                continue                
    
    def plot(self, lat, lon):
            while True:
                try:
                    id = self.find_element(By.ID, "mapsprosearch-field")
                    id.send_keys(str(lat) + "," + str(lon))
                    break
                except :
                    time.sleep(0.1)
                    continue
            while True:
                try :
                    self.find_element(By.ID, "mapsprosearch-button").click()
                    break
                except:
                    time.sleep(0.1)
                    continue
            while True:
                try :
                    self.find_element(By.XPATH,f"//div[@title='{lat},{lon}']").click()
                    break
                except:
                    time.sleep(0.1)
                    continue
            while True:
                try :
                    self.find_element(By.ID, "addtomap-button").click()
                    break
                except:
                    time.sleep(0.1)
                    continue
        
        
class ChromeOption(Options):
    def __init__(self, chromepath, profilename) -> None:
        super().__init__()
        self.add_argument(f"--user-data-dir=C:{chromepath}")
        self.add_argument(f"--profile-directory={profilename}")##chrome://version のプロフィールパスで確認
        # self.add_argument('--headless')
        self.add_argument("--no-sandbox")
        self.add_argument("--disable-dev-shm-usage")
        
    
if __name__ == "__main__":
    
    ##使う人のコンピュータによって違う(秀島はこれ)#####################################
    chromepath = "\\Users\\taiko\\AppData\\Local\\Google\\Chrome\\User Data" 
    profilename = "Profile 7"
    ################################################################################
    
    
    filename = "0625test"
    lat, lon = 35.796763, 139.89185
    options = ChromeOption(chromepath=chromepath, profilename=profilename)
    driver = Google_map(options=options)
    driver.connect_map(filename=filename)
    
    try:
        while True:
            driver.plot(lat=lat, lon=lon)
            time.sleep(2)
            lat += 0.001
            lon += 0.001
    finally :
        driver.close()

    

