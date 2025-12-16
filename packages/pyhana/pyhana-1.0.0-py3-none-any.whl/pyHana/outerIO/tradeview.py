from   bs4      import BeautifulSoup
import time  
import pandas   as pd
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import datetime
from ..common  import urlProc, conf, dataProc

def get_value_bs(tr):    
    listRes = []
    tds = tr.select("td")

    shCode = tds[0].select("span>a")[0].text
    shName = tds[0].select("sup")[0].text

    x = tds[1].text.replace('USD','').replace(',','').strip()
    if len(x) == 0 or x in ( "-", "—"):
        price = 0
    else:
        price = float(x)

    x = tds[2].text.replace('%','').replace(',','').replace('−','-').strip()
    if len(x) == 0 or x in ( "-", "—"):
        change = 0
    else:
        change = float(x)

    x = tds[3].text.replace('\u202f','').replace(',','').strip()
    if len(x) == 0 or x in ( "-", "—"):
        volume = 0
    else:
        unit = 1
        if x[-1] < '0' or x[-1] > '9':        
            if x[-1] == 'B':
                unit = 1000000000
            elif x[-1] == 'M':
                unit = 1000000
            elif x[-1] == 'K':
                unit = 1000
            x = x[:-1]        
        volume = int(float(x) * unit)    

    x = tds[4].text.replace(',','').replace('%','').strip()
    if len(x) == 0 or x in ( "-", "—"):
        relVolume = 0
    else:
        relVolume = float(x)

    x = tds[5].text.replace('USD','').replace(',','').replace('\u202f','').strip()
    if len(x) == 0 or x in ( "-", "—"):
        marketCap = 0
    else:
        unit = 1
        if x[-1] < '0' or x[-1] > '9':        
            if x[-1] == 'T':
                unit = 1000000000000
            elif x[-1] == 'B':
                unit = 1000000000
            elif x[-1] == 'M':
                unit = 1000000
            elif x[-1] == 'K':
                unit = 1000
            x = x[:-1]        
        marketCap = float(x) * unit / 1000000

    x = tds[6].text.replace('%','').replace(',','').replace('−','-').strip()
    if len(x) == 0 or x in ( "-", "—"):
        per = 0
    else:
        per = float(x)

    x = tds[7].text.replace('USD','').replace(',','').replace('−','-').strip()
    if len(x) == 0 or x in ( "-", "—"):
        eps = 0
    else:
        eps = float(x)

    x = tds[8].text.replace('%','').replace(',','').replace('−','-').strip()
    if len(x) == 0 or x in ( "-", "—"):
        epsGrowth = 0
    else:
        epsGrowth = float(x)    

    x = tds[9].text.replace('%','').replace(',','').strip()
    if len(x) == 0 or x in ( "-", "—"):
        dividend = 0
    else:
        dividend = float(x)    

    sector = tds[10].text    

    analyst = tds[11].text        

    return [shCode, shName, price, change, volume, relVolume, marketCap, per, eps, epsGrowth, dividend, sector, analyst]

def GetStockInfoUSA():
    # 크롤링 환경 설정
    options = Options()
    options.add_experimental_option("detach", True)                         # 브라우저 꺼짐 방지 옵션
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 불필요한 에러 메시지 삭제
    options.add_argument("no-sandbox")                                      # 탭간에 옮겨 다니면서 원하는 액션 수행 가능
    # chrome 창 open
    try:            
        # s = Service(ChromeDriverManager().install())
        # chrome = webdriver.Chrome(service=s, options=options)    

        # 2024-08-05 '[winerror 193] %1은(는) 올바른 win32 응용 프로그램이 아닙니다' 에러 발생
        # 해결방법 : https://private.tistory.com/178 [오토봇팩토리:티스토리]

        driver_path = ChromeDriverManager().install()
        correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
        chrome = webdriver.Chrome(service=Service(executable_path=correct_driver_path), options=options)


    except Exception as e:
        print(e)    

    # 데이터 조회 (Selenium) 

    # 최초 url
    url = "https://www.tradingview.com/markets/stocks-usa/market-movers-all-stocks/"

    chrome.get(url)   

    while True:
        
        # 다음 조회 버튼이 있는 경우 다음 버튼 click 처리
        try :
            if chrome.find_elements(By.XPATH, '//*[@id="js-category-content"]/div[2]/div/div[4]/div[3]/button'):
                chrome.find_elements(By.XPATH, '//*[@id="js-category-content"]/div[2]/div/div[4]/div[3]/button')[0].click()
                time.sleep(1)
            else:
                break
        except:
            break    
            
    #-------------#
    # 데이터 추출 #
    #-------------#
    resList = []

    html_txt = chrome.page_source
    # ## Selenium 처리 - end        
    chrome.close()

    soup = BeautifulSoup(html_txt, "html.parser")
    trs = soup.select("tbody tr")

    if len(trs):
        for idx, tr in enumerate(trs):
            print("\r", idx, end="")
            resList.append(get_value_bs(tr))

    dfRes = pd.DataFrame(resList, columns=['종목코드', '종목명', '현재가', '등락률', '거래량', '상대볼륨', '시가총액_백만', 
                                           'PER', 'EPS', 'EPS증감률', '배당율', '섹터', '투자의견'])            
    
    return dfRes