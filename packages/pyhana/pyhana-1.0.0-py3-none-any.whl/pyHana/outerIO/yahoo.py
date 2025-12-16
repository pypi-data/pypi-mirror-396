from   bs4      import BeautifulSoup as bs
import time  
import re
import pandas   as pd
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 속도향상 : Pageload Strategy 설정 변경
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "none"

import datetime
from ..common  import urlProc, conf, dataProc

#치환 문자열 
replacements = {
    'Jan':'01',    'Feb':'02',    'Mar':'03',    'Apr':'04',    'May':'05',    'Jun':'06',
    'Jul':'07',    'Aug':'08',    'Sep':'09',    'Oct':'10',    'Nov':'11',    'Dec':'12'
}

def mreplace(text, replacements):
    regex = re.compile("|".join(map(re.escape, replacements.keys())), re.IGNORECASE)

    def rmatch(match):
        return replacements[match.group(0)]

    return regex.sub(rmatch, text)

## 미국 주식 종목 일별 주가 정보 가져오기
def GetStockTradeInfoUSA(shCode='', frDt = '20100101', toDt = '99991231', method='S'):
    return GetEtfTradeInfoUSA(shCode=shCode, frDt = frDt, toDt = toDt, method=method)

## 미국 ETF 종목 일별 주가 정보 가져오기
def GetEtfTradeInfoUSA(shCode='', frDt = '20100101', toDt = '99991231', splitAdjInd = False, method='S'):
    splitRatio = 1
    lstSplitDt = '99991231'
    lstSplitRatio = 1
    
    frSec = (datetime.datetime.strptime(frDt, '%Y%m%d') - datetime.datetime.strptime('19700101', '%Y%m%d')).days *86400
    toSec = (datetime.datetime.strptime(toDt, '%Y%m%d') - datetime.datetime.strptime('19700101', '%Y%m%d')).days *86400
    # frSec, toSec

    urlTmp = "https://finance.yahoo.com/quote/{}/history/?period1={}&period2={}"
    url = urlTmp.format(shCode, frSec, toSec)

    if method == 'S':
        # 크롤링 환경 설정
        options = Options()
        #options.headless = True                                                 # 성능향상
        #options.add_argument("--headless=new")                                  # 성능향상
        #options.add_experimental_option("detach", True)                         # 브라우저 꺼짐 방지 옵션
        #options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 불필요한 에러 메시지 삭제
        #options.add_argument("no-sandbox")                                      # 탭간에 옮겨 다니면서 원하는 액션 수행 가능
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        # chrome 창 open
        try:   
            #driver_path = ChromeDriverManager().install()
            #correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")            
            #chrome = webdriver.Chrome(service=Service(executable_path=correct_driver_path), options=options)            
            chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        except Exception as e:
            print(e)    

        # 데이터 조회 (Selenium) 
        chrome.get(url)   
        WebDriverWait(chrome, 10).until( 
            EC.presence_of_element_located((By.XPATH, '//*[@id="main-content-wrapper"]/div[1]/div[3]'))  )  
            #EC.presence_of_element_located((By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/div[1]/div[3]'))  )  

        #-------------#
        # 데이터 추출 #
        #-------------#
        html_txt = chrome.page_source
        soup = bs(html_txt, "html.parser")        
        
        # ## Selenium 처리 - end    
        chrome.close()        
        
    else:
        headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                   "accept-encoding":"gzip, deflate, br, zstd",
                   "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
                   }
        res = urlProc.requests_url_call(url, headers=headers, method='GET')           
        soup = bs(res.text, "html.parser")

    resData = []
    divData = []
    if len(soup.select("section.container > h1")) == 1:
        shName = soup.select_one("section.container > h1").text
    else:
        shName = ''

    if len(soup.select("table > tbody")) == 1:
        trs = soup.select("table > tbody > tr")

        for tr in trs:
            tds = tr.select("td")
            if len(tds) > 1:
                x = tds[0].text.strip().replace(",","").split()
                if len(x) != 3:
                    print(shCode, "Data not found")
                    break

                trDt = x[2] + mreplace(x[0], replacements) + "%02d"%( int(x[1]) )

                ## 액면분할 등 주식수 변동 시 display
                if tr.text.strip().find('Splits',0) >= 0:
                    print('\r' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), shName, tds[1].text.strip(), '('+trDt+')')
                    if splitAdjInd == True:
                        splitInfo = tds[1].text.replace("Stock Splits","").strip().split(":")
                        lstSplitDt = trDt
                        lstSplitRatio = (int(splitInfo[1]) / int(splitInfo[0]))
                ## 배당금 추출
                elif len(tds) == 2 and tds[1].text.strip().find('Dividend',0) >= 0:
                    divData.append([trDt, float(tds[1].text.replace("Dividend",'').strip().replace(",",""))])                
                ## 주식거래정보 추출
                else:
                    line = [shCode]
                    for idx, td in enumerate(tds):
                        if idx == 0:
#                             x = td.text.strip().replace(",","").split()
                            line.append(trDt)          
                        elif idx <=5:
                            price = float(td.text.strip().replace(",","")) * splitRatio
                            line.append(price)
                        else:
                            volume = int( int(td.text.strip().replace(",","").replace("-","0")) / splitRatio )
                            line.append(volume)
                    resData.append(line)    
                    
                    if splitAdjInd == True and lstSplitDt == trDt:
                        splitRatio *= lstSplitRatio                    
            else:
                print(shCode, "Data not found")

    # 주식거래 + 배당금 merge
    dfTrade = pd.DataFrame(resData, columns=['종목코드','일자','시가','고가','저가','종가','조정가','거래량'])
    dfDividend = pd.DataFrame(divData, columns=['일자','배당금'])
    dfMerge = pd.merge(dfTrade, dfDividend, how='left').sort_values('일자').reset_index(inplace=False).fillna(0)

    return dfMerge[['종목코드','일자','시가','고가','저가','종가','거래량','배당금']]       

## 미국 ETF 종목정보 가져오기
def GetEtfListUSA(method='S'):
    print(datetime.datetime.now(), '미국 ETF 종목정보 가져오기 Start')
    
    urlTmp = "https://finance.yahoo.com/markets/etfs/most-active/?start={}&count={}"
    resData = []
    frCnt = 0
    pgCnt = 100
    
    if method == 'S':
        # 크롤링 환경 설정
        options = Options()
        options.headless = True                                                 # 성능향상
        options.add_experimental_option("detach", True)                         # 브라우저 꺼짐 방지 옵션
        options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 불필요한 에러 메시지 삭제
        options.add_argument("no-sandbox")                                      # 탭간에 옮겨 다니면서 원하는 액션 수행 가능
        # chrome 창 open
        try:            
            driver_path = ChromeDriverManager().install()
            correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
            chrome = webdriver.Chrome(service=Service(executable_path=correct_driver_path), options=options)

        except Exception as e:
            print(e)    
    else:
        # 뷰티풀숲 환경 설정        
        headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                   "accept-encoding":"gzip, deflate, br, zstd",
                   "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
                   }        

    while 1:        
        url = urlTmp.format(frCnt, pgCnt)
        print('\r' + str(datetime.datetime.now()), url, end='')
        
        if method == 'S':
            # 데이터 조회 (Selenium) 
            chrome.get(url)   
            # pagenationContainer 페이지 번호 부분
            WebDriverWait(chrome, 10).until( 
                EC.presence_of_element_located((By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[1]/div/div[2]'))  )  
                
            html_txt = chrome.page_source
            soup = bs(html_txt, "html.parser")            
        else:
            res = urlProc.requests_url_call(url, headers=headers, method='GET')           
            soup = bs(res.text, "html.parser")

            
        if len(soup.select("table > tbody")) == 1 and len(soup.select("table > tbody > tr")) > 1:
            trs = soup.select("table > tbody > tr")

            for tr in trs:
                # x = tr.select("td")[0].select("div > span")
                x = tr.select("td")
                resData.append([x[0].text.strip(), x[1].text.strip()])
        else:
            break

        frCnt += pgCnt
        
    if method == 'S':
        # ## Selenium 처리 - end        
        chrome.close()    

    print('\r' + str(datetime.datetime.now()), '미국 ETF 종목정보 가져오기 End : ', len(resData), '개 종목', ' '*50)
    return pd.DataFrame(sorted(resData), columns=['종목코드','종목명'])